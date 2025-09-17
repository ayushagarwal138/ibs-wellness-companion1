-- Migration: 002_add_user_analytics_views.sql
-- Description: Add analytical views for user insights and ML model training data
-- Created: 2024-01-15
-- Author: IBS Wellness Companion

-- Create view for user symptom trends
CREATE OR REPLACE VIEW user_symptom_trends AS
SELECT 
    s.user_id,
    u.ibs_subtype,
    DATE_TRUNC('week', s.recorded_at) as week_start,
    AVG(CASE 
        WHEN s.abdominal_pain = 'none' THEN 0
        WHEN s.abdominal_pain = 'mild' THEN 1
        WHEN s.abdominal_pain = 'moderate' THEN 2
        WHEN s.abdominal_pain = 'severe' THEN 3
        ELSE 0
    END) as avg_abdominal_pain,
    AVG(CASE 
        WHEN s.bloating = 'none' THEN 0
        WHEN s.bloating = 'mild' THEN 1
        WHEN s.bloating = 'moderate' THEN 2
        WHEN s.bloating = 'severe' THEN 3
        ELSE 0
    END) as avg_bloating,
    AVG(CASE 
        WHEN s.diarrhea = 'none' THEN 0
        WHEN s.diarrhea = 'mild' THEN 1
        WHEN s.diarrhea = 'moderate' THEN 2
        WHEN s.diarrhea = 'severe' THEN 3
        ELSE 0
    END) as avg_diarrhea,
    AVG(CASE 
        WHEN s.constipation = 'none' THEN 0
        WHEN s.constipation = 'mild' THEN 1
        WHEN s.constipation = 'moderate' THEN 2
        WHEN s.constipation = 'severe' THEN 3
        ELSE 0
    END) as avg_constipation,
    AVG(s.mood_score) as avg_mood_score,
    AVG(s.stress_level) as avg_stress_level,
    AVG(s.sleep_quality) as avg_sleep_quality,
    COUNT(*) as symptom_entries,
    COUNT(CASE WHEN s.flare_status = 'active' THEN 1 END) as flare_days
FROM symptoms s
JOIN users u ON s.user_id = u.id
WHERE s.recorded_at >= NOW() - INTERVAL '1 year'
GROUP BY s.user_id, u.ibs_subtype, DATE_TRUNC('week', s.recorded_at);

-- Create view for dietary patterns analysis
CREATE OR REPLACE VIEW user_dietary_patterns AS
SELECT 
    d.user_id,
    u.ibs_subtype,
    DATE_TRUNC('month', d.logged_at) as month_start,
    COUNT(*) as total_meals,
    COUNT(CASE WHEN d.fodmap_level = 'low' THEN 1 END) as low_fodmap_meals,
    COUNT(CASE WHEN d.fodmap_level = 'medium' THEN 1 END) as medium_fodmap_meals,
    COUNT(CASE WHEN d.fodmap_level = 'high' THEN 1 END) as high_fodmap_meals,
    COUNT(CASE WHEN d.trigger_foods = true THEN 1 END) as trigger_food_meals,
    AVG(d.fiber_grams) as avg_fiber_intake,
    AVG(d.calories) as avg_calories,
    AVG(d.digestive_comfort_score) as avg_digestive_comfort,
    ROUND(
        COUNT(CASE WHEN d.fodmap_level = 'low' THEN 1 END)::numeric / 
        NULLIF(COUNT(*), 0) * 100, 2
    ) as fodmap_adherence_percentage
FROM diet_logs d
JOIN users u ON d.user_id = u.id
WHERE d.logged_at >= NOW() - INTERVAL '1 year'
GROUP BY d.user_id, u.ibs_subtype, DATE_TRUNC('month', d.logged_at);

-- Create view for medication effectiveness analysis
CREATE OR REPLACE VIEW medication_effectiveness AS
SELECT 
    ml.user_id,
    m.name as medication_name,
    m.medication_type,
    DATE_TRUNC('month', ml.taken_at) as month_start,
    COUNT(*) as doses_taken,
    AVG(ml.effectiveness_rating) as avg_effectiveness,
    COUNT(CASE WHEN ml.side_effects_experienced = true THEN 1 END) as side_effect_occurrences,
    ROUND(
        COUNT(CASE WHEN ml.side_effects_experienced = true THEN 1 END)::numeric / 
        NULLIF(COUNT(*), 0) * 100, 2
    ) as side_effect_percentage
FROM medication_logs ml
JOIN medications m ON ml.medication_id = m.id
WHERE ml.taken_at >= NOW() - INTERVAL '1 year'
GROUP BY ml.user_id, m.name, m.medication_type, DATE_TRUNC('month', ml.taken_at);

-- Create view for ML model training data
CREATE OR REPLACE VIEW ml_training_features AS
SELECT 
    s.user_id,
    s.recorded_at,
    -- User profile features
    EXTRACT(YEAR FROM AGE(s.recorded_at, u.date_of_birth)) as age,
    u.gender,
    u.ibs_subtype,
    CASE 
        WHEN u.height_cm IS NOT NULL AND u.weight_kg IS NOT NULL 
        THEN u.weight_kg / POWER(u.height_cm / 100.0, 2)
        ELSE NULL 
    END as bmi,
    EXTRACT(YEAR FROM AGE(s.recorded_at, u.diagnosis_date)) as years_since_diagnosis,
    
    -- Symptom features (converted to numeric)
    CASE 
        WHEN s.abdominal_pain = 'none' THEN 0
        WHEN s.abdominal_pain = 'mild' THEN 1
        WHEN s.abdominal_pain = 'moderate' THEN 2
        WHEN s.abdominal_pain = 'severe' THEN 3
        ELSE 0
    END as abdominal_pain_score,
    CASE 
        WHEN s.bloating = 'none' THEN 0
        WHEN s.bloating = 'mild' THEN 1
        WHEN s.bloating = 'moderate' THEN 2
        WHEN s.bloating = 'severe' THEN 3
        ELSE 0
    END as bloating_score,
    CASE 
        WHEN s.diarrhea = 'none' THEN 0
        WHEN s.diarrhea = 'mild' THEN 1
        WHEN s.diarrhea = 'moderate' THEN 2
        WHEN s.diarrhea = 'severe' THEN 3
        ELSE 0
    END as diarrhea_score,
    CASE 
        WHEN s.constipation = 'none' THEN 0
        WHEN s.constipation = 'mild' THEN 1
        WHEN s.constipation = 'moderate' THEN 2
        WHEN s.constipation = 'severe' THEN 3
        ELSE 0
    END as constipation_score,
    
    -- Lifestyle features
    s.mood_score,
    s.stress_level,
    s.sleep_quality,
    
    -- Target variables
    s.overall_severity,
    CASE WHEN s.flare_status = 'active' THEN 1 ELSE 0 END as flare_active,
    
    -- Recent dietary context (last 7 days)
    (
        SELECT AVG(CASE WHEN d.fodmap_level = 'low' THEN 1 ELSE 0 END)
        FROM diet_logs d 
        WHERE d.user_id = s.user_id 
        AND d.logged_at BETWEEN s.recorded_at - INTERVAL '7 days' AND s.recorded_at
    ) as recent_fodmap_adherence,
    
    (
        SELECT AVG(d.fiber_grams)
        FROM diet_logs d 
        WHERE d.user_id = s.user_id 
        AND d.logged_at BETWEEN s.recorded_at - INTERVAL '7 days' AND s.recorded_at
    ) as recent_avg_fiber,
    
    (
        SELECT COUNT(*)::float / 7
        FROM diet_logs d 
        WHERE d.user_id = s.user_id 
        AND d.trigger_foods = true
        AND d.logged_at BETWEEN s.recorded_at - INTERVAL '7 days' AND s.recorded_at
    ) as recent_trigger_food_frequency

FROM symptoms s
JOIN users u ON s.user_id = u.id
WHERE s.recorded_at >= NOW() - INTERVAL '2 years';

-- Create view for user engagement metrics
CREATE OR REPLACE VIEW user_engagement_metrics AS
SELECT 
    u.id as user_id,
    u.created_at as registration_date,
    EXTRACT(DAYS FROM NOW() - u.created_at) as days_since_registration,
    
    -- Symptom logging engagement
    (SELECT COUNT(*) FROM symptoms WHERE user_id = u.id) as total_symptom_logs,
    (SELECT COUNT(*) FROM symptoms WHERE user_id = u.id AND recorded_at >= NOW() - INTERVAL '30 days') as symptom_logs_last_30d,
    (SELECT MAX(recorded_at) FROM symptoms WHERE user_id = u.id) as last_symptom_log,
    
    -- Diet logging engagement
    (SELECT COUNT(*) FROM diet_logs WHERE user_id = u.id) as total_diet_logs,
    (SELECT COUNT(*) FROM diet_logs WHERE user_id = u.id AND logged_at >= NOW() - INTERVAL '30 days') as diet_logs_last_30d,
    (SELECT MAX(logged_at) FROM diet_logs WHERE user_id = u.id) as last_diet_log,
    
    -- Medication tracking engagement
    (SELECT COUNT(*) FROM medication_logs WHERE user_id = u.id) as total_medication_logs,
    (SELECT COUNT(*) FROM medication_logs WHERE user_id = u.id AND taken_at >= NOW() - INTERVAL '30 days') as medication_logs_last_30d,
    
    -- Chat engagement
    (SELECT COUNT(*) FROM chat_sessions WHERE user_id = u.id) as total_chat_sessions,
    (SELECT COUNT(*) FROM chat_sessions WHERE user_id = u.id AND created_at >= NOW() - INTERVAL '30 days') as chat_sessions_last_30d,
    
    -- ML predictions usage
    (SELECT COUNT(*) FROM ml_predictions WHERE user_id = u.id) as total_ml_predictions,
    (SELECT COUNT(*) FROM ml_predictions WHERE user_id = u.id AND predicted_at >= NOW() - INTERVAL '30 days') as ml_predictions_last_30d

FROM users u;

-- Create materialized view for performance (refresh daily)
CREATE MATERIALIZED VIEW user_summary_stats AS
SELECT 
    u.id as user_id,
    u.ibs_subtype,
    u.gender,
    EXTRACT(YEAR FROM AGE(u.date_of_birth)) as age_years,
    
    -- Recent symptom averages (last 30 days)
    COALESCE(recent_symptoms.avg_severity, 0) as recent_avg_severity,
    COALESCE(recent_symptoms.flare_frequency, 0) as recent_flare_frequency,
    COALESCE(recent_symptoms.avg_stress, 5) as recent_avg_stress,
    
    -- Recent dietary patterns (last 30 days)
    COALESCE(recent_diet.fodmap_adherence, 0) as recent_fodmap_adherence,
    COALESCE(recent_diet.avg_fiber, 25) as recent_avg_fiber,
    
    -- Engagement metrics
    COALESCE(engagement.symptom_logs_last_30d, 0) as recent_symptom_logs,
    COALESCE(engagement.diet_logs_last_30d, 0) as recent_diet_logs,
    
    NOW() as last_updated

FROM users u
LEFT JOIN (
    SELECT 
        user_id,
        AVG(overall_severity) as avg_severity,
        COUNT(CASE WHEN flare_status = 'active' THEN 1 END)::float / COUNT(*) as flare_frequency,
        AVG(stress_level) as avg_stress
    FROM symptoms 
    WHERE recorded_at >= NOW() - INTERVAL '30 days'
    GROUP BY user_id
) recent_symptoms ON u.id = recent_symptoms.user_id
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(CASE WHEN fodmap_level = 'low' THEN 1 END)::float / COUNT(*) as fodmap_adherence,
        AVG(fiber_grams) as avg_fiber
    FROM diet_logs 
    WHERE logged_at >= NOW() - INTERVAL '30 days'
    GROUP BY user_id
) recent_diet ON u.id = recent_diet.user_id
LEFT JOIN user_engagement_metrics engagement ON u.id = engagement.user_id;

-- Create index on materialized view
CREATE INDEX idx_user_summary_stats_ibs_subtype ON user_summary_stats (ibs_subtype);
CREATE INDEX idx_user_summary_stats_engagement ON user_summary_stats (recent_symptom_logs DESC, recent_diet_logs DESC);

-- Add comments for documentation
COMMENT ON VIEW user_symptom_trends IS 'Weekly symptom trends for tracking user progress';
COMMENT ON VIEW user_dietary_patterns IS 'Monthly dietary pattern analysis for FODMAP adherence tracking';
COMMENT ON VIEW medication_effectiveness IS 'Medication effectiveness analysis by user and time period';
COMMENT ON VIEW ml_training_features IS 'Prepared features for ML model training and validation';
COMMENT ON VIEW user_engagement_metrics IS 'User engagement metrics across all app features';
COMMENT ON MATERIALIZED VIEW user_summary_stats IS 'Cached user summary statistics for dashboard performance';

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
    '{"migration": "002_add_user_analytics_views", "description": "Added analytical views for user insights and ML model training data"}',
    NOW()
);