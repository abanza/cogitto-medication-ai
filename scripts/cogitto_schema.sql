## scripts/cogitto_schema.sql
-- Cogitto PostgreSQL Database Schema
-- Production-ready database design for medication AI assistant

-- Create database (run this separately)
-- CREATE DATABASE cogitto_production;

-- Users table - core user management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    date_of_birth DATE,
    phone_number VARCHAR(20),
    
    -- Medical profile
    age_range VARCHAR(20), -- "18-30", "31-50", etc. for privacy
    allergies TEXT[], -- Array of known allergies
    medical_conditions TEXT[], -- Array of medical conditions
    
    -- Account status
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    verification_token VARCHAR(255),
    
    -- Privacy and compliance
    privacy_consent BOOLEAN DEFAULT false,
    hipaa_acknowledgment BOOLEAN DEFAULT false,
    terms_accepted_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    
    -- Soft delete support
    deleted_at TIMESTAMP NULL
);

-- Medications table - enhanced FDA medication data
CREATE TABLE medications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Core medication info
    generic_name VARCHAR(255) NOT NULL,
    brand_names TEXT[], -- Array of brand names
    dosage_form VARCHAR(100),
    strength VARCHAR(100),
    route_of_administration TEXT[],
    
    -- Regulatory info
    prescription_required BOOLEAN DEFAULT true,
    controlled_substance_schedule VARCHAR(10), -- I, II, III, IV, V
    ndc_numbers TEXT[], -- National Drug Code numbers
    
    -- Clinical information
    indications TEXT[], -- What it treats
    warnings TEXT[], -- Safety warnings
    contraindications TEXT[], -- When not to use
    side_effects TEXT[], -- Common side effects
    
    -- FDA data
    manufacturer VARCHAR(255),
    fda_approval_date DATE,
    data_source VARCHAR(50) DEFAULT 'FDA_ORANGE_BOOK',
    rxcui VARCHAR(20), -- RxNorm concept identifier
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexing for search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', generic_name || ' ' || COALESCE(array_to_string(brand_names, ' '), ''))
    ) STORED
);

-- User medications - personal medication lists
CREATE TABLE user_medications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    medication_id UUID NOT NULL REFERENCES medications(id),
    
    -- Personal medication details
    prescribed_by VARCHAR(255), -- Doctor name
    prescribed_date DATE,
    dosage_prescribed VARCHAR(255), -- "Take 1 tablet twice daily"
    start_date DATE,
    end_date DATE, -- NULL for ongoing
    
    -- User notes and tracking
    user_notes TEXT,
    adherence_notes TEXT,
    side_effects_experienced TEXT[],
    
    -- Status
    is_currently_taking BOOLEAN DEFAULT true,
    discontinued_reason TEXT,
    discontinued_date DATE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, medication_id) -- Prevent duplicates
);

-- Chat sessions - conversation management
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Session info
    session_name VARCHAR(255), -- User-friendly name
    device_info JSONB, -- Browser, mobile app, etc.
    ip_address INET,
    
    -- Session state
    is_active BOOLEAN DEFAULT true,
    total_messages INTEGER DEFAULT 0,
    high_risk_queries INTEGER DEFAULT 0,
    professional_referrals_made INTEGER DEFAULT 0,
    
    -- Privacy
    anonymized BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- For session cleanup
    ended_at TIMESTAMP
);

-- Conversations - individual conversation threads
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Conversation metadata
    title VARCHAR(255), -- Auto-generated or user-set
    topic VARCHAR(100), -- drug_interaction, side_effects, etc.
    
    -- Safety tracking
    overall_risk_level VARCHAR(20) DEFAULT 'low', -- low, medium, high, critical
    safety_flags TEXT[], -- Array of safety concerns
    professional_referral_suggested BOOLEAN DEFAULT false,
    disclaimer_acknowledged BOOLEAN DEFAULT false,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- active, completed, requires_professional
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages - individual chat messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    
    -- Message content
    role VARCHAR(20) NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    
    -- Message metadata
    mentioned_medications TEXT[], -- Extracted medication names
    risk_level VARCHAR(20), -- low, medium, high, critical
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    requires_followup BOOLEAN DEFAULT false,
    
    -- AI metadata (for assistant messages)
    ai_model VARCHAR(50), -- gpt-4, cogitto-fallback, etc.
    processing_time_ms INTEGER,
    token_count INTEGER,
    
    -- Safety and compliance
    safety_review_required BOOLEAN DEFAULT false,
    flagged_content BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Message ordering
    sequence_number INTEGER NOT NULL,
    
    UNIQUE(conversation_id, sequence_number)
);

-- Drug interactions - enhanced interaction database
CREATE TABLE drug_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Interacting medications
    medication_1_id UUID REFERENCES medications(id),
    medication_2_id UUID REFERENCES medications(id),
    medication_1_name VARCHAR(255) NOT NULL, -- For non-registered medications
    medication_2_name VARCHAR(255) NOT NULL,
    
    -- Interaction details
    severity VARCHAR(20) NOT NULL, -- minor, moderate, major, contraindicated
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    clinical_significance TEXT,
    
    -- Evidence and sources
    evidence_level VARCHAR(20), -- established, probable, theoretical
    data_source VARCHAR(100) NOT NULL, -- FDA_RXNORM, DRUGBANK, COGITTO_CURATED
    source_url TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate interactions
    UNIQUE(medication_1_name, medication_2_name),
    -- Also prevent reverse duplicates
    CHECK (medication_1_name < medication_2_name) -- Alphabetical ordering
);

-- AI queries - track AI processing for analytics
CREATE TABLE ai_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Query analysis
    original_question TEXT NOT NULL,
    processed_question TEXT,
    query_type VARCHAR(50), -- drug_information, interaction_check, etc.
    intent_confidence DECIMAL(3,2),
    
    -- Extracted entities
    mentioned_medications TEXT[],
    mentioned_conditions TEXT[],
    mentioned_symptoms TEXT[],
    
    -- AI processing
    ai_model_used VARCHAR(50),
    response_generated BOOLEAN DEFAULT false,
    processing_time_ms INTEGER,
    token_usage JSONB, -- {input: 100, output: 200, total: 300}
    
    -- Safety assessment
    safety_risk_level VARCHAR(20),
    safety_concerns TEXT[],
    requires_professional_referral BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log - track important actions for compliance
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Who and what
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL, -- login, medication_added, high_risk_query, etc.
    entity_type VARCHAR(50), -- user, medication, conversation, etc.
    entity_id UUID,
    
    -- Details
    description TEXT,
    old_values JSONB,
    new_values JSONB,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    session_id UUID REFERENCES chat_sessions(id) ON DELETE SET NULL,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_medications_search ON medications USING GIN(search_vector);
CREATE INDEX idx_medications_generic_name ON medications(generic_name);
CREATE INDEX idx_user_medications_user_active ON user_medications(user_id) WHERE is_currently_taking = true;
CREATE INDEX idx_chat_sessions_user_active ON chat_sessions(user_id) WHERE is_active = true;
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_messages_conversation_sequence ON messages(conversation_id, sequence_number);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_drug_interactions_severity ON drug_interactions(severity);
CREATE INDEX idx_ai_queries_user_type ON ai_queries(user_id, query_type);
CREATE INDEX idx_audit_log_user_action ON audit_log(user_id, action);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);

-- Functions for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medications_updated_at BEFORE UPDATE ON medications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_medications_updated_at BEFORE UPDATE ON user_medications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_drug_interactions_updated_at BEFORE UPDATE ON drug_interactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample data permissions and roles (for production)
-- Create application user with limited permissions
CREATE ROLE cogitto_app_user WITH LOGIN PASSWORD 'C33eda8bdb';
GRANT CONNECT ON DATABASE cogitto_production TO cogitto_app_user;
GRANT USAGE ON SCHEMA public TO cogitto_app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO cogitto_app_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO cogitto_app_user;

-- Create read-only user for analytics
CREATE ROLE cogitto_analytics_user WITH LOGIN PASSWORD 'C33eda8bdb';
GRANT CONNECT ON DATABASE cogitto_production TO cogitto_analytics_user;
GRANT USAGE ON SCHEMA public TO cogitto_analytics_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO cogitto_analytics_user;