from typing import List

from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

# from app.models.job import Job

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    
    jobs: Mapped[List["Job"]] = relationship(
        "Job",
        back_populates="owner", 
        cascade="all, delete-orphan"
    )