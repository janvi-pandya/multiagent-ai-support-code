"""
agents/router_with_sentiment.py
Drop-in replacement for router.py that adds sentiment-aware routing.

Usage (in main.py):
    from agents.router_with_sentiment import SentimentAwareRouter
    router = SentimentAwareRouter()
"""

import json
import asyncio
from typing import List, Dict, Any

from agents.billing   import BillingAgent
from agents.technical import TechnicalAgent
from agents.product   import ProductAgent
from agents.complaint import ComplaintAgent
from agents.faq       import FAQAgent
from agents.llm_client import GROQ_MODEL, client
from agents.sentiment import SentimentAgent
from rag.pipeline     import RAGPipeline

AGENT_REGISTRY: Dict[str, Any] = {
    "billing":   BillingAgent(),
    "technical": TechnicalAgent(),
    "product":   ProductAgent(),
    "complaint": ComplaintAgent(),
    "faq":       FAQAgent(),
}

SENTIMENT_TONE_PROMPTS = {
    "empathetic":    "\n\nIMPORTANT: This customer is frustrated or distressed. Lead with genuine empathy, acknowledge their feelings explicitly before any solution.",
    "professional":  "",
    "friendly":      "\n\nIMPORTANT: This customer seems satisfied. Keep the tone warm and friendly.",
}


class IntentDetectionAgent:
    SYSTEM_PROMPT = """You are an intent router for TechMart Electronics customer support.
Return ONLY raw JSON (no markdown):
{"intent":"short phrase","agents":["billing"|"technical"|"product"|"complaint"|"faq"],"reasoning":"one sentence"}
Select ALL relevant agents. A message may need multiple."""

    async def detect(self, message: str, history: List[Dict]) -> Dict:
        msgs = [{"role": m["role"], "content": m["content"]} for m in history[-4:]]
        msgs.append({"role": "user", "content": message})
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": self.SYSTEM_PROMPT}] + msgs,
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        return json.loads(response.choices[0].message.content)


class SentimentAwareRouter:
    """
    Full pipeline:
      sentiment analysis → intent detection → agent calls (parallel) → aggregate
    """

    def __init__(self):
        self.intent_agent   = IntentDetectionAgent()
        self.sentiment_agent = SentimentAgent()
        self.rag             = RAGPipeline()

    async def route(self, message: str, session_id: str, history: List[Dict]) -> Dict:
        # ── Run sentiment + intent detection in parallel ──────────────────────
        sentiment_task = self.sentiment_agent.analyse(message, history)
        intent_task    = self.intent_agent.detect(message, history)
        sentiment_result, routing = await asyncio.gather(sentiment_task, intent_task)

        selected = routing.get("agents", ["faq"])

        # ── Sentiment-based agent injection ──────────────────────────────────
        if sentiment_result["is_frustrated"] and "complaint" not in selected:
            selected = ["complaint"] + selected

        # ── RAG retrieval (shared context) ────────────────────────────────────
        rag_context = await self.rag.retrieve(message, top_k=4)

        # ── Build tone modifier for each agent's system prompt ───────────────
        tone = sentiment_result.get("recommended_tone", "professional")
        tone_suffix = SENTIMENT_TONE_PROMPTS.get(tone, "")

        # ── Call all agents in parallel ───────────────────────────────────────
        async def call_agent(key: str):
            agent = AGENT_REGISTRY[key]
            # Temporarily patch system prompt with tone guidance
            original = agent.SYSTEM_PROMPT
            agent.SYSTEM_PROMPT = original + tone_suffix
            resp = await agent.respond(message, history, rag_context)
            agent.SYSTEM_PROMPT = original
            return {"agent": key, "response": resp}

        agent_results = await asyncio.gather(*[call_agent(k) for k in selected if k in AGENT_REGISTRY])

        # ── Aggregate ─────────────────────────────────────────────────────────
        labels = {
            "billing":   "💳 Billing", "technical": "🔧 Technical Support",
            "product":   "📦 Product Info", "complaint": "🚨 Complaint Resolution",
            "faq":       "❓ General Info",
        }

        if len(agent_results) == 1:
            final_response = agent_results[0]["response"]
        else:
            final_response = "\n\n".join(
                f"**{labels.get(r['agent'], r['agent'])}**\n{r['response']}"
                for r in agent_results
            )

        # ── Escalation notice ─────────────────────────────────────────────────
        escalation_data = {}
        if sentiment_result.get("escalate"):
            flags = sentiment_result.get("risk_flags", [])
            flag_text = ", ".join(flags) if flags else "high distress level"
            final_response += (
                "\n\n---\n"
                "⚠️ **Your case has been flagged for priority human review.**\n"
                f"Reason: {flag_text}. A senior specialist will follow up within 2 hours."
            )
            escalation_data = {
                "escalated": True,
                "reason": flag_text,
                "risk_flags": flags,
            }

        return {
            "response":  final_response,
            "agents":    selected,
            "intent":    routing.get("intent"),
            "reasoning": routing.get("reasoning"),
            "sentiment": {
                "label":        sentiment_result.get("sentiment"),
                "score":        round(sentiment_result.get("sentiment_score", 0), 2),
                "urgency":      sentiment_result.get("urgency"),
                "tone_applied": tone,
            },
            "sources":   rag_context,
            **escalation_data,
        }
