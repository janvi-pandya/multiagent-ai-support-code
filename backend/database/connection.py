"""
database/connection.py  – MongoDB async connection
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = "techmart_support"

_client: AsyncIOMotorClient = None


async def init_db():
    global _client
    _client = AsyncIOMotorClient(MONGO_URI)
    print(f"Connected to MongoDB: {MONGO_URI}")


def get_db():
    return _client[DB_NAME]
