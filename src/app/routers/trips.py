from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.schemas.trip import TripCreate, TripResponse
from src.app.models.trip import Trip, TripFile
from src.app.database import get_db
from sqlalchemy import select
from uuid import UUID
from src.app.services.storage import upload_file
from fastapi import UploadFile


router = APIRouter()


@router.post("/trips", response_model=TripResponse)
async def create_trip(trip: TripCreate, db: AsyncSession = Depends(get_db)):
    db_trip = Trip(title=trip.title, description=trip.description)
    db.add(db_trip)
    await db.commit()
    await db.refresh(db_trip)
    return db_trip


@router.get("/trips", response_model=list[TripResponse])
async def get_trips(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trip))
    trips = result.scalars().all()
    return trips


@router.get("/trips/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    return trip


@router.post("/trips/{trip_id}/files")
async def add_files(
    trip_id: UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db)
):
    content = await file.read()
    s3_key = await upload_file(content, file.filename, file.content_type)
    trip_file = TripFile(
        trip_id=trip_id,
        filename=file.filename,
        s3_key=s3_key,
        content_type=file.content_type
    )
    db.add(trip_file)
    await db.commit()
    await db.refresh(trip_file)
    return trip_file
