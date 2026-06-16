import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class UserSession(Base):
    __tablename__ = "user_sessions"

    # Cryptographically secure random string sent to the browser cookie
    session_token: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign Key linking back to the User table
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Lifecycle Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False
    )

    # Optional ORM relationship mapping back to your existing User model
    user: Mapped["User"] = relationship("User")