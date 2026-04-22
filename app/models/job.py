from uuid import uuid4
from uuid import UUID as PyUUID

from sqlalchemy import Date, DateTime, String, Text, Boolean, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Job(Base):
    __tablename__ = "Job"

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid = True),
        primary_key=True,
        default=uuid4
    )
    job_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    job_title: Mapped[str | None] = mapped_column(String(255), unique=False, nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), unique=False, nullable=True)
    