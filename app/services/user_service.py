# app/services/user_service.py
import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from ..infrastructure.database.models import User
from ..infrastructure.auth.password_manager import PasswordManager
from ..infrastructure.auth.jwt_manager import JWTManager
from ..infrastructure.auth.models import (
    UserRegistration, UserLogin, UserProfile, TokenResponse, MedicalProfileUpdate
)

class UserService:
    """User management service for Cogitto"""
    
    def __init__(self):
        self.password_manager = PasswordManager()
        self.jwt_manager = JWTManager()
    
    async def register_user(self, session: AsyncSession, user_data: UserRegistration) -> UserProfile:
        """Register a new user"""
        
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == user_data.email.lower())
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash password
        hashed_password = self.password_manager.hash_password(user_data.password)
        
        # Parse date of birth
        date_of_birth = None
        if user_data.date_of_birth:
            try:
                date_of_birth = datetime.strptime(user_data.date_of_birth, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
        
        # Calculate age range for privacy
        age_range = self._calculate_age_range(date_of_birth) if date_of_birth else None
        
        # Create new user
        new_user = User(
            email=user_data.email.lower(),
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            date_of_birth=date_of_birth,
            age_range=age_range,
            verification_token=self.password_manager.generate_secure_token()
        )
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        return self._user_to_profile(new_user)
    
    async def authenticate_user(self, session: AsyncSession, login_data: UserLogin) -> Optional[TokenResponse]:
        """Authenticate user and return tokens"""
        
        # Find user by email
        result = await session.execute(
            select(User).where(User.email == login_data.email.lower())
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return None
        
        # Verify password
        if not self.password_manager.verify_password(login_data.password, user.hashed_password):
            return None
        
        # Update last login
        await session.execute(
            update(User)
            .where(User.id == user.id)
            .values(last_login_at=datetime.utcnow())
        )
        await session.commit()
        
        # Create tokens
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = self.jwt_manager.create_access_token(token_data)
        refresh_token = self.jwt_manager.create_refresh_token(token_data)
        
        user.last_login_at = datetime.utcnow()  # Update for response
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes
            user=self._user_to_profile(user)
        )
    
    async def get_user_by_id(self, session: AsyncSession, user_id: str) -> Optional[UserProfile]:
        """Get user by ID"""
        result = await session.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()
        
        if user:
            return self._user_to_profile(user)
        return None
    
    def _user_to_profile(self, user: User) -> UserProfile:
        """Convert User model to UserProfile"""
        return UserProfile(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            phone_number=user.phone_number,
            date_of_birth=user.date_of_birth.isoformat() if user.date_of_birth else None,
            age_range=user.age_range,
            allergies=user.allergies or [],
            medical_conditions=user.medical_conditions or [],
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
    
    def _calculate_age_range(self, date_of_birth: date) -> str:
        """Calculate age range for privacy"""
        today = date.today()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        
        if age < 18:
            return "under-18"
        elif age <= 30:
            return "18-30"
        elif age <= 40:
            return "31-40"
        elif age <= 50:
            return "41-50"
        elif age <= 60:
            return "51-60"
        elif age <= 70:
            return "61-70"
        else:
            return "71+"
