from uuid import uuid4
from uuid import UUID as PyUUID
from datetime import date, datetime

from sqlalchemy import Date, DateTime, String, Text, Boolean, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid = True),
        primary_key=True,
        default=uuid4
    )
    job_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    job_title: Mapped[str | None] = mapped_column(String(255), unique=False, nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), unique=False, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), unique=False, nullable=True)
    work_mode : Mapped[str | None] = mapped_column(String(255), unique=False, nullable=True)
    job_description : Mapped[str | None] = mapped_column(Text, unique=False, nullable=True)
    date_posted: Mapped[date | None] = mapped_column(Date, unique=False, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="saved",
        server_default="saved",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )