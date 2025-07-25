# app/domain/models/medication.py
"""Core medication model for Cogitto"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class MedicationForm(Enum):
    TABLET = "tablet"
    CAPSULE = "capsule"
    LIQUID = "liquid"
    INJECTION = "injection"
    TOPICAL = "topical"
    INHALER = "inhaler"

@dataclass
class Medication:
    """Core medication entity for Cogitto"""
    id: str
    generic_name: str
    brand_names: List[str]
    dosage_form: MedicationForm
    strength_description: str
    prescription_required: bool = True
    indications: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.indications is None:
            self.indications = []
        if self.warnings is None:
            self.warnings = []
        
        if not self.generic_name:
            raise ValueError("Generic name is required")
