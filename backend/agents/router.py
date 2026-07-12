"""
agents/router.py
Intent Detection Agent + Agent Router

Workflow:
  1. IntentDetectionAgent analyses the customer query
  2. AgentRouter selects and invokes specialized agents
  3. ResponseAggregator merges multi-agent outputs
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
from rag.pipeline     import RAGPipeline

AGENT_REGISTRY: Dict[str, Any] = {
    "billing":   BillingAgent(),
    "technical": TechnicalAgent(),
    "product":   ProductAgent(),
    "complaint": ComplaintAgent(),
    "faq":       FAQAgent(),
}


class IntentDetectionAgent:
    """Classifies customer intent and selects relevant agents."""

    SYSTEM_PROMPT = """You are an intent detection system for TechMart Electronics customer support.
Analyse the customer message and return ONLY raw JSON:
{
  "intent": "<brief phrase>",
  "agents": ["billing"|"technical"|"product"|"complaint"|"faq"],
  "confidence": 0.0-1.0,
  "reasoning": "<one sentence>"
}
Choose ALL relevant agents. A single message may require multiple."""

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


class AgentRouter:
    """Routes a query to the correct specialized agent(s) and aggregates results."""

    def __init__(self):
        self.intent_agent = IntentDetectionAgent()
        self.rag = RAGPipeline()

    async def route(
        self,
        message: str,
        session_id: str,
        history: List[Dict],
    ) -> Dict:
        # Step 1 – intent detection
        routing = await self.intent_agent.detect(message, history)
        selected = routing.get("agents", ["faq"])

        # Step 2 – RAG retrieval (shared context for all agents)
        rag_context = await self.rag.retrieve(message, top_k=4)

        # Step 3 – invoke agents in parallel
        tasks = [
            AGENT_REGISTRY[key].respond(message, history, rag_context)
            for key in selected
            if key in AGENT_REGISTRY
        ]
        results = await asyncio.gather(*tasks)

        # Step 4 – aggregate
        agent_outputs = [
            {"agent": selected[i], "response": results[i]}
            for i in range(len(results))
        ]

        final = ResponseAggregator.merge(agent_outputs)

        return {
            "intent":    routing.get("intent"),
            "agents":    selected,
            "reasoning": routing.get("reasoning"),
            "response":  final,
            "sources":   rag_context,
        }


class ResponseAggregator:
    """Merges multiple agent responses into a single coherent reply."""

    @staticmethod
    def merge(agent_outputs: List[Dict]) -> str:
        if len(agent_outputs) == 1:
            return agent_outputs[0]["response"]

        sections = []
        labels = {
            "billing":   "💳 Billing",
            "technical": "🔧 Technical Support",
            "product":   "📦 Product Info",
            "complaint": "🚨 Escalation",
            "faq":       "❓ General Info",
        }
        for item in agent_outputs:
            label = labels.get(item["agent"], item["agent"].title())
            sections.append(f"**{label}**\n{item['response']}")

        return "\n\n".join(sections)
