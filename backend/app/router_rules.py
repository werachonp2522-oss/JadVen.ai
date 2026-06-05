from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from . import crud, schemas
from .database import get_db
from app.router_auth import require_authenticated, require_head_nurse_or_admin

router = APIRouter(prefix="/rules", tags=["Rules"])

@router.get("/", response_model=List[schemas.Rule])
def read_all_rules(skip: int = 0, limit: int = 100, current_user = Depends(require_authenticated), db: Session = Depends(get_db)):
    return crud.get_all_rules(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.Rule)
def create_rule(rule: schemas.RuleCreate, current_user = Depends(require_head_nurse_or_admin), db: Session = Depends(get_db)):
    return crud.create_rule(db=db, rule=rule)

@router.put("/{rule_id}/toggle", response_model=schemas.Rule)
def toggle_rule(rule_id: int, is_active: bool, current_user = Depends(require_head_nurse_or_admin), db: Session = Depends(get_db)):
    return crud.toggle_rule(db=db, rule_id=rule_id, is_active=is_active)
