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


class TripFileResponse(BaseModel):
    id: UUID
    trip_id: UUID
    filename: str
    s3_key: str
    content_type: str

    model_config = ConfigDict(from_attributes=True)


class TripUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
