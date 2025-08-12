import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from google.oauth2 import id_token
from google.auth.transport import requests
import database
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id")

# Rate limiting configuration
RATE_LIMITS = {
    "generate-pdf": {"max_requests": 10, "window_minutes": 60},  # 10 PDFs per hour
    "default": {"max_requests": 100, "window_minutes": 60}        # 100 requests per hour
}

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_google_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify Google ID token"""
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        return idinfo
    except ValueError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = database.get_user_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current admin user"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def generate_invitation_code() -> str:
    """Generate a unique invitation code"""
    return secrets.token_urlsafe(16)

def check_rate_limit_middleware(user_id: int, endpoint: str):
    """Check rate limit for a specific endpoint"""
    rate_limit_config = RATE_LIMITS.get(endpoint, RATE_LIMITS["default"])
    
    if not database.check_rate_limit(
        user_id, 
        endpoint, 
        rate_limit_config["max_requests"], 
        rate_limit_config["window_minutes"]
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {rate_limit_config['max_requests']} requests per {rate_limit_config['window_minutes']} minutes."
        )

# Authentication flow functions
def authenticate_user_with_google(google_token: str) -> Dict[str, Any]:
    """Authenticate user with Google token and return user info"""
    google_user_info = verify_google_token(google_token)
    if not google_user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    google_id = google_user_info["sub"]
    email = google_user_info["email"]
    name = google_user_info.get("name", email)
    
    # Check if user exists
    user = database.get_user_by_google_id(google_id)
    if user:
        return user
    
    # Check if this is the first user (becomes admin)
    is_first_user = database.is_first_user()
    
    # Create new user
    user_id = database.create_user(google_id, email, name, is_first_user)
    user = database.get_user_by_id(user_id)
    
    return user

def create_user_tokens(user: Dict[str, Any]) -> Dict[str, str]:
    """Create access and refresh tokens for user"""
    access_token = create_access_token(data={"sub": str(user["id"])})
    refresh_token = create_refresh_token(data={"sub": str(user["id"])})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
