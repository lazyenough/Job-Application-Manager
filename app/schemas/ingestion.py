from pydantic import BaseModel, HttpUrl


class JobIngestRequest(BaseModel):
    job_url: HttpUrl
    

class JobIngestPreviewResponse(BaseModel):
    job_url: HttpUrl
    job_title: str | None
    job_description_preview: str | None
    work_mode: str | None
    company_name: str | None
    location: str | None