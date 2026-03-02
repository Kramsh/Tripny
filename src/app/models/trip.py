import datetime
from uuid import uuid4, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import DateTime, ForeignKey


class Base(DeclarativeBase):
    pass


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str]
    description: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now())


class TripFile(Base):
    __tablename__ = "trip_files"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    trip_id: Mapped[UUID] = mapped_column(ForeignKey("trips.id"))
    filename: Mapped[str]
    s3_key: Mapped[str]
    content_type: Mapped[str]
