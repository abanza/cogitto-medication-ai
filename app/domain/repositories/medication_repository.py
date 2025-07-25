# /app/domain/repositories/medication_repository.py

from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.medication import Medication

class MedicationRepository(ABC):
    """Repository interface for Cogitto's medication data access"""
    
    @abstractmethod
    async def find_by_id(self, medication_id: str) -> Optional[Medication]:
        pass
    
    @abstractmethod
    async def find_by_generic_name(self, name: str) -> Optional[Medication]:
        pass
    
    @abstractmethod
    async def search(self, query: str) -> List[Medication]:
        pass
