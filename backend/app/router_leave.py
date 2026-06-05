from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from typing import Optional
from app.router_auth import require_authenticated, require_head_nurse_or_admin

router = APIRouter(prefix="/leave", tags=["Leave Requests"])

class LeaveCreate(BaseModel):
    staff_id: int
    staff_name: str
    leave_date: str
    leave_type: str = "ลาป่วย"
    reason: str = ""

class LeaveUpdate(BaseModel):
    status: str  # approved, rejected

@router.get("/")
def get_all_leaves(current_user: models.User = Depends(require_head_nurse_or_admin), db: Session = Depends(get_db)):
    leaves = db.query(models.LeaveRequest).order_by(models.LeaveRequest.created_at.desc()).all()
    result = [{"id": l.id, "staff_id": l.staff_id, "staff_name": l.staff_name,
               "leave_date": l.leave_date, "leave_type": l.leave_type,
               "reason": l.reason, "status": l.status,
               "created_at": str(l.created_at)} for l in leaves]
    return result

@router.post("/")
def create_leave(req: LeaveCreate, current_user: models.User = Depends(require_authenticated), db: Session = Depends(get_db)):
    leave = models.LeaveRequest(
        staff_id=req.staff_id, staff_name=req.staff_name,
        leave_date=req.leave_date, leave_type=req.leave_type,
        reason=req.reason
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return {"message": "Leave request created", "id": leave.id}

@router.put("/{leave_id}")
def update_leave_status(leave_id: int, req: LeaveUpdate, current_user: models.User = Depends(require_head_nurse_or_admin), db: Session = Depends(get_db)):
    leave = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    leave.status = req.status
    db.commit()
    return {"message": f"Leave {req.status}"}

@router.delete("/{leave_id}")
def delete_leave(leave_id: int, current_user: models.User = Depends(require_head_nurse_or_admin), db: Session = Depends(get_db)):
    leave = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    db.delete(leave)
    db.commit()
    return {"message": "Leave deleted"}
