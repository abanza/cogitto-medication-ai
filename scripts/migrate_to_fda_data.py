# scripts/migrate_to_fda_data.py
import asyncio
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.fda_data_loader import FDADataLoader

class DatabaseMigration:
    """Migrate Cogitto from 6 sample medications to FDA database"""
    
    def __init__(self):
        self.fda_loader = FDADataLoader()
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
    
    async def run_migration(self):
        """Execute the complete migration process"""
        
        print("🚀 Starting Cogitto FDA Database Migration...")
        print("=" * 50)
        
        # Step 1: Load FDA medications
        print("\n📊 Step 1: Loading medications from FDA Orange Book...")
        fda_medications = await self.fda_loader.load_common_medications()
        
        if not fda_medications:
            print("❌ No medications loaded from FDA. Check API connectivity.")
            return False
        
        print(f"✅ Loaded {len(fda_medications)} medications from FDA")
        
        # Step 2: Enhance with RxNorm data
        print("\n🔗 Step 2: Enhancing with RxNorm standardization...")
        enhanced_medications = await self.fda_loader.enhance_with_rxnorm_data(fda_medications)
        print(f"✅ Enhanced {len(enhanced_medications)} medications with RxNorm data")
        
        # Step 3: Load drug interactions
        print("\n⚡ Step 3: Loading drug interactions...")
        interactions = await self.fda_loader.load_drug_interactions(enhanced_medications)
        print(f"✅ Loaded {len(interactions)} drug interactions")
        
        # Step 4: Save processed data
        print("\n💾 Step 4: Saving processed data...")
        await self.save_processed_data(enhanced_medications, interactions)
        
        # Step 5: Generate migration summary
        print("\n📋 Step 5: Generating migration summary...")
        self.generate_migration_summary(enhanced_medications, interactions)
        
        print("\n🎉 Migration completed successfully!")
        print("Next step: Update your app.py to use the new FDA medication data.")
        
        return True
    
    async def save_processed_data(self, medications: list, interactions: list):
        """Save processed FDA data to files"""
        
        # Save medications
        medications_file = self.data_dir / "fda_medications.json"
        with open(medications_file, 'w') as f:
            json.dump(medications, f, indent=2, default=str)
        print(f"💾 Saved medications to: {medications_file}")
        
        # Save interactions
        interactions_file = self.data_dir / "fda_interactions.json"
        with open(interactions_file, 'w') as f:
            json.dump(interactions, f, indent=2, default=str)
        print(f"💾 Saved interactions to: {interactions_file}")
        
        # Generate Python code for easy integration
        python_code = self.generate_python_code(medications, interactions)
        code_file = self.data_dir / "fda_data_integration.py"
        with open(code_file, 'w') as f:
            f.write(python_code)
        print(f"🐍 Generated Python integration code: {code_file}")
    
    def generate_python_code(self, medications: list, interactions: list) -> str:
        """Generate Python code for easy app.py integration"""
        
        code = '''# Generated FDA Medication Data for Cogitto
# This file contains real FDA medication data to replace your sample data

from datetime import datetime

# FDA Medications Data - Ready for Cogitto Integration
FDA_MEDICATIONS_DATA = [
'''
        
        # Add first 25 medications (manageable size for initial integration)
        for med in medications[:25]:
            code += f"""    {{
        "id": "{med.get('generic_name', '').replace(' ', '_')}",
        "generic_name": "{med.get('generic_name', '')}",
        "brand_names": {med.get('brand_names', [])},
        "dosage_form": "{med.get('dosage_form', 'tablet')}",
        "strength": "{med.get('strength', 'varies')}",
        "prescription_required": {med.get('prescription_required', True)},
        "indications": {med.get('indications', ['as prescribed'])},
        "warnings": {med.get('warnings', ['follow healthcare provider instructions'])},
        "manufacturer": "{med.get('manufacturer', 'various')}",
        "data_source": "FDA_ORANGE_BOOK",
        "rxcui": "{med.get('rxcui', '')}"
    }},
"""
        
        code += "]\n\n# FDA Drug Interactions Data\nFDA_INTERACTIONS = {\n"
        
        # Add interactions
        for interaction in interactions[:50]:  # Limit to 50 interactions initially
            med1 = interaction.get('medication_1', '')
            med2 = interaction.get('medication_2', '')
            if med1 and med2 and med1 != med2:
                code += f'''    ("{med1}", "{med2}"): {{
        "severity": "{interaction.get('severity', 'unknown')}",
        "description": "{interaction.get('description', '')[:100]}...",
        "source": "FDA_RXNORM"
    }},
'''
        
        code += "}\n\n"
        
        # Add integration instructions
        code += '''
# Integration Instructions:
# 1. Replace MEDICATIONS_DATA in your app.py with FDA_MEDICATIONS_DATA
# 2. Replace INTERACTIONS with FDA_INTERACTIONS  
# 3. Update any ID references to use the new format
# 4. Test your endpoints to ensure compatibility

# Example usage:
# MEDICATIONS = [Medication(**med) for med in FDA_MEDICATIONS_DATA]

print(f"🏥 FDA Data loaded: {len(FDA_MEDICATIONS_DATA)} medications, {len(FDA_INTERACTIONS)} interactions")
'''
        
        return code
    
    def generate_migration_summary(self, medications: list, interactions: list):
        """Generate detailed migration summary"""
        
        print("\n" + "="*60)
        print("📊 COGITTO FDA MIGRATION SUMMARY")
        print("="*60)
        
        print(f"\n📋 Data Loaded:")
        print(f"   • Medications: {len(medications)}")
        print(f"   • Drug Interactions: {len(interactions)}")
        
        print(f"\n💊 Medication Breakdown:")
        prescription_count = sum(1 for med in medications if med.get('prescription_required', True))
        otc_count = len(medications) - prescription_count
        print(f"   • Prescription: {prescription_count}")
        print(f"   • Over-the-counter: {otc_count}")
        
        print(f"\n🏭 Data Sources:")
        print(f"   • FDA Orange Book: Drug approvals and labeling")
        print(f"   • RxNorm: Standardized drug names")
        print(f"   • FDA Drug Labels: Clinical information")
        
        print(f"\n⚡ Interaction Severity Breakdown:")
        severity_counts = {}
        for interaction in interactions:
            severity = interaction.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        for severity, count in severity_counts.items():
            print(f"   • {severity.title()}: {count}")
        
        print(f"\n🔍 Sample Medications Loaded:")
        for med in medications[:5]:
            brand_names = ", ".join(med.get('brand_names', [])[:2])
            print(f"   • {med.get('generic_name', '').title()}")
            if brand_names:
                print(f"     Brand names: {brand_names}")
        
        print(f"\n📁 Files Generated:")
        print(f"   • data/fda_medications.json")
        print(f"   • data/fda_interactions.json") 
        print(f"   • data/fda_data_integration.py")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Review generated data files")
        print(f"   2. Update app.py with FDA data")
        print(f"   3. Test API endpoints")
        print(f"   4. Deploy enhanced Cogitto!")
        
        print("="*60)

async def main():
    """Run the FDA migration"""
    migration = DatabaseMigration()
    
    try:
        success = await migration.run_migration()
        if success:
            print("\n✅ Migration completed successfully!")
            print("Check the 'data' directory for generated files.")
        else:
            print("\n❌ Migration failed. Check error messages above.")
    
    except Exception as e:
        print(f"\n💥 Migration error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

# Quick test script to verify FDA API connectivity
# scripts/test_fda_connectivity.py
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.external.fda_api_client import FDAOrangeBookClient

async def test_fda_connection():
    """Test FDA API connectivity"""
    
    print("🔍 Testing FDA API connectivity...")
    
    async with FDAOrangeBookClient() as fda_client:
        # Test with a common medication
        results = await fda_client.search_medications("acetaminophen", limit=5)
        
        if results:
            print(f"✅ FDA API working! Found {len(results)} results for acetaminophen")
            print(f"Sample result: {results[0].get('generic_name', 'Unknown')}")
            return True
        else:
            print("❌ FDA API test failed - no results returned")
            return False

if __name__ == "__main__":
    asyncio.run(test_fda_connection())