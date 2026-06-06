from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime
from .database import Base

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    role_type = Column(String)  # RN, PN, or NA
    seniority = Column(String)  # Senior, Junior, or N/A
    ward = Column(String, default="แผนก ER (ฉุกเฉิน)")  # Ward assignment
    is_active = Column(Boolean, default=True)

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)  # e.g., H1, H2, U1
    name = Column(String)
    description = Column(String)
    rule_type = Column(String) # Global, Unit, Specific
    is_active = Column(Boolean, default=True)

class ScheduleHistory(Base):
    __tablename__ = "schedule_history"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    period = Column(String, index=True) # e.g., "2024-03"
    department = Column(String) # e.g., "ER"
    schedule_data = Column(JSON) # Store the generated schedule JSON here
    fairness_score = Column(Integer, nullable=True) # Score given by the system

class WardConfig(Base):
    __tablename__ = "ward_config"

    id = Column(Integer, primary_key=True, index=True)
    ward_name = Column(String, unique=True, index=True)  # e.g., "แผนก ER"
    config = Column(JSON)  # Staffing requirements per shift

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, index=True)
    staff_name = Column(String)
    leave_date = Column(String)  # e.g., "2026-03-05"
    leave_type = Column(String, default="ลาป่วย")  # ลาป่วย, ลาพักร้อน, ลากิจ
    reason = Column(String, default="")
    status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, default="")
    role = Column(String, default="nurse")  # admin, head_nurse, nurse
    ward = Column(String, default="แผนก ER (ฉุกเฉิน)")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class SwapRequest(Base):
    __tablename__ = "swap_requests"

    id = Column(Integer, primary_key=True, index=True)
    requester_username = Column(String, index=True)
    requester_name = Column(String)
    request_date = Column(String)  # YYYY-MM-DD
    request_shift = Column(String)
    target_username = Column(String, index=True)
    target_name = Column(String)
    target_date = Column(String)  # YYYY-MM-DD
    target_shift = Column(String)
    ward = Column(String, index=True)
    status = Column(String, default="pending_target")  # pending_target, accepted_target, rejected_target, approved, rejected_admin
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
