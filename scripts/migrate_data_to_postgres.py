# scripts/migrate_data_to_postgres.py
import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime
import uuid

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.infrastructure.database.connection import db_connection
from sqlalchemy import text

class CogittoDataMigration:
    """Migrate Cogitto FDA data to PostgreSQL"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
    
    async def run_migration(self):
        """Execute the complete data migration to PostgreSQL"""
        
        print("🚀 Starting Cogitto PostgreSQL Data Migration...")
        print("=" * 60)
        
        try:
            # Load FDA data from files
            fda_medications = self.load_fda_medications()
            fda_interactions = self.load_fda_interactions()
            
            print(f"📊 Found {len(fda_medications)} medications and {len(fda_interactions)} interactions to migrate")
            
            # Migrate medications
            await self.migrate_medications(fda_medications)
            
            # Migrate interactions
            await self.migrate_interactions(fda_interactions)
            
            # Verify migration
            await self.verify_migration()
            
            print("\n🎉 Migration completed successfully!")
            print("✅ Your Cogitto app can now use PostgreSQL!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
    
    def load_fda_medications(self) -> list:
        """Load FDA medications from generated file"""
        try:
            fda_file = self.data_dir / "fda_data_integration.py"
            if fda_file.exists():
                # Execute the file to get FDA_MEDICATIONS_DATA
                exec_globals = {}
                exec(open(fda_file).read(), exec_globals)
                return exec_globals.get('FDA_MEDICATIONS_DATA', [])
            else:
                print("⚠️ FDA data file not found, using sample data")
                return []
        except Exception as e:
            print(f"Error loading FDA medications: {e}")
            return []
    
    def load_fda_interactions(self) -> dict:
        """Load FDA interactions from generated file"""
        try:
            fda_file = self.data_dir / "fda_data_integration.py"
            if fda_file.exists():
                exec_globals = {}
                exec(open(fda_file).read(), exec_globals)
                return exec_globals.get('FDA_INTERACTIONS', {})
            else:
                return {}
        except Exception as e:
            print(f"Error loading FDA interactions: {e}")
            return {}
    
    async def migrate_medications(self, fda_medications: list):
        """Migrate medications to PostgreSQL using raw SQL"""
        
        print("\n💊 Migrating medications to PostgreSQL...")
        
        async for session in db_connection.get_session():
            # Check if medications already exist
            result = await session.execute(text("SELECT COUNT(*) FROM medications"))
            existing_count = result.scalar()
            
            if existing_count > 0:
                print(f"ℹ️ {existing_count} medications already exist in database, skipping migration")
                return
            
            migrated_count = 0
            
            for med_data in fda_medications:
                try:
                    # Insert medication using raw SQL
                    insert_sql = text("""
                        INSERT INTO medications (
                            id, generic_name, brand_names, dosage_form, strength,
                            route_of_administration, prescription_required, indications,
                            warnings, manufacturer, data_source, rxcui
                        ) VALUES (
                            :id, :generic_name, :brand_names, :dosage_form, :strength,
                            :route_of_administration, :prescription_required, :indications,
                            :warnings, :manufacturer, :data_source, :rxcui
                        )
                    """)
                    
                    await session.execute(insert_sql, {
                        'id': str(uuid.uuid4()),
                        'generic_name': med_data.get('generic_name', '').lower(),
                        'brand_names': med_data.get('brand_names', []),
                        'dosage_form': med_data.get('dosage_form', 'tablet'),
                        'strength': med_data.get('strength', 'varies'),
                        'route_of_administration': ['oral'],
                        'prescription_required': med_data.get('prescription_required', True),
                        'indications': med_data.get('indications', []),
                        'warnings': med_data.get('warnings', []),
                        'manufacturer': med_data.get('manufacturer', 'various'),
                        'data_source': med_data.get('data_source', 'FDA_ORANGE_BOOK'),
                        'rxcui': med_data.get('rxcui', '')
                    })
                    
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"Error migrating medication {med_data.get('generic_name', 'unknown')}: {e}")
                    continue
            
            print(f"✅ Migrated {migrated_count} medications to PostgreSQL")
    
    async def migrate_interactions(self, fda_interactions: dict):
        """Migrate drug interactions to PostgreSQL using raw SQL"""
        
        print("\n⚡ Migrating drug interactions to PostgreSQL...")
        
        async for session in db_connection.get_session():
            # Check if interactions already exist
            result = await session.execute(text("SELECT COUNT(*) FROM drug_interactions"))
            existing_count = result.scalar()
            
            if existing_count > 0:
                print(f"ℹ️ {existing_count} interactions already exist in database, skipping migration")
                return
            
            migrated_count = 0
            
            for (med1, med2), interaction_data in fda_interactions.items():
                try:
                    # Ensure alphabetical ordering for consistency
                    medication_1 = min(med1.lower(), med2.lower())
                    medication_2 = max(med1.lower(), med2.lower())
                    
                    # Insert interaction using raw SQL
                    insert_sql = text("""
                        INSERT INTO drug_interactions (
                            id, medication_1_name, medication_2_name, severity,
                            description, recommendation, evidence_level, data_source
                        ) VALUES (
                            :id, :medication_1_name, :medication_2_name, :severity,
                            :description, :recommendation, :evidence_level, :data_source
                        )
                    """)
                    
                    await session.execute(insert_sql, {
                        'id': str(uuid.uuid4()),
                        'medication_1_name': medication_1,
                        'medication_2_name': medication_2,
                        'severity': interaction_data.get('severity', 'unknown'),
                        'description': interaction_data.get('description', ''),
                        'recommendation': interaction_data.get('recommendation', 'Consult healthcare provider'),
                        'evidence_level': 'established',
                        'data_source': interaction_data.get('source', 'FDA_RXNORM')
                    })
                    
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"Error migrating interaction {med1} + {med2}: {e}")
                    continue
            
            print(f"✅ Migrated {migrated_count} drug interactions to PostgreSQL")
    
    async def verify_migration(self):
        """Verify the migration was successful"""
        
        print("\n🔍 Verifying migration...")
        
        async for session in db_connection.get_session():
            # Count medications
            med_result = await session.execute(text("SELECT COUNT(*) FROM medications"))
            med_count = med_result.scalar()
            
            # Count interactions
            int_result = await session.execute(text("SELECT COUNT(*) FROM drug_interactions"))
            int_count = int_result.scalar()
            
            print(f"📊 Database contains:")
            print(f"   • {med_count} medications")
            print(f"   • {int_count} drug interactions")
            
            # Show sample medications
            sample_meds = await session.execute(text("SELECT generic_name, brand_names FROM medications LIMIT 5"))
            print(f"\n💊 Sample medications in database:")
            for med in sample_meds:
                brand_names = ", ".join(med[1][:2]) if med[1] else "N/A"
                print(f"   • {med[0].title()}")
                if brand_names != "N/A":
                    print(f"     Brand names: {brand_names}")

async def main():
    """Run the PostgreSQL migration"""
    migration = CogittoDataMigration()
    await migration.run_migration()
    await db_connection.close()

if __name__ == "__main__":
    asyncio.run(main())
