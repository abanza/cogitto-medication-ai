# cogitto-medication-ai/app.py
# app.py - Cogitto: Medication AI Assistant
# Add these imports at the top
from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import uvicorn

# Add these imports to the top of your existing app.py
import uuid
from datetime import datetime
from openai import AsyncOpenAI
import json

# Load environment variables
load_dotenv()

# Initialize database connection after loading environment variables
from app.infrastructure.database.connection import db_connection
db_connection.initialize()

# Initialize authentication components
from app.infrastructure.auth.dependencies import initialize_auth_components
initialize_auth_components()

# Add these imports to the top of your app.py (after your existing imports)
from app.routers.auth import auth_router
from app.routers.user_medications import router as user_medications_router
from app.infrastructure.auth.dependencies import get_current_user_optional

# Verify OpenAI key is loaded (optional check)
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️ Warning: OPENAI_API_KEY not found in environment variables")
else:
    print("✅ OpenAI API key loaded successfully")

# Data models
class Medication(BaseModel):
    id: str
    generic_name: str
    brand_names: List[str]
    dosage_form: str
    strength: str
    prescription_required: bool
    indications: List[str]
    warnings: List[str]

class SearchResult(BaseModel):
    query: str
    results: List[Medication]
    count: int

class InteractionCheck(BaseModel):
    medication1: str
    medication2: str
    interaction_found: bool
    severity: Optional[str] = None
    description: Optional[str] = None
    recommendation: Optional[str] = None
    disclaimer: str

# Add these new data models for chat (add after your existing models)

class ChatMessageRequest(BaseModel):
    message: str
    session_id: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    session_id: str
    user_message: dict
    assistant_response: dict
    cogitto_insights: dict
    disclaimer: str
    session_context: dict

# Sample medication data
# MEDICATIONS_DATA = []
# Load the FDA medication data
exec(open('data/fda_data_integration.py').read())  

# Convert FDA data to Medication objects
MEDICATIONS = [Medication(**med) for med in FDA_MEDICATIONS_DATA]

# Drug interaction database
INTERACTIONS = {
    ("warfarin", "ibuprofen"): {
        "severity": "major",
        "description": "Increased bleeding risk due to antiplatelet effects",
        "recommendation": "Avoid combination. Use acetaminophen instead for pain relief."
    },
    ("warfarin", "acetaminophen"): {
        "severity": "moderate",
        "description": "High doses may enhance warfarin effect",
        "recommendation": "Monitor INR if using >2g/day acetaminophen"
    },
    ("lisinopril", "ibuprofen"): {
        "severity": "moderate",
        "description": "Reduced effectiveness of ACE inhibitor",
        "recommendation": "Monitor blood pressure. Consider acetaminophen alternative."
    },
    ("metformin", "atorvastatin"): {
        "severity": "minor",
        "description": "Rare reports of muscle problems",
        "recommendation": "Monitor for muscle pain or weakness"
    }
}
# Update interactions with FDA data
INTERACTIONS.update(FDA_INTERACTIONS)

# Add this AFTER your INTERACTIONS dictionary and BEFORE CHAT_SESSIONS = {}

# Create the real OpenAI client (add this after INTERACTIONS)
class CogittoOpenAI:
    """Real OpenAI integration for Cogitto"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ Warning: OPENAI_API_KEY not found, using fallback responses")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=api_key)
            print("✅ OpenAI client initialized successfully")
        
        # Enhanced medication knowledge for GPT-4 context
        self.medication_db = {med.generic_name: {
            "brand_names": med.brand_names,
            "uses": med.indications,
            "warnings": med.warnings,
            "prescription_required": med.prescription_required,
            "dosage_form": med.dosage_form,
            "strength": med.strength
        } for med in MEDICATIONS}
    
    async def generate_intelligent_response(self, message: str, mentioned_medications: List[str], user_context: dict = None) -> dict:
        """Generate intelligent response using GPT-4 with Cogitto's medical expertise"""
        
        # Fallback to mock if no OpenAI client
        if not self.client:
            return await self._generate_fallback_response(message, mentioned_medications)
        
        try:
            # Build context about mentioned medications
            medication_context = {}
            for med in mentioned_medications:
                if med in self.medication_db:
                    medication_context[med] = self.medication_db[med]
            
            # Check for interactions in our database
            interaction_info = self._check_interactions(mentioned_medications)
            
            # Build comprehensive system prompt
            system_prompt = f"""You are Cogitto, an advanced AI medication assistant. You provide accurate, helpful, and safe medication information.

CORE PRINCIPLES:
1. Patient safety is the absolute priority
2. Provide evidence-based information  
3. Always recommend consulting healthcare providers for medical decisions
4. Be clear about limitations and when professional help is needed
5. Use clear, empathetic communication

CURRENT USER QUERY: "{message}"

COGITTO'S MEDICATION DATABASE FOR MENTIONED DRUGS:
{json.dumps(medication_context, indent=2) if medication_context else "No specific medications in our database"}

INTERACTION ANALYSIS:
{json.dumps(interaction_info, indent=2) if interaction_info else "No known interactions in our database"}

USER CONTEXT:
{json.dumps(user_context, indent=2) if user_context else "No additional context provided"}

RESPONSE GUIDELINES:
1. Use the medication database above for accurate information
2. Include interaction warnings if found in the analysis above
3. Always include appropriate safety disclaimers
4. Recommend consulting healthcare providers for personalized advice
5. Use clear formatting with sections and bullet points
6. If emergency keywords detected, prioritize immediate care instructions

SAFETY PROTOCOLS:
- Emergency situations: Recommend calling 911/poison control immediately
- High-risk medications: Emphasize professional consultation
- Drug interactions: Clearly state severity and recommendations
- Pregnancy/breastfeeding: Require immediate healthcare provider consultation

Format your response clearly with sections like:
**Medication Information:**
**Safety Considerations:**
**Recommendations:**
**When to Seek Help:**"""

            # Prepare messages for GPT-4
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Call GPT-4
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=800,
                temperature=0.3,  # Lower temperature for medical accuracy
                presence_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content
            
            # Enhance with Cogitto's safety analysis
            enhanced_response = self._add_cogitto_safety_enhancements(
                ai_response, mentioned_medications, interaction_info
            )
            
            # Assess risk level
            risk_level = self._assess_risk_level(message, mentioned_medications, enhanced_response)
            
            return {
                "response": enhanced_response,
                "risk_level": risk_level,
                "confidence_score": 0.92,
                "mentioned_medications": mentioned_medications,
                "interaction_warnings": interaction_info.get("warnings", []) if interaction_info else [],
                "requires_consultation": self._requires_consultation(risk_level, enhanced_response),
                "ai_model": "gpt-4",
                "processing_successful": True
            }
            
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            # Fallback to safe response
            return await self._generate_fallback_response(message, mentioned_medications, str(e))
    
    def _check_interactions(self, medications: List[str]) -> dict:
        """Check for drug interactions using our interaction database"""
        warnings = []
        details = []
        
        if len(medications) >= 2:
            for i, med1 in enumerate(medications):
                for med2 in medications[i+1:]:
                    # Check our INTERACTIONS database
                    interaction = INTERACTIONS.get((med1, med2)) or INTERACTIONS.get((med2, med1))
                    if interaction:
                        warnings.append(f"{interaction['severity'].upper()}: {med1} + {med2}")
                        details.append({
                            "medications": [med1, med2],
                            "severity": interaction["severity"],
                            "description": interaction["description"],
                            "recommendation": interaction["recommendation"]
                        })
        
        return {"warnings": warnings, "details": details} if warnings else None
    
    def _add_cogitto_safety_enhancements(self, ai_response: str, medications: List[str], interactions: dict) -> str:
        """Add Cogitto's specialized safety enhancements"""
        enhanced = ai_response
        
        # Add interaction alerts
        if interactions and interactions.get("details"):
            enhanced += "\n\n🚨 **COGITTO INTERACTION ALERTS:**\n"
            for detail in interactions["details"]:
                severity_emoji = {"major": "⚠️", "moderate": "⚡", "minor": "ℹ️"}.get(detail["severity"], "⚠️")
                enhanced += f"\n{severity_emoji} **{detail['severity'].upper()}**: {' + '.join(detail['medications'])}\n"
                enhanced += f"**Issue**: {detail['description']}\n"
                enhanced += f"**Recommendation**: {detail['recommendation']}\n"
        
        # Add medication-specific safety info
        for med in medications:
            if med in self.medication_db:
                med_info = self.medication_db[med]
                if med_info.get("warnings"):
                    enhanced += f"\n\n🛡️ **{med.title()} Safety Information**:\n"
                    for warning in med_info["warnings"][:3]:  # Top 3 warnings
                        enhanced += f"• {warning}\n"
        
        return enhanced
    
    def _assess_risk_level(self, message: str, medications: List[str], response: str) -> str:
        """Assess overall risk level"""
        message_lower = message.lower()
        response_upper = response.upper()
        
        # Critical risk indicators
        if any(word in message_lower for word in ["emergency", "overdose", "poisoning"]):
            return "critical"
        if "CALL 911" in response_upper or "EMERGENCY" in response_upper:
            return "critical"
        
        # High risk indicators  
        if "MAJOR" in response_upper or "CONTRAINDICATED" in response_upper:
            return "high"
        if any(med in medications for med in ["warfarin"]):  # High-risk medications
            return "high"
        if any(word in message_lower for word in ["pregnant", "pregnancy", "breastfeeding"]):
            return "high"
        
        # Medium risk indicators
        if "MODERATE" in response_upper or len(medications) >= 2:
            return "medium"
        
        return "low"
    
    def _requires_consultation(self, risk_level: str, response: str) -> bool:
        """Determine if professional consultation is required"""
        return (risk_level in ["high", "critical"] or 
                any(phrase in response.lower() for phrase in ["consult", "see your doctor", "healthcare provider"]))
    
    async def _generate_fallback_response(self, message: str, medications: List[str], error: str = None) -> dict:
        """Generate fallback response when OpenAI is unavailable"""
        # Use your existing generate_ai_response function as fallback
        fallback_response = generate_ai_response(message, medications)
        risk_level = assess_risk_level(message, medications)
        
        return {
            "response": fallback_response + "\n\n**Note**: Using Cogitto's built-in knowledge base (OpenAI temporarily unavailable).",
            "risk_level": risk_level,
            "confidence_score": 0.75,
            "mentioned_medications": medications,
            "interaction_warnings": [],
            "requires_consultation": risk_level in ["high", "critical"],
            "ai_model": "cogitto-fallback",
            "processing_successful": False,
            "error": error or "OpenAI client not initialized"
        } # type: ignore

# Initialize the OpenAI client (add this after the class definition)
cogitto_ai = CogittoOpenAI()

# Simple in-memory storage for chat (add after INTERACTIONS)
CHAT_SESSIONS = {}
CONVERSATIONS = {}

# Mock AI responses (add after INTERACTIONS)
def generate_ai_response(message: str, mentioned_medications: List[str]) -> str:
    """Generate intelligent responses using Cogitto's knowledge"""
    message_lower = message.lower()
    
    # Drug interaction queries
    if any(word in message_lower for word in ["interact", "together", "with", "and"]) and len(mentioned_medications) >= 2:
        med1, med2 = mentioned_medications[0], mentioned_medications[1]
        
        # Check our interaction database
        interaction = INTERACTIONS.get((med1, med2)) or INTERACTIONS.get((med2, med1))
        
        if interaction:
            if interaction["severity"] == "major":
                return f"⚠️ **MAJOR INTERACTION FOUND**\n\nThere is a significant interaction between {med1} and {med2}. {interaction['description']}.\n\n**Recommendation**: {interaction['recommendation']}\n\nPlease consult your healthcare provider immediately."
            elif interaction["severity"] == "moderate":
                return f"⚡ **Moderate Interaction**\n\nThere is a moderate interaction between {med1} and {med2}. {interaction['description']}.\n\n**Recommendation**: {interaction['recommendation']}"
            else:
                return f"ℹ️ **Minor Interaction**\n\nThere is a minor interaction between {med1} and {med2}. {interaction['description']}"
        else:
            return f"✅ **No Major Interactions Found**\n\nI don't have any major interaction warnings for {med1} and {med2} in my current database.\n\n**Important**: Always consult your pharmacist when starting new medications."
    
    # Single medication information
    elif len(mentioned_medications) == 1:
        med_name = mentioned_medications[0]
        
        # Find medication in our database
        medication = None
        for med in MEDICATIONS:
            if med.generic_name.lower() == med_name.lower():
                medication = med
                break
            # Check brand names
            for brand in med.brand_names:
                if brand.lower() == med_name.lower():
                    medication = med
                    break
        
        if medication:
            response = f"**{medication.generic_name.title()} Information:**\n\n"
            response += f"**Brand Names**: {', '.join(medication.brand_names)}\n\n"
            response += f"**Form**: {medication.dosage_form} ({medication.strength})\n\n"
            response += f"**Uses**: {', '.join(medication.indications)}\n\n"
            response += f"**Important Warnings**:\n"
            for warning in medication.warnings:
                response += f"• {warning}\n"
            response += f"\n**Prescription Required**: {'Yes' if medication.prescription_required else 'No (Over-the-counter)'}"
            return response
        else:
            return f"I don't have detailed information about {med_name} in my current database. For comprehensive medication information, please consult your pharmacist or check the FDA's Orange Book."
    
    # General health questions
    elif any(word in message_lower for word in ["dosage", "dose", "how much"]):
        return "Dosage recommendations depend on many individual factors including your age, weight, medical conditions, and other medications. I cannot provide specific dosing advice.\n\n**Please consult**:\n• Your prescribing healthcare provider\n• Your pharmacist\n• The medication package insert"
    
    elif any(word in message_lower for word in ["side effect", "adverse", "reaction"]):
        if mentioned_medications:
            med_name = mentioned_medications[0]
            return f"Side effects can vary from person to person. For {med_name}, please:\n\n• Check the medication package insert\n• Consult your pharmacist\n• Contact your healthcare provider if you experience concerning symptoms\n\nAlways report serious side effects to your healthcare team."
        else:
            return "I can help you understand side effects for specific medications. Which medication are you asking about?"
    
    # Emergency situations
    elif any(word in message_lower for word in ["emergency", "overdose", "poisoning"]):
        return "🚨 **MEDICAL EMERGENCY**\n\nIf this is a medical emergency involving overdose or poisoning:\n\n**CALL IMMEDIATELY**:\n• 911 (Emergency)\n• Poison Control: 1-800-222-1222\n\nDo not delay seeking immediate medical attention."
    
    # Default helpful response
    else:
        return "I'm Cogitto, your medication AI assistant. I can help with:\n\n• Drug interaction checking\n• General medication information\n• Side effect information\n• Safety warnings\n\nWhat specific medication question can I help you with today? You can ask things like:\n• 'Can I take ibuprofen with warfarin?'\n• 'Tell me about acetaminophen'\n• 'What are the side effects of lisinopril?'"

def extract_medications_from_text(text: str) -> List[str]:
    """Extract medication names from user message"""
    text_lower = text.lower()
    found_medications = []
    
    # Check against our medication database
    for med in MEDICATIONS:
        # Check generic name
        if med.generic_name.lower() in text_lower:
            found_medications.append(med.generic_name.lower())
        
        # Check brand names
        for brand in med.brand_names:
            if brand.lower() in text_lower and med.generic_name.lower() not in found_medications:
                found_medications.append(med.generic_name.lower())
    
    return found_medications

def assess_risk_level(message: str, medications: List[str]) -> str:
    """Assess risk level of the query"""
    message_lower = message.lower()
    
    # Critical risk keywords
    if any(word in message_lower for word in ["emergency", "overdose", "poisoning"]):
        return "critical"
    
    # High risk scenarios
    high_risk_meds = ["warfarin"]
    if any(med in medications for med in high_risk_meds):
        return "high"
    
    # Moderate risk
    if any(word in message_lower for word in ["pregnant", "pregnancy", "breastfeeding"]):
        return "high"
    
    if len(medications) >= 2:  # Multiple medications
        return "medium"
    
    return "low"

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Cogitto: Medication AI Assistant started successfully!")
    print(f"📊 Loaded {len(MEDICATIONS)} medications")
    print(f"⚡ Tracking {len(INTERACTIONS)} drug interactions")
    print("🌐 Server running at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Test search: http://localhost:8000/medications/search?q=acetaminophen")
    yield
    # Shutdown
    print("👋 Shutting down Cogitto")

# Create FastAPI app (ONLY ONE DEFINITION)
app = FastAPI(
    title="Cogitto: Medication AI Assistant",
    description="AI-powered medication information, search, and interaction checking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ADD CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add these router includes (after your existing app = FastAPI() line)
app.include_router(auth_router)
app.include_router(user_medications_router)

@app.get("/")
async def root():
    """Welcome endpoint with API information"""
    return {
        "message": "🧠 Cogitto: Medication AI Assistant",
        "version": "1.0.0",
        "status": "running",
        "description": "AI-powered medication information, search, and interaction checking",
        "total_medications": len(MEDICATIONS),
        "features": [
            "Medication search by generic or brand name",
            "Drug interaction checking with safety levels", 
            "Detailed medication information with warnings",
            "Prescription vs OTC filtering",
            "Interactive API documentation"
        ],
        "endpoints": {
            "search": "/medications/search?q=acetaminophen",
            "details": "/medications/1",
            "list_all": "/medications",
            "interactions": "/interactions/check?med1=warfarin&med2=ibuprofen",
            "stats": "/stats"
        },
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "cogitto-medication-ai",
        "version": "1.0.0",
        "medications_loaded": len(MEDICATIONS),
        "interactions_tracked": len(INTERACTIONS)
    }

@app.get("/medications/search", response_model=SearchResult)
async def search_medications(
    q: str = Query(..., description="Search query (minimum 2 characters)", min_length=2)
):
    """Search medications by generic name or brand name"""
    query_lower = q.lower().strip()
    results = []
    
    for medication in MEDICATIONS:
        # Check generic name
        if query_lower in medication.generic_name.lower():
            results.append(medication)
            continue
        
        # Check brand names
        for brand in medication.brand_names:
            if query_lower in brand.lower():
                results.append(medication)
                break
    
    return SearchResult(query=q, results=results, count=len(results))

@app.get("/medications/{medication_id}", response_model=Medication)
async def get_medication(medication_id: str):
    """Get detailed medication information by ID"""
    for medication in MEDICATIONS:
        if medication.id == medication_id:
            return medication
    
    raise HTTPException(status_code=404, detail=f"Medication with ID {medication_id} not found")

@app.get("/medications", response_model=List[Medication])
async def list_medications():
    """List all available medications"""
    return MEDICATIONS

@app.get("/medications/filter/prescription")
async def get_prescription_medications():
    """Get medications that require prescription"""
    prescription_meds = [med for med in MEDICATIONS if med.prescription_required]
    return {
        "medications": prescription_meds,
        "count": len(prescription_meds),
        "type": "prescription_required"
    }

@app.get("/medications/filter/otc")
async def get_otc_medications():
    """Get over-the-counter medications"""
    otc_meds = [med for med in MEDICATIONS if not med.prescription_required]
    return {
        "medications": otc_meds,
        "count": len(otc_meds),
        "type": "over_the_counter"
    }

@app.get("/interactions/check", response_model=InteractionCheck)
async def check_drug_interactions(
    med1: str = Query(..., description="First medication (generic name)"),
    med2: str = Query(..., description="Second medication (generic name)")
):
    """Check for drug interactions between two medications"""
    
    # Normalize medication names
    medication1 = med1.lower().strip()
    medication2 = med2.lower().strip()
    
    # Check for interaction in both directions
    interaction = INTERACTIONS.get((medication1, medication2)) or INTERACTIONS.get((medication2, medication1))
    
    if interaction:
        return InteractionCheck(
            medication1=med1,
            medication2=med2,
            interaction_found=True,
            severity=interaction["severity"],
            description=interaction["description"],
            recommendation=interaction["recommendation"],
            disclaimer="⚠️ Always consult your pharmacist or healthcare provider about drug interactions."
        )
    else:
        return InteractionCheck(
            medication1=med1,
            medication2=med2,
            interaction_found=False,
            disclaimer="⚠️ No known major interactions found in our database. This is not comprehensive - always consult your pharmacist."
        )

@app.get("/stats")
async def get_statistics():
    """Get medication database statistics"""
    prescription_count = sum(1 for med in MEDICATIONS if med.prescription_required)
    otc_count = len(MEDICATIONS) - prescription_count
    
    return {
        "total_medications": len(MEDICATIONS),
        "prescription_required": prescription_count,
        "over_the_counter": otc_count,
        "known_interactions": len(INTERACTIONS),
        "dosage_forms": list(set(med.dosage_form for med in MEDICATIONS))
    }

# Add these new chat endpoints to your existing app (add after your current endpoints)

@app.post("/chat/start-session")
async def start_chat_session(
    current_medications: List[str] = [],
    user_id: Optional[str] = None
):
    """Start a new chat session with Cogitto"""
    session_id = str(uuid.uuid4())
    
    session = {
        "id": session_id,
        "user_id": user_id,
        "current_medications": [med.lower() for med in current_medications],
        "allergies": [],
        "created_at": datetime.utcnow(),
        "total_queries": 0,
        "conversations": []
    }
    
    CHAT_SESSIONS[session_id] = session
    
    return {
        "session_id": session_id,
        "message": "🧠 Chat session started with Cogitto!",
        "current_medications": session["current_medications"],
        "instructions": "You can now send messages using the /chat/message endpoint"
    }

# Replace your existing @app.post("/chat/message") endpoint with this:

@app.post("/chat/message", response_model=Dict[str, Any])
async def send_chat_message_with_openai(request: ChatMessageRequest):
    """Send a message to Cogitto and get GPT-4 powered intelligent response"""
    
    # Get or create session
    session = CHAT_SESSIONS.get(request.session_id)
    if not session:
        session = {
            "id": request.session_id,
            "current_medications": [],
            "allergies": [],
            "created_at": datetime.utcnow(),
            "total_queries": 0,
            "conversations": []
        }
        CHAT_SESSIONS[request.session_id] = session
    
    # Get or create conversation
    if request.conversation_id and request.conversation_id in CONVERSATIONS:
        conversation = CONVERSATIONS[request.conversation_id]
    else:
        conversation_id = str(uuid.uuid4())
        conversation = {
            "id": conversation_id,
            "session_id": request.session_id,
            "messages": [],
            "created_at": datetime.utcnow(),
            "risk_level": "low"
        }
        CONVERSATIONS[conversation_id] = conversation
        session["conversations"].append(conversation_id)
    
    # Extract medications from message
    mentioned_medications = extract_medications_from_text(request.message)
    
    # Prepare user context for AI
    user_context = {
        "current_medications": session.get("current_medications", []),
        "allergies": session.get("allergies", []),
        "session_queries": session.get("total_queries", 0)
    }
    
    # Generate intelligent AI response using OpenAI GPT-4
    ai_result = await cogitto_ai.generate_intelligent_response(
        request.message, mentioned_medications, user_context
    )
    
    # Create user message
    user_message = {
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": request.message,
        "timestamp": datetime.utcnow(),
        "mentioned_medications": mentioned_medications
    }
    
    # Create assistant message with enhanced AI response
    assistant_message = {
        "id": str(uuid.uuid4()),
        "role": "assistant", 
        "content": ai_result["response"],
        "timestamp": datetime.utcnow(),
        "risk_level": ai_result["risk_level"],
        "confidence_score": ai_result["confidence_score"],
        "ai_model": ai_result["ai_model"]
    }
    
    # Add messages to conversation
    conversation["messages"].extend([user_message, assistant_message])
    conversation["risk_level"] = ai_result["risk_level"]
    
    # Update session stats
    session["total_queries"] += 1
    
    # Generate enhanced disclaimer
    if ai_result["risk_level"] == "critical":
        disclaimer = "🚨 CRITICAL: This query involves potentially serious medical concerns. Please seek immediate medical attention."
    elif ai_result["risk_level"] == "high":
        disclaimer = "⚠️ IMPORTANT: Please consult your healthcare provider or pharmacist immediately about this medication concern."
    elif ai_result["risk_level"] == "medium":
        disclaimer = "⚡ Please discuss this information with your pharmacist or healthcare provider."
    else:
        disclaimer = "ℹ️ Cogitto provides educational information only. Always consult your healthcare provider for medical advice."
    
    # Generate enhanced insights
    insights = {
        "mentioned_medications": mentioned_medications,
        "medication_insights": [f"AI Analysis: {', '.join(mentioned_medications)}"] if mentioned_medications else [],
        "safety_recommendations": [
            f"Response generated by {ai_result['ai_model']}",
            "Information cross-referenced with Cogitto's medical database",
            "Always verify with healthcare professionals"
        ],
        "interaction_warnings": ai_result.get("interaction_warnings", []),
        "followup_questions": [
            "Would you like more details about any specific medication?",
            "Do you have questions about timing or dosages?",
            "Are there other medications you're concerned about?"
        ],
        "ai_processing": {
            "model_used": ai_result["ai_model"],
            "confidence_score": ai_result["confidence_score"],
            "processing_successful": ai_result["processing_successful"]
        }
    }
    
    return {
        "conversation_id": conversation["id"],
        "session_id": request.session_id,
        "user_message": user_message,
        "assistant_response": assistant_message,
        "cogitto_insights": insights,
        "disclaimer": disclaimer,
        "session_context": {
            "total_queries": session["total_queries"],
            "current_medications": session["current_medications"],
            "overall_risk_level": ai_result["risk_level"]
        }
    }

@app.get("/chat/conversation/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """Get conversation history"""
    conversation = CONVERSATIONS.get(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "conversation_id": conversation["id"],
        "messages": conversation["messages"],
        "created_at": conversation["created_at"],
        "total_messages": len(conversation["messages"]),
        "risk_level": conversation["risk_level"]
    }

@app.get("/chat/demo")
async def chat_demo():
    """Demo endpoint to showcase Cogitto chat capabilities"""
    session_id = str(uuid.uuid4())
    
    return {
        "message": "🧠 Welcome to Cogitto Chat Demo!",
        "demo_session_id": session_id,
        "try_these_questions": [
            "Can I take ibuprofen with warfarin?",
            "What is acetaminophen used for?",
            "Tell me about lisinopril side effects",
            "Is it safe to take Tylenol and Advil together?"
        ],
        "api_usage": {
            "start_session": f"POST /chat/start-session",
            "send_message": f"POST /chat/message",
            "example_request": {
                "message": "Can I take ibuprofen with warfarin?",
                "session_id": session_id
            }
        },
        "features": [
            "🔍 Intelligent medication search",
            "⚡ Drug interaction checking",
            "🛡️ Safety risk assessment", 
            "💡 Personalized recommendations",
            "🧠 Context-aware conversations"
        ]
    }

# Add this test endpoint before if __name__ == "__main__":
@app.get("/chat/openai-test")
async def test_openai_integration():
    """Test OpenAI integration"""
    try:
        # Simple test query
        test_result = await cogitto_ai.generate_intelligent_response(
            "What is acetaminophen used for?", 
            ["acetaminophen"], 
            {}
        )
        
        return {
            "status": "OpenAI integration working!" if test_result["processing_successful"] else "Using fallback mode",
            "test_response": test_result["response"][:200] + "...",
            "model_used": test_result["ai_model"],
            "confidence": test_result["confidence_score"],
            "processing_successful": test_result["processing_successful"]
        }
    except Exception as e:
        return {
            "status": "OpenAI integration test failed",
            "error": str(e),
            "fallback_available": True
        }

if __name__ == "__main__":
    print("🚀 Starting Cogitto: Medication AI Assistant...")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)