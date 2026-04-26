from fastapi import FastAPI

from app.routes.jobs import jobs_router


app = FastAPI()

app.include_router(jobs_router)


@app.get("/health")
def healthCheck():
    return {"status": "ok"}
