from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from models.case import Location

class Evidence(BaseModel):
    type: str = Field(description = "Type of evidence: 'photo', 'video' or else.")
    url: str
    description: Optional[str] = None

class ReporterContact(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    preferred_contact: Optional[str] = "email"

class IncidentDetails(BaseModel):
    date: datetime
    location: Location
    description: str
    violation_types: List[str]

class IncidentReport(Document):
    report_id: str = Field(..., unique = True)
    reporter_type: str = "victim"
    anonymous: bool = False
    contact_info: Optional[ReporterContact] = None
    incident_details: IncidentDetails
    evidence: Optional[List[Evidence]] = None
    status: str = Field(default = "new", description = "Can be 'new', 'verified', 'linked_to_case'")
    assigned_to: Optional[PydanticObjectId] = None
    created_at: datetime = Field(default_factory = datetime.utcnow)

    class Settings:
        name = "incident_reports"


class UpdateIncidentReport(BaseModel):
    status: Optional[str] = None

class ViolationTypeAnalytics(BaseModel):
    id: str = Field(alias = "_id")
    count: int