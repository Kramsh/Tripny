from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TripCreate(BaseModel):
    title: str
    description: str


class TripResponse(BaseModel):
    id: UUID
    title: str
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
