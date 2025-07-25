# app/domain/services/medication_service.py
from typing import List, Optional
from ..models.medication import Medication
from ..repositories.medication_repository import MedicationRepository

class CogittoMedicationService:
    """Cogitto's core medication business logic"""
    
    def __init__(self, repository: MedicationRepository):
        self.repository = repository
    
    async def search_medications(self, query: str) -> List[Medication]:
        """Intelligent medication search with validation"""
        if not query or len(query.strip()) < 2:
            raise ValueError("Search query must be at least 2 characters")
        
        results = await self.repository.search(query.strip())
        return results
    
    async def get_medication_by_id(self, medication_id: str) -> Optional[Medication]:
        """Get medication by ID with validation"""
        if not medication_id:
            raise ValueError("Medication ID is required")
        
        return await self.repository.find_by_id(medication_id)
    
    async def get_medication_insights(self, medication_id: str) -> dict:
        """Get comprehensive medication insights - Cogitto's enhanced view"""
        medication = await self.get_medication_by_id(medication_id)
        
        if not medication:
            raise ValueError(f"Medication not found: {medication_id}")
        
        # Cogitto's safety assessment
        safety_level = "low"
        safety_factors = []
        
        if medication.prescription_required:
            safety_level = "medium"
            safety_factors.append("prescription_required")
        
        # Check for high-risk warnings
        high_risk_keywords = ["monitor", "toxicity", "bleeding", "liver", "kidney"]
        for warning in medication.warnings:
            if any(keyword in warning.lower() for keyword in high_risk_keywords):
                safety_level = "high"
                safety_factors.append("requires_monitoring")
                break
        
        return {
            "medication": medication,
            "safety_level": safety_level,
            "safety_factors": safety_factors,
            "cogitto_recommendation": self._generate_recommendation(medication, safety_level),
            "disclaimer": "Cogitto provides educational information only. Always consult your healthcare provider."
        }
    
    def _generate_recommendation(self, medication: Medication, safety_level: str) -> str:
        """Generate Cogitto's intelligent recommendation"""
        if safety_level == "high":
            return f"⚠️ {medication.generic_name} requires careful monitoring. Consult your healthcare provider."
        elif safety_level == "medium":
            return f"💊 {medication.generic_name} is prescription-only. Follow your doctor's instructions."
        else:
            return f"ℹ️ {medication.generic_name} is generally safe when used as directed."
