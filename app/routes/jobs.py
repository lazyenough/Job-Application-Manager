from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
import requests
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.dependencies import getDB
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.schemas.ingestion import JobIngestRequest, JobIngestPreviewResponse
from app.services.job_services import createJob, deleteJob, isJobExists, readJobById, readJobs, updateJob
from app.services.ingestion_service import ingest_job_url, preview_job_ingestion, preview_job_ingestion_debug
from app.services.login_service import get_current_user


jobs_router = APIRouter(prefix="/jobs", tags=["Jobs APIs"])


def getJobByID(db: Session, job_id: UUID, current_user: User):
    job = readJobById(db, job_id, current_user)
    
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found with job ID: {job_id}")

    return job


# @jobs_router.get("", response_model=list[JobResponse])
# def getJobsEndpoint(job_status: str | None = None, company_name: str | None = None, db: Session = Depends(getDB)):
#     return readJobs(db, job_status, company_name)


@jobs_router.post("", response_model=JobResponse)
def createJobEndpoint(job_data: JobCreate, db: Session = Depends(getDB), current_user: User = Depends(get_current_user)):
    return createJob(db, job_data, current_user)


@jobs_router.get("/{job_id}", response_model=JobResponse)
def getJobByIdEndpoint(job_id: UUID, db: Session = Depends(getDB), current_user: User = Depends(get_current_user)): 
    job = getJobByID(db, job_id, current_user)
    
    return job


@jobs_router.patch("/{job_id}", response_model=JobResponse)
def updateJobEndpoint(job_id: UUID, job_data: JobUpdate, db: Session = Depends(getDB), current_user: User = Depends(get_current_user)):
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this job record."
        )
    job = getJobByID(db, job_id, current_user)
    updated_job = updateJob(db, job, job_data, current_user)
    
    return updated_job


@jobs_router.delete("/{job_id}")
def deleteJobEndpoint(job_id: UUID, db: Session = Depends(getDB), current_user: User = Depends(get_current_user)):
    job = getJobByID(db, job_id, current_user)
    deleteJob(db, job)

    return {"message": f"Job with ID: {job_id}, deleted successfully."}


# @jobs_router.post("/ingest", response_model=JobResponse)
# def ingest_job(job_request: JobIngestRequest, db: Session = Depends(getDB)):
#     try:
#         return ingest_job_url(db, str(job_request.job_url))
#     except requests.exceptions.RequestException as exc:
#         raise HTTPException(status_code=502, detail=f"Failed to fetch job page: {str(exc)}")
#     except ValueError as exc:
#         raise HTTPException(status_code=422, detail=str(exc))


@jobs_router.post("/ingest", response_model=JobResponse)
def ingest_job(job_data: JobCreate, db: Session = Depends(getDB), current_user: User = Depends(get_current_user)):
    try:
        return createJob(db, job_data, current_user)
    except IntegrityError:
        # Catch duplicate URLs and rollback the failed transaction
        db.rollback()
        raise HTTPException(status_code=409, detail="This job URL has already been saved.")
    except requests.exceptions.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Failed to save job: {str(exc)}")
    

@jobs_router.post("/ingest/preview", response_model=JobIngestPreviewResponse)
def preview_job_ingest(job_request: JobIngestRequest, db: Session = Depends(getDB), current_user: User = Depends(get_current_user)):
    try:
        if isJobExists(db, str(job_request.job_url), current_user):
            raise HTTPException(
                status_code=409, 
                detail="This job has already been saved."
        )
        return preview_job_ingestion(str(job_request.job_url))
    except requests.exceptions.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch job page: {str(exc)}")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@jobs_router.post("/ingest/preview/debug")
def preview_job_ingest_debug(job_request: JobIngestRequest):
    try:
        return preview_job_ingestion_debug(str(job_request.job_url))
    except requests.exceptions.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch job page: {str(exc)}")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@jobs_router.get("", response_model=List[JobResponse])
def get_user_jobs(
    db: Session = Depends(getDB),
    # 🔒 CRITICAL: This dependency forces FastAPI to check for a valid session cookie first
    current_user: User = Depends(get_current_user) 
):
    """
    Fetches only the jobs belonging to the logged-in user.
    If no cookie is present, get_current_user will automatically 
    raise a 401 Unauthorized error.
    """
    # Filter the database query so users only see their own rows
    user_jobs = db.query(Job).filter(Job.user_id == current_user.id).all()
    
    return user_jobs