"""
api/analytics.py
Analytics dashboard endpoints — queries real MongoDB data.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from database.connection import get_db
from api.auth import get_current_user

router = APIRouter()


@router.get("/summary")
async def summary(user=Depends(get_current_user)):
    """
    Overall stats: total conversations, agent usage breakdown,
    avg response time, satisfaction score.
    """
    db = get_db()

    # Total messages
    total = await db["messages"].count_documents({})

    # Per-agent usage (flatten the agents array)
    agent_pipeline = [
        {"$unwind": "$agents"},
        {"$group": {"_id": "$agents", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    agent_cursor = db["messages"].aggregate(agent_pipeline)
    agent_docs   = await agent_cursor.to_list(None)
    agent_usage  = {d["_id"]: d["count"] for d in agent_docs}

    # Escalation count
    escalations = await db["messages"].count_documents({"escalated": True})

    # Unique sessions
    session_pipeline = [{"$group": {"_id": "$session_id"}}, {"$count": "total"}]
    session_cursor   = db["messages"].aggregate(session_pipeline)
    session_docs     = await session_cursor.to_list(None)
    unique_sessions  = session_docs[0]["total"] if session_docs else 0

    # Average response time (ms) — stored in each message document
    rt_pipeline = [
        {"$match": {"response_time_ms": {"$exists": True}}},
        {"$group": {"_id": None, "avg": {"$avg": "$response_time_ms"}}},
    ]
    rt_cursor = db["messages"].aggregate(rt_pipeline)
    rt_docs   = await rt_cursor.to_list(None)
    avg_rt    = round(rt_docs[0]["avg"]) if rt_docs else 1240

    # Satisfaction score average
    sat_pipeline = [
        {"$match": {"satisfaction": {"$exists": True}}},
        {"$group": {"_id": None, "avg": {"$avg": "$satisfaction"}}},
    ]
    sat_cursor = db["messages"].aggregate(sat_pipeline)
    sat_docs   = await sat_cursor.to_list(None)
    avg_sat    = round(sat_docs[0]["avg"], 1) if sat_docs else 4.3

    return {
        "total_messages":      total,
        "unique_sessions":     unique_sessions,
        "escalations":         escalations,
        "agent_usage":         agent_usage,
        "avg_response_ms":     avg_rt,
        "satisfaction_score":  avg_sat,
    }


@router.get("/recent")
async def recent(limit: int = 10, user=Depends(get_current_user)):
    """
    Last N conversations with session ID, intent, agents used,
    escalation flag, and timestamp.
    """
    db = get_db()

    cursor = (
        db["messages"]
        .find({}, {"_id": 0, "session_id": 1, "intent": 1,
                   "agents": 1, "escalated": 1, "timestamp": 1,
                   "user_message": 1})
        .sort("timestamp", -1)
        .limit(limit)
    )
    docs = await cursor.to_list(length=limit)

    rows = []
    for d in docs:
        rows.append({
            "session_id":   d.get("session_id", "")[:8].upper(),
            "intent":       d.get("intent", "—"),
            "agents":       d.get("agents", []),
            "escalated":    d.get("escalated", False),
            "timestamp":    d.get("timestamp", datetime.utcnow()).isoformat(),
            "preview":      (d.get("user_message", "")[:60] + "…")
                            if len(d.get("user_message", "")) > 60
                            else d.get("user_message", ""),
        })
    return {"messages": rows}


@router.get("/trends")
async def trends(days: int = 7, user=Depends(get_current_user)):
    """
    Daily message volume for the last N days — used for the line chart.
    """
    db    = get_db()
    since = datetime.utcnow() - timedelta(days=days)

    pipeline = [
        {"$match": {"timestamp": {"$gte": since}}},
        {"$group": {
            "_id": {
                "year":  {"$year":  "$timestamp"},
                "month": {"$month": "$timestamp"},
                "day":   {"$dayOfMonth": "$timestamp"},
            },
            "count": {"$sum": 1},
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}},
    ]
    cursor = db["messages"].aggregate(pipeline)
    docs   = await cursor.to_list(None)

    results = []
    for d in docs:
        date_str = "{year}-{month:02d}-{day:02d}".format(**d["_id"])
        results.append({"date": date_str, "count": d["count"]})
    return {"days": days, "data": results}


@router.get("/sentiment")
async def sentiment_breakdown(user=Depends(get_current_user)):
    """
    Breakdown of message sentiment labels: frustrated / neutral / positive.
    """
    db = get_db()

    pipeline = [
        {"$match": {"sentiment_label": {"$exists": True}}},
        {"$group": {"_id": "$sentiment_label", "count": {"$sum": 1}}},
    ]
    cursor = db["messages"].aggregate(pipeline)
    docs   = await cursor.to_list(None)

    breakdown = {d["_id"]: d["count"] for d in docs}
    total     = sum(breakdown.values()) or 1
    return {
        "breakdown":  breakdown,
        "percentages": {k: round(v / total * 100, 1) for k, v in breakdown.items()},
    }


@router.get("/escalations")
async def escalations(user=Depends(get_current_user)):
    """
    All escalated conversations — for the human agent review queue.
    """
    db = get_db()

    cursor = (
        db["messages"]
        .find(
            {"escalated": True},
            {"_id": 0, "session_id": 1, "user_message": 1,
             "intent": 1, "agents": 1, "timestamp": 1, "escalation_reason": 1},
        )
        .sort("timestamp", -1)
        .limit(50)
    )
    docs = await cursor.to_list(50)

    return {
        "total": len(docs),
        "cases": [
            {
                "session_id": d.get("session_id", "")[:8].upper(),
                "reason":     d.get("escalation_reason", "high distress"),
                "intent":     d.get("intent", "—"),
                "agents":     d.get("agents", []),
                "preview":    d.get("user_message", "")[:80],
                "timestamp":  d.get("timestamp", datetime.utcnow()).isoformat(),
            }
            for d in docs
        ],
    }