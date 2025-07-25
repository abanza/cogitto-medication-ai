# scripts/run_app.py
import uvicorn
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == "__main__":
    print("🚀 Starting Cogitto: Medication AI Assistant...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
