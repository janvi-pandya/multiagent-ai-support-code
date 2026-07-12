"""
agents/base.py
Base class for all specialized agents.
"""

from typing import List, Dict

from agents.llm_client import GROQ_MODEL, client


class BaseAgent:
    """
    All specialized agents inherit from this class.
    Subclasses must define:
        - SYSTEM_PROMPT : str
        - AGENT_NAME    : str
    """

    SYSTEM_PROMPT: str = ""
    AGENT_NAME:    str = "Base Agent"

    async def respond(
        self,
        user_message: str,
        history: List[Dict],
        rag_context: List[Dict] = None,
    ) -> str:
        """
        Generate a response using this agent's system prompt.
        Injects RAG context when available.
        """
        system = self.SYSTEM_PROMPT

        if rag_context:
            context_block = "\n\n".join(
                f"[Source: {c['source']}]\n{c['text']}" for c in rag_context
            )
            system += f"\n\n--- KNOWLEDGE BASE CONTEXT ---\n{context_block}\n--- END CONTEXT ---"

        msgs = [{"role": m["role"], "content": m["content"]} for m in history[-6:]]
        msgs.append({"role": "user", "content": user_message})

        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": system}] + msgs,
            temperature=0.3,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
