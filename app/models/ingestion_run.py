from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from uuid import UUID as PyUUID, uuid4
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    
    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid = True),
        primary_key=True,
        default=uuid4
    )
    job_url: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="queued"
    )
    job_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
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