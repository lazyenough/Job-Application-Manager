import bcrypt
from fastapi import Depends, HTTPException, Request, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.dependencies import getDB
from app.models.user import User

# Tell PassLib to use bcrypt. 
# "deprecated='auto'" ensures that if passlib updates its internals in the future, 
# it handles legacy hashes smoothly.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Takes a plain text password and returns a secure, salted cryptographic hash."""
    # 1. Convert the plain text string into raw bytes (required by bcrypt)
    password_bytes = password.encode('utf-8')
    
    # 2. Generate a random secure salt
    salt = bcrypt.gensalt()
    
    # 3. Hash the password with the salt
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    
    # 4. Convert the final hash back into a standard string to save in Postgres
    return hashed_bytes.decode('utf-8')

def get_user_by_email(email, db):
    stmt = select(User).where(User.email == email)
    
    user = db.execute(stmt).scalar_one_or_none()
    
    return user

def get_current_user(request: Request, db: Session = Depends(getDB)):
    # 1. Read the session cookie from the incoming request headers
    session_id = request.cookies.get("session_user_id")
    
    # 2. If the cookie is missing, block the request immediately
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
        
    # 3. Look up the user in the database
    user = db.query(User).filter(User.id == int(session_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User profile not found"
        )
        
    return user

def verify_password(received_password, stored_password):
    """Compares a plain text password with a stored hash safely using bcrypt."""
    # 1. Convert both strings into raw bytes
    received_bytes = received_password.encode('utf-8')
    stored_bytes = stored_password.encode('utf-8')
    
    # 2. Let bcrypt safely handle the salt extraction and constant-time check
    return bcrypt.checkpw(received_bytes, stored_bytes)