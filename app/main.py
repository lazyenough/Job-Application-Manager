import os
# from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.exceptions import ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.routes.jobs import jobs_router
from app.routes.auth import auth_router
from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.models.session import UserSession

from contextlib import asynccontextmanager

# load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    
    
app = FastAPI(lifespan=lifespan)

routers = [jobs_router, auth_router]

for router in routers:
    app.include_router(router)


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


# @app.get("/")
# def read_root():
#     return {"message": "API is running"}


@app.get("/debug-cookies")
def debug_cookies(request: Request):
    print("\n--- 🍪 INCOMING COOKIES DEBUG ---")
    print(f"All Raw Cookies: {request.cookies}")
    print(f"Target Session Cookie: {request.cookies.get('session_user_id')}")
    print("---------------------------------\n")
    
    return {
        "message": "Cookie check completed", 
        "cookies_received": request.cookies
    }
    

app.mount("/", StaticFiles(directory="Frontend", html=True), name="Frontend")