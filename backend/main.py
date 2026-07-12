"""
TechMart Electronics – Multi-Agent AI Customer Support Backend
FastAPI entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat import router as chat_router
from api.auth import router as auth_router
from api.analytics import router as analytics_router
from database.connection import init_db

app = FastAPI(
    title="TechMart AI Support API",
    description="Multi-Agent Customer Support powered by RAG + LLMs",
    version="1.0.0",
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

@app.get("/")
async def root():
    return {"message": "TechMart AI Support API", "status": "running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
