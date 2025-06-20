from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Location(BaseModel):
    country: str
    region: str
    coordinates: dict = Field(..., example = {"type": "Point", "coordinates": [35.2027, 31.9038]})

class Perpetrator(BaseModel):
    name: str
    type: str

class Evidence(BaseModel):
    type: str = Field(description = "Type of evidence, e.g., 'photo', 'video', 'pdf'")
    url: str
    description: Optional[str] = None
    date_captured: datetime = Field(default_factory = datetime.utcnow)

class Case(Document):
    case_id: str = Field(..., unique = True, description = "Unique human-readable case identifier")
    title: str = Field(..., max_length = 100)
    description: Optional[str] = Field(None, max_length = 500)
    violation_types: List[str]
    status: str = Field(default = "new", description = "Can be 'new', 'under_investigation', 'resolved'")
    priority: str = Field(default = "medium", description = "Can be 'low', 'medium', 'high'")
    location: Location
    date_occurred: datetime
    date_reported: datetime = Field(default_factory = datetime.utcnow)
    victims: Optional[List[PydanticObjectId]] = None
    perpetrators: Optional[List[Perpetrator]] = None
    created_by: PydanticObjectId
    is_archived: bool = Field(default = False, description = "Whether the case is archived or not")
    evidence: Optional[List[Evidence]] = Field(default=[])

    class Settings:
        name = "cases"

class UpdateCase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    violation_types: Optional[List[str]] = None
    status: Optional[str] = None
    priority: Optional[str] = None

    class Config:
        orm_mode = True

class CaseStatusHistory(Document):
    case_id: PydanticObjectId
    previous_status: str
    new_status: str
    changed_at: datetime = Field(default_factory = datetime.utcnow)
    changed_by: PydanticObjectId

    class Settings:
        name = "case_status_history"