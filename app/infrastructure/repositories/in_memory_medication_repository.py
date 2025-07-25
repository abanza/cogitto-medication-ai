# app/infrastructure/repositories/in_memory_medication_repository.py
from typing import List, Optional
from ...domain.models.medication import Medication, MedicationForm

class InMemoryMedicationRepository:
    """In-memory repository for Cogitto - rapid prototyping"""
    
    def __init__(self):
        # Enhanced sample data with more medications
        self.medications = [
            Medication(
                id="1",
                generic_name="acetaminophen",
                brand_names=["Tylenol", "Panadol"],
                dosage_form=MedicationForm.TABLET,
                strength_description="500mg",
                prescription_required=False,
                indications=["pain relief", "fever reduction"],
                warnings=["Do not exceed 4000mg per day", "Hepatotoxicity with overdose"]
            ),
            Medication(
                id="2", 
                generic_name="ibuprofen",
                brand_names=["Advil", "Motrin"],
                dosage_form=MedicationForm.TABLET,
                strength_description="200mg",
                prescription_required=False,
                indications=["pain relief", "inflammation", "fever"],
                warnings=["Take with food", "GI bleeding risk", "Cardiovascular risk"]
            ),
            Medication(
                id="3",
                generic_name="lisinopril",
                brand_names=["Prinivil", "Zestril"],
                dosage_form=MedicationForm.TABLET,
                strength_description="10mg",
                prescription_required=True,
                indications=["high blood pressure", "heart failure"],
                warnings=["Monitor blood pressure", "May cause dry cough", "Kidney monitoring"]
            ),
            Medication(
                id="4",
                generic_name="metformin",
                brand_names=["Glucophage", "Fortamet"],
                dosage_form=MedicationForm.TABLET,
                strength_description="500mg",
                prescription_required=True,
                indications=["type 2 diabetes"],
                warnings=["Take with meals", "Monitor kidney function", "Lactic acidosis risk"]
            ),
            Medication(
                id="5",
                generic_name="atorvastatin",
                brand_names=["Lipitor"],
                dosage_form=MedicationForm.TABLET,
                strength_description="20mg",
                prescription_required=True,
                indications=["high cholesterol", "cardiovascular disease prevention"],
                warnings=["Monitor liver function", "Muscle pain risk", "Drug interactions"]
            ),
            Medication(
                id="6",
                generic_name="omeprazole",
                brand_names=["Prilosec"],
                dosage_form=MedicationForm.CAPSULE,
                strength_description="20mg",
                prescription_required=False,
                indications=["heartburn", "GERD", "stomach ulcers"],
                warnings=["Long-term use concerns", "Magnesium deficiency", "B12 deficiency"]
            )
        ]
    
    async def find_by_id(self, medication_id: str) -> Optional[Medication]:
        """Find medication by ID"""
        for med in self.medications:
            if med.id == medication_id:
                return med
        return None
    
    async def find_by_generic_name(self, name: str) -> Optional[Medication]:
        """Find medication by generic name"""
        name_lower = name.lower()
        for med in self.medications:
            if med.generic_name.lower() == name_lower:
                return med
        return None
    
    async def search(self, query: str) -> List[Medication]:
        """Search medications by name (generic or brand)"""
        query_lower = query.lower()
        results = []
        
        for med in self.medications:
            # Check generic name
            if query_lower in med.generic_name.lower():
                results.append(med)
                continue
            
            # Check brand names
            for brand in med.brand_names:
                if query_lower in brand.lower():
                    results.append(med)
                    break
        
        return results
    
    async def get_all(self) -> List[Medication]:
        """Get all medications"""
        return self.medications
