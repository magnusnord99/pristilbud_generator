# backend/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
from write_to_pdf import generate_pdf
import auth
import database
from models import (
    GoogleAuthRequest, AuthResponse, RefreshTokenRequest,
    CreateInvitationRequest, InvitationResponse, UseInvitationRequest,
    UserResponse, UserListResponse, PromoteUserRequest, DeleteUserRequest,
    HealthResponse
)
from datetime import datetime

app = FastAPI(title="Pristilbud Generator API", version="1.0.0")

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

# Health check endpoint
@app.get("/healthz", response_model=HealthResponse)
async def healthz():
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(),
        database="connected"
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
        auth.check_rate_limit_middleware(current_user["id"], "generate-pdf")
        
        buffer, filename = generate_pdf(req.url, req.language, req.reise, req.mva)
    except ValueError as ve:
        # e.g., invalid URL format
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as ex:
        # Upstream errors (e.g., Google API, credentials, etc.)
        raise HTTPException(status_code=502, detail="Kunne ikke hente data fra Google Sheets") from ex

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

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
    """Test authentication without Google OAuth (remove in production)"""
    try:
        # Check if any users exist
        if database.is_first_user():
            raise HTTPException(status_code=400, detail="No users exist yet")
        
        # Get the first user (admin)
        users = database.get_all_users()
        if not users:
            raise HTTPException(status_code=400, detail="No users found")
        
        user = users[0]  # First user is admin
        
        # Create tokens for this user
        tokens = auth.create_user_tokens(user)
        
        return {
            "message": "Test authentication successful",
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"],
            "user": user
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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