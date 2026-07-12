"""
agents/sentiment.py
Sentiment Analysis Agent

Analyses customer messages for:
  - Emotional tone  (frustrated / neutral / positive)
  - Urgency level   (high / medium / low)
  - Risk indicators (chargeback threat, legal mention, viral threat)

Output influences:
  - Agent routing  (frustrated → complaint agent prepended)
  - Response tone  (terse if urgent, empathetic if distressed)
  - Escalation     (auto-flag for human handoff if risk = high)
"""

import json
from typing import Dict, List

from agents.llm_client import GROQ_MODEL, client

# Sentiment score thresholds
FRUSTRATION_THRESHOLD = 0.65   # above → prepend complaint agent
ESCALATION_THRESHOLD  = 0.85   # above → flag for human handoff


class SentimentAgent:
    """
    Classifies customer sentiment before routing.
    Returns a SentimentResult dict consumed by AgentRouter.
    """

    SYSTEM_PROMPT = """You are a customer sentiment analyser for TechMart Electronics.

Analyse the customer message and return ONLY raw JSON (no markdown):
{
  "sentiment":        "frustrated" | "neutral" | "positive",
  "sentiment_score":  0.0 to 1.0,
  "urgency":          "high" | "medium" | "low",
  "urgency_score":    0.0 to 1.0,
  "risk_flags":       ["chargeback", "legal_threat", "social_media_threat", "cancel_subscription"],
  "emotional_cues":   ["brief phrases that indicate the customer's emotion"],
  "recommended_tone": "empathetic" | "professional" | "friendly",
  "needs_human":      true | false,
  "reasoning":        "one sentence"
}

Risk flags to detect:
- chargeback: "dispute", "chargeback", "credit card company", "bank"
- legal_threat: "lawyer", "sue", "legal", "court", "attorney"
- social_media_threat: "twitter", "reddit", "viral", "post about this", "review"
- cancel_subscription: "cancel", "unsubscribe", "refund everything"

needs_human = true if sentiment_score > 0.85 OR urgency_score > 0.85 OR any risk_flags present."""

    async def analyse(self, message: str, history: List[Dict] = None) -> Dict:
        """
        Analyse sentiment of the current message (with conversation context).
        Returns a SentimentResult dict.
        """
        history = history or []

        # Include the last 2 exchanges for context
        context_msgs = [
            {"role": m["role"], "content": m["content"]}
            for m in history[-4:]
        ]
        context_msgs.append({"role": "user", "content": message})

        try:
            response = await client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    *context_msgs,
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=300,
            )
            result = json.loads(response.choices[0].message.content)

            # Normalise & add derived fields
            result.setdefault("risk_flags", [])
            result.setdefault("emotional_cues", [])
            result.setdefault("needs_human", False)
            result["is_frustrated"] = (
                result.get("sentiment_score", 0) >= FRUSTRATION_THRESHOLD
                or result.get("sentiment") == "frustrated"
            )
            result["is_urgent"] = result.get("urgency") == "high"
            result["escalate"]  = (
                result.get("sentiment_score", 0) >= ESCALATION_THRESHOLD
                or bool(result.get("risk_flags"))
                or result.get("needs_human", False)
            )
            return result

        except Exception as e:
            # Graceful fallback – never block the chat
            return {
                "sentiment": "neutral", "sentiment_score": 0.0,
                "urgency": "low", "urgency_score": 0.0,
                "risk_flags": [], "emotional_cues": [],
                "recommended_tone": "professional",
                "needs_human": False, "is_frustrated": False,
                "is_urgent": False, "escalate": False,
                "reasoning": f"Sentiment analysis unavailable: {e}",
            }


class SentimentRouter:
    """
    Wraps AgentRouter and injects sentiment-aware decisions before routing.

    Changes made when sentiment is detected:
      1. Frustrated customers → 'complaint' agent prepended to agent list
      2. Urgent queries      → system prompt includes urgency note
      3. Escalation triggers → response tagged with human-handoff request
      4. Tone injection      → recommended_tone passed to agents
    """

    def __init__(self, base_router):
        self.router    = base_router
        self.sentiment = SentimentAgent()

    async def route(self, message: str, session_id: str, history: List[Dict]) -> Dict:
        # Step 1: Sentiment analysis (parallel-friendly but run first for routing)
        sentiment_result = await self.sentiment.analyse(message, history)

        # Step 2: Standard intent routing
        result = await self.router.route(message, session_id, history)

        # Step 3: Sentiment-based adjustments
        agents = result.get("agents", [])

        if sentiment_result["is_frustrated"] and "complaint" not in agents:
            agents = ["complaint"] + agents          # complaint agent first
            result["agents"] = agents

        if sentiment_result["escalate"] and "complaint" not in agents:
            agents = ["complaint"] + agents
            result["agents"] = agents

        # Step 4: Append escalation notice to response if needed
        if sentiment_result["escalate"]:
            flags = sentiment_result.get("risk_flags", [])
            flag_text = ", ".join(flags) if flags else "high distress"
            escalation_note = (
                "\n\n---\n"
                "⚠️ **This conversation has been flagged for priority human review.**\n"
                f"Reason: {flag_text}. A senior support specialist will follow up within 2 hours."
            )
            result["response"] = result.get("response", "") + escalation_note
            result["escalated"] = True
            result["escalation_reason"] = flag_text

        # Step 5: Attach sentiment data to result
        result["sentiment"] = sentiment_result

        return result


# ─── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio

    agent = SentimentAgent()

    test_messages = [
        "Hi, what are your business hours?",
        "I've been waiting 3 weeks for my refund and no one is responding! This is ridiculous!",
        "I love TechMart Pro, just want to know about the Ultra upgrade.",
        "I'm going to dispute this charge with my credit card company if you don't fix this NOW!",
    ]

    async def run():
        for msg in test_messages:
            r = await agent.analyse(msg)
            print(f"\nMessage : {msg[:60]}...")
            print(f"Sentiment: {r['sentiment']} ({r['sentiment_score']:.2f}) | Urgency: {r['urgency']} | Escalate: {r['escalate']}")
            if r["risk_flags"]:
                print(f"⚠ Risk flags: {r['risk_flags']}")

    asyncio.run(run())
