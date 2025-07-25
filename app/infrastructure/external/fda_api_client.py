# app/infrastructure/external/fda_api_client.py
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import pandas as pd
from urllib.parse import quote

class FDAOrangeBookClient:
    """Client for FDA Orange Book API - real medication data"""
    
    def __init__(self):
        self.base_url = "https://api.fda.gov/drug"
        self.session = None
        
        # FDA Orange Book provides generic drug approvals and therapeutic equivalence
        # No API key required for basic usage (up to 240 requests per minute)
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search_medications(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search FDA database for medications"""
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # FDA Drug Labels API endpoint
            endpoint = f"{self.base_url}/label.json"
            
            # Build search query for drug labels
            params = {
                "search": f"openfda.generic_name:{quote(query)}",
                "limit": min(limit, 100)  # FDA limit is 100 per request
            }
            
            async with self.session.get(endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._process_fda_drug_labels(data.get("results", []))
                else:
                    print(f"FDA API error: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"FDA API request failed: {e}")
            return []
    
    async def get_drug_details(self, generic_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific drug"""
        
        try:
            # Search for specific drug
            results = await self.search_medications(generic_name, limit=1)
            return results[0] if results else None
            
        except Exception as e:
            print(f"Error getting drug details for {generic_name}: {e}")
            return None
    
    async def get_therapeutic_equivalents(self, generic_name: str) -> List[Dict[str, Any]]:
        """Get therapeutically equivalent medications"""
        
        try:
            endpoint = f"{self.base_url}/ndc.json"
            params = {
                "search": f"generic_name:{quote(generic_name)}",
                "limit": 50
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(endpoint, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._process_ndc_data(data.get("results", []))
                else:
                    return []
                    
        except Exception as e:
            print(f"Error getting therapeutic equivalents: {e}")
            return []
    
    async def bulk_load_medications(self, medication_list: List[str]) -> List[Dict[str, Any]]:
        """Bulk load multiple medications efficiently"""
        
        medications = []
        
        # Process in batches to respect rate limits
        batch_size = 10
        for i in range(0, len(medication_list), batch_size):
            batch = medication_list[i:i + batch_size]
            
            # Process batch concurrently
            tasks = [self.get_drug_details(med) for med in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, dict):
                    medications.append(result)
            
            # Rate limiting - FDA allows 240 requests per minute
            await asyncio.sleep(0.5)  # Small delay between batches
        
        return medications
    
    async def _process_fda_drug_labels(self, raw_results: List[Dict]) -> List[Dict[str, Any]]:
        """Process FDA drug label data into Cogitto format"""
        
        processed_medications = []
        
        for result in raw_results:
            try:
                # Extract OpenFDA data
                openfda = result.get("openfda", {})
                
                # Basic medication info
                generic_name = self._extract_first_value(openfda.get("generic_name", []))
                brand_names = openfda.get("brand_name", [])
                
                if not generic_name:
                    continue  # Skip if no generic name
                
                # Extract dosage and route information
                dosage_form = self._extract_first_value(openfda.get("dosage_form", []))
                route = openfda.get("route", [])
                
                # Extract indications and usage
                indications_and_usage = result.get("indications_and_usage", [])
                indications = self._extract_indications(indications_and_usage)
                
                # Extract warnings and precautions
                warnings = self._extract_warnings(result)
                
                # Determine if prescription required (most FDA drugs are prescription)
                prescription_required = self._determine_prescription_status(result, openfda)
                
                processed_med = {
                    "generic_name": generic_name.lower(),
                    "brand_names": [name for name in brand_names if name][:5],  # Limit to 5 brand names
                    "dosage_form": dosage_form or "unknown",
                    "strength": self._extract_strength(openfda),
                    "route_of_administration": route[:3] if route else ["oral"],  # Limit to 3 routes
                    "prescription_required": prescription_required,
                    "indications": indications[:5],  # Limit to 5 indications
                    "warnings": warnings[:5],  # Limit to 5 warnings
                    "manufacturer": self._extract_first_value(openfda.get("manufacturer_name", [])),
                    "ndc_numbers": openfda.get("product_ndc", [])[:3],  # Limit to 3 NDCs
                    "data_source": "FDA_DRUG_LABELS",
                    "last_updated": datetime.utcnow().isoformat()
                }
                
                processed_medications.append(processed_med)
                
            except Exception as e:
                print(f"Error processing FDA result: {e}")
                continue
        
        return processed_medications
    
    async def _process_ndc_data(self, raw_results: List[Dict]) -> List[Dict[str, Any]]:
        """Process FDA NDC data"""
        
        processed = []
        for result in raw_results:
            try:
                processed.append({
                    "product_ndc": result.get("product_ndc"),
                    "generic_name": result.get("generic_name", "").lower(),
                    "brand_name": result.get("brand_name"),
                    "dosage_form": result.get("dosage_form"),
                    "route": result.get("route"),
                    "marketing_status": result.get("marketing_status")
                })
            except Exception as e:
                print(f"Error processing NDC data: {e}")
                continue
        
        return processed
    
    def _extract_first_value(self, value_list: List[str]) -> str:
        """Extract first non-empty value from list"""
        return next((val for val in value_list if val and val.strip()), "")
    
    def _extract_strength(self, openfda: Dict) -> str:
        """Extract strength information"""
        substance_name = openfda.get("substance_name", [])
        if substance_name:
            return f"{substance_name[0]} strength varies"
        return "strength not specified"
    
    def _extract_indications(self, indications_raw: List[str]) -> List[str]:
        """Extract and clean indications"""
        if not indications_raw:
            return ["indication not specified"]
        
        # Take first indication text and extract key phrases
        text = indications_raw[0] if indications_raw else ""
        
        # Simple extraction of key medical terms
        common_indications = [
            "pain", "inflammation", "blood pressure", "diabetes", "infection",
            "cholesterol", "heart", "depression", "anxiety", "seizure",
            "cancer", "arthritis", "asthma", "allergy"
        ]
        
        found_indications = []
        text_lower = text.lower()
        
        for indication in common_indications:
            if indication in text_lower:
                found_indications.append(indication)
        
        return found_indications if found_indications else ["as prescribed by healthcare provider"]
    
    def _extract_warnings(self, result: Dict) -> List[str]:
        """Extract warnings and precautions"""
        warnings = []
        
        # Check various warning fields
        warning_fields = [
            "boxed_warning",
            "warnings_and_cautions", 
            "warnings",
            "contraindications"
        ]
        
        for field in warning_fields:
            if field in result and result[field]:
                warning_text = result[field][0] if isinstance(result[field], list) else result[field]
                if warning_text:
                    # Extract first sentence or key warning
                    first_sentence = warning_text.split('.')[0]
                    if len(first_sentence) < 200:  # Keep warnings concise
                        warnings.append(first_sentence.strip())
        
        # Add default warning if no specific warnings found
        if not warnings:
            warnings.append("Follow healthcare provider instructions")
        
        return warnings
    
    def _determine_prescription_status(self, result: Dict, openfda: Dict) -> bool:
        """Determine if medication requires prescription"""
        
        # Check marketing status or other indicators
        marketing_status = result.get("marketing_status", "")
        
        # Most FDA-tracked drugs are prescription
        # OTC drugs are less commonly in the drug label database
        return True  # Default to prescription required for safety