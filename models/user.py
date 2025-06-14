from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class User(Document):
    username: str = Field(..., unique = True, min_length = 3, max_length = 50, description = "Unique username")
    password: str
    email: Optional[str] = Field(None, unique = True)
    created_at: datetime = Field(default_factory = datetime.utcnow)

    class Settings:
        name = "users"

class Login(BaseModel):
    username: str
    password: str

class CurrentUser(BaseModel):
    id: PydanticObjectId
    username: str