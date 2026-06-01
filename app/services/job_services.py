from datetime import date

from sqlalchemy import select
from uuid import UUID

from app.db.session import SessionLocal
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate

def createJob(db, job_data: JobCreate, current_user: User) -> Job:

    job = Job(
        job_url=str(job_data.job_url),
        job_title=job_data.job_title,
        company_name=job_data.company_name,
        location=job_data.location,
        work_mode=job_data.work_mode,
        job_description=job_data.job_description,
        date_posted=job_data.date_posted,
        job_summary=job_data.job_summary.model_dump() if job_data.job_summary else None,
        status=job_data.status,
        user_id = current_user.id
    )

    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def readJobs(db, current_user: User, job_status: str | None = None, company_name: str | None = None) -> list[Job]:
    statement = select(Job).where(Job.user_id == current_user.id)

    if job_status is not None:
        statement = statement.where(Job.status == job_status)
    if company_name is not None:
        statement = statement.where(Job.company_name == company_name)

    jobs = db.execute(statement).scalars().all()

    return jobs


def readJobById(db, job_id: UUID, current_user: User):

    statement = select(Job).where(Job.id == job_id).where(Job.user_id == current_user.id)
    job = db.execute(statement).scalar_one_or_none()
    return job


def updateJob(db, job: Job, updated_job: JobUpdate, current_user: User) -> Job:
    update_data = updated_job.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return job


def deleteJob(db, job: Job) -> bool:
    db.delete(job)
    db.commit()
    return


def get_job_by_url(db, job_url: str, current_user: User) -> Job | None:
    statement = select(Job).where(Job.job_url == job_url).where(Job.user_id == current_user.id)
    
    job = db.execute(statement).scalar_one_or_none()
    
    return job


def isJobExists(db, job_url: str, current_user: User) -> bool:
    statement = select(Job).where(Job.job_url == job_url).where(Job.user_id == current_user.id)
    
    job = db.execute(statement).scalar_one_or_none()
    
    if job:
        return True

    return False