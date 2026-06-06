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
    start_on_call_staff_id: Optional[str] = None

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
    
    # Calculate start date of the roster period
    start_date = None
    if request.period:
        try:
            if len(request.period) == 7:  # "YYYY-MM"
                year, month = map(int, request.period.split("-"))
                start_date = dt.date(year, month, 1)
            elif len(request.period) == 10:  # "YYYY-MM-DD"
                start_date = dt.date.fromisoformat(request.period)
        except Exception:
            pass

    if not start_date:
        today = dt.date.today()
        start_date = dt.date(today.year, today.month, 1)

    for leave in approved_leaves:
        try:
            leave_date = dt.date.fromisoformat(leave.leave_date)
            day_idx = (leave_date - start_date).days
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


    # Dynamic active shifts list
    # Always starts with "OFF" as index 0
    active_shifts = ["OFF"]
    if shift_reqs:
        active_shifts += list(shift_reqs.keys())
    else:
        # Fallback to standard M, E, N
        active_shifts += ["M", "E", "N"]
        shift_reqs = {
            "M": {"min_total": 1, "min_rn": 1},
            "E": {"min_total": 1, "min_rn": 0},
            "N": {"min_total": 1, "min_rn": 1}
        }
    
    OFF = 0
    num_shifts = len(active_shifts)
    
    # Map shift string codes to indices
    MORNING = active_shifts.index("M") if "M" in active_shifts else -1
    EVENING = active_shifts.index("E") if "E" in active_shifts else -1
    NIGHT = active_shifts.index("N") if "N" in active_shifts else -1
    
    # Model
    model = cp_model.CpModel()

    # Variables: shift_matrix[n, d] = shift assigned to nurse n on day d
    shift_matrix = {}
    for n in all_nurses:
        for d in all_days:
            shift_matrix[(n, d)] = model.NewIntVar(0, num_shifts - 1, f'shift_n{n}d{d}')

    # --- Approved Leave: Force OFF on leave days ---
    for nurse_idx, leave_days in leave_map.items():
        if nurse_idx < num_nurses:
            for day_idx in leave_days:
                if 0 <= day_idx < num_days:
                    model.Add(shift_matrix[(nurse_idx, day_idx)] == OFF)

    # --- Constraints ---
    is_it_dept = False
    if request.department:
        dept_lower = request.department.lower()
        # Match various IT department name formats (Thai/English)
        if ("it" in dept_lower or 
            "ไอที" in request.department or 
            "ไอที" in dept_lower or
            "งานit" in dept_lower or
            "แผนกit" in dept_lower or
            "information technology" in dept_lower):
            is_it_dept = True

    if is_it_dept:
        # IT Specific Constraints
        
        # 1. Segment days into weeks (7 days)
        weeks = []
        for start_day in range(0, num_days, 7):
            end_day = min(start_day + 7, num_days)
            # Qualify as a week if it has at least 4 days
            if (end_day - start_day) >= 4:
                weeks.append(range(start_day, end_day))
        num_weeks = len(weeks)
        
        # 2. Weekly on-call variables (0 or 1)
        # week_on_call[n, w] = 1 if IT staff n is on-call during week w
        week_on_call = {}
        for n in all_nurses:
            for w in range(num_weeks):
                week_on_call[(n, w)] = model.NewBoolVar(f'week_on_call_n{n}_w{w}')
                
        # 3. Weekly On-Call Constraints
        for w in range(num_weeks):
            # Exactly 1 person is ON_CALL (NIGHT) per week
            model.Add(sum(week_on_call[(n, w)] for n in all_nurses) == 1)
            
            for n in all_nurses:
                # If on-call this week, shifts for all days in this week are NIGHT
                # If not on-call, shifts cannot be NIGHT (must be MORNING or OFF)
                for d in weeks[w]:
                    if NIGHT != -1:
                        model.Add(shift_matrix[(n, d)] == NIGHT).OnlyEnforceIf(week_on_call[(n, w)])
                        model.Add(shift_matrix[(n, d)] != NIGHT).OnlyEnforceIf(week_on_call[(n, w)].Not())
                    
        # 4. Rotation: No consecutive weeks on-call
        for n in all_nurses:
            for w in range(num_weeks - 1):
                model.Add(week_on_call[(n, w)] + week_on_call[(n, w+1)] <= 1)

        # 4a. Special limit: any staff with '470' in their ID/name → at most 1 on-call week per month
        for n in all_nurses:
            nurse_id   = request.nurses[n].id
            nurse_name = request.nurses[n].name
            if '470' in nurse_id or '470' in nurse_name:
                model.Add(sum(week_on_call[(n, w)] for w in range(num_weeks)) <= 1)

        # 4.5. On-Call Continuity and Manual Override for Week 1 (Week index 0)
        forced_start_idx = None
        if request.start_on_call_staff_id:
            # Try to match by nurse id
            for idx, nurse in enumerate(request.nurses):
                if nurse.id == request.start_on_call_staff_id:
                    forced_start_idx = idx
                    break

        prev_period = None
        if request.period and len(request.period) == 7:  # "YYYY-MM"
            try:
                y, m = map(int, request.period.split("-"))
                if m == 1:
                    prev_y, prev_m = y - 1, 12
                else:
                    prev_y, prev_m = y, m - 1
                prev_period = f"{prev_y:04d}-{prev_m:02d}"
            except Exception:
                pass

        last_on_call_staff_name = None
        if prev_period:
            prev_schedule_record = db.query(models.ScheduleHistory).filter(
                models.ScheduleHistory.period == prev_period,
                models.ScheduleHistory.department == (request.department or "งานไอที")
            ).order_by(models.ScheduleHistory.created_at.desc()).first()

            if prev_schedule_record and prev_schedule_record.schedule_data:
                try:
                    prev_schedule = prev_schedule_record.schedule_data
                    max_n_shifts = 0
                    for row in prev_schedule:
                        nurse_name = row.get("nurse")
                        shifts = row.get("shifts", [])
                        last_7_shifts = shifts[-7:] if len(shifts) >= 7 else shifts
                        n_count = last_7_shifts.count("N")
                        if n_count > max_n_shifts:
                            max_n_shifts = n_count
                            last_on_call_staff_name = nurse_name
                except Exception:
                    pass

        prev_nurse_idx = None
        if last_on_call_staff_name:
            for idx, nurse in enumerate(request.nurses):
                if nurse.name == last_on_call_staff_name:
                    prev_nurse_idx = idx
                    break

        # Apply constraints based on override or automatic transition
        override_objective_terms = []
        if forced_start_idx is not None:
            # Manual override: force selected nurse to start on-call in Week 1
            model.Add(week_on_call[(forced_start_idx, 0)] == 1)
        elif prev_nurse_idx is not None and num_nurses > 1:
            # Rule 1: The last on-call staff of previous month cannot be on-call in week 1
            model.Add(week_on_call[(prev_nurse_idx, 0)] == 0)
            
            # Rule 2: Soft preference for the next nurse in sequence
            next_nurse_idx = (prev_nurse_idx + 1) % num_nurses
            pref_term = model.NewIntVar(0, 5, f'pref_term_next')
            model.Add(pref_term == 5 * (1 - week_on_call[(next_nurse_idx, 0)]))
            override_objective_terms.append(pref_term)
                
        # 5. Office Hours (MORNING) covering weekdays
        import datetime as dt
        start_date = None
        if request.period:
            try:
                if len(request.period) == 7:  # "YYYY-MM"
                    year, month = map(int, request.period.split("-"))
                    start_date = dt.date(year, month, 1)
                elif len(request.period) == 10:  # "YYYY-MM-DD"
                    start_date = dt.date.fromisoformat(request.period)
            except Exception:
                pass
        if not start_date:
            today = dt.date.today()
            start_date = dt.date(today.year, today.month, 1)
            
        for d in all_days:
            current_date = start_date + dt.timedelta(days=d)
            is_wkday = current_date.weekday() < 5 # Monday-Friday
            
            if is_wkday:
                # Weekdays: Non-on-call staff MUST be working MORNING (M)
                for w_idx, w_range in enumerate(weeks):
                    if d in w_range:
                        for n in all_nurses:
                            if MORNING != -1:
                                model.Add(shift_matrix[(n, d)] == MORNING).OnlyEnforceIf(week_on_call[(n, w_idx)].Not())
            else:
                # Weekends: Non-on-call staff must be OFF
                # That means only the on-call person is working (NIGHT). The rest are OFF (0).
                for w_idx, w_range in enumerate(weeks):
                    if d in w_range:
                        for n in all_nurses:
                            model.Add(shift_matrix[(n, d)] == OFF).OnlyEnforceIf(week_on_call[(n, w_idx)].Not())

        # 6. Workload and Fairness Balancing
        # Calculate total worked shifts for each staff member
        nurse_total_shifts = []
        for n in all_nurses:
            working_days = []
            for d in all_days:
                is_working = model.NewBoolVar(f'is_working_n{n}_d{d}')
                model.Add(shift_matrix[(n, d)] != OFF).OnlyEnforceIf(is_working)
                model.Add(shift_matrix[(n, d)] == OFF).OnlyEnforceIf(is_working.Not())
                working_days.append(is_working)
            total_shifts = model.NewIntVar(0, num_days, f'total_shifts_n{n}')
            model.Add(total_shifts == sum(working_days))
            nurse_total_shifts.append(total_shifts)
            
        # Define nurse_night_counts (needed for final fairness evaluation)
        nurse_night_counts = []
        for n in all_nurses:
            night_bools = []
            for d in all_days:
                is_night = model.NewBoolVar(f'is_night_count_n{n}d{d}')
                if NIGHT != -1:
                    model.Add(shift_matrix[(n, d)] == NIGHT).OnlyEnforceIf(is_night)
                    model.Add(shift_matrix[(n, d)] != NIGHT).OnlyEnforceIf(is_night.Not())
                else:
                    model.Add(is_night == 0)
                night_bools.append(is_night)
            total_nights = model.NewIntVar(0, num_days, f'total_nights_n{n}')
            model.Add(total_nights == sum(night_bools))
            nurse_night_counts.append(total_nights)

        # Minimize difference in workload
        avg_shifts = num_days // len(all_nurses) if len(all_nurses) > 0 else 0
        objective_terms = []
        for n in all_nurses:
            diff = model.NewIntVar(-num_days, num_days, f'diff_n{n}')
            model.Add(diff == nurse_total_shifts[n] - avg_shifts)
            abs_diff = model.NewIntVar(0, num_days, f'abs_diff_n{n}')
            model.Add(abs_diff >= diff)
            model.Add(abs_diff >= -diff)
            objective_terms.append(abs_diff)
            
        if override_objective_terms:
            objective_terms.extend(override_objective_terms)
            
        model.Minimize(sum(objective_terms))

    else:
        # H1: "ห้ามดึกต่อเช้า" (Night -> Morning is blocked)
        if "H1" in active_rule_codes and NIGHT != -1 and MORNING != -1:
            for n in all_nurses:
                for d in range(num_days - 1):
                    is_night_today = model.NewBoolVar(f'is_night_n{n}d{d}')
                    model.Add(shift_matrix[(n, d)] == NIGHT).OnlyEnforceIf(is_night_today)
                    model.Add(shift_matrix[(n, d)] != NIGHT).OnlyEnforceIf(is_night_today.Not())
                    
                    is_morning_tomorrow = model.NewBoolVar(f'is_morning_n{n}d{d+1}')
                    model.Add(shift_matrix[(n, d+1)] == MORNING).OnlyEnforceIf(is_morning_tomorrow)
                    model.Add(shift_matrix[(n, d+1)] != MORNING).OnlyEnforceIf(is_morning_tomorrow.Not())
                    
                    model.AddImplication(is_night_today, is_morning_tomorrow.Not())

        # S1: "ห้ามบ่ายต่อเช้า" (Evening -> Morning is blocked - Quick Return)
        if "S1" in active_rule_codes and EVENING != -1 and MORNING != -1:
            for n in all_nurses:
                for d in range(num_days - 1):
                    is_eve_today = model.NewBoolVar(f'is_eve_n{n}d{d}')
                    model.Add(shift_matrix[(n, d)] == EVENING).OnlyEnforceIf(is_eve_today)
                    model.Add(shift_matrix[(n, d)] != EVENING).OnlyEnforceIf(is_eve_today.Not())
                    
                    is_morn_tomorrow = model.NewBoolVar(f'is_morn_s1_n{n}d{d+1}')
                    model.Add(shift_matrix[(n, d+1)] == MORNING).OnlyEnforceIf(is_morn_tomorrow)
                    model.Add(shift_matrix[(n, d+1)] != MORNING).OnlyEnforceIf(is_morn_tomorrow.Not())
                    
                    model.AddImplication(is_eve_today, is_morn_tomorrow.Not())

        # W2: "จำกัดการทำงานติดต่อกันสูงสุด" (Max 6 consecutive working days)
        if "W2" in active_rule_codes:
            for n in all_nurses:
                for d in range(num_days - 6):
                    consec_days = range(d, d + 7)
                    offs = []
                    for cd in consec_days:
                        is_off = model.NewBoolVar(f'consec_off_n{n}d{cd}')
                        model.Add(shift_matrix[(n, cd)] == OFF).OnlyEnforceIf(is_off)
                        model.Add(shift_matrix[(n, cd)] != OFF).OnlyEnforceIf(is_off.Not())
                        offs.append(is_off)
                    model.Add(sum(offs) >= 1)

        # Setup roles
        rn_indices = [i for i, n in enumerate(request.nurses) if n.type == 'RN']
        
        # Helper: count people assigned to a specific shift
        def count_shift(model, shift_matrix, shift_val, indices, day, prefix):
            bools = [model.NewBoolVar(f'{prefix}_d{day}_n{n}') for n in indices]
            for n, b in zip(indices, bools):
                model.Add(shift_matrix[(n, day)] == shift_val).OnlyEnforceIf(b)
                model.Add(shift_matrix[(n, day)] != shift_val).OnlyEnforceIf(b.Not())
            return bools

        # Apply shift requirements dynamically
        for d in all_days:
            for shift_code, reqs in shift_reqs.items():
                if shift_code in active_shifts:
                    shift_idx = active_shifts.index(shift_code)
                    min_total = reqs.get("min_total", 0)
                    min_rn = reqs.get("min_rn", 0)
                    
                    if min_total > 0:
                        shift_all = count_shift(model, shift_matrix, shift_idx, list(all_nurses), d, f'{shift_code}_all')
                        model.Add(sum(shift_all) >= min_total)
                    if min_rn > 0 and rn_indices:
                        shift_rns = count_shift(model, shift_matrix, shift_idx, rn_indices, d, f'{shift_code}_rn')
                        model.Add(sum(shift_rns) >= min_rn)

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
        total_needed_shifts = sum(reqs.get("min_total", 0) for reqs in shift_reqs.values()) * num_days
        min_shifts = max(1, (total_needed_shifts // num_nurses) - 2) if num_nurses > 0 else 1
        for n in all_nurses:
            model.Add(nurse_total_shifts[n] >= min_shifts)

        # 5B: Night Shift Balancing - กระจายเวรดึกให้เท่ากัน
        nurse_night_counts = []
        for n in all_nurses:
            night_bools = []
            for d in all_days:
                is_night = model.NewBoolVar(f'is_night_count_n{n}d{d}')
                if NIGHT != -1:
                    model.Add(shift_matrix[(n, d)] == NIGHT).OnlyEnforceIf(is_night)
                    model.Add(shift_matrix[(n, d)] != NIGHT).OnlyEnforceIf(is_night.Not())
                else:
                    model.Add(is_night == 0)
                night_bools.append(is_night)
            total_nights = model.NewIntVar(0, num_days, f'total_nights_n{n}')
            model.Add(total_nights == sum(night_bools))
            nurse_night_counts.append(total_nights)

        # 5C: Objective - Minimize total workload difference + night imbalance + weekend unfairness
        avg_shifts = total_needed_shifts // num_nurses if num_nurses > 0 else 0
        
        total_nights_needed = (shift_reqs.get("N", {}).get("min_total", 0) if "N" in active_shifts else 0) * num_days
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
            if NIGHT != -1:
                night_diff = model.NewIntVar(-num_days, num_days, f'night_diff_n{n}')
                model.Add(night_diff == nurse_night_counts[n] - avg_nights)
                abs_night_diff = model.NewIntVar(0, num_days, f'abs_night_diff_n{n}')
                model.Add(abs_night_diff >= night_diff)
                model.Add(abs_night_diff >= -night_diff)
                objective_terms.append(abs_night_diff * 2)

        # W1: "เฉลี่ยวันหยุดสุดสัปดาห์" (Weekend Off Fairness)
        if "W1" in active_rule_codes:
            import datetime as dt
            start_date = None
            if request.period:
                try:
                    if len(request.period) == 7:  # "YYYY-MM"
                        year, month = map(int, request.period.split("-"))
                        start_date = dt.date(year, month, 1)
                    elif len(request.period) == 10:  # "YYYY-MM-DD"
                        start_date = dt.date.fromisoformat(request.period)
                except Exception:
                    pass
            if not start_date:
                today = dt.date.today()
                start_date = dt.date(today.year, today.month, 1)
            
            weekend_indices = []
            for d in all_days:
                current_date = start_date + dt.timedelta(days=d)
                if current_date.weekday() >= 5:  # Saturday or Sunday
                    weekend_indices.append(d)
            
            if weekend_indices and num_nurses > 0:
                nurse_weekend_offs = []
                for n in all_nurses:
                    off_days = []
                    for d in weekend_indices:
                        is_off = model.NewBoolVar(f'wk_off_n{n}_d{d}')
                        model.Add(shift_matrix[(n, d)] == OFF).OnlyEnforceIf(is_off)
                        model.Add(shift_matrix[(n, d)] != OFF).OnlyEnforceIf(is_off.Not())
                        off_days.append(is_off)
                    total_wk_offs = model.NewIntVar(0, len(weekend_indices), f'wk_offs_n{n}')
                    model.Add(total_wk_offs == sum(off_days))
                    nurse_weekend_offs.append(total_wk_offs)
                
                avg_wk_offs = len(weekend_indices) // num_nurses
                for n in all_nurses:
                    diff = model.NewIntVar(-len(weekend_indices), len(weekend_indices), f'wk_diff_n{n}')
                    model.Add(diff == nurse_weekend_offs[n] - avg_wk_offs)
                    abs_diff = model.NewIntVar(0, len(weekend_indices), f'abs_wk_diff_n{n}')
                    model.Add(abs_diff >= diff)
                    model.Add(abs_diff >= -diff)
                    objective_terms.append(abs_diff * 3)

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
