"""api/chat.py – Chat endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
from agents.router import AgentRouter
from api.auth import get_current_user

router = AgentRouter()
api    = APIRouter()

class ChatRequest(BaseModel):
    message:    str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response:   str
    agents:     List[str]
    intent:     str
    session_id: str
    message_id: str
    timestamp:  str

@api.post("/message", response_model=ChatResponse)
async def send_message(body: ChatRequest, user=Depends(get_current_user)):
    session_id = body.session_id or str(uuid.uuid4())
    try:
        result = await router.route(message=body.message, session_id=session_id, history=[])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return ChatResponse(
        response=result["response"], agents=result["agents"],
        intent=result["intent"], session_id=session_id,
        message_id=str(uuid.uuid4()), timestamp=datetime.utcnow().isoformat(),
    )

@api.get("/history/{session_id}")
async def get_history(session_id: str, user=Depends(get_current_user)):
    return {"session_id": session_id, "messages": []}
