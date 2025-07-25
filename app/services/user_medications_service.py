# app/services/user_medications_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, date
import logging
import uuid

from app.models.user_medications import (
    UserMedicationCreate, 
    UserMedicationUpdate, 
    UserMedication,
    UserMedicationResponse,
    UserMedicationListResponse
)

logger = logging.getLogger(__name__)

class UserMedicationsService:
    def __init__(self, db: Session):
        self.db = db

    def create_user_medication(self, user_id: uuid.UUID, medication_data: UserMedicationCreate) -> UserMedication:
        """Create a new user medication"""
        try:
            # Check if medication already exists for user
            existing = self.get_user_medication_by_name(user_id, medication_data.medication_name)
            if existing and existing.is_active:
                raise ValueError(f"Medication '{medication_data.medication_name}' already exists in your list")

            # Insert new medication
            query = text("""
                INSERT INTO user_medications 
                (user_id, medication_name, brand_name, dosage, frequency, start_date, end_date, notes)
                VALUES (:user_id, :medication_name, :brand_name, :dosage, :frequency, :start_date, :end_date, :notes)
                RETURNING *
            """)
            
            result = self.db.execute(query, {
                "user_id": str(user_id),  # Convert UUID to string for PostgreSQL
                "medication_name": medication_data.medication_name.lower().strip(),
                "brand_name": medication_data.brand_name,
                "dosage": medication_data.dosage,
                "frequency": medication_data.frequency,
                "start_date": medication_data.start_date,
                "end_date": medication_data.end_date,
                "notes": medication_data.notes
            })
            
            self.db.commit()
            row = result.fetchone()
            return self._row_to_medication(row)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user medication: {e}")
            raise

    def get_user_medications(self, user_id: uuid.UUID, include_inactive: bool = False) -> UserMedicationListResponse:
        """Get all medications for a user"""
        try:
            # Build query based on active status
            where_clause = "WHERE user_id = :user_id"
            if not include_inactive:
                where_clause += " AND is_active = TRUE"
            
            query = text(f"""
                SELECT * FROM user_medications 
                {where_clause}
                ORDER BY created_at DESC
            """)
            
            result = self.db.execute(query, {"user_id": str(user_id)})
            rows = result.fetchall()
            
            medications = [self._row_to_medication_response(row) for row in rows]
            
            # Calculate counts
            total_count = len(medications)
            active_count = sum(1 for med in medications if med.is_active)
            inactive_count = total_count - active_count
            
            return UserMedicationListResponse(
                medications=medications,
                total_count=total_count,
                active_count=active_count,
                inactive_count=inactive_count
            )
            
        except Exception as e:
            logger.error(f"Error getting user medications: {e}")
            raise

    def get_user_medication(self, user_id: uuid.UUID, medication_id: int) -> Optional[UserMedication]:
        """Get a specific user medication"""
        try:
            query = text("""
                SELECT * FROM user_medications 
                WHERE user_id = :user_id AND id = :medication_id
            """)
            
            result = self.db.execute(query, {
                "user_id": str(user_id),
                "medication_id": medication_id
            })
            
            row = result.fetchone()
            return self._row_to_medication(row) if row else None
            
        except Exception as e:
            logger.error(f"Error getting user medication: {e}")
            raise

    def get_user_medication_by_name(self, user_id: uuid.UUID, medication_name: str) -> Optional[UserMedication]:
        """Get user medication by name"""
        try:
            query = text("""
                SELECT * FROM user_medications 
                WHERE user_id = :user_id AND LOWER(medication_name) = LOWER(:medication_name)
                ORDER BY created_at DESC
                LIMIT 1
            """)
            
            result = self.db.execute(query, {
                "user_id": str(user_id),
                "medication_name": medication_name.strip()
            })
            
            row = result.fetchone()
            return self._row_to_medication(row) if row else None
            
        except Exception as e:
            logger.error(f"Error getting user medication by name: {e}")
            raise

    def update_user_medication(self, user_id: uuid.UUID, medication_id: int, 
                             medication_data: UserMedicationUpdate) -> Optional[UserMedication]:
        """Update a user medication"""
        try:
            # Build dynamic update query
            update_fields = []
            params = {"user_id": str(user_id), "medication_id": medication_id}
            
            for field, value in medication_data.model_dump(exclude_unset=True).items():
                if field == "medication_name" and value:
                    update_fields.append("medication_name = :medication_name")
                    params["medication_name"] = value.lower().strip()
                elif value is not None:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = value
            
            if not update_fields:
                return self.get_user_medication(user_id, medication_id)
            
            query = text(f"""
                UPDATE user_medications 
                SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = :user_id AND id = :medication_id
                RETURNING *
            """)
            
            result = self.db.execute(query, params)
            self.db.commit()
            
            row = result.fetchone()
            return self._row_to_medication(row) if row else None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user medication: {e}")
            raise

    def delete_user_medication(self, user_id: uuid.UUID, medication_id: int) -> bool:
        """Delete (deactivate) a user medication"""
        try:
            query = text("""
                UPDATE user_medications 
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = :user_id AND id = :medication_id
                RETURNING id
            """)
            
            result = self.db.execute(query, {
                "user_id": str(user_id),
                "medication_id": medication_id
            })
            self.db.commit()
            
            return result.fetchone() is not None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting user medication: {e}")
            raise

    def get_active_medication_names(self, user_id: uuid.UUID) -> List[str]:
        """Get list of active medication names for AI context"""
        try:
            query = text("""
                SELECT medication_name FROM user_medications 
                WHERE user_id = :user_id AND is_active = TRUE
                ORDER BY medication_name
            """)
            
            result = self.db.execute(query, {"user_id": str(user_id)})
            rows = result.fetchall()
            
            return [row[0] for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting active medication names: {e}")
            return []

    def _row_to_medication(self, row) -> UserMedication:
        """Convert database row to UserMedication model"""
        return UserMedication(
            id=row.id,
            user_id=uuid.UUID(str(row.user_id)),  # Convert string back to UUID
            medication_name=row.medication_name,
            brand_name=row.brand_name,
            dosage=row.dosage,
            frequency=row.frequency,
            start_date=row.start_date,
            end_date=row.end_date,
            notes=row.notes,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at
        )

    def _row_to_medication_response(self, row) -> UserMedicationResponse:
        """Convert database row to UserMedicationResponse model"""
        # Calculate duration if both dates are present
        duration_days = None
        if row.start_date and row.end_date:
            duration_days = (row.end_date - row.start_date).days

        # Check if medication is current (not expired)
        is_current = row.is_active
        if row.end_date and row.end_date < date.today():
            is_current = False

        return UserMedicationResponse(
            id=row.id,
            medication_name=row.medication_name,
            brand_name=row.brand_name,
            dosage=row.dosage,
            frequency=row.frequency,
            start_date=row.start_date,
            end_date=row.end_date,
            notes=row.notes,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
            duration_days=duration_days,
            is_current=is_current
        )
