from datetime import date
from uuid import UUID

from app.services.job_services import createJob, readJobs, updateJobStatus, deleteJob
from app.db.session import SessionLocal


if __name__ == "__main__":
    db = SessionLocal()

    created_job = createJob(
        db,
        job_url="https://example.com/job/789",
        job_title="ML Engineer",
        company_name="Acme AI",
        location="Bengaluru",
        work_mode="remote",
        job_description="Build AI systems.",
        date_posted=date.today(),
    )
    print("Created:", created_job.id, created_job.job_title)

    jobs = readJobs(db)
    for job in jobs:
        print(job.id, job.job_title, job.status)

    updated_job = updateJobStatus(db, created_job.id, "applied")
    if updated_job:
        print("Updated:", updated_job.id, updated_job.status)

    deleted = deleteJob(db, created_job.id)
    print("Deleted:", deleted)
