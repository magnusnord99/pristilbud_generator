# backend/main.py
from fastapi import FastAPI, HTTPException, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, List
from write_to_pdf import generate_pdf
from pdf_generators.price_quote import generate_pdf_from_data
import auth
import database
from models import (
    GoogleAuthRequest, AuthResponse, RefreshTokenRequest,
    CreateInvitationRequest, InvitationResponse, UseInvitationRequest,
    UserResponse, UserListResponse, PromoteUserRequest, DeleteUserRequest,
    HealthResponse, ProjectType, GenerateContentRequest, GeneratedContent,
    ImageUploadResponse, ProjectDescriptionRequest, ProjectDescriptionResponse,
    QuoteDataRequest, QuoteDataResponse, GeneratePDFFromDataRequest,
    CreateCustomerRequest, UpdateCustomerRequest, CustomerResponse, CustomerListResponse,
    CreateProjectRequest, UpdateProjectRequest, ProjectResponse, ProjectListResponse, ProjectOverviewResponse
)
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Pristilbud Generator API", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and create required directories"""
    try:
        print("🚀 Starting Pristilbud Generator API...")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"🐍 Python version: {os.sys.version}")
        print(f"🔧 Environment: {os.environ.get('ENVIRONMENT', 'development')}")
        
        # Create required directories
        os.makedirs("uploads", exist_ok=True)
        os.makedirs("downloads", exist_ok=True)
        print("✅ Directories created successfully")
        
        # Initialize database
        database.init_database()
        print("✅ Database initialized successfully")
        
        # Check Google Sheets credentials
        google_creds = os.environ.get("GOOGLE_CREDENTIALS_JSON")
        if google_creds:
            print("✅ Google Sheets credentials found")
            print(f"   Credentials length: {len(google_creds)}")
            
            # Test if it's valid JSON
            try:
                import json
                json.loads(google_creds)
                print("✅ Credentials are valid JSON")
            except json.JSONDecodeError as e:
                print(f"❌ Credentials are NOT valid JSON: {e}")
                print(f"❌ First 200 chars: {google_creds[:200]}...")
        else:
            print("⚠️  Google Sheets credentials not found")
            print("   Set GOOGLE_CREDENTIALS_JSON environment variable")
            
        print("✅ Pristilbud Generator API startup completed successfully")
        
    except Exception as e:
        print(f"❌ Critical error during startup: {e}")
        import traceback
        traceback.print_exc()
        # Don't raise here - let the app start but log the error

# CORS (adjust origins for your deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PDFRequest(BaseModel):
    url: str = Field(min_length=10)
    language: Literal["NO", "EN"]
    reise: Literal["y", "n"]
    mva: Literal["y", "n"]
    discount_percent: Literal[0, 10, 15, 20, 25, 30, 40] = Field(default=0, description="Rabatt i prosent (0, 10, 15, 20, 25, 30, 40)")
    currency: Literal["NOK", "EUR"] = "NOK"

# Simple public health check (no auth required)
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Simple health check endpoint for deployment monitoring"""
    try:
        # Basic checks
        db_status = "connected" if database.init_database() else "error"
        
        return HealthResponse(
            status="ok",
            timestamp=datetime.now(),
            database=db_status,
            user=None
        )
    except Exception as e:
        return HealthResponse(
            status="error",
            timestamp=datetime.now(),
            database="error",
            user=None
        )

# Simple ping endpoint (no dependencies)
@app.get("/ping")
async def ping():
    """Simple ping endpoint to test if server is running"""
    return {"message": "pong", "timestamp": datetime.now().isoformat()}

# Health check endpoint
@app.get("/healthz", response_model=HealthResponse)
async def healthz(current_user: dict = Depends(auth.get_current_user)):
    """Health check endpoint that also validates authentication"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(),
        database="connected",
        user=current_user.get("email") if current_user else None
    )

# Authentication endpoints
@app.post("/auth/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest):
    """Authenticate user with Google token"""
    try:
        user = auth.authenticate_user_with_google(request.google_token)
        tokens = auth.create_user_tokens(user)
        return AuthResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            user=user
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        payload = auth.verify_token(request.refresh_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user_id = int(payload["sub"])
        user = database.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        tokens = auth.create_user_tokens(user)
        return AuthResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            user=user
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Invitation endpoints
@app.post("/invitations", response_model=InvitationResponse)
async def create_invitation(
    request: CreateInvitationRequest,
    current_admin: dict = Depends(auth.get_current_admin_user)
):
    """Create a new invitation (admin only)"""
    try:
        invitation_code = auth.generate_invitation_code()
        invitation_id = database.create_invitation(
            invitation_code, 
            request.email, 
            current_admin["id"]
        )
        
        invitation = database.get_invitation_by_code(invitation_code)
        return InvitationResponse(
            id=invitation["id"],
            code=invitation["code"],
            email=invitation["email"],
            created_at=invitation["created_at"],
            is_used=invitation["is_used"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/invitations/use")
async def use_invitation(request: UseInvitationRequest):
    """Use an invitation code (returns success message)"""
    invitation = database.get_invitation_by_code(request.invitation_code)
    if not invitation:
        raise HTTPException(status_code=400, detail="Invalid or expired invitation code")
    
    return {"message": "Invitation code is valid", "email": invitation["email"]}

# User management endpoints (admin only)
@app.get("/admin/users", response_model=UserListResponse)
async def get_all_users(current_admin: dict = Depends(auth.get_current_admin_user)):
    """Get all users (admin only)"""
    users = database.get_all_users()
    return UserListResponse(users=users)

@app.post("/admin/users/promote")
async def promote_user(
    request: PromoteUserRequest,
    current_admin: dict = Depends(auth.get_current_admin_user)
):
    """Promote user to admin (admin only)"""
    success = database.promote_to_admin(request.user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to promote user")
    return {"message": "User promoted to admin successfully"}

@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: dict = Depends(auth.get_current_admin_user)
):
    """Delete a user (admin only)"""
    if user_id == current_admin["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    success = database.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete user")
    return {"message": "User deleted successfully"}

# Protected PDF generation endpoint
@app.post("/generate-pdf")
def create_pdf(
    req: PDFRequest,
    current_user: dict = Depends(auth.get_current_user)
):
    """Generate PDF (requires authentication)"""
    try:
        # Check rate limit
        auth.check_rate_limit_middleware(current_user["id"], "generate-pdf", current_user)
        
        buffer, filename = generate_pdf(req.url, req.language, req.reise, req.mva, req.discount_percent, req.currency)
    except ValueError as ve:
        # e.g., invalid URL format
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as ex:
        # Upstream errors (e.g., Google API, credentials, etc.)
        error_detail = f"Kunne ikke hente data fra Google Sheets: {str(ex)}"
        print(f"❌ PDF generation error: {error_detail}")
        print(f"   Exception type: {type(ex).__name__}")
        raise HTTPException(status_code=502, detail=error_detail) from ex

    # Debug: log what we're sending
    print(f"🔍 Backend response headers:")
    print(f"   Content-Disposition: attachment; filename=\"{filename}\"")
    print(f"   Media type: application/pdf")
    print(f"   Buffer size: {len(buffer.getvalue())} bytes")
    
    # Alternative: send filename in custom header
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "X-Filename": filename,  # Custom header as backup
        "Access-Control-Expose-Headers": "Content-Disposition, X-Filename"
    }
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers=headers
    )

# New structured API endpoints for quotes
@app.post("/api/quotes/data", response_model=QuoteDataResponse)
async def get_quote_data(
    req: QuoteDataRequest,
    current_user: dict = Depends(auth.get_current_user)
):
    """
    Fetch quote data from Google Sheets and return as JSON
    
    This endpoint separates data retrieval from PDF generation,
    allowing you to fetch data once and use it for both
    interactive display and PDF generation.
    """
    try:
        # Import here to avoid startup issues
        from services.quote_service import fetch_quote_data, prepare_quote_data_for_pdf
        
        # Check rate limit
        auth.check_rate_limit_middleware(current_user["id"], "fetch-quote-data", current_user)
        
        # Fetch data from Google Sheets
        data = fetch_quote_data(req.url)
        
        # Convert grouped_sums from list of tuples to list of lists for JSON serialization
        grouped_sums_list = [[item[0], item[1]] for item in data["grouped_sums"]]
        
        return QuoteDataResponse(
            grouped_sums=grouped_sums_list,
            total_days=data["total_days"],
            post_prod_days=data["post_prod_days"],
            pre_prod_days=data["pre_prod_days"],
            details=data["details"],
            company_info=data["company_info"],
            total_excl_mva=data["total_excl_mva"],
            total_incl_mva=data["total_incl_mva"],
            sheet_id=data["sheet_id"]
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as ex:
        error_detail = f"Kunne ikke hente data fra Google Sheets: {str(ex)}"
        print(f"❌ Quote data fetch error: {error_detail}")
        raise HTTPException(status_code=502, detail=error_detail) from ex


@app.post("/api/quotes/pdf")
async def generate_pdf_from_quote_data(
    req: GeneratePDFFromDataRequest,
    current_user: dict = Depends(auth.get_current_user)
):
    """
    Generate PDF from quote data (JSON)
    
    Use this endpoint when you already have quote data from /api/quotes/data.
    This avoids fetching data twice - fetch once, use for display, then generate PDF.
    """
    try:
        # Import here to avoid startup issues
        from services.quote_service import prepare_quote_data_for_pdf
        
        # Check rate limit
        auth.check_rate_limit_middleware(current_user["id"], "generate-pdf", current_user)
        
        # Convert grouped_sums from list of lists back to list of tuples
        data_dict = req.data if isinstance(req.data, dict) else req.data.dict()
        grouped_sums_tuples = [(item[0], item[1]) for item in data_dict.get("grouped_sums", [])]
        
        # Prepare data dictionary
        pdf_data = {
            "grouped_sums": grouped_sums_tuples,
            "total_days": data_dict.get("total_days"),
            "post_prod_days": data_dict.get("post_prod_days"),
            "pre_prod_days": data_dict.get("pre_prod_days"),
            "details": data_dict.get("details", {}),
            "company_info": data_dict.get("company_info", {}),
            "total_excl_mva": data_dict.get("total_excl_mva"),
            "total_incl_mva": data_dict.get("total_incl_mva"),
        }
        
        # Generate PDF
        buffer, filename = generate_pdf_from_data(
            pdf_data,
            req.language,
            req.reise,
            req.mva,
            req.discount_percent,
            req.currency
        )
        
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Filename": filename,
            "Access-Control-Expose-Headers": "Content-Disposition, X-Filename"
        }
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers=headers
        )
    except Exception as ex:
        error_detail = f"Kunne ikke generere PDF: {str(ex)}"
        print(f"❌ PDF generation error: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail) from ex

# Test endpoint for creating first user (remove in production)
@app.post("/test/create-first-user")
async def create_first_user():
    """Create the first user for testing (remove in production)"""
    try:
        # Check if any users exist
        if not database.is_first_user():
            raise HTTPException(status_code=400, detail="Users already exist")
        
        # Create a test user (first user becomes admin)
        user_id = database.create_user(
            google_id="test-google-id-123",
            email="admin@test.com",
            name="Test Admin",
            is_first_user=True
        )
        
        user = database.get_user_by_id(user_id)
        
        # Create tokens for this user
        tokens = auth.create_user_tokens(user)
        
        return {
            "message": "First user created successfully",
            "user": user,
            "tokens": tokens
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Test endpoint for creating invitations (remove in production)
@app.post("/test/create-invitation")
async def create_test_invitation():
    """Create a test invitation (remove in production)"""
    try:
        # Check if any users exist
        if database.is_first_user():
            raise HTTPException(status_code=400, detail="No users exist yet")
        
        # Get the first user (admin)
        users = database.get_all_users()
        if not users:
            raise HTTPException(status_code=400, detail="No users found")
        
        admin_user = users[0]  # First user is admin
        
        # Create invitation
        invitation_code = auth.generate_invitation_code()
        invitation_id = database.create_invitation(
            invitation_code, 
            "test@example.com", 
            admin_user["id"]
        )
        
        invitation = database.get_invitation_by_code(invitation_code)
        
        return {
            "message": "Test invitation created successfully",
            "invitation": {
                "code": invitation["code"],
                "email": invitation["email"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Test endpoint for authentication without Google OAuth (remove in production)
@app.post("/test/auth")
async def test_auth():
    """Test authentication endpoint that bypasses Google OAuth"""
    try:
        print("🔐 Test auth requested")
        
        # Check if test user exists, if not create it
        existing_user = database.get_user_by_email("test@example.com")
        print(f"📋 Existing user check: {existing_user is not None}")
        
        if not existing_user:
            print("👤 Creating test user...")
            # Create test user in database
            user_id = database.create_test_user(
                email="test@example.com",
                name="Test User",
                role="admin"
            )
            print(f"✅ Test user created with ID: {user_id}")
            
            # Get the created user
            existing_user = database.get_user_by_email("test@example.com")
            print(f"📋 Retrieved created user: {existing_user is not None}")
        
        if not existing_user:
            raise Exception("Failed to create or retrieve test user")
        
        print(f"🔑 Creating tokens for user: {existing_user['email']}")
        tokens = auth.create_user_tokens(existing_user)
        print("✅ Tokens created successfully")
        
        return AuthResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            user=existing_user
        )
    except Exception as e:
        print(f"❌ Test auth error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Test authentication failed: {str(e)}")

# API Key management endpoint (admin only)
@app.get("/admin/api-key")
async def get_api_key_info(current_admin: dict = Depends(auth.get_current_admin_user)):
    """Get information about API key configuration (admin only)"""
    api_key_configured = bool(os.getenv("API_KEY") or os.getenv("QUOTE_API_TOKEN"))
    
    if api_key_configured:
        return {
            "message": "API key is configured",
            "note": "Use the API key from your environment variable (API_KEY or QUOTE_API_TOKEN) as Bearer token for server-side authentication"
        }
    else:
        return {
            "message": "API key is not configured",
            "instructions": "Set API_KEY or QUOTE_API_TOKEN environment variable to enable server-side API authentication",
            "example": "API_KEY=your-secret-api-key-here"
        }

@app.post("/admin/generate-api-key")
async def generate_api_key(current_admin: dict = Depends(auth.get_current_admin_user)):
    """Generate a new API key for server-side use (admin only)"""
    import secrets
    new_api_key = secrets.token_urlsafe(32)
    
    return {
        "api_key": new_api_key,
        "message": "Save this API key securely. It will not be shown again.",
        "usage": "Use this as QUOTE_API_TOKEN in your Next.js .env.local file",
        "header_format": f"Authorization: Bearer {new_api_key}"
    }

# Customer endpoints
@app.post("/api/customers", response_model=CustomerResponse)
async def create_customer(
    req: CreateCustomerRequest,
    current_user: dict = Depends(auth.get_current_user)
):
    """Create a new customer"""
    try:
        customer_id = database.create_customer(
            name=req.name,
            email=req.email,
            company=req.company,
            phone=req.phone,
            address=req.address,
            notes=req.notes,
            created_by=current_user["id"]
        )
        customer = database.get_customer_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=500, detail="Failed to retrieve created customer")
        return customer
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/customers", response_model=CustomerListResponse)
async def get_all_customers(current_user: dict = Depends(auth.get_current_user)):
    """Get all customers"""
    try:
        customers = database.get_all_customers()
        return CustomerListResponse(customers=customers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    current_user: dict = Depends(auth.get_current_user)
):
    """Get customer by ID"""
    customer = database.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.put("/api/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    req: UpdateCustomerRequest,
    current_user: dict = Depends(auth.get_current_user)
):
    """Update customer information"""
    customer = database.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = req.dict(exclude_unset=True)
    if update_data:
        database.update_customer(customer_id, **update_data)
        customer = database.get_customer_by_id(customer_id)
    
    return customer

# Project endpoints
@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(
    req: CreateProjectRequest,
    current_user: dict = Depends(auth.get_current_user)
):
    """Create a new project"""
    # Verify customer exists
    customer = database.get_customer_by_id(req.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    try:
        project_id = database.create_project(
            customer_id=req.customer_id,
            name=req.name,
            description=req.description,
            status=req.status,
            created_by=current_user["id"]
        )
        project = database.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=500, detail="Failed to retrieve created project")
        return project
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/projects", response_model=ProjectListResponse)
async def get_all_projects(current_user: dict = Depends(auth.get_current_user)):
    """Get all projects"""
    try:
        projects = database.get_all_projects()
        return ProjectListResponse(projects=projects)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}/projects", response_model=ProjectListResponse)
async def get_customer_projects(
    customer_id: int,
    current_user: dict = Depends(auth.get_current_user)
):
    """Get all projects for a customer"""
    customer = database.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    try:
        projects = database.get_projects_by_customer(customer_id)
        return ProjectListResponse(projects=projects)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: dict = Depends(auth.get_current_user)
):
    """Get project by ID"""
    project = database.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.get("/api/projects/{project_id}/overview", response_model=ProjectOverviewResponse)
async def get_project_overview(
    project_id: int,
    current_user: dict = Depends(auth.get_current_user)
):
    """Get complete project overview with customer, quotes, contracts, and descriptions"""
    overview = database.get_project_overview(project_id)
    if not overview:
        raise HTTPException(status_code=404, detail="Project not found")
    return overview

@app.put("/api/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    req: UpdateProjectRequest,
    current_user: dict = Depends(auth.get_current_user)
):
    """Update project information"""
    project = database.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = req.dict(exclude_unset=True)
    if update_data:
        database.update_project(project_id, **update_data)
        project = database.get_project_by_id(project_id)
    
    return project

# Project Description endpoints
@app.get("/project-types", response_model=List[ProjectType])
async def get_project_types():
    """Get available project types for description generation"""
    project_types = [
        ProjectType(
            id="event",
            name="Event",
            description="Festivaler, konferanser, lanseringer og andre arrangementer",
            template_prompts=[
                "Skriv en engasjerende beskrivelse av målgruppen",
                "Beskriv hovedkonseptet og temaet for arrangementet",
                "List opp nøkkelfunksjoner og aktiviteter"
            ]
        ),
        ProjectType(
            id="advertising",
            name="Reklamekampanje",
            description="Digital markedsføring, sosiale medier og tradisjonell reklame",
            template_prompts=[
                "Definer målgruppen og deres behov",
                "Beskriv kampanjens hovedbudskap",
                "List opp kanaler og distribusjonsmetoder"
            ]
        ),
        ProjectType(
            id="product",
            name="Produktlansering",
            description="Nye produkter, tjenester eller løsninger",
            template_prompts=[
                "Beskriv produktets hovedfunksjoner",
                "Identifiser målgruppen og deres smertepunkter",
                "List opp konkurransefordeler"
            ]
        ),
        ProjectType(
            id="branding",
            name="Merkevarebygging",
            description="Visuell identitet, logoer og merkevarestrategi",
            template_prompts=[
                "Beskriv merkevarens personlighet og verdier",
                "Definer målgruppen og deres preferanser",
                "List opp nøkkelforskjeller fra konkurrenter"
            ]
        )
    ]
    return project_types

@app.post("/generate-content", response_model=GeneratedContent)
async def generate_ai_content(
    request: GenerateContentRequest,
    current_user: dict = Depends(auth.get_current_user)
):
    """Generate AI content for project description"""
    try:
        # TODO: Integrate with actual AI service (OpenAI, Claude, etc.)
        # For now, return template content based on project type
        
        if request.project_type == "event":
            content = GeneratedContent(
                goals="Skape et minneverdig arrangement som engasjerer målgruppen og oppnår definerte mål",
                concept=f"Et innovativt {request.project_name} som kombinerer kreativitet med praktisk funksjonalitet",
                target_audience=request.target_audience or "Primært målgruppe som er interessert i innholdet",
                key_features="Interaktive elementer, profesjonell produksjon, engasjerende innhold",
                timeline="Planlegging: 3 måneder, Produksjon: 1 måned, Lansering: 1 uke",
                success_metrics="Deltakerantall, engasjement, feedback, måloppnåelse"
            )
        elif request.project_type == "advertising":
            content = GeneratedContent(
                goals="Øke merkevarebevissthet og drive handlinger fra målgruppen",
                concept=f"En kreativ reklamekampanje for {request.project_name} som skiller seg ut",
                target_audience=request.target_audience or "Målgruppe som kan dra nytte av produktet/tjenesten",
                key_features="Kreativt budskap, strategisk plassering, målbare resultater",
                timeline="Strategi: 2 uker, Produksjon: 3 uker, Kjøring: 8 uker",
                success_metrics="Reach, engasjement, klikk, konverteringer"
            )
        elif request.project_type == "product":
            content = GeneratedContent(
                goals="Lansere et produkt som løser reelle problemer for målgruppen",
                concept=f"En innovativ løsning som revolusjonerer hvordan {request.project_name} fungerer",
                target_audience=request.target_audience or "Brukere som trenger denne typen løsning",
                key_features="Brukervennlig design, kraftig funksjonalitet, skalerbar arkitektur",
                timeline="Utvikling: 6 måneder, Testing: 2 måneder, Lansering: 1 måned",
                success_metrics="Brukeradopsjon, tilbakemeldinger, salg, tilbakevendende kunder"
            )
        else:  # branding
            content = GeneratedContent(
                goals="Skape en sterk og gjenkjennelig merkevareidentitet",
                concept=f"En visuell identitet som reflekterer {request.project_name} sin essens og verdier",
                target_audience=request.target_audience or "Kunder og potensielle kunder som identifiserer seg med merkevaren",
                key_features="Konsistent design, emosjonell tilknytning, fleksibilitet på tvers av medier",
                timeline="Research: 2 uker, Design: 4 uker, Implementering: 6 uker",
                success_metrics="Merkevaregjenkjenning, kundelojalitet, visuell konsistens"
            )
        
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feil ved generering av innhold: {str(e)}")

@app.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    placeholder_type: str = Form(...),
    current_user: dict = Depends(auth.get_current_user)
):
    """Upload image for project description"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Kun bildefiler er tillatt")
        
        # Generate unique filename
        import uuid
        import os
        from PIL import Image
        
        file_extension = file.filename.split('.')[-1]
        image_id = str(uuid.uuid4())
        filename = f"{image_id}.{file_extension}"
        
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        
        # Save and process image
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process image (resize if needed, add watermark, etc.)
        with Image.open(file_path) as img:
            print(f"📸 Image uploaded: {img.format} {img.mode} {img.width}x{img.height}")
            # Resize if too large (max 1920x1080)
            if img.width > 1920 or img.height > 1080:
                print(f"🔄 Resizing image from {img.width}x{img.height} to max 1920x1080")
                img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                img.save(file_path, quality=85, optimize=True)
                print(f"✅ Image resized and saved")
            else:
                print(f"✅ Image size OK, no resizing needed")
        
        # Return image info
        return ImageUploadResponse(
            image_id=image_id,
            filename=filename,
            url=f"/uploads/{filename}",
            placeholder_type=placeholder_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feil ved bildeopplasting: {str(e)}")

@app.post("/generate-project-description", response_model=ProjectDescriptionResponse)
async def generate_project_description_pdf(
    request: ProjectDescriptionRequest,
    current_user: dict = Depends(auth.get_current_user)
):
    """Generate PDF project description with images and AI content"""
    try:
        from write_to_pdf import generate_project_description_pdf as generate_pdf
        import uuid
        import os
        
        project_id = str(uuid.uuid4())
        
        print(f"📄 Generating PDF for project: {request.project_name}")
        print(f"📊 Content sections: {len(request.generated_content.dict())}")
        print(f"🖼️ Images: {len(request.images)}")
        for i, img in enumerate(request.images):
            print(f"  🖼️ Image {i+1}: {img.filename} ({img.placeholder_type}) - {img.url}")
        
        # Generate PDF using the new function
        pdf_buffer = generate_pdf(
            project_type=request.project_type,
            project_name=request.project_name,
            generated_content=request.generated_content.dict(),
            images=request.images,
            language=request.language
        )
        
        # Create downloads directory if it doesn't exist
        download_dir = "downloads"
        os.makedirs(download_dir, exist_ok=True)
        
        # Save PDF to file
        pdf_filename = f"{project_id}.pdf"
        pdf_path = os.path.join(download_dir, pdf_filename)
        
        with open(pdf_path, "wb") as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"✅ PDF saved to: {pdf_path}")
        print(f"📏 File size: {os.path.getsize(pdf_path)} bytes")
        
        return ProjectDescriptionResponse(
            pdf_url=f"/downloads/{pdf_filename}",
            project_id=project_id,
            created_at=datetime.now()
        )
    except Exception as e:
        print(f"❌ PDF generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Feil ved PDF-generering: {str(e)}")

# Serve uploaded files
@app.get("/uploads/{filename}")
async def serve_upload(filename: str):
    """Serve uploaded images"""
    import os
    file_path = os.path.join("uploads", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Fil ikke funnet")

# Serve downloaded PDFs
@app.get("/downloads/{filename}")
async def serve_download(
    filename: str,
    current_user: dict = Depends(auth.get_current_user)
):
    """Serve generated PDFs (requires authentication)"""
    import os
    file_path = os.path.join("downloads", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF ikke funnet")
    
    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        raise HTTPException(status_code=500, detail="PDF-fil er tom")
    
    print(f"📥 Serving PDF: {filename} (size: {file_size} bytes) for user: {current_user.get('email')}")
    
    return FileResponse(
        file_path, 
        media_type='application/pdf', 
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# Root endpoint (shows login form)
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="no">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pristilbud Generator - Login</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .loading { display: none; }
            .error { color: red; margin-top: 10px; }
            .success { color: green; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1>🎬 Pristilbud Generator</h1>
        <p>Du må logge inn for å bruke tjenesten. Kontakt administrator for invitasjon.</p>
        
        <div id="loginForm">
            <h2>Logg inn med Google</h2>
            <div class="form-group">
                <label for="invitationCode">Invitasjonskode:</label>
                <input type="text" id="invitationCode" placeholder="Skriv inn invitasjonskode" required>
            </div>
            
            <div class="form-group">
                <label for="googleToken">Google Token:</label>
                <input type="text" id="googleToken" placeholder="Google OAuth token" required>
            </div>
            
            <button onclick="login()">Logg inn</button>
        </div>
        
        <div class="loading" id="loading">
            <p>Logger inn... Vennligst vent.</p>
        </div>
        
        <div id="error" class="error" style="display: none;"></div>
        <div id="success" class="success" style="display: none;"></div>
        
        <script>
            async function login() {
                const invitationCode = document.getElementById('invitationCode').value;
                const googleToken = document.getElementById('googleToken').value;
                
                if (!invitationCode || !googleToken) {
                    showError('Vennligst fyll ut alle feltene');
                    return;
                }
                
                // First verify invitation
                try {
                    const inviteResponse = await fetch('/invitations/use', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ invitation_code: invitationCode })
                    });
                    
                    if (!inviteResponse.ok) {
                        const error = await inviteResponse.text();
                        showError('Ugyldig invitasjonskode: ' + error);
                        return;
                    }
                    
                    // Then authenticate with Google
                    const authResponse = await fetch('/auth/google', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ google_token: googleToken })
                    });
                    
                    if (authResponse.ok) {
                        const authData = await authResponse.json();
                        localStorage.setItem('access_token', authData.access_token);
                        localStorage.setItem('refresh_token', authData.refresh_token);
                        showSuccess('Innlogging vellykket! Du kan nå bruke API-et.');
                    } else {
                        const error = await authResponse.text();
                        showError('Innlogging feilet: ' + error);
                    }
                } catch (error) {
                    showError('En feil oppstod: ' + error.message);
                }
            }
            
            function showError(message) {
                document.getElementById('error').textContent = message;
                document.getElementById('error').style.display = 'block';
                document.getElementById('success').style.display = 'none';
            }
            
            function showSuccess(message) {
                document.getElementById('success').textContent = message;
                document.getElementById('success').style.display = 'block';
                document.getElementById('error').style.display = 'none';
            }
        </script>
    </body>
    </html>
    """