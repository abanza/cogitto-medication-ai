#
-- User Medications Table
CREATE TABLE IF NOT EXISTS user_medications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    medication_name VARCHAR(255) NOT NULL,
    brand_name VARCHAR(255),
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    start_date DATE,
    end_date DATE,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure user can't have duplicate active medications
    UNIQUE(user_id, medication_name) WHERE is_active = TRUE
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_user_medications_user_id ON user_medications(user_id);
CREATE INDEX IF NOT EXISTS idx_user_medications_active ON user_medications(user_id, is_active);

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_user_medications_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_medications_updated_at
    BEFORE UPDATE ON user_medications
    FOR EACH ROW
    EXECUTE FUNCTION update_user_medications_updated_at();
