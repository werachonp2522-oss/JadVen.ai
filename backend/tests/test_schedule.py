import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.router_schedule import router
from app.database import Base, get_db

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app = FastAPI()
app.include_router(router, prefix="/api")
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_generate_schedule_success():
    payload = {
        "num_days": 7,
        "nurses": [
            {"id": "1", "name": "RN-A", "type": "RN", "seniority": "Senior"},
            {"id": "2", "name": "RN-B", "type": "RN", "seniority": "Junior"},
            {"id": "3", "name": "RN-C", "type": "RN", "seniority": "Junior"},
            {"id": "4", "name": "PN-D", "type": "PN", "seniority": "N/A"},
            {"id": "5", "name": "PN-E", "type": "PN", "seniority": "N/A"}
        ]
    }
    response = client.post("/api/schedule/generate", json=payload)
    
    # 1. Check HTTP status and basic structure
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "schedule" in data
    assert len(data["schedule"]) == 5  # 5 nurses
    
    schedule_data = {row["nurse"]: row["shifts"] for row in data["schedule"]}
    
    # 2. Hard Constraint Check: No Night -> Morning
    for nurse, shifts in schedule_data.items():
        for i in range(len(shifts) - 1):
            if shifts[i] == "N":
                assert shifts[i+1] != "M", f"Rule violation: {nurse} has Night followed by Morning on day {i+1} to {i+2}"
                
    # 3. Constraint Check: Max 5 shifts
    for nurse, shifts in schedule_data.items():
        worked_shifts = sum(1 for s in shifts if s != "OFF")
        assert worked_shifts <= 5, f"Rule violation: {nurse} worked {worked_shifts} shifts, which is > 5"

    # 4. Individual Constraint Check (from OR-Tools logic)
    if "RN-A" in schedule_data:
        assert schedule_data["RN-A"][1] == "OFF", "Individual Rule violation: RN-A should be OFF on day 2"
        assert schedule_data["RN-A"][2] == "OFF", "Individual Rule violation: RN-A should be OFF on day 3"
        
    if "PN-D" in schedule_data:
        assert "N" not in schedule_data["PN-D"], "Individual Rule violation: PN-D should have no Night shifts"

def test_generate_schedule_infeasible_lack_of_staff():
    # Provide only 2 nurses for 7 days, which won't meet the minimum staffing requirements
    payload = {
        "num_days": 7,
        "nurses": [
            {"id": "1", "name": "RN-A", "type": "RN", "seniority": "Senior"},
            {"id": "2", "name": "RN-B", "type": "RN", "seniority": "Junior"}
        ]
    }
    response = client.post("/api/schedule/generate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "No feasible schedule found" in data["message"]
