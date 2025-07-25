# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from ..infrastructure.database.connection import get_db
from ..infrastructure.auth.models import (
    UserRegistration, UserLogin, UserProfile, TokenResponse, MedicalProfileUpdate
)
from ..infrastructure.auth.dependencies import get_current_user
from ..services.user_service import UserService

# Create authentication router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
user_service = UserService()

@auth_router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistration,
    session: AsyncSession = Depends(get_db)
):
    """Register a new user account"""
    try:
        user_profile = await user_service.register_user(session, user_data)
        return user_profile
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@auth_router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    session: AsyncSession = Depends(get_db)
):
    """Authenticate user and return access tokens"""
    token_response = await user_service.authenticate_user(session, login_data)
    
    if not token_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return token_response

@auth_router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: UserProfile = Depends(get_current_user)
):
    """Get current user's profile information"""
    return current_user

@auth_router.post("/logout")
async def logout_user(
    current_user: UserProfile = Depends(get_current_user)
):
    """Logout current user"""
    return {"message": "Successfully logged out"}
