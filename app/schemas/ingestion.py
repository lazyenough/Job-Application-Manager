from datetime import date
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class JobIngestRequest(BaseModel):
    job_url: HttpUrl
    
    
class JobSummary(BaseModel):
    required_experience: str | None = None
    key_skills: list[str] | None = None


class JobIngestPreviewResponse(BaseModel):
    job_url: HttpUrl
    job_title: str | None
    job_description_preview: str | None
    work_mode: str | None
    company_name: str | None
    location: str | None
    job_summary: JobSummary | None


class AIJobExtractionResponse(BaseModel):
    company_name: str | None = None
    job_title: str | None = None
    location: str | None = None
    date_posted: date | None = None
    job_summary: JobSummary | None = None


class IngestionRunResponse(BaseModel):
    ingestion_run_id: UUID
    status: str 
