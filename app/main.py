from fastapi import FastAPI, Depends, HTTPException

from sqlalchemy.orm import Session

from app.db.dependencies import getDB
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.services.job_services import createJob, readJobs, readJobById, updateJob, deleteJob

from uuid import UUID

app = FastAPI()


@app.get("/health")
def healthCheck():
    return {"status": "ok"}


@app.post("/jobs", response_model=JobResponse)
def createJobEndpoint(job_data: JobCreate, db: Session = Depends(getDB)):
    return createJob(db, job_data)


@app.get("/jobs", response_model=list[JobResponse])
def getJobsEndpoint(db: Session = Depends(getDB)):
    return readJobs(db)


@app.get("/jobs/{job_id}", response_model=JobResponse)
def getJobByIdEndpoint(job_id: UUID, db: Session = Depends(getDB),):
    job = readJobById(db, job_id)

    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found with job ID: {job_id}")
    
    return job


@app.patch("/jobs/{job_id}", response_model=JobResponse)
def updateJobEndpoint(job_id: UUID, job_data: JobUpdate, db: Session = Depends(getDB)):
    updated_job = updateJob(db, job_id, job_data)

    if updated_job is None:
        raise HTTPException(status_code=404, detail=f"Job not found with job ID: {job_id}")
    
    return updated_job


@app.delete("/jobs/{job_id}")
def deleteJobEndpoint(job_id: UUID, db: Session = Depends(getDB)):
    is_deleted = deleteJob(db, job_id)

    if not is_deleted:
        raise HTTPException(status_code=404, detail=f"Job not found with job ID: {job_id}")

    return {"message": f"Job with ID: {job_id}, deleted successfully."}