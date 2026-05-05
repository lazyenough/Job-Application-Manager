from pydantic import BaseModel, HttpUrl


class JobIngestRequest(BaseModel):
    job_url: HttpUrl