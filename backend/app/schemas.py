from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime

# --- Staff Schemas ---
class StaffBase(BaseModel):
    employee_id: str
    name: str
    role_type: str
    seniority: str
    ward: str = "แผนก ER (ฉุกเฉิน)"
    is_active: bool = True

class StaffCreate(StaffBase):
    pass

class Staff(StaffBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Rule Schemas ---
class RuleBase(BaseModel):
    code: str
    name: str
    description: str
    rule_type: str
    is_active: bool = True

class RuleCreate(RuleBase):
    pass

class Rule(RuleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Schedule History Schemas ---
class ScheduleHistoryBase(BaseModel):
    period: str
    department: str
    schedule_data: Any # JSON
    fairness_score: Optional[int] = None

class ScheduleHistoryCreate(ScheduleHistoryBase):
    pass

class ScheduleHistory(ScheduleHistoryBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Ward Config Schemas ---
class WardConfigBase(BaseModel):
    ward_name: str
    config: Any  # JSON

class WardConfigCreate(WardConfigBase):
    pass

class WardConfig(WardConfigBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

