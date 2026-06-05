from sqlalchemy.orm import Session
from . import models, schemas

# --- Staff CRUD ---
def get_staff(db: Session, staff_id: int):
    return db.query(models.Staff).filter(models.Staff.id == staff_id).first()

def get_staff_by_employee_id(db: Session, employee_id: str):
    return db.query(models.Staff).filter(models.Staff.employee_id == employee_id).first()

def get_all_staff(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Staff).offset(skip).limit(limit).all()

def create_staff(db: Session, staff: schemas.StaffCreate):
    db_staff = models.Staff(**staff.model_dump())
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    return db_staff

def update_staff(db: Session, staff_id: int, staff_data: dict):
    db.query(models.Staff).filter(models.Staff.id == staff_id).update(staff_data)
    db.commit()
    return get_staff(db, staff_id)

def delete_staff(db: Session, staff_id: int):
    db_staff = get_staff(db, staff_id)
    if db_staff:
        db.delete(db_staff)
        db.commit()
        return True
    return False

# --- Rules CRUD ---
def get_rule(db: Session, rule_id: int):
    return db.query(models.Rule).filter(models.Rule.id == rule_id).first()

def get_all_rules(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Rule).offset(skip).limit(limit).all()

def create_rule(db: Session, rule: schemas.RuleCreate):
    db_rule = models.Rule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def toggle_rule(db: Session, rule_id: int, is_active: bool):
    db.query(models.Rule).filter(models.Rule.id == rule_id).update({"is_active": is_active})
    db.commit()
    return get_rule(db, rule_id)

# --- Schedule History CRUD ---
def get_schedule_history(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.ScheduleHistory).order_by(models.ScheduleHistory.created_at.desc()).offset(skip).limit(limit).all()

def create_schedule_history(db: Session, schedule: schemas.ScheduleHistoryCreate):
    db_schedule = models.ScheduleHistory(**schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

# --- Ward Config CRUD ---
def get_ward_config(db: Session, ward_name: str):
    return db.query(models.WardConfig).filter(models.WardConfig.ward_name == ward_name).first()

def get_all_ward_configs(db: Session):
    return db.query(models.WardConfig).all()

def create_ward_config(db: Session, config: schemas.WardConfigCreate):
    db_config = models.WardConfig(**config.model_dump())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def update_ward_config(db: Session, config_id: int, config_data: dict):
    db.query(models.WardConfig).filter(models.WardConfig.id == config_id).update(config_data)
    db.commit()
    return db.query(models.WardConfig).filter(models.WardConfig.id == config_id).first()

def delete_ward_config(db: Session, config_id: int):
    db_config = db.query(models.WardConfig).filter(models.WardConfig.id == config_id).first()
    if db_config:
        db.delete(db_config)
        db.commit()
        return True
    return False

