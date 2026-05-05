from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import getDB
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.schemas.ingestion import JobIngestRequest
from app.services.job_services import createJob, deleteJob, readJobById, readJobs, updateJob
from app.services.ingestion_service import ingest_job_url


jobs_router = APIRouter(prefix="/jobs", tags=["Jobs APIs"])


def getJobByID(db: Session, job_id: UUID):
    job = readJobById(db, job_id)
    
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found with job ID: {job_id}")

    return job


@jobs_router.get("", response_model=list[JobResponse])
def getJobsEndpoint(job_status: str | None = None, company_name: str | None = None, db: Session = Depends(getDB)):
    return readJobs(db, job_status, company_name)


@jobs_router.post("", response_model=JobResponse)
def createJobEndpoint(job_data: JobCreate, db: Session = Depends(getDB)):
    return createJob(db, job_data)


@jobs_router.get("/{job_id}", response_model=JobResponse)
def getJobByIdEndpoint(job_id: UUID, db: Session = Depends(getDB),): 
    job = getJobByID(db, job_id)
    
    return job


@jobs_router.patch("/jobs/{job_id}", response_model=JobResponse)
def updateJobEndpoint(job_id: UUID, job_data: JobUpdate, db: Session = Depends(getDB)):
    job = getJobByID(db, job_id)
    updated_job = updateJob(db, job, job_data)
    
    return updated_job


@jobs_router.delete("/jobs/{job_id}")
def deleteJobEndpoint(job_id: UUID, db: Session = Depends(getDB)):
    job = getJobByID(db, job_id)
    deleteJob(db, job)

    return {"message": f"Job with ID: {job_id}, deleted successfully."}


@jobs_router.post("/ingest", response_model=JobResponse)
def ingest_job(job_request: JobIngestRequest, db: Session = Depends(getDB)):
    return ingest_job_url(db, str(job_request.job_url))