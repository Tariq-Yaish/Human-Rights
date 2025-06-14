from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Demographics(BaseModel):
    gender: Optional[str] = None
    age: Optional[int] = None
    ethnicity: Optional[str] = None
    occupation: Optional[str] = None

class VictimContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    secure_messaging: Optional[str] = None

class RiskAssessment(BaseModel):
    level: str = Field(default = "low", description = "Can be 'low', 'medium', 'high'")
    threats: Optional[List[str]] = Field(default = [])
    protection_needed: bool = False

class UpdateVictimRisk(BaseModel):
    level: Optional[str] = None
    threats: Optional[List[str]] = None
    protection_needed: Optional[bool] = None

class Individual(Document):
    individual_id: str = Field(..., unique=True)  # <-- Add this new field
    type: str = Field(default="victim", description="Can be 'victim' or 'witness'")
    anonymous: bool = False
    pseudonym: Optional[str] = None
    demographics: Demographics
    contact_info: VictimContactInfo
    cases_involved: List[PydanticObjectId] = Field(default = [])
    risk_assessment: RiskAssessment = Field(default_factory = RiskAssessment)
    support_services: Optional[List[dict]] = Field(default = []) # Using dict for flexibility
    created_at: datetime = Field(default_factory = datetime.utcnow)
    updated_at: datetime = Field(default_factory = datetime.utcnow)

    class Settings:
        name = "individuals"