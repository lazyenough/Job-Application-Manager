import os
# from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.jobs import jobs_router
from app.db.base import Base
from app.db.session import engine

from contextlib import asynccontextmanager

# load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    
    
app = FastAPI(lifespan=lifespan)

app.include_router(jobs_router)


frontend_url = os.getenv("FRONTEND_URL")

origins = [
    frontend_url,
    "http://localhost:5500", # Common for VS Code Live Server
    "http://localhost:3000", # Common for React/Vue dev servers
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def healthCheck():
    return {"status": "ok"}


@app.get("/")
def read_root():
    return {"message": "API is running"}