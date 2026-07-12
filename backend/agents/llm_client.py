"""
Shared Groq chat client configuration.
"""

import os

from openai import AsyncOpenAI

GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url=GROQ_BASE_URL,
)
