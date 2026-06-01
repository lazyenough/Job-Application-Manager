from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Response

from app.models.user import User
from app.services.login_service import get_user_by_email, hash_password, verify_password
from app.schemas.auth import UserCredential, UserResponse
from app.db.dependencies import getDB

auth_router = APIRouter(prefix="/auth", tags=["Auth APIs"])

@auth_router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCredential, db: Session = Depends(getDB)):
    normalized_email = user_data.email.strip().lower()
    
    user = get_user_by_email(normalized_email, db)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )
    
    print(user_data.password)
    hashed_password = hash_password(user_data.password)
    new_user = User(email=normalized_email, hashed_password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@auth_router.post("/login")
def login_user(user_data: UserCredential, response: Response, db: Session = Depends(getDB)):
    normalized_email = user_data.email.strip().lower()
    
    user = get_user_by_email(normalized_email, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    
    response = JSONResponse(content={"message": "Login successful!"})
    
    response.set_cookie(
        key="session_user_id",
        value=str(user.id),
        path="/",
        httponly=True,       # Prevents hackers from stealing the cookie via JS (XSS defense)
        secure=False,        # Set to True in production (requires HTTPS)
        samesite="lax",      # Protects against Cross-Site Request Forgery (CSRF)
        max_age=1800         # Cookie automatically expires after 30 minutes (1800 seconds)
    )
    
    return response

@auth_router.post("/logout")
def logout_user():
    """
    Logs the user out by instructing the browser to clear 
    the session cookie immediately.
    """
    # 1. Create a clear JSON response packet
    response = JSONResponse(content={"message": "Logged out successfully!"})
    
    # 2. Tell the browser to invalidate and delete the session cookie
    response.delete_cookie(
        key="session_user_id",
        path="/",          # Must match the path where the cookie was created
        domain=None        # Matches the host domain
    )
    
    return response

