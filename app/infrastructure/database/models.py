# app/infrastructure/database/models.py
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ARRAY, Date, DECIMAL, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from datetime import datetime
from uuid import uuid4
from .connection import Base

class User(Base):
    """User model for Cogitto"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    date_of_birth = Column(Date)
    phone_number = Column(String(20))
    
    # Medical profile
    age_range = Column(String(20))  # "18-30", "31-50", etc.
    allergies = Column(ARRAY(Text))
    medical_conditions = Column(ARRAY(Text))
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255))
    
    # Privacy and compliance
    privacy_consent = Column(Boolean, default=False)
    hipaa_acknowledgment = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime)
    deleted_at = Column(DateTime)
    
    # Relationships
    user_medications = relationship("UserMedication", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")

class Medication(Base):
    """Enhanced medication model with FDA data"""
    __tablename__ = "medications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Core medication info
    generic_name = Column(String(255), nullable=False, index=True)
    brand_names = Column(ARRAY(Text))
    dosage_form = Column(String(100))
    strength = Column(String(100))
    route_of_administration = Column(ARRAY(Text))
    
    # Regulatory info
    prescription_required = Column(Boolean, default=True)
    controlled_substance_schedule = Column(String(10))
    ndc_numbers = Column(ARRAY(Text))
    
    # Clinical information
    indications = Column(ARRAY(Text))
    warnings = Column(ARRAY(Text))
    contraindications = Column(ARRAY(Text))
    side_effects = Column(ARRAY(Text))
    
    # FDA data
    manufacturer = Column(String(255))
    fda_approval_date = Column(Date)
    data_source = Column(String(50), default='FDA_ORANGE_BOOK')
    rxcui = Column(String(20))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user_medications = relationship("UserMedication", back_populates="medication")

class UserMedication(Base):
    """User's personal medication list"""
    __tablename__ = "user_medications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    medication_id = Column(UUID(as_uuid=True), ForeignKey("medications.id"), nullable=False)
    
    # Personal medication details
    prescribed_by = Column(String(255))
    prescribed_date = Column(Date)
    dosage_prescribed = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)
    
    # User notes and tracking
    user_notes = Column(Text)
    adherence_notes = Column(Text)
    side_effects_experienced = Column(ARRAY(Text))
    
    # Status
    is_currently_taking = Column(Boolean, default=True)
    discontinued_reason = Column(Text)
    discontinued_date = Column(Date)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_medications")
    medication = relationship("Medication", back_populates="user_medications")

class ChatSession(Base):
    """Chat session management"""
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Session info
    session_name = Column(String(255))
    device_info = Column(JSONB)
    ip_address = Column(INET)
    
    # Session state
    is_active = Column(Boolean, default=True)
    total_messages = Column(Integer, default=0)
    high_risk_queries = Column(Integer, default=0)
    professional_referrals_made = Column(Integer, default=0)
    
    # Privacy
    anonymized = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime)
    ended_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    conversations = relationship("Conversation", back_populates="chat_session")

class Conversation(Base):
    """Individual conversation threads"""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Conversation metadata
    title = Column(String(255))
    topic = Column(String(100))
    
    # Safety tracking
    overall_risk_level = Column(String(20), default='low')
    safety_flags = Column(ARRAY(Text))
    professional_referral_suggested = Column(Boolean, default=False)
    disclaimer_acknowledged = Column(Boolean, default=False)
    
    # Status
    status = Column(String(20), default='active')
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    chat_session = relationship("ChatSession", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    """Individual chat messages"""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    
    # Message content
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # Message metadata
    mentioned_medications = Column(ARRAY(Text))
    risk_level = Column(String(20))
    confidence_score = Column(DECIMAL(3,2))
    requires_followup = Column(Boolean, default=False)
    
    # AI metadata
    ai_model = Column(String(50))
    processing_time_ms = Column(Integer)
    token_count = Column(Integer)
    
    # Safety and compliance
    safety_review_required = Column(Boolean, default=False)
    flagged_content = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    sequence_number = Column(Integer, nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class DrugInteraction(Base):
    """Enhanced drug interaction database"""
    __tablename__ = "drug_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Interacting medications
    medication_1_id = Column(UUID(as_uuid=True), ForeignKey("medications.id"))
    medication_2_id = Column(UUID(as_uuid=True), ForeignKey("medications.id"))
    medication_1_name = Column(String(255), nullable=False)
    medication_2_name = Column(String(255), nullable=False)
    
    # Interaction details
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    clinical_significance = Column(Text)
    
    # Evidence and sources
    evidence_level = Column(String(20))
    data_source = Column(String(100), nullable=False)
    source_url = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('medication_1_name < medication_2_name', name='medication_order_check'),
    )

class AIQuery(Base):
    """Track AI processing for analytics"""
    __tablename__ = "ai_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Query analysis
    original_question = Column(Text, nullable=False)
    processed_question = Column(Text)
    query_type = Column(String(50))
    intent_confidence = Column(DECIMAL(3,2))
    
    # Extracted entities
    mentioned_medications = Column(ARRAY(Text))
    mentioned_conditions = Column(ARRAY(Text))
    mentioned_symptoms = Column(ARRAY(Text))
    
    # AI processing
    ai_model_used = Column(String(50))
    response_generated = Column(Boolean, default=False)
    processing_time_ms = Column(Integer)
    token_usage = Column(JSONB)
    
    # Safety assessment
    safety_risk_level = Column(String(20))
    safety_concerns = Column(ARRAY(Text))
    requires_professional_referral = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())

class AuditLog(Base):
    """Audit log for compliance tracking"""
    __tablename__ = "audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Who and what
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(UUID(as_uuid=True))
    
    # Details
    description = Column(Text)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    
    # Context
    ip_address = Column(INET)
    user_agent = Column(Text)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"))
    
    # Timestamp
    created_at = Column(DateTime, default=func.now())