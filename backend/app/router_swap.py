from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import copy
from sqlalchemy.orm.attributes import flag_modified

from . import models, schemas
from .database import get_db
from .router_auth import get_current_user

router = APIRouter(prefix="/swap", tags=["Shift Swapping"])

def swap_shifts_in_history(
    db: Session, 
    ward: str, 
    requester_name: str, 
    target_name: str, 
    request_date: str, 
    target_date: str
) -> bool:
    # Determine periods (format: YYYY-MM)
    p1 = request_date[:7]
    p2 = target_date[:7]
    
    # Day index: 1-indexed date to 0-indexed index
    day_idx1 = int(request_date.split("-")[2]) - 1
    day_idx2 = int(target_date.split("-")[2]) - 1
    
    # Get latest ScheduleHistory for both periods
    history1 = db.query(models.ScheduleHistory).filter(
        models.ScheduleHistory.department == ward,
        models.ScheduleHistory.period == p1
    ).order_by(models.ScheduleHistory.created_at.desc()).first()
    
    history2 = db.query(models.ScheduleHistory).filter(
        models.ScheduleHistory.department == ward,
        models.ScheduleHistory.period == p2
    ).order_by(models.ScheduleHistory.created_at.desc()).first()
    
    if not history1 or not history2:
        return False
        
    if history1.id == history2.id:
        # Swap within the same month/period schedule
        data = copy.deepcopy(history1.schedule_data)
        row_req = next((r for r in data if r["nurse"] == requester_name), None)
        row_tar = next((r for r in data if r["nurse"] == target_name), None)
        
        if row_req and row_tar:
            try:
                shift_req = row_req["shifts"][day_idx1]
                shift_tar = row_tar["shifts"][day_idx2]
                
                row_req["shifts"][day_idx1] = shift_tar
                row_tar["shifts"][day_idx2] = shift_req
                
                history1.schedule_data = data
                db.add(history1)
                flag_modified(history1, "schedule_data")
                db.commit()
                return True
            except IndexError:
                return False
    else:
        # Swap across different month schedules
        data1 = copy.deepcopy(history1.schedule_data)
        data2 = copy.deepcopy(history2.schedule_data)
        
        row_req1 = next((r for r in data1 if r["nurse"] == requester_name), None)
        row_tar1 = next((r for r in data1 if r["nurse"] == target_name), None)
        
        row_req2 = next((r for r in data2 if r["nurse"] == requester_name), None)
        row_tar2 = next((r for r in data2 if r["nurse"] == target_name), None)
        
        if row_req1 and row_tar1 and row_req2 and row_tar2:
            try:
                shift_req = row_req1["shifts"][day_idx1]
                shift_tar = row_tar2["shifts"][day_idx2]
                
                row_req1["shifts"][day_idx1] = shift_tar
                row_tar2["shifts"][day_idx2] = shift_req
                
                history1.schedule_data = data1
                history2.schedule_data = data2
                db.add(history1)
                db.add(history2)
                flag_modified(history1, "schedule_data")
                flag_modified(history2, "schedule_data")
                db.commit()
                return True
            except IndexError:
                return False
    return False

@router.post("/request", response_model=schemas.SwapRequestResponse)
def create_swap_request(
    req: schemas.SwapRequestCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check target user
    target_user = db.query(models.User).filter(
        models.User.username == req.target_username
    ).first()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found"
        )
        
    if target_user.ward != current_user.ward:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target user must belong to the same department"
        )
        
    if target_user.username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot swap shifts with yourself"
        )
        
    db_request = models.SwapRequest(
        requester_username=current_user.username,
        requester_name=current_user.full_name or current_user.username,
        request_date=req.request_date,
        request_shift=req.request_shift,
        target_username=target_user.username,
        target_name=target_user.full_name or target_user.username,
        target_date=req.target_date,
        target_shift=req.target_shift,
        ward=current_user.ward,
        status="pending_target"
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

@router.get("/incoming", response_model=List[schemas.SwapRequestResponse])
def get_incoming_swap_requests(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.SwapRequest).filter(
        models.SwapRequest.target_username == current_user.username,
        models.SwapRequest.ward == current_user.ward
    ).order_by(models.SwapRequest.created_at.desc()).all()

@router.get("/outgoing", response_model=List[schemas.SwapRequestResponse])
def get_outgoing_swap_requests(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.SwapRequest).filter(
        models.SwapRequest.requester_username == current_user.username,
        models.SwapRequest.ward == current_user.ward
    ).order_by(models.SwapRequest.created_at.desc()).all()

@router.get("/pending-approval", response_model=List[schemas.SwapRequestResponse])
def get_pending_approvals(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["admin", "head_nurse"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Head Nurse or Admin role required."
        )
        
    return db.query(models.SwapRequest).filter(
        models.SwapRequest.ward == current_user.ward,
        models.SwapRequest.status == "accepted_target"
    ).order_by(models.SwapRequest.created_at.desc()).all()

@router.put("/{request_id}/respond", response_model=schemas.SwapRequestResponse)
def respond_swap_request(
    request_id: int,
    req_update: schemas.SwapRequestUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_req = db.query(models.SwapRequest).filter(models.SwapRequest.id == request_id).first()
    if not db_req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found"
        )
        
    if db_req.target_username != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only target staff can respond to this request"
        )
        
    if db_req.status != "pending_target":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request is already processed or completed"
        )
        
    if req_update.status not in ["accepted_target", "rejected_target"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status response"
        )
        
    db_req.status = req_update.status
    db.commit()
    db.refresh(db_req)
    return db_req

@router.put("/{request_id}/approve", response_model=schemas.SwapRequestResponse)
def approve_swap_request(
    request_id: int,
    req_update: schemas.SwapRequestUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["admin", "head_nurse"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Head Nurse or Admin role required."
        )
        
    db_req = db.query(models.SwapRequest).filter(models.SwapRequest.id == request_id).first()
    if not db_req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found"
        )
        
    if db_req.ward != current_user.ward:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot approve request from another department"
        )
        
    if db_req.status != "accepted_target":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request must be accepted by target first"
        )
        
    if req_update.status not in ["approved", "rejected_admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action"
        )
        
    if req_update.status == "approved":
        # Modify schedule in database
        success = swap_shifts_in_history(
            db, 
            db_req.ward, 
            db_req.requester_name, 
            db_req.target_name, 
            db_req.request_date, 
            db_req.target_date
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to swap shifts in active schedule. Make sure schedules exist for the dates."
            )
            
    db_req.status = req_update.status
    db.commit()
    db.refresh(db_req)
    return db_req
