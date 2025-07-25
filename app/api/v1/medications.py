# app/api/v1/medications.py
"""API endpoints for medication-related operations"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from ...domain.services.medication_service import CogittoMedicationService
from ...infrastructure.repositories.in_memory_medication_repository import InMemoryMedicationRepository
from ..schemas.medication_schemas import MedicationResponse, MedicationInsightsResponse

router = APIRouter()

# Dependency injection for Cogitto
def get_cogitto_service() -> CogittoMedicationService:
    repository = InMemoryMedicationRepository()
    return CogittoMedicationService(repository)

@router.get("/medications/search", response_model=List[MedicationResponse])
async def search_medications(
    q: str = Query(..., description="Search query", min_length=2),
    service: CogittoMedicationService = Depends(get_cogitto_service)
):
    """Search medications with Cogitto's intelligent matching"""
    try:
        medications = await service.search_medications(q)
        return [MedicationResponse.from_domain(med) for med in medications]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/medications/{medication_id}", response_model=MedicationResponse)
async def get_medication(
    medication_id: str,
    service: CogittoMedicationService = Depends(get_cogitto_service)
):
    """Get basic medication information"""
    try:
        medication = await service.get_medication_by_id(medication_id)
        if not medication:
            raise HTTPException(status_code=404, detail="Medication not found")
        return MedicationResponse.from_domain(medication)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get medication: {str(e)}")

@router.get("/medications/{medication_id}/insights", response_model=MedicationInsightsResponse)
async def get_medication_insights(
    medication_id: str,
    service: CogittoMedicationService = Depends(get_cogitto_service)
):
    """Get Cogitto's intelligent medication insights"""
    try:
        insights = await service.get_medication_insights(medication_id)
        return MedicationInsightsResponse.from_service_result(insights)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")
