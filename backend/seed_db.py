from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal, engine
from app import models
from app.router_auth import hash_password

models.Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(models.Staff).count() == 0:
        staff_data = [
            {"employee_id": "RN-A", "name": "นางสาว สมศรี ใจดี", "role_type": "RN", "seniority": "Senior", "ward": "แผนก ER (ฉุกเฉิน)", "is_active": True},
            {"employee_id": "RN-B", "name": "นางสาว มาลี สุขใจ", "role_type": "RN", "seniority": "Junior", "ward": "แผนก ER (ฉุกเฉิน)", "is_active": True},
            {"employee_id": "RN-C", "name": "นาย สมชาย เย็นฤดี", "role_type": "RN", "seniority": "Junior", "ward": "แผนก ER (ฉุกเฉิน)", "is_active": True},
            {"employee_id": "RN-D", "name": "นาง วิลาวัลย์ รักดี", "role_type": "RN", "seniority": "Senior", "ward": "แผนก ER (ฉุกเฉิน)", "is_active": True},
            {"employee_id": "RN-E", "name": "นางสาว พิมพ์ใจ แสนดี", "role_type": "RN", "seniority": "Junior", "ward": "แผนก ER (ฉุกเฉิน)", "is_active": True},
            {"employee_id": "RN-F", "name": "นาย ธนพล สุขสันต์", "role_type": "RN", "seniority": "Junior", "ward": "แผนก ER (ฉุกเฉิน)", "is_active": True},
            {"employee_id": "NA-G", "name": "นาง สุดา ช่วยดี", "role_type": "NA", "seniority": "N/A", "ward": "แผนก ER (ฉุกเฉิน)", "is_active": True},
            {"employee_id": "NA-H", "name": "นาย วิชัย ใจดำ", "role_type": "NA", "seniority": "N/A", "ward": "แผนก ER (ฉุกเฉิน)", "is_active": True},
        ]
        for s in staff_data:
            db.add(models.Staff(**s))
            
    # Seed Rules (upsert by code)
    rules_data = [
        {"code": "H1", "name": "ห้ามดึกต่อเช้า (No Night -> Morning)", "description": "ป้องกันความเหนื่อยล้า พยาบาลที่ลงเวรดึก (08:00) ห้ามลงเวรเช้าในวันถัดไป", "rule_type": "global", "is_active": True},
        {"code": "H3", "name": "จำกัดชั่วโมงทำงาน (Max 5 Shifts)", "description": "พยาบาล 1 คนทำงานได้สูงสุด 5 กะต่อสัปดาห์ (ต้องมีวันหยุดอย่างน้อย 2 วัน)", "rule_type": "global", "is_active": True},
        {"code": "H2", "name": "RN ยืนพื้น (RN Requirement)", "description": "ทุกกะ (เช้า, บ่าย, ดึก) ต้องมีพยาบาลวิชาชีพ (RN) อย่างน้อย 1 คนเสมอ", "rule_type": "unit", "is_active": True},
        {"code": "I1", "name": "คู่หูพยาบาล (Buddy System)", "description": "จับคู่พยาบาลจบใหม่ (Junior) กับพยาบาลพี่เลี้ยง (Senior) เสมอ", "rule_type": "specific", "is_active": False},
        {"code": "S1", "name": "ห้ามบ่ายต่อเช้า (Quick Return Block)", "description": "ป้องกันความเหนื่อยล้าจากการได้พักผ่อนน้อยกว่า 11 ชั่วโมง (ห้ามลงเวรบ่ายแล้วต่อด้วยเวรเช้าวันรุ่งขึ้น)", "rule_type": "global", "is_active": True},
        {"code": "W1", "name": "เฉลี่ยวันหยุดสุดสัปดาห์ (Weekend Off Fairness)", "description": "เกลี่ยการกระจายวันหยุดช่วงเสาร์-อาทิตย์ ให้เจ้าหน้าที่ทุกคนได้รับวันหยุดเท่าเทียมกัน", "rule_type": "global", "is_active": True},
        {"code": "W2", "name": "จำกัดวันทำงานติดต่อกันสูงสุด (Max Consecutive Work)", "description": "ห้ามทำงานติดต่อกันเกิน 6 วันโดยไม่มีวันหยุดขั้นต่ำ 1 วัน", "rule_type": "global", "is_active": True},
    ]
    for r in rules_data:
        existing = db.query(models.Rule).filter(models.Rule.code == r["code"]).first()
        if not existing:
            db.add(models.Rule(**r))
        else:
            # Update values if name/description changes
            existing.name = r["name"]
            existing.description = r["description"]

    # Seed Ward Configs (upsert by ward_name)
    ward_configs = [
        {
            "ward_name": "แผนก ER (ฉุกเฉิน)",
            "config": {
                "shifts": {
                    "M": {"label": "เช้า", "min_rn": 1, "min_na": 0, "min_total": 2},
                    "E": {"label": "บ่าย", "min_rn": 1, "min_na": 0, "min_total": 1},
                    "N": {"label": "ดึก", "min_rn": 1, "min_na": 0, "min_total": 2}
                },
                "max_shifts_per_week": 6,
                "min_shifts_per_week": 1,
                "role_types": ["RN", "NA"]
            }
        },
        {
            "ward_name": "แผนก IT",
            "config": {
                "shifts": {
                    "M": {"label": "ทำงานปกติ", "min_rn": 0, "min_na": 0, "min_total": 1},
                    "E": {"label": "บ่าย (ไม่มี)", "min_rn": 0, "min_na": 0, "min_total": 0},
                    "N": {"label": "เวรประจำสัปดาห์", "min_rn": 0, "min_na": 0, "min_total": 1}
                },
                "max_shifts_per_week": 7,
                "min_shifts_per_week": 1,
                "role_types": ["IT"]
            }
        },
        {
            "ward_name": "แผนกผู้ป่วยนอก (OPD)",
            "config": {
                "shifts": {
                    "M": {"label": "เวรเช้า (08:00 - 16:00)", "min_rn": 1, "min_na": 0, "min_total": 2},
                    "E": {"label": "เวรเย็น (12:00 - 20:00)", "min_rn": 1, "min_na": 0, "min_total": 1}
                },
                "max_shifts_per_week": 5,
                "min_shifts_per_week": 1,
                "role_types": ["RN", "NA"]
            }
        },
        {
            "ward_name": "แผนกเภสัชกรรม (Pharmacy)",
            "config": {
                "shifts": {
                    "M": {"label": "เวรเช้า (08:00 - 16:00)", "min_rn": 1, "min_na": 0, "min_total": 2},
                    "E": {"label": "เวรบ่าย (12:00 - 20:00)", "min_rn": 1, "min_na": 0, "min_total": 1}
                },
                "max_shifts_per_week": 5,
                "min_shifts_per_week": 1,
                "role_types": ["Pharmacist", "Assistant"]
            }
        },
        {
            "ward_name": "แผนกเทคนิคการแพทย์ (Lab)",
            "config": {
                "shifts": {
                    "M": {"label": "เวรเช้า (08:00 - 16:00)", "min_rn": 0, "min_na": 0, "min_total": 2},
                    "E": {"label": "เวรบ่าย (16:00 - 00:00)", "min_rn": 0, "min_na": 0, "min_total": 1},
                    "N": {"label": "เวรดึก (00:00 - 08:00)", "min_rn": 0, "min_na": 0, "min_total": 1}
                },
                "max_shifts_per_week": 6,
                "min_shifts_per_week": 1,
                "role_types": ["Technologist", "Assistant"]
            }
        }
    ]
    for wc in ward_configs:
        existing = db.query(models.WardConfig).filter(models.WardConfig.ward_name == wc["ward_name"]).first()
        if not existing:
            db.add(models.WardConfig(**wc))
        else:
            existing.config = wc["config"]

    # Seed default users
    if db.query(models.User).count() == 0:
        default_users = [
            {"username": "admin", "password": "admin1234", "full_name": "ผู้ดูแลระบบ", "role": "admin", "ward": "แผนก ER (ฉุกเฉิน)"},
            {"username": "headnurse", "password": "nurse1234", "full_name": "หัวหน้าพยาบาล ER", "role": "head_nurse", "ward": "แผนก ER (ฉุกเฉิน)"},
            {"username": "nurse01", "password": "nurse1234", "full_name": "พยาบาล 01", "role": "nurse", "ward": "แผนก ER (ฉุกเฉิน)"},
        ]
        for u in default_users:
            db.add(models.User(
                username=u["username"],
                hashed_password=hash_password(u["password"]),
                full_name=u["full_name"],
                role=u["role"],
                ward=u["ward"],
            ))
        print("✅ Seeded default users:")
        print("   admin / admin1234 (Admin)")
        print("   headnurse / nurse1234 (Head Nurse)")
        print("   nurse01 / nurse1234 (Nurse)")
            
    db.commit()
    db.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()

