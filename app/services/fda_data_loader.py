# app/services/fda_data_loader.py
import asyncio
from typing import List, Dict, Any
from ..infrastructure.external.fda_api_client import FDAOrangeBookClient
from ..infrastructure.external.rxnorm_client import RxNormClient

class FDADataLoader:
    """Service to load and process FDA medication data"""
    
    def __init__(self):
        self.fda_client = FDAOrangeBookClient()
        self.rxnorm_client = RxNormClient()
    
    async def load_common_medications(self) -> List[Dict[str, Any]]:
        """Load common medications from FDA database"""
        
        # List of common medications to load initially
        common_medications = [
            "acetaminophen", "ibuprofen", "aspirin", "lisinopril", "metformin",
            "atorvastatin", "amlodipine", "metoprolol", "omeprazole", "simvastatin",
            "losartan", "hydrochlorothiazide", "gabapentin", "sertraline", "levothyroxine",
            "amoxicillin", "prednisone", "tramadol", "ciprofloxacin", "warfarin",
            "furosemide", "pantoprazole", "escitalopram", "montelukast", "bupropion"
        ]
        
        print(f"Loading {len(common_medications)} common medications from FDA...")
        
        async with self.fda_client as fda, self.rxnorm_client as rxnorm:
            medications = await fda.bulk_load_medications(common_medications)
        
        print(f"Successfully loaded {len(medications)} medications from FDA database")
        return medications
    
    async def enhance_with_rxnorm_data(self, medications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance medication data with RxNorm standardization"""
        
        enhanced_medications = []
        
        async with self.rxnorm_client as rxnorm:
            for med in medications:
                try:
                    # Get RxNorm data for standardization
                    rxnorm_data = await rxnorm.search_drugs(med["generic_name"])
                    
                    if rxnorm_data:
                        med["rxcui"] = rxnorm_data[0].get("rxcui")
                        med["normalized_name"] = rxnorm_data[0].get("name", "").lower()
                    
                    enhanced_medications.append(med)
                    
                except Exception as e:
                    print(f"Error enhancing {med['generic_name']} with RxNorm: {e}")
                    enhanced_medications.append(med)  # Add without enhancement
        
        return enhanced_medications
    
    async def load_drug_interactions(self, medications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Load drug interactions for medications"""
        
        interactions = []
        
        async with self.rxnorm_client as rxnorm:
            for med in medications:
                rxcui = med.get("rxcui")
                if rxcui:
                    try:
                        med_interactions = await rxnorm.get_drug_interactions(rxcui)
                        for interaction in med_interactions:
                            interactions.append({
                                "medication_1": med["generic_name"],
                                "medication_2": interaction.get("drug2", "").lower(),
                                "severity": interaction.get("severity", "unknown"),
                                "description": interaction.get("description", ""),
                                "source": "RxNorm"
                            })
                    except Exception as e:
                        print(f"Error loading interactions for {med['generic_name']}: {e}")
        
        print(f"Loaded {len(interactions)} drug interactions from RxNorm")
        return interactions