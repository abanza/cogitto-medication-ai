# app/infrastructure/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ..database.connection import get_db
from .jwt_manager import JWTManager
from ...services.user_service import UserService
from .models import UserProfile

# Security scheme
security = HTTPBearer()

# Create JWT manager (will be initialized when needed)
jwt_manager = JWTManager()

# Create user service (will be initialized when needed)
user_service = UserService()

def initialize_auth_components():
    """Initialize authentication components"""
    jwt_manager.initialize()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db)
) -> UserProfile:
    """Get current authenticated user"""
    
    # Ensure JWT manager is initialized
    jwt_manager._ensure_initialized()
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = jwt_manager.verify_token(credentials.credentials, "access")
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Get user from database
        user = await user_service.get_user_by_id(session, user_id)
        if user is None:
            raise credentials_exception
        
        return user
        
    except Exception:
        raise credentials_exception

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    session: AsyncSession = Depends(get_db)
) -> Optional[UserProfile]:
    """Get current user if authenticated, otherwise None"""
    
    if not credentials:
        return None
    
    try:
        # Ensure JWT manager is initialized
        jwt_manager._ensure_initialized()
        
        payload = jwt_manager.verify_token(credentials.credentials, "access")
        if payload is None:
            return None
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        return await user_service.get_user_by_id(session, user_id)
        
    except Exception:
        return None
