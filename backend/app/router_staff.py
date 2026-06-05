from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, schemas
from .database import get_db

router = APIRouter(prefix="/staff", tags=["Staff"])

@router.get("/", response_model=List[schemas.Staff])
def read_all_staff(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    staff_members = crud.get_all_staff(db, skip=skip, limit=limit)
    return staff_members

@router.post("/", response_model=schemas.Staff)
def create_staff(staff: schemas.StaffCreate, db: Session = Depends(get_db)):
    db_staff = crud.get_staff_by_employee_id(db, employee_id=staff.employee_id)
    if db_staff:
        raise HTTPException(status_code=400, detail="Employee ID already registered")
    return crud.create_staff(db=db, staff=staff)

@router.put("/{staff_id}", response_model=schemas.Staff)
def update_staff(staff_id: int, staff_data: dict, db: Session = Depends(get_db)):
    db_staff = crud.get_staff(db, staff_id=staff_id)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return crud.update_staff(db=db, staff_id=staff_id, staff_data=staff_data)

@router.delete("/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    success = crud.delete_staff(db=db, staff_id=staff_id)
    if not success:
        raise HTTPException(status_code=404, detail="Staff not found")
    return {"message": "Staff successfully deleted"}
