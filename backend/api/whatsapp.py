"""
api/whatsapp.py
WhatsApp Integration via Twilio

Flow:
  WhatsApp user sends message
    → Twilio forwards to POST /api/whatsapp/webhook
    → SentimentAwareRouter processes message
    → TwiML response sent back to Twilio
    → User receives AI reply on WhatsApp

Setup:
  1. pip install twilio
  2. Add to .env:
       TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
       TWILIO_AUTH_TOKEN=your_auth_token
       TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
  3. In Twilio Console → Messaging → WhatsApp Sandbox
     Set Webhook URL: https://your-api.railway.app/api/whatsapp/webhook
  4. Include router in main.py:
       from api.whatsapp import router as whatsapp_router
       app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["WhatsApp"])
"""

import os
import hashlib
import hmac
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator

from agents.router_with_sentiment import SentimentAwareRouter
from database.models import Message

router    = APIRouter()
ai_router = SentimentAwareRouter()

TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER  = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

# In-memory session store (swap for Redis in production)
# Maps WhatsApp number → session_id
_sessions: dict[str, str] = {}


def _get_or_create_session(phone: str) -> str:
    """Return an existing session ID or create a new one for this phone number."""
    import uuid
    if phone not in _sessions:
        _sessions[phone] = str(uuid.uuid4())
    return _sessions[phone]


def _validate_twilio_signature(request_url: str, params: dict, signature: str) -> bool:
    """Verify the request is genuinely from Twilio."""
    if not TWILIO_AUTH_TOKEN:
        return True  # skip validation in dev mode
    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    return validator.validate(request_url, params, signature)


def _format_for_whatsapp(response: str) -> str:
    """
    Convert markdown-ish formatting to WhatsApp-compatible text.
    WhatsApp supports *bold*, _italic_, ~strikethrough~.
    """
    # ** → * for bold
    text = response.replace("**", "*")
    # Section dividers
    text = text.replace("---", "────────────")
    # Remove HTML-style markers
    text = text.replace("<br>", "\n")
    # Trim to WhatsApp's 1600-char message limit
    if len(text) > 1580:
        text = text[:1560] + "\n\n_[Message truncated – visit techmart.com/chat for full reply]_"
    return text.strip()


@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    From:    str = Form(...),
    Body:    str = Form(...),
    To:      str = Form(default=""),
):
    """
    Twilio webhook endpoint.
    Receives an inbound WhatsApp message and returns a TwiML reply.
    """
    # ── Signature validation ──────────────────────────────────────────────────
    form_data  = await request.form()
    params     = dict(form_data)
    signature  = request.headers.get("X-Twilio-Signature", "")
    url        = str(request.url)

    if TWILIO_AUTH_TOKEN and not _validate_twilio_signature(url, params, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    # ── Handle special commands ───────────────────────────────────────────────
    clean_body = Body.strip()
    twiml      = MessagingResponse()

    if clean_body.lower() in ("reset", "new session", "start over"):
        _sessions.pop(From, None)
        twiml.message("🔄 Session cleared! Starting a fresh conversation. How can TechMart help you?")
        return Response(content=str(twiml), media_type="application/xml")

    if clean_body.lower() in ("help", "hi", "hello", "hey"):
        twiml.message(
            "👋 *Welcome to TechMart AI Support!*\n\n"
            "I can help with:\n"
            "💳 Billing & refunds\n"
            "🔧 Technical issues\n"
            "📦 Products & pricing\n"
            "❓ General questions\n\n"
            "Just type your question and I'll connect you to the right specialist instantly."
        )
        return Response(content=str(twiml), media_type="application/xml")

    # ── Route through AI pipeline ─────────────────────────────────────────────
    session_id = _get_or_create_session(From)

    try:
        result = await ai_router.route(
            message=clean_body,
            session_id=session_id,
            history=[],   # extend with DB lookup for multi-turn memory
        )
    except Exception as e:
        twiml.message(
            "⚠️ Sorry, our AI assistant is temporarily unavailable.\n"
            "Please contact us directly:\n"
            "📧 support@techmart.com\n"
            "📞 1-800-TECHMART"
        )
        return Response(content=str(twiml), media_type="application/xml")

    # ── Build WhatsApp reply ──────────────────────────────────────────────────
    agents_used  = result.get("agents", [])
    ai_text      = result.get("response", "")
    sentiment    = result.get("sentiment", {})
    is_escalated = result.get("escalated", False)

    # Agent emoji header
    agent_icons = {
        "billing": "💳", "technical": "🔧",
        "product": "📦", "complaint": "🚨", "faq": "❓",
    }
    header = " ".join(agent_icons.get(a, "") for a in agents_used)
    if header:
        ai_text = f"{header}\n\n{ai_text}"

    # Format for WhatsApp
    whatsapp_reply = _format_for_whatsapp(ai_text)

    # Add escalation follow-up card
    if is_escalated:
        whatsapp_reply += (
            "\n\n────────────\n"
            "🔴 *Priority Case Opened*\n"
            "Case ID: " + session_id[:8].upper() + "\n"
            "A specialist will contact you within 2 hours."
        )

    twiml.message(whatsapp_reply)

    # ── Persist to MongoDB ────────────────────────────────────────────────────
    try:
        await Message.save(
            session_id=session_id,
            user_id=From,
            user_message=clean_body,
            ai_response=result.get("response", ""),
            agents=agents_used,
            intent=result.get("intent", ""),
        )
    except Exception:
        pass  # non-blocking

    return Response(content=str(twiml), media_type="application/xml")


@router.get("/status")
async def whatsapp_status():
    """Health check endpoint to verify WhatsApp integration is configured."""
    return {
        "status": "active",
        "from_number": TWILIO_FROM_NUMBER,
        "auth_configured": bool(TWILIO_AUTH_TOKEN),
        "active_sessions": len(_sessions),
    }


@router.post("/send")
async def send_proactive_message(phone: str, message: str):
    """
    Send a proactive outbound WhatsApp message (e.g. order updates, follow-ups).
    Requires Twilio account to have approved template messages for outbound.
    """
    from twilio.rest import Client
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    if not account_sid or not TWILIO_AUTH_TOKEN:
        raise HTTPException(status_code=500, detail="Twilio credentials not configured")

    client = Client(account_sid, TWILIO_AUTH_TOKEN)
    msg = client.messages.create(
        from_=TWILIO_FROM_NUMBER,
        to=f"whatsapp:{phone}",
        body=message,
    )
    return {"sid": msg.sid, "status": msg.status}
