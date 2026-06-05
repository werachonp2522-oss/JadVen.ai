import os
from dotenv import load_dotenv
load_dotenv() # Load environment variables before importing other modules

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router_schedule import router as schedule_router
from app.router_gemini import router as gemini_router
from app.router_staff import router as staff_router
from app.router_rules import router as rules_router
from app.router_ward_config import router as ward_config_router
from app.router_leave import router as leave_router
from app.router_auth import router as auth_router
from app.router_users import router as users_router
from app.database import engine
from app import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="JadVen.ai API", description="API for AI-Driven Nurse Scheduling")

# Configure CORS for frontend access
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
]
cors_env = os.getenv("CORS_ORIGINS")
if cors_env:
    origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to JadVen.ai Backend API"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

app.include_router(schedule_router, prefix="/api")
app.include_router(gemini_router, prefix="/api")
app.include_router(staff_router, prefix="/api")
app.include_router(rules_router, prefix="/api")
app.include_router(ward_config_router, prefix="/api")
app.include_router(leave_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
