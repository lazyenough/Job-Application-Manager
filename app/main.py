from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes.jobs import jobs_router
from app.db.base import Base
from app.db.session import engine
import app.models

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    
    
app = FastAPI(lifespan=lifespan)

app.include_router(jobs_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/health")
def healthCheck():
    return {"status": "ok"}


@app.get("/")
def serve_home():
    return FileResponse("app/static/index.html")