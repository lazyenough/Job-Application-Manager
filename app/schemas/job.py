from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class JobCreate(BaseModel):
    job_url: HttpUrl
    job_title: str | None = Field(default=None, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    work_mode: str | None = Field(default=None, max_length=255)
    job_description: str | None = None
    date_posted: date | None = None
    status: str = Field(default="saved", max_length=50)


class JobUpdate(BaseModel):
    job_title: str | None = Field(default=None, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    work_mode: str | None = Field(default=None, max_length=50)
    job_description: str | None = None
    date_posted: date | None = None
    status: str | None = Field(default=None, max_length=50)


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_url: HttpUrl
    job_title: str | None = None
    company_name: str | None = None
    location: str | None = None
    work_mode: str | None = None
    job_description: str | None = None
    date_posted: date | None = None
    status: str 
    created_at: datetime
    updated_at: datetime