import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()   # Load .env

GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

print("GROQ_API_KEY =", os.getenv("GROQ_API_KEY"))

client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url=GROQ_BASE_URL,
)