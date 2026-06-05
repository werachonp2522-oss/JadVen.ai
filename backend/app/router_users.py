from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.router_auth import get_current_user, hash_password, require_admin

router = APIRouter(prefix="/users", tags=["User Management"])

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str = ""
    role: str = "nurse"  # admin, head_nurse, nurse
    ward: str = "แผนก ER (ฉุกเฉิน)"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    ward: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None  # optional password change

@router.get("/")
def list_users(current_user: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    result = [{"id": u.id, "username": u.username, "full_name": u.full_name,
               "role": u.role, "ward": u.ward, "is_active": u.is_active} for u in users]
    return result

@router.post("/")
def create_user(req: UserCreate, current_user: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username นี้มีอยู่แล้ว")
    user = models.User(
        username=req.username,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role=req.role,
        ward=req.ward,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "สร้างผู้ใช้สำเร็จ", "id": user.id}

@router.put("/{user_id}")
def update_user(user_id: int, req: UserUpdate, current_user: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้")
    if req.full_name is not None: user.full_name = req.full_name
    if req.role is not None: user.role = req.role
    if req.ward is not None: user.ward = req.ward
    if req.is_active is not None: user.is_active = req.is_active
    if req.password: user.hashed_password = hash_password(req.password)
    db.commit()
    return {"message": "อัปเดตข้อมูลสำเร็จ"}

@router.delete("/{user_id}")
def delete_user(user_id: int, current_user: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้")
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="ไม่สามารถลบ admin ได้")
    db.delete(user)
    db.commit()
    return {"message": "ลบผู้ใช้สำเร็จ"}
