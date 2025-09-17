-- Migration: 001_add_ml_prediction_indexes.sql
-- Description: Add performance indexes for ML predictions and user queries
-- Created: 2024-01-15
-- Author: IBS Wellness Companion

-- Add indexes for better query performance on ML predictions table
CREATE INDEX IF NOT EXISTS idx_ml_predictions_user_type_date 
ON ml_predictions (user_id, prediction_type, predicted_at DESC);

CREATE INDEX IF NOT EXISTS idx_ml_predictions_confidence 
ON ml_predictions (confidence_score DESC) 
WHERE confidence_score > 0.7;

CREATE INDEX IF NOT EXISTS idx_ml_predictions_model_version 
ON ml_predictions (model_version, predicted_at DESC);

-- Add indexes for symptoms table queries
CREATE INDEX IF NOT EXISTS idx_symptoms_user_severity_date 
ON symptoms (user_id, overall_severity, recorded_at DESC);

CREATE INDEX IF NOT EXISTS idx_symptoms_flare_date 
ON symptoms (flare_status, recorded_at DESC) 
WHERE flare_status IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_symptoms_stress_mood 
ON symptoms (stress_level, mood_score, recorded_at DESC) 
WHERE stress_level IS NOT NULL AND mood_score IS NOT NULL;

-- Add indexes for diet_logs table queries
CREATE INDEX IF NOT EXISTS idx_diet_logs_user_fodmap_date 
ON diet_logs (user_id, fodmap_level, logged_at DESC);

CREATE INDEX IF NOT EXISTS idx_diet_logs_trigger_foods 
ON diet_logs (user_id, logged_at DESC) 
WHERE trigger_foods = true;

CREATE INDEX IF NOT EXISTS idx_diet_logs_digestive_comfort 
ON diet_logs (digestive_comfort_score, logged_at DESC) 
WHERE digestive_comfort_score IS NOT NULL;

-- Add indexes for medication_logs table queries
CREATE INDEX IF NOT EXISTS idx_medication_logs_user_date 
ON medication_logs (user_id, taken_at DESC);

CREATE INDEX IF NOT EXISTS idx_medication_logs_effectiveness 
ON medication_logs (effectiveness_rating, taken_at DESC) 
WHERE effectiveness_rating IS NOT NULL;

-- Add composite index for user profile queries
CREATE INDEX IF NOT EXISTS idx_users_profile_data 
ON users (ibs_subtype, gender, date_of_birth) 
WHERE ibs_subtype IS NOT NULL;

-- Add index for chat sessions and messages
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_date 
ON chat_sessions (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_date 
ON chat_messages (session_id, created_at ASC);

-- Add partial index for active notifications
CREATE INDEX IF NOT EXISTS idx_notifications_active 
ON notifications (user_id, scheduled_for ASC) 
WHERE sent_at IS NULL AND scheduled_for > NOW();

-- Add index for audit logs by action type
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_date 
ON audit_logs (action_type, created_at DESC);

-- Add GIN index for JSONB columns (if using PostgreSQL with JSONB support)
CREATE INDEX IF NOT EXISTS idx_ml_predictions_input_data_gin 
ON ml_predictions USING GIN (input_data);

CREATE INDEX IF NOT EXISTS idx_ml_predictions_prediction_data_gin 
ON ml_predictions USING GIN (prediction_data);

-- Add index for user preferences JSONB
CREATE INDEX IF NOT EXISTS idx_users_preferences_gin 
ON users USING GIN (preferences);

-- Performance optimization: Add statistics targets for better query planning
ALTER TABLE symptoms ALTER COLUMN overall_severity SET STATISTICS 1000;
ALTER TABLE diet_logs ALTER COLUMN fodmap_level SET STATISTICS 1000;
ALTER TABLE ml_predictions ALTER COLUMN prediction_type SET STATISTICS 1000;

-- Add comments for documentation
COMMENT ON INDEX idx_ml_predictions_user_type_date IS 'Optimizes ML prediction queries by user and type';
COMMENT ON INDEX idx_symptoms_user_severity_date IS 'Optimizes symptom severity analysis queries';
COMMENT ON INDEX idx_diet_logs_user_fodmap_date IS 'Optimizes FODMAP adherence tracking queries';
COMMENT ON INDEX idx_notifications_active IS 'Optimizes active notification retrieval';

-- Migration completion log
INSERT INTO audit_logs (
    user_id, 
    action_type, 
    table_name, 
    details, 
    created_at
) VALUES (
    NULL,
    'MIGRATION',
    'SYSTEM',
    '{"migration": "001_add_ml_prediction_indexes", "description": "Added performance indexes for ML predictions and user queries"}',
    NOW()
);