"""
database/models.py
MongoDB document schemas + data-access helpers (Motor async driver).

Collections:
  - users         : account records
  - messages       : individual chat turns
  - conversations  : session-level metadata
"""

from datetime import datetime
from typing import List, Dict, Optional
from database.connection import get_db


class Conversation:
    """Session-level conversation metadata and history retrieval."""

    @staticmethod
    async def get_history(session_id: str, limit: int = 20) -> List[Dict]:
        db = get_db()
        cursor = (
            db["messages"]
            .find({"session_id": session_id})
            .sort("timestamp", 1)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)

        history = []
        for d in docs:
            history.append({"role": "user", "content": d["user_message"], "timestamp": d["timestamp"].isoformat()})
            history.append({"role": "assistant", "content": d["ai_response"], "agents": d.get("agents", []), "timestamp": d["timestamp"].isoformat()})
        return history

    @staticmethod
    async def list_sessions(user_id: str) -> List[Dict]:
        db = get_db()
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$session_id",
                "last_message": {"$max": "$timestamp"},
                "message_count": {"$sum": 1},
            }},
            {"$sort": {"last_message": -1}},
        ]
        results = await db["messages"].aggregate(pipeline).to_list(None)
        return [
            {"session_id": r["_id"], "last_message": r["last_message"].isoformat(), "message_count": r["message_count"]}
            for r in results
        ]


class Message:
    """Individual chat-turn persistence."""

    @staticmethod
    async def save(
        session_id: str,
        user_id: str,
        user_message: str,
        ai_response: str,
        agents: List[str],
        intent: str,
    ):
        db = get_db()
        await db["messages"].insert_one({
            "session_id":   session_id,
            "user_id":      user_id,
            "user_message": user_message,
            "ai_response":  ai_response,
            "agents":       agents,
            "intent":       intent,
            "timestamp":    datetime.utcnow(),
        })


class User:
    """User account helpers."""

    @staticmethod
    async def find_by_email(email: str) -> Optional[Dict]:
        db = get_db()
        return await db["users"].find_one({"email": email})

    @staticmethod
    async def find_by_id(user_id: str) -> Optional[Dict]:
        db = get_db()
        return await db["users"].find_one({"_id": user_id})
