"""api/auth.py – JWT Authentication"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt, bcrypt, uuid
from datetime import datetime, timedelta

router  = APIRouter()
bearer  = HTTPBearer()
SECRET  = "CHANGE_THIS_IN_PRODUCTION"
ALGO    = "HS256"

def create_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.utcnow() + timedelta(hours=24)}
    return jwt.encode(payload, SECRET, algorithm=ALGO)

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        data = jwt.decode(creds.credentials, SECRET, algorithms=[ALGO])
        return {"id": data["sub"]}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(body: RegisterRequest):
    user_id = str(uuid.uuid4())
    return {"token": create_token(user_id), "user_id": user_id}

@router.post("/login")
async def login(body: LoginRequest):
    user_id = str(uuid.uuid4())
    return {"token": create_token(user_id), "user_id": user_id}
