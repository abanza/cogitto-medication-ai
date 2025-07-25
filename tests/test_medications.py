# tests/test_medications.py
import pytest
from app.domain.models.medication import Medication, MedicationForm
from app.infrastructure.repositories.in_memory_medication_repository import InMemoryMedicationRepository
from app.domain.services.medication_service import CogittoMedicationService

@pytest.mark.asyncio
async def test_cogitto_search():
    """Test Cogitto's medication search"""
    repo = InMemoryMedicationRepository()
    service = CogittoMedicationService(repo)
    
    # Test search
    results = await service.search_medications("acetaminophen")
    assert len(results) == 1
    assert results[0].generic_name == "acetaminophen"

@pytest.mark.asyncio
async def test_cogitto_insights():
    """Test Cogitto's medication insights"""
    repo = InMemoryMedicationRepository()
    service = CogittoMedicationService(repo)
    
    # Test insights for prescription medication
    insights = await service.get_medication_insights("3")  # lisinopril
    assert insights["safety_level"] in ["medium", "high"]
    assert "cogitto_recommendation" in insights
