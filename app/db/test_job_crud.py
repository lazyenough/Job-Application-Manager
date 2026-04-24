from datetime import date
from uuid import UUID

from app.services.job_services import createJob, readJobs, updateJob, deleteJob
from app.db.session import SessionLocal
from app.schemas.job import JobCreate, JobUpdate, JobResponse


if __name__ == "__main__":
    db = SessionLocal()

    new_job = JobCreate(
        job_url="https://example.com/job/789",
        job_title="ML Engineer",
        company_name="Acme AI",
        location="Bengaluru",
        work_mode="remote",
        job_description="Build AI systems.",
        date_posted=date.today(),
        status="saved"
    )

    created_job = createJob(db, new_job)
    job_response = JobResponse.model_validate(created_job)
    print(job_response.model_dump())
    print("Created:", created_job.id, created_job.job_title)

    jobs = readJobs(db)
    for job in jobs:
        print(job.id, job.job_title, job.status)

    job_update = JobUpdate(
        status="applied",
        location="Hyderabad",
    )
    updated_job = updateJob(db, created_job.id, job_update)
    updated_response = JobResponse.model_validate(updated_job)
    print(updated_response.model_dump())
    # if updated_job:
    #     print("Updated Job with job_id:", updated_job.id, updated_job.status, updated_job.location)

    deleted = deleteJob(db, created_job.id)
    print("Deleted:", deleted)
