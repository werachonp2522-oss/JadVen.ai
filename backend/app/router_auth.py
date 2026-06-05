from fastapi import APIRouter, HTTPException, Depends, Request, Response
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
import bcrypt

router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set! The application cannot start without a secure secret key.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

legacy_pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# Simple in-memory rate limiter for failed login attempts
# Key: client_ip (str), Value: list of attempt timestamps (datetime)
failed_login_attempts: dict[str, list[datetime]] = {}

def rate_limit_login(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = datetime.now()
    
    if client_ip in failed_login_attempts:
        # Keep only attempts within the last 5 minutes
        failed_login_attempts[client_ip] = [
            t for t in failed_login_attempts[client_ip]
            if now - t < timedelta(minutes=5)
        ]
        
        # Lockout if 5 or more failed attempts
        if len(failed_login_attempts[client_ip]) >= 5:
            last_attempt = failed_login_attempts[client_ip][-1]
            if now - last_attempt < timedelta(minutes=15):
                minutes_left = int(15 - (now - last_attempt).total_seconds() / 60)
                raise HTTPException(
                    status_code=429,
                    detail=f"คุณป้อนรหัสผ่านผิดเกินกำหนด โปรดลองใหม่ในอีก {max(1, minutes_left)} นาที"
                )

class LoginRequest(BaseModel):
    username: str
    password: str

def verify_password(plain: str, hashed: str) -> bool:
    if hashed.startswith("$2a$") or hashed.startswith("$2b$") or hashed.startswith("$2y$"):
        try:
            return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    try:
        return legacy_pwd_context.verify(plain, hashed)
    except Exception:
        return False

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = None
    
    # 1. Try to extract from Authorization Bearer header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        
    # 2. Fallback to HttpOnly cookie
    if not token:
        token = request.cookies.get("access_token")
        
    if not token:
        raise HTTPException(status_code=401, detail="โปรดเข้าสู่ระบบเพื่อดำเนินการ")
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="โทเค็นไม่ถูกต้อง")
    except JWTError:
        raise HTTPException(status_code=401, detail="โทเค็นไม่ถูกต้องหรือหมดอายุ")
        
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="ไม่พบผู้ใช้")
    return user

# Centralized Role Authorization Dependencies
def require_authenticated(current_user: models.User = Depends(get_current_user)):
    return current_user

def require_head_nurse_or_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ["admin", "head_nurse"]:
        raise HTTPException(status_code=403, detail="เฉพาะหัวหน้าพยาบาลหรือผู้ดูแลระบบเท่านั้น")
    return current_user

def require_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="เฉพาะผู้ดูแลระบบเท่านั้น")
    return current_user

@router.post("/login")
def login(req: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    rate_limit_login(request)
    
    client_ip = request.client.host if request.client else "unknown"
    user = db.query(models.User).filter(models.User.username == req.username).first()
    
    if not user or not verify_password(req.password, user.hashed_password):
        # Record failed attempt
        now = datetime.now()
        failed_login_attempts.setdefault(client_ip, []).append(now)
        raise HTTPException(status_code=401, detail="ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
        
    if not user.is_active:
        raise HTTPException(status_code=403, detail="บัญชีถูกระงับการใช้งาน")
        
    # Clear failed attempts on success
    if client_ip in failed_login_attempts:
        failed_login_attempts.pop(client_ip)
        
    token = create_access_token({"sub": user.username, "role": user.role})
    
    # Set HttpOnly cookie for extra XSS protection
    is_prod = os.getenv("ENVIRONMENT") == "production"
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=is_prod
    )
    
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

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", samesite="lax")
    return {"message": "ออกจากระบบสำเร็จ"}

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
