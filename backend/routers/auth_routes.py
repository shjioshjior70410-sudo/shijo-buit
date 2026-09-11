"""
Authentication API Endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from backend.models import UserLogin, UserRegister, AuthResponse, UserProfile
from backend.auth import hash_password, verify_password, create_access_token, get_current_user
from backend.database import db_client
import uuid

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse)
def register(user_in: UserRegister):
    """Registers a new user into Firebase / database."""
    existing_user = db_client.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    user_dict = {
        "id": f"user-{uuid.uuid4().hex[:8]}",
        "email": user_in.email.strip().lower(),
        "fullName": user_in.fullName.strip(),
        "role": user_in.role,
        "company": user_in.company,
        "passwordHash": hash_password(user_in.password)
    }

    db_client.create_user(user_dict)
    token = create_access_token({"sub": user_dict["email"], "role": user_dict["role"]})

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfile(
            id=user_dict["id"],
            email=user_dict["email"],
            fullName=user_dict["fullName"],
            role=user_dict["role"],
            company=user_dict["company"]
        )
    )


@router.post("/login", response_model=AuthResponse)
def login(credentials: UserLogin):
    """Authenticates user credentials and returns JWT bearer token."""
    user = db_client.get_user_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user.get("passwordHash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token({"sub": user["email"], "role": user.get("role", "Project Manager")})

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfile(
            id=user["id"],
            email=user["email"],
            fullName=user["fullName"],
            role=user.get("role", "Project Manager"),
            company=user.get("company", "BuildPulse Partner")
        )
    )


@router.post("/demo-login/{role}", response_model=AuthResponse)
def demo_login(role: str):
    """Convenient 1-click evaluation access for demoing the dashboard."""
    role_map = {
        "manager": ("manager@buildpulse.io", "Elena Rostova", "Project Manager", "Apex Structural Builders Corp."),
        "engineer": ("engineer@buildpulse.io", "Marcus Sterling", "Site Superintendent", "Pacific Marine Infrastructure")
    }

    key = role.lower()
    if key not in role_map:
        key = "manager"

    email, name, job_title, company = role_map[key]
    user = db_client.get_user_by_email(email)
    if not user:
        # Create on the fly if missing
        user = {
            "id": f"demo-{key}",
            "email": email,
            "fullName": name,
            "role": job_title,
            "company": company,
            "passwordHash": hash_password("manager123")
        }
        db_client.create_user(user)

    token = create_access_token({"sub": user["email"], "role": user.get("role", job_title)})

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfile(
            id=user["id"],
            email=user["email"],
            fullName=user["fullName"],
            role=user.get("role", job_title),
            company=user.get("company", company)
        )
    )


@router.get("/me", response_model=UserProfile)
def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Retrieves authenticated user details."""
    return UserProfile(
        id=current_user["id"],
        email=current_user["email"],
        fullName=current_user["fullName"],
        role=current_user.get("role", "Project Manager"),
        company=current_user.get("company")
    )
