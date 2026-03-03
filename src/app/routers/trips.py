from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.schemas.trip import TripCreate, TripResponse, TripFileResponse, TripUpdate
from src.app.models.trip import Trip, TripFile
from src.app.database import get_db
from sqlalchemy import select
from uuid import UUID
from src.app.services.storage import upload_file, get_file_from_storage, delete_file_from_storage
from fastapi import UploadFile, Response


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
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.post("/trips/{trip_id}/files")
async def add_files(
    trip_id: UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db)
):
    content = await file.read()
    s3_key = await upload_file(content, file.filename, file.content_type, trip_id)
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


@router.get("/trips/{trip_id}/files", response_model=list[TripFileResponse])
async def get_files(
    trip_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(TripFile).where(TripFile.trip_id == trip_id))
    files = result.scalars().all()
    return files


@router.get("/trips/{trip_id}/files/{file_id}/download")
async def download_file(
    trip_id: UUID,
    file_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    find_file = await db.execute(select(TripFile).where(
        TripFile.id == file_id, TripFile.trip_id == trip_id
    ))
    file = find_file.scalar_one_or_none()
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    result = await get_file_from_storage(file.s3_key)
    return Response(
        content=result,
        media_type=file.content_type,
        headers={"Content-Disposition": f"attachment; filename={file.filename}"}
    )


@router.delete("/trips/{trip_id}")
async def delete_trip(
    trip_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    find_trip = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = find_trip.scalar_one_or_none()
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    find_trip_files = await db.execute(select(TripFile).where(TripFile.trip_id == trip.id))
    trip_files = find_trip_files.scalars().all()
    for file in trip_files:
        await delete_file_from_storage(file.s3_key)
        await db.delete(file)
    await db.flush()
    await db.delete(trip)
    await db.commit()


@router.delete("/trips/{trip_id}/files/{file_id}")
async def delete_file(
    trip_id: UUID,
    file_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    find_trip = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = find_trip.scalar_one_or_none()
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    find_trip_files = await db.execute(select(TripFile).where(
        TripFile.id == file_id,
        TripFile.trip_id == trip_id))
    file = find_trip_files.scalar_one_or_none()
    if file is None:
        raise HTTPException(status_code=404, detail="File not found")
    await delete_file_from_storage(file.s3_key)
    await db.delete(file)
    await db.commit()


@router.patch("/trips/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: UUID,
    trip: TripUpdate,
    db: AsyncSession = Depends(get_db)
):
    find_trip = await db.execute(select(Trip).where(trip_id == Trip.id))
    found_trip = find_trip.scalar_one_or_none()
    if found_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.title is not None:
        found_trip.title = trip.title
    if trip.description is not None:
        found_trip.description = trip.description
    await db.commit()
    await db.refresh(found_trip)
    return found_trip
