from app.schemas.ingestion import IngestionRunResponse
from app.models.ingestion_run import IngestionRun


def create_ingestion_run(db, job_url:str) ->  IngestionRunResponse:
    ingestion_run = IngestionRun(
        job_url = job_url,
        status = "queued"
    )
    
    db.add(ingestion_run)
    db.commit()
    db.refresh(ingestion_run)
    
    return IngestionRunResponse(
        ingestion_run_id=ingestion_run.id,
        status=ingestion_run.status,
    )