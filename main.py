from contextlib import asynccontextmanager
import motor
from motor import motor_asyncio
from beanie import init_beanie
from fastapi import FastAPI
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str
    db_name: str
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.db_client = motor.motor_asyncio.AsyncIOMotorClient(settings.db_url)
    await init_beanie(
        database=app.db_client[settings.db_name],
        document_models=[]
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

@app.get("/")
async def root():
    return {"message": "Welcome to the Human Rights Monitor"}