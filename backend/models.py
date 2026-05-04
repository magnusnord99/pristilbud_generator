from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
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
    user: Optional[str] = None

# Project Description models
class ProjectType(BaseModel):
    id: str
    name: str
    description: str
    template_prompts: List[str]

class GenerateContentRequest(BaseModel):
    project_type: str
    project_name: str
    brief_description: str
    target_audience: Optional[str] = None
    style_preference: Optional[str] = None

class GeneratedContent(BaseModel):
    goals: str
    concept: str
    target_audience: str
    key_features: str
    timeline: str
    success_metrics: str

class ImageUploadResponse(BaseModel):
    image_id: str
    filename: str
    url: str
    placeholder_type: str

class ProjectDescriptionRequest(BaseModel):
    project_type: str
    project_name: str
    generated_content: GeneratedContent
    images: List[ImageUploadResponse]
    language: Literal["NO", "EN"] = "NO"

class ProjectDescriptionResponse(BaseModel):
    pdf_url: str
    project_id: str
    created_at: datetime

# Quote Data models
class QuoteDataResponse(BaseModel):
    """Response model for quote data"""
    grouped_sums: List[List]  # List of [category: str, amount: float] lists
    total_days: Optional[float] = None
    post_prod_days: Optional[float] = None
    pre_prod_days: Optional[float] = None
    details: dict
    company_info: dict
    total_excl_mva: Optional[float] = None
    total_incl_mva: Optional[float] = None
    sheet_id: str

class QuoteDataRequest(BaseModel):
    """Request model for fetching quote data"""
    url: str = Field(min_length=10, description="Google Sheets URL")

class GeneratePDFFromDataRequest(BaseModel):
    """Request model for generating PDF from data"""
    data: dict  # Changed from QuoteDataResponse to dict to avoid potential validation issues
    language: Literal["NO", "EN"] = "NO"
    reise: Literal["y", "n"] = "n"
    mva: Literal["y", "n"] = "n"
    discount_percent: Literal[0, 10, 15, 20, 25, 30, 40] = Field(default=0, description="Rabatt i prosent")
    currency: Literal["NOK", "EUR"] = "NOK"

# Customer models
class CreateCustomerRequest(BaseModel):
    """Request model for creating a customer"""
    name: str = Field(min_length=1, description="Kundenavn")
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class UpdateCustomerRequest(BaseModel):
    """Request model for updating a customer"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class CustomerResponse(BaseModel):
    """Response model for customer"""
    id: int
    name: str
    email: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class CustomerListResponse(BaseModel):
    """Response model for customer list"""
    customers: List[CustomerResponse]

# Project models
class CreateProjectRequest(BaseModel):
    """Request model for creating a project"""
    customer_id: int
    name: str = Field(min_length=1, description="Prosjektnavn")
    description: Optional[str] = None
    status: Literal["active", "completed", "cancelled", "on_hold"] = "active"

class UpdateProjectRequest(BaseModel):
    """Request model for updating a project"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Literal["active", "completed", "cancelled", "on_hold"]] = None

class ProjectResponse(BaseModel):
    """Response model for project"""
    id: int
    customer_id: int
    name: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

class ProjectListResponse(BaseModel):
    """Response model for project list"""
    projects: List[ProjectResponse]

class ProjectOverviewResponse(BaseModel):
    """Response model for complete project overview"""
    project: ProjectResponse
    customer: Optional[CustomerResponse] = None
    quotes: List[dict] = []
    contracts: List[dict] = []
    description: Optional[dict] = None
