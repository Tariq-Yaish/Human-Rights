from contextlib import asynccontextmanager
import motor
from motor import motor_asyncio
from beanie import init_beanie
from fastapi import FastAPI, Depends
from config import BaseConfig

from models.case import Case, CaseStatusHistory
from models.user import User
from models.incident import IncidentReport
from models.victim import Individual

from routers import cases as  cases_router
from routers import users as users_router
from routers import incidents as incidents_router
from routers import victims as victims_router
from routers.analytics import router as analytics_router

settings = BaseConfig()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.db_client = motor.motor_asyncio.AsyncIOMotorClient(settings.DB_URL)
    await init_beanie(
        database=app.db_client[settings.DB_NAME],
        document_models=[Case, CaseStatusHistory, User, IncidentReport, Individual]
    )
    print("Database Connected")
    yield

    app.db_client.close()
    print("Database Disconnected & Closed")

app = FastAPI(
    title="Human Rights Monitor API",
    summary="Documenting, Tracking & Analyzing Human Rights Violations",
    lifespan=lifespan
)

app.include_router(cases_router.router, tags = ["Cases"], prefix = "/cases")
app.include_router(users_router.router, tags = ["Users"], prefix = "/users")
app.include_router(incidents_router.router, tags = ["Incidents"], prefix = "/reports")
app.include_router(victims_router.router, tags=["Victims"], prefix="/victims")
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Human Rights Monitor."}