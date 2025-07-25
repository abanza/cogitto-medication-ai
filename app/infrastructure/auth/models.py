# app/infrastructure/auth/models.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
import re

class UserRegistration(BaseModel):
    """User registration data"""
    email: EmailStr
    password: str
    full_name: str
    phone_number: Optional[str] = None
    date_of_birth: Optional[str] = None  # YYYY-MM-DD format
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        return v
    
    @validator('phone_number')
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v and not re.match(r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$', v):
            raise ValueError('Invalid phone number format')
        return v

class UserLogin(BaseModel):
    """User login data"""
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    """User profile data"""
    id: str
    email: str
    full_name: str
    phone_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    age_range: Optional[str] = None
    allergies: Optional[list] = []
    medical_conditions: Optional[list] = []
    is_verified: bool = False
    created_at: datetime
    last_login_at: Optional[datetime] = None

class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile

class MedicalProfileUpdate(BaseModel):
    """Medical profile update data"""
    allergies: Optional[list] = None
    medical_conditions: Optional[list] = None
    age_range: Optional[str] = None
    
    @validator('age_range')
    def validate_age_range(cls, v):
        """Validate age range"""
        valid_ranges = ["18-30", "31-40", "41-50", "51-60", "61-70", "71+"]
        if v and v not in valid_ranges:
            raise ValueError(f'Age range must be one of: {", ".join(valid_ranges)}')
        return v
