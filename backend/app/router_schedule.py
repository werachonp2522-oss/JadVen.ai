from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ortools.sat.python import cp_model
from . import crud, schemas, models
from .database import get_db

router = APIRouter(prefix="/schedule", tags=["Schedule"])

class Nurse(BaseModel):
    id: str
    name: str
    type: str # 'RN' or 'PN'
    seniority: str # 'Senior' or 'Junior'

class ScheduleRequest(BaseModel):
    num_days: int
    nurses: List[Nurse]
    period: Optional[str] = None      # e.g., "2026-03"
    department: Optional[str] = None  # e.g., "แผนก ER (ฉุกเฉิน)"

@router.post("/generate")
def generate_schedule(request: ScheduleRequest, db: Session = Depends(get_db)):
    # 0. Fetch active rules and ward config from DB
    db_rules = crud.get_all_rules(db)
    active_rule_codes = [r.code for r in db_rules if r.is_active]
    
    # Fetch ward config for specific department or default
    target_ward = request.department or "แผนก ER (ฉุกเฉิน)"
    db_ward_config = crud.get_ward_config(db, target_ward)
    ward_cfg = db_ward_config.config if db_ward_config else None
    
    if not ward_cfg:
        # Fallback to the first available config if target_ward config doesn't exist
        ward_configs = crud.get_all_ward_configs(db)
        ward_cfg = ward_configs[0].config if ward_configs else None
    
    # Extract config values with fallbacks
    max_shifts = ward_cfg.get("max_shifts_per_week", 5) if ward_cfg else 5
    min_shifts_week = ward_cfg.get("min_shifts_per_week", 1) if ward_cfg else 1
    shift_reqs = ward_cfg.get("shifts", {}) if ward_cfg else {}
    
    m_min_total = shift_reqs.get("M", {}).get("min_total", 1)
    m_min_rn = shift_reqs.get("M", {}).get("min_rn", 1)
    e_min_total = shift_reqs.get("E", {}).get("min_total", 1)
    e_min_rn = shift_reqs.get("E", {}).get("min_rn", 0)
    n_min_total = shift_reqs.get("N", {}).get("min_total", 1)
    n_min_rn = shift_reqs.get("N", {}).get("min_rn", 1)

    # Fetch approved leaves → build leave_map: {nurse_index: [day_index, ...]}
    import datetime as dt
    leave_map: dict[int, list[int]] = {}
    approved_leaves = db.query(models.LeaveRequest).filter(
        models.LeaveRequest.status == "approved"
    ).all()
    nurse_name_to_idx = {n.name: i for i, n in enumerate(request.nurses)}
    nurse_id_to_idx = {n.id: i for i, n in enumerate(request.nurses)}
    today = dt.date.today()
    week_start = today - dt.timedelta(days=today.weekday())  # Monday
    for leave in approved_leaves:
        try:
            leave_date = dt.date.fromisoformat(leave.leave_date)
            day_idx = (leave_date - week_start).days
            if 0 <= day_idx < request.num_days:
                # match by staff_name or staff_id
                idx = nurse_name_to_idx.get(leave.staff_name)
                if idx is None:
                    idx = nurse_id_to_idx.get(str(leave.staff_id))
                if idx is not None:
                    leave_map.setdefault(idx, []).append(day_idx)
        except Exception:
            pass

    num_days = request.num_days
    num_nurses = len(request.nurses)
    all_nurses = range(num_nurses)
    all_days = range(num_days)


    # Shifts: 0: OFF, 1: Morning, 2: Evening, 3: Night
    OFF = 0
    MORNING = 1
    EVENING = 2
    NIGHT = 3
    
    # Model
    model = cp_model.CpModel()

    # Variables: shift_matrix[n, d] = shift assigned to nurse n on day d
    shift_matrix = {}
    for n in all_nurses:
        for d in all_days:
            shift_matrix[(n, d)] = model.NewIntVar(0, 3, f'shift_n{n}d{d}')

    # --- Approved Leave: Force OFF on leave days ---
    for nurse_idx, leave_days in leave_map.items():
        if nurse_idx < num_nurses:
            for day_idx in leave_days:
                if 0 <= day_idx < num_days:
                    model.Add(shift_matrix[(nurse_idx, day_idx)] == OFF)

    # --- Constraints ---

    
    # H1: "ห้ามดึกต่อเช้า" (Night -> Morning is blocked)
    if "H1" in active_rule_codes:
        for n in all_nurses:
            for d in range(num_days - 1):
                is_night_today = model.NewBoolVar(f'is_night_n{n}d{d}')
                model.Add(shift_matrix[(n, d)] == NIGHT).OnlyEnforceIf(is_night_today)
                model.Add(shift_matrix[(n, d)] != NIGHT).OnlyEnforceIf(is_night_today.Not())
                
                is_morning_tomorrow = model.NewBoolVar(f'is_morning_n{n}d{d+1}')
                model.Add(shift_matrix[(n, d+1)] == MORNING).OnlyEnforceIf(is_morning_tomorrow)
                model.Add(shift_matrix[(n, d+1)] != MORNING).OnlyEnforceIf(is_morning_tomorrow.Not())
                
                model.AddImplication(is_night_today, is_morning_tomorrow.Not())

    # Setup roles
    rn_indices = [i for i, n in enumerate(request.nurses) if n.type == 'RN']
    na_indices = [i for i, n in enumerate(request.nurses) if n.type != 'RN']
    
    # Helper: count people assigned to a specific shift (defined outside loop to avoid closure issues)
    def count_shift(model, shift_matrix, shift_val, indices, day, prefix):
        bools = [model.NewBoolVar(f'{prefix}_d{day}_n{n}') for n in indices]
        for n, b in zip(indices, bools):
            model.Add(shift_matrix[(n, day)] == shift_val).OnlyEnforceIf(b)
            model.Add(shift_matrix[(n, day)] != shift_val).OnlyEnforceIf(b.Not())
        return bools

    for d in all_days:
        # --- Ward Config based staffing ---
        
        # Morning (M) - min total and min RN from config
        m_all = count_shift(model, shift_matrix, MORNING, list(all_nurses), d, 'm_all')
        model.Add(sum(m_all) >= m_min_total)
        if m_min_rn > 0 and rn_indices:
            m_rns = count_shift(model, shift_matrix, MORNING, rn_indices, d, 'm_rn')
            model.Add(sum(m_rns) >= m_min_rn)
        
        # Evening (E) - min total from config
        e_all = count_shift(model, shift_matrix, EVENING, list(all_nurses), d, 'e_all')
        model.Add(sum(e_all) >= e_min_total)
        if e_min_rn > 0 and rn_indices:
            e_rns = count_shift(model, shift_matrix, EVENING, rn_indices, d, 'e_rn')
            model.Add(sum(e_rns) >= e_min_rn)
        
        # Night (N) - min total and min RN from config
        n_all = count_shift(model, shift_matrix, NIGHT, list(all_nurses), d, 'n_all')
        model.Add(sum(n_all) >= n_min_total)
        if n_min_rn > 0 and rn_indices:
            n_rns = count_shift(model, shift_matrix, NIGHT, rn_indices, d, 'n_rn')
            model.Add(sum(n_rns) >= n_min_rn)

    # H3: Max & Min shifts per week (from WardConfig)
    nurse_total_shifts = []
    for n in all_nurses:
        # Enforce max/min shifts per week (7 days)
        for start_day in range(0, num_days, 7):
            week_days = range(start_day, min(start_day + 7, num_days))
            week_working_days = []
            for d in week_days:
                is_working = model.NewBoolVar(f'is_working_n{n}w{start_day // 7}d{d}')
                model.Add(shift_matrix[(n, d)] != OFF).OnlyEnforceIf(is_working)
                model.Add(shift_matrix[(n, d)] == OFF).OnlyEnforceIf(is_working.Not())
                week_working_days.append(is_working)
            
            # Max shifts per week
            if "H3" in active_rule_codes:
                model.Add(sum(week_working_days) <= max_shifts)
            
            # Min shifts per week (only for full or mostly full weeks)
            if len(week_days) >= 4:
                model.Add(sum(week_working_days) >= min_shifts_week)
                
        # Total shifts for the entire period (used for fairness balancing)
        working_days = []
        for d in all_days:
            is_working = model.NewBoolVar(f'is_working_n{n}d{d}')
            model.Add(shift_matrix[(n, d)] != OFF).OnlyEnforceIf(is_working)
            model.Add(shift_matrix[(n, d)] == OFF).OnlyEnforceIf(is_working.Not())
            working_days.append(is_working)
        
        total_shifts = model.NewIntVar(0, num_days, f'total_shifts_n{n}')
        model.Add(total_shifts == sum(working_days))
        nurse_total_shifts.append(total_shifts)

    # --- Phase 5: Fairness Boost ---
    
    # 5A: Minimum Shift Constraint - ทุกคนต้องได้อย่างน้อย min_shifts กะ
    total_needed_shifts = (m_min_total + e_min_total + n_min_total) * num_days
    min_shifts = max(1, (total_needed_shifts // num_nurses) - 2) if num_nurses > 0 else 1
    for n in all_nurses:
        model.Add(nurse_total_shifts[n] >= min_shifts)

    # 5B: Night Shift Balancing - กระจายเวรดึกให้เท่ากัน
    nurse_night_counts = []
    for n in all_nurses:
        night_bools = []
        for d in all_days:
            is_night = model.NewBoolVar(f'is_night_count_n{n}d{d}')
            model.Add(shift_matrix[(n, d)] == NIGHT).OnlyEnforceIf(is_night)
            model.Add(shift_matrix[(n, d)] != NIGHT).OnlyEnforceIf(is_night.Not())
            night_bools.append(is_night)
        total_nights = model.NewIntVar(0, num_days, f'total_nights_n{n}')
        model.Add(total_nights == sum(night_bools))
        nurse_night_counts.append(total_nights)

    # 5C: Objective - Minimize total workload difference + night imbalance
    avg_shifts = total_needed_shifts // num_nurses if num_nurses > 0 else 0
    
    total_nights_needed = n_min_total * num_days
    avg_nights = total_nights_needed // num_nurses if num_nurses > 0 else 0

    objective_terms = []
    for n in all_nurses:
        # Workload balance
        diff = model.NewIntVar(-num_days, num_days, f'diff_n{n}')
        model.Add(diff == nurse_total_shifts[n] - avg_shifts)
        abs_diff = model.NewIntVar(0, num_days, f'abs_diff_n{n}')
        model.Add(abs_diff >= diff)
        model.Add(abs_diff >= -diff)
        objective_terms.append(abs_diff)
        
        # Night balance (weight x2 because night shifts matter more)
        night_diff = model.NewIntVar(-num_days, num_days, f'night_diff_n{n}')
        model.Add(night_diff == nurse_night_counts[n] - avg_nights)
        abs_night_diff = model.NewIntVar(0, num_days, f'abs_night_diff_n{n}')
        model.Add(abs_night_diff >= night_diff)
        model.Add(abs_night_diff >= -night_diff)
        objective_terms.append(abs_night_diff * 2)

    model.Minimize(sum(objective_terms))

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        schedule = []
        for n in all_nurses:
            nurse_shifts = []
            for d in all_days:
                val = solver.Value(shift_matrix[(n, d)])
                shift_name = "OFF"
                if val == MORNING: shift_name = "M"
                elif val == EVENING: shift_name = "E"
                elif val == NIGHT: shift_name = "N"
                nurse_shifts.append(shift_name)
            
            schedule.append({
                "nurse": request.nurses[n].name,
                "type": request.nurses[n].type,
                "shifts": nurse_shifts
            })
            
        # Calculate Fairness Score (0-100) from solved values
        shift_counts = [solver.Value(nurse_total_shifts[n]) for n in all_nurses]
        night_counts = [solver.Value(nurse_night_counts[n]) for n in all_nurses]
        
        # Workload variance: how spread out are the shift counts?
        avg_actual = sum(shift_counts) / num_nurses if num_nurses > 0 else 0
        workload_diff = sum(abs(s - avg_actual) for s in shift_counts)
        
        # Night variance
        avg_night_actual = sum(night_counts) / num_nurses if num_nurses > 0 else 0
        night_diff_sum = sum(abs(n - avg_night_actual) for n in night_counts)
        
        # Combined score: max 100, penalty for each unit of difference
        max_penalty = num_nurses * 3  # normalize against team size
        raw_penalty = workload_diff + night_diff_sum
        calculated_fairness = max(0, int(100 - (raw_penalty / max(max_penalty, 1)) * 100))

        # Save to database
        period = request.period or dt.date.today().strftime("%Y-%m")
        department = request.department or "แผนก ER (ฉุกเฉิน)"
        db_schedule = schemas.ScheduleHistoryCreate(
            period=period, 
            department=department, 
            schedule_data=schedule,
            fairness_score=calculated_fairness
        )
        crud.create_schedule_history(db, db_schedule)
        
        return {
            "status": "success",
            "message": "Optimal & Fair schedule found!",
            "schedule": schedule,
            "fairness_score": calculated_fairness
        }
    else:
        return {
            "status": "error",
            "message": "No feasible schedule found with the given constraints.",
            "diagnostics": solver.ResponseStats()
        }

@router.get("/history", response_model=List[schemas.ScheduleHistory])
def get_schedule_history(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    history = crud.get_schedule_history(db, skip=skip, limit=limit)
    return history
