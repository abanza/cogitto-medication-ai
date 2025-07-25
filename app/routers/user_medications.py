# app/routers/user_medications.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.infrastructure.database.connection import get_db
from app.infrastructure.auth.dependencies import get_current_user
from app.models.user_medications import (
    UserMedicationCreate,
    UserMedicationUpdate,
    UserMedicationResponse,
    UserMedicationListResponse
)
from app.services.user_medications_service import UserMedicationsService

router = APIRouter(prefix="/user-medications", tags=["User Medications"])

@router.post("/", response_model=UserMedicationResponse)
async def create_user_medication(
    medication_data: UserMedicationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new medication to user's personal list"""
    try:
        service = UserMedicationsService(db)
        user_id = uuid.UUID(current_user["user_id"])
        
        medication = service.create_user_medication(user_id, medication_data)
        return service._row_to_medication_response(medication)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create medication"
        )

@router.get("/", response_model=UserMedicationListResponse)
async def get_user_medications(
    include_inactive: bool = False,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all medications for the current user"""
    try:
        service = UserMedicationsService(db)
        user_id = uuid.UUID(current_user["user_id"])
        
        return service.get_user_medications(user_id, include_inactive)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medications"
        )

@router.get("/{medication_id}", response_model=UserMedicationResponse)
async def get_user_medication(
    medication_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific medication from user's list"""
    try:
        service = UserMedicationsService(db)
        user_id = uuid.UUID(current_user["user_id"])
        
        medication = service.get_user_medication(user_id, medication_id)
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )
            
        return service._row_to_medication_response(medication)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medication"
        )

@router.put("/{medication_id}", response_model=UserMedicationResponse)
async def update_user_medication(
    medication_id: int,
    medication_data: UserMedicationUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a medication in user's list"""
    try:
        service = UserMedicationsService(db)
        user_id = uuid.UUID(current_user["user_id"])
        
        medication = service.update_user_medication(user_id, medication_id, medication_data)
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )
            
        return service._row_to_medication_response(medication)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update medication"
        )

@router.delete("/{medication_id}")
async def delete_user_medication(
    medication_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a medication from user's list (soft delete)"""
    try:
        service = UserMedicationsService(db)
        user_id = uuid.UUID(current_user["user_id"])
        
        success = service.delete_user_medication(user_id, medication_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )
            
        return {"message": "Medication removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete medication"
        )

@router.get("/active/names", response_model=List[str])
async def get_active_medication_names(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of active medication names for AI context"""
    try:
        service = UserMedicationsService(db)
        user_id = uuid.UUID(current_user["user_id"])
        
        return service.get_active_medication_names(user_id)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve active medications"
        )
