# app/api/schemas/medication_schemas.py
"""Schemas for medication-related API responses"""
from pydantic import BaseModel
from typing import List
from ...domain.models.medication import Medication, MedicationForm

class MedicationResponse(BaseModel):
    """Response model for Cogitto medication data"""
    id: str
    generic_name: str
    brand_names: List[str]
    dosage_form: str
    strength_description: str
    prescription_required: bool
    indications: List[str]
    warnings: List[str]
    
    @classmethod
    def from_domain(cls, medication: Medication) -> "MedicationResponse":
        return cls(
            id=medication.id,
            generic_name=medication.generic_name,
            brand_names=medication.brand_names,
            dosage_form=medication.dosage_form.value,
            strength_description=medication.strength_description,
            prescription_required=medication.prescription_required,
            indications=medication.indications,
            warnings=medication.warnings
        )

class MedicationInsightsResponse(BaseModel):
    """Cogitto's enhanced medication insights"""
    medication: MedicationResponse
    safety_level: str
    safety_factors: List[str]
    cogitto_recommendation: str
    disclaimer: str
    
    @classmethod
    def from_service_result(cls, service_result: dict) -> "MedicationInsightsResponse":
        return cls(
            medication=MedicationResponse.from_domain(service_result["medication"]),
            safety_level=service_result["safety_level"],
            safety_factors=service_result["safety_factors"],
            cogitto_recommendation=service_result["cogitto_recommendation"],
            disclaimer=service_result["disclaimer"]
        )
