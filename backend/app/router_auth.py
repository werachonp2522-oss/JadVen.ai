from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
import os
import secrets
import logging

router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    logging.warning("⚠️ SECRET_KEY is not set in environment! Using a stable default key.")
    SECRET_KEY = "jadven_default_stable_secret_key_for_development_purposes"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="บัญชีถูกระงับการใช้งาน")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "ward": user.ward,
        }
    }

@router.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "ward": current_user.ward,
        "is_active": current_user.is_active,
    }

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UpdateProfileRequest(BaseModel):
    full_name: str

@router.put("/change-password")
def change_password(req: ChangePasswordRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(req.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="รหัสผ่านปัจจุบันไม่ถูกต้อง")
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="รหัสผ่านใหม่ต้องมีอย่างน้อย 6 ตัวอักษร")
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    user.hashed_password = hash_password(req.new_password)
    db.commit()
    return {"message": "เปลี่ยนรหัสผ่านสำเร็จ"}

@router.put("/profile")
def update_profile(req: UpdateProfileRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    user.full_name = req.full_name
    db.commit()
    updated = {"id": user.id, "username": user.username, "full_name": user.full_name, "role": user.role, "ward": user.ward}
    return {"message": "อัปเดตโปรไฟล์สำเร็จ", "user": updated}
