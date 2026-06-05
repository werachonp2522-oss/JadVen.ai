from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from . import crud, schemas
from .database import get_db

router = APIRouter(prefix="/ward-config", tags=["Ward Configuration"])

@router.get("/", response_model=List[schemas.WardConfig])
def get_all_configs(db: Session = Depends(get_db)):
    return crud.get_all_ward_configs(db)

@router.get("/{ward_name}", response_model=schemas.WardConfig)
def get_config(ward_name: str, db: Session = Depends(get_db)):
    config = crud.get_ward_config(db, ward_name)
    if not config:
        return {"error": "Ward not found"}
    return config

@router.put("/{config_id}", response_model=schemas.WardConfig)
def update_config(config_id: int, config_data: dict, db: Session = Depends(get_db)):
    return crud.update_ward_config(db, config_id, {"config": config_data})

@router.post("/", response_model=schemas.WardConfig)
def create_config(config: schemas.WardConfigCreate, db: Session = Depends(get_db)):
    # Check if exists
    existing = crud.get_ward_config(db, config.ward_name)
    if existing:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Ward name already exists")
    
    # If config dict is empty, provide default setup
    if not config.config:
        config.config = {
            "shifts": {
                "M": {"label": "08:00 - 16:00", "min_total": 5, "min_rn": 3, "min_na": 1},
                "E": {"label": "16:00 - 00:00", "min_total": 4, "min_rn": 2, "min_na": 1},
                "N": {"label": "00:00 - 08:00", "min_total": 3, "min_rn": 2, "min_na": 1}
            },
            "max_shifts_per_week": 5,
            "min_shifts_per_week": 1
        }
    return crud.create_ward_config(db, config)

@router.delete("/{config_id}")
def delete_config(config_id: int, db: Session = Depends(get_db)):
    success = crud.delete_ward_config(db, config_id)
    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Ward config not found")
    return {"status": "success", "message": "Ward deleted successfully"}
