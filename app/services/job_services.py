from datetime import date

from sqlalchemy import select
from uuid import UUID

from app.db.session import SessionLocal
from app.models.job import Job

def createJob(
    db,
    job_url: str,
    job_title: str | None = None,
    company_name: str | None = None,
    location: str | None = None,
    work_mode: str | None = None,
    job_description: str | None = None,
    date_posted=None,
    status: str = "saved",
) -> Job:

    try:
        job = Job(
            job_url=job_url,
            job_title=job_title,
            company_name=company_name,
            location=location,
            work_mode=work_mode,
            job_description=job_description,
            date_posted=date_posted,
            status=status,
        )

        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    finally:
        db.close()


def readJobs(db) -> list[Job]:
    try:
        statement = select(Job)
        jobs = db.execute(statement).scalars().all()

        return jobs
    finally:
        db.close()


def updateJobStatus(db, job_id: UUID, new_status: str) -> Job:
    try:
        statement = select(Job).where(Job.id == job_id)
        job = db.execute(statement).scalar_one_or_none()

        if job is None:
            print("Job not found")
            db.close()
            return

        job.status = new_status
        db.commit()
        db.refresh(job)
        return job
    finally:
        db.close()


def deleteJob(db, job_id: UUID) -> bool:
    try:
        statement = select(Job).where(Job.id == job_id)
        job = db.execute(statement).scalar_one_or_none()

        if job is None:
            return False

        db.delete(job)
        db.commit()
        return True
    finally:
        db.close()