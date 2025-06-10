from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Location(BaseModel):
    country: str
    region: str
    coordinates: dict = Field(..., example = {"type": "Points", "coordinates": [29.48762, 59.2487]})

class Perpetrator(BaseModel):
    name: str
    type: str

class Case(BaseModel):
    case_id: str = Field(..., unique=True, description = "Case ID")
    title: str = Field(..., max_length = 100, description = "Case title")
    description: Optional[str] = Field(None, max_length = 500, description = "Case description")
    violation_type: List[str]
    status: str = Field(default = "New", description = "Case status. Value can be 'New', 'Under_Investigation', 'Resolved'")
    priority: str = Field(default = "Normal", description = "Case priority. Value can be 'Normal', 'Low', 'Medium', 'High'.")
    location: Location
    date_occured: datetime
    date_reported: datetime = Field(default_factory = datetime.utcnow)
    victims: Optional[List[PydanticObjectId]] = None
    perpetrators: Optional[List[Perpetrator]] = None
    created_by: PydanticObjectId

    class Settings:
        name = "Case"