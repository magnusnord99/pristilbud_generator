from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Authentication models
class GoogleAuthRequest(BaseModel):
    google_token: str

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Invitation models
class CreateInvitationRequest(BaseModel):
    email: EmailStr

class InvitationResponse(BaseModel):
    id: int
    code: str
    email: str
    created_at: datetime
    is_used: bool

class UseInvitationRequest(BaseModel):
    invitation_code: str

# User models
class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime

class UserListResponse(BaseModel):
    users: List[UserResponse]

# Rate limiting models
class RateLimitInfo(BaseModel):
    endpoint: str
    max_requests: int
    window_minutes: int
    current_usage: Optional[int] = None

# Admin models
class PromoteUserRequest(BaseModel):
    user_id: int

class DeleteUserRequest(BaseModel):
    user_id: int

# Health check model
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database: str
