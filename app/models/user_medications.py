# app/models/user_medications.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
import uuid

class FrequencyEnum(str, Enum):
    ONCE_DAILY = "once_daily"
    TWICE_DAILY = "twice_daily"
    THREE_TIMES_DAILY = "three_times_daily"
    FOUR_TIMES_DAILY = "four_times_daily"
    AS_NEEDED = "as_needed"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class UserMedicationBase(BaseModel):
    medication_name: str = Field(..., min_length=1, max_length=255, description="Name of the medication")
    brand_name: Optional[str] = Field(None, max_length=255, description="Brand name if applicable")
    dosage: Optional[str] = Field(None, max_length=100, description="Dosage amount (e.g., '500mg', '10ml')")
    frequency: Optional[str] = Field(None, max_length=100, description="How often to take")
    start_date: Optional[date] = Field(None, description="When medication was started")
    end_date: Optional[date] = Field(None, description="When to stop medication")
    notes: Optional[str] = Field(None, description="Additional notes about the medication")

class UserMedicationCreate(UserMedicationBase):
    pass

class UserMedicationUpdate(BaseModel):
    medication_name: Optional[str] = Field(None, min_length=1, max_length=255)
    brand_name: Optional[str] = Field(None, max_length=255)
    dosage: Optional[str] = Field(None, max_length=100)
    frequency: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class UserMedication(UserMedicationBase):
    id: int
    user_id: uuid.UUID  # Changed from int to UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserMedicationResponse(BaseModel):
    id: int
    medication_name: str
    brand_name: Optional[str]
    dosage: Optional[str]
    frequency: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Additional computed fields
    duration_days: Optional[int] = None
    is_current: bool = True
    medication_info: Optional[dict] = None  # Will be populated with FDA data

class UserMedicationListResponse(BaseModel):
    medications: List[UserMedicationResponse]
    total_count: int
    active_count: int
    inactive_count: int
