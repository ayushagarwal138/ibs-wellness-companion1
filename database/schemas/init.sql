-- IBS Wellness Companion Database Schema
-- PostgreSQL with TimescaleDB extension for time-series data

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
CREATE TYPE user_role AS ENUM ('patient', 'doctor', 'admin');
CREATE TYPE symptom_severity AS ENUM ('none', 'mild', 'moderate', 'severe');
CREATE TYPE flare_status AS ENUM ('none', 'mild', 'moderate', 'severe');
CREATE TYPE notification_type AS ENUM ('medication', 'symptom_log', 'appointment', 'diet', 'general');
CREATE TYPE notification_status AS ENUM ('pending', 'sent', 'delivered', 'failed');

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(20),
    role user_role DEFAULT 'patient',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    avatar_url TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    
    -- OAuth fields
    google_id VARCHAR(255),
    github_id VARCHAR(255),
    
    -- Profile fields
    height_cm INTEGER,
    weight_kg DECIMAL(5,2),
    diagnosis_date DATE,
    ibs_subtype VARCHAR(50), -- IBS-D, IBS-C, IBS-M, IBS-U
    
    -- Preferences
    notification_preferences JSONB DEFAULT '{}',
    privacy_settings JSONB DEFAULT '{}',
    
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Create indexes for users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Symptoms table (time-series data)
CREATE TABLE symptoms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Core IBS symptoms
    abdominal_pain symptom_severity DEFAULT 'none',
    bloating symptom_severity DEFAULT 'none',
    gas symptom_severity DEFAULT 'none',
    diarrhea symptom_severity DEFAULT 'none',
    constipation symptom_severity DEFAULT 'none',
    urgency symptom_severity DEFAULT 'none',
    incomplete_evacuation symptom_severity DEFAULT 'none',
    
    -- Additional symptoms
    nausea symptom_severity DEFAULT 'none',
    fatigue symptom_severity DEFAULT 'none',
    headache symptom_severity DEFAULT 'none',
    anxiety symptom_severity DEFAULT 'none',
    
    -- Overall assessment
    overall_severity symptom_severity DEFAULT 'none',
    flare_status flare_status DEFAULT 'none',
    
    -- Additional data
    notes TEXT,
    mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
    sleep_quality INTEGER CHECK (sleep_quality >= 1 AND sleep_quality <= 10),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert symptoms to hypertable for time-series optimization
SELECT create_hypertable('symptoms', 'recorded_at');

-- Create indexes for symptoms
CREATE INDEX idx_symptoms_user_id ON symptoms(user_id);
CREATE INDEX idx_symptoms_recorded_at ON symptoms(recorded_at DESC);
CREATE INDEX idx_symptoms_user_recorded ON symptoms(user_id, recorded_at DESC);
CREATE INDEX idx_symptoms_flare_status ON symptoms(flare_status);

-- Medications table
CREATE TABLE medications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100),
    frequency VARCHAR(100), -- e.g., "twice daily", "as needed"
    medication_type VARCHAR(100), -- e.g., "antispasmodic", "probiotic", "fiber supplement"
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT true,
    prescribing_doctor VARCHAR(255),
    notes TEXT,
    side_effects TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Medication logs (time-series data)
CREATE TABLE medication_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    medication_id UUID NOT NULL REFERENCES medications(id) ON DELETE CASCADE,
    taken_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    dosage_taken VARCHAR(100),
    effectiveness_rating INTEGER CHECK (effectiveness_rating >= 1 AND effectiveness_rating <= 5),
    side_effects TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert medication_logs to hypertable
SELECT create_hypertable('medication_logs', 'taken_at');

-- Diet logs table (time-series data)
CREATE TABLE diet_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    logged_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meal_type VARCHAR(50), -- breakfast, lunch, dinner, snack
    food_items JSONB NOT NULL, -- Array of food items with quantities
    calories INTEGER,
    fiber_grams DECIMAL(5,2),
    fat_grams DECIMAL(5,2),
    protein_grams DECIMAL(5,2),
    carbs_grams DECIMAL(5,2),
    
    -- FODMAP tracking
    fodmap_level VARCHAR(20), -- low, moderate, high
    trigger_foods TEXT[], -- Array of potential trigger foods
    
    -- User assessment
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
    digestive_comfort INTEGER CHECK (digestive_comfort >= 1 AND digestive_comfort <= 5),
    notes TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert diet_logs to hypertable
SELECT create_hypertable('diet_logs', 'logged_at');

-- Food items reference table
CREATE TABLE food_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100),
    fodmap_level VARCHAR(20),
    calories_per_100g INTEGER,
    fiber_per_100g DECIMAL(5,2),
    fat_per_100g DECIMAL(5,2),
    protein_per_100g DECIMAL(5,2),
    carbs_per_100g DECIMAL(5,2),
    common_triggers BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ML Predictions table
CREATE TABLE ml_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    prediction_type VARCHAR(100) NOT NULL, -- flare_risk, symptom_forecast, diet_recommendation
    model_version VARCHAR(50),
    input_data JSONB NOT NULL,
    prediction_data JSONB NOT NULL,
    confidence_score DECIMAL(5,4),
    predicted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_until TIMESTAMPTZ,
    feedback_rating INTEGER CHECK (feedback_rating >= 1 AND feedback_rating <= 5),
    feedback_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert ml_predictions to hypertable
SELECT create_hypertable('ml_predictions', 'predicted_at');

-- Notifications table
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    status notification_status DEFAULT 'pending',
    scheduled_for TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    
    -- Notification channels
    email_enabled BOOLEAN DEFAULT true,
    push_enabled BOOLEAN DEFAULT true,
    
    -- Additional data
    action_url TEXT,
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat sessions table (for AI chatbot)
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}', -- For storing context, sources, etc.
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User sessions table (for authentication)
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT true
);

-- Audit log table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert audit_logs to hypertable
SELECT create_hypertable('audit_logs', 'created_at');

-- Create additional indexes
CREATE INDEX idx_medications_user_id ON medications(user_id);
CREATE INDEX idx_medications_active ON medications(user_id, is_active);
CREATE INDEX idx_medication_logs_user_id ON medication_logs(user_id);
CREATE INDEX idx_medication_logs_taken_at ON medication_logs(taken_at DESC);

CREATE INDEX idx_diet_logs_user_id ON diet_logs(user_id);
CREATE INDEX idx_diet_logs_logged_at ON diet_logs(logged_at DESC);
CREATE INDEX idx_diet_logs_meal_type ON diet_logs(meal_type);

CREATE INDEX idx_food_items_name ON food_items(name);
CREATE INDEX idx_food_items_category ON food_items(category);
CREATE INDEX idx_food_items_fodmap ON food_items(fodmap_level);

CREATE INDEX idx_ml_predictions_user_id ON ml_predictions(user_id);
CREATE INDEX idx_ml_predictions_type ON ml_predictions(prediction_type);
CREATE INDEX idx_ml_predictions_predicted_at ON ml_predictions(predicted_at DESC);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_scheduled ON notifications(scheduled_for);

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_active ON chat_sessions(user_id, is_active);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_sent_at ON chat_messages(sent_at DESC);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_active ON user_sessions(is_active, expires_at);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_symptoms_updated_at BEFORE UPDATE ON symptoms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medications_updated_at BEFORE UPDATE ON medications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notifications_updated_at BEFORE UPDATE ON notifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create retention policies for time-series data (optional)
-- Keep symptom data for 2 years
SELECT add_retention_policy('symptoms', INTERVAL '2 years');

-- Keep medication logs for 2 years
SELECT add_retention_policy('medication_logs', INTERVAL '2 years');

-- Keep diet logs for 1 year
SELECT add_retention_policy('diet_logs', INTERVAL '1 year');

-- Keep ML predictions for 6 months
SELECT add_retention_policy('ml_predictions', INTERVAL '6 months');

-- Keep audit logs for 1 year
SELECT add_retention_policy('audit_logs', INTERVAL '1 year');