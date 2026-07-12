"""
main.py  (updated with all bonus features)
TechMart Electronics – Multi-Agent AI Customer Support Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat       import router as chat_router
from api.auth       import router as auth_router
from api.analytics  import router as analytics_router
from api.whatsapp   import router as whatsapp_router   # ← Bonus: WhatsApp
from database.connection import init_db

app = FastAPI(
    title="TechMart AI Support API",
    description="Multi-Agent Customer Support — RAG + Sentiment + WhatsApp",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(auth_router,      prefix="/api/auth",      tags=["Authentication"])
app.include_router(chat_router,      prefix="/api/chat",      tags=["Chat"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(whatsapp_router,  prefix="/api/whatsapp",  tags=["WhatsApp"])

@app.get("/")
async def root():
    return {"message": "TechMart AI Support API v2.0", "status": "running",
            "features": ["multi-agent", "rag", "sentiment-routing", "whatsapp"]}

@app.get("/health")
async def health():
    return {"status": "healthy"}
