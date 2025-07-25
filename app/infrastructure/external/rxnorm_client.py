# app/infrastructure/external/rxnorm_client.py
import aiohttp
from typing import List, Dict, Any, Optional
import json

class RxNormClient:
    """Client for RxNorm API - standardized medication names"""
    
    def __init__(self):
        self.base_url = "https://rxnav.nlm.nih.gov/REST"
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search_drugs(self, name: str) -> List[Dict[str, Any]]:
        """Search for drugs by name"""
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            endpoint = f"{self.base_url}/drugs.json"
            params = {"name": name}
            
            async with self.session.get(endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_drug_search_results(data)
                else:
                    return []
                    
        except Exception as e:
            print(f"RxNorm API error: {e}")
            return []
    
    async def get_drug_interactions(self, rxcui: str) -> List[Dict[str, Any]]:
        """Get drug interactions for a specific RxCUI"""
        
        try:
            endpoint = f"{self.base_url}/interaction/interaction.json"
            params = {"rxcui": rxcui}
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_interaction_results(data)
                else:
                    return []
                    
        except Exception as e:
            print(f"RxNorm interaction API error: {e}")
            return []
    
    async def normalize_drug_name(self, name: str) -> Optional[str]:
        """Normalize drug name using RxNorm"""
        
        try:
            drugs = await self.search_drugs(name)
            if drugs:
                # Return the first normalized name
                return drugs[0].get("name", "").lower()
            return None
            
        except Exception as e:
            print(f"Drug name normalization error: {e}")
            return None
    
    def _process_drug_search_results(self, data: Dict) -> List[Dict[str, Any]]:
        """Process RxNorm drug search results"""
        
        drugs = []
        drug_group = data.get("drugGroup", {})
        concept_group = drug_group.get("conceptGroup", [])
        
        for group in concept_group:
            concept_properties = group.get("conceptProperties", [])
            for concept in concept_properties:
                drugs.append({
                    "rxcui": concept.get("rxcui"),
                    "name": concept.get("name"),
                    "synonym": concept.get("synonym"),
                    "tty": concept.get("tty"),  # Term type
                    "language": concept.get("language")
                })
        
        return drugs
    
    def _process_interaction_results(self, data: Dict) -> List[Dict[str, Any]]:
        """Process RxNorm interaction results"""
        
        interactions = []
        interaction_type_group = data.get("interactionTypeGroup", [])
        
        for type_group in interaction_type_group:
            interaction_type = type_group.get("interactionType", [])
            for interaction in interaction_type:
                interaction_pair = interaction.get("interactionPair", [])
                for pair in interaction_pair:
                    interactions.append({
                        "severity": pair.get("severity"),
                        "description": pair.get("description"),
                        "drug1": pair.get("interactionConcept", [{}])[0].get("minConceptItem", {}).get("name") if pair.get("interactionConcept") else None,
                        "drug2": pair.get("interactionConcept", [{}])[1].get("minConceptItem", {}).get("name") if len(pair.get("interactionConcept", [])) > 1 else None
                    })
        
        return interactions