-- Migration: Add optimization tables and indexes for data storage optimization
-- Version: 004
-- Description: Creates tables for daily/weekly summaries and optimization tracking

BEGIN;

-- Create daily nutrition summary table for faster analytics
CREATE TABLE IF NOT EXISTS daily_nutrition_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_calories INTEGER DEFAULT 0,
    total_protein_g DECIMAL(8,2) DEFAULT 0,
    total_carbs_g DECIMAL(8,2) DEFAULT 0,
    total_fat_g DECIMAL(8,2) DEFAULT 0,
    total_fiber_g DECIMAL(8,2) DEFAULT 0,
    total_sugar_g DECIMAL(8,2) DEFAULT 0,
    total_sodium_mg DECIMAL(8,2) DEFAULT 0,
    meals_count INTEGER DEFAULT 0,
    nutrition_quality_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Create weekly symptom summary table for trend analysis
CREATE TABLE IF NOT EXISTS weekly_symptom_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    avg_severity DECIMAL(3,2),
    max_severity DECIMAL(3,2),
    most_common_type VARCHAR(50),
    symptom_days INTEGER DEFAULT 0,
    total_symptoms INTEGER DEFAULT 0,
    trigger_foods JSONB,
    pattern_insights JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, week_start)
);

-- Create optimization metrics tracking table
CREATE TABLE IF NOT EXISTS optimization_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_type VARCHAR(100) NOT NULL,
    records_processed INTEGER DEFAULT 0,
    storage_saved_mb DECIMAL(10,2) DEFAULT 0,
    execution_time_seconds DECIMAL(10,3) DEFAULT 0,
    compression_ratio DECIMAL(5,3),
    index_efficiency_gain DECIMAL(5,2),
    operation_details JSONB,
    performed_by UUID REFERENCES users(id),
    performed_at TIMESTAMP DEFAULT NOW()
);

-- Create archive table for old diet logs
CREATE TABLE IF NOT EXISTS diet_logs_archive (
    LIKE diet_logs INCLUDING ALL
);

-- Create archive table for old symptoms
CREATE TABLE IF NOT EXISTS symptoms_archive (
    LIKE symptoms INCLUDING ALL
);

-- Add indexes for daily nutrition summary
CREATE INDEX IF NOT EXISTS idx_daily_nutrition_user_date 
ON daily_nutrition_summary(user_id, date DESC);

CREATE INDEX IF NOT EXISTS idx_daily_nutrition_date_calories 
ON daily_nutrition_summary(date, total_calories);

CREATE INDEX IF NOT EXISTS idx_daily_nutrition_quality_score 
ON daily_nutrition_summary(nutrition_quality_score DESC) 
WHERE nutrition_quality_score IS NOT NULL;

-- Add indexes for weekly symptom summary
CREATE INDEX IF NOT EXISTS idx_weekly_symptom_user_week 
ON weekly_symptom_summary(user_id, week_start DESC);

CREATE INDEX IF NOT EXISTS idx_weekly_symptom_severity 
ON weekly_symptom_summary(avg_severity DESC) 
WHERE avg_severity IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_weekly_symptom_type 
ON weekly_symptom_summary(most_common_type) 
WHERE most_common_type IS NOT NULL;

-- Add indexes for optimization metrics
CREATE INDEX IF NOT EXISTS idx_optimization_metrics_type_date 
ON optimization_metrics(operation_type, performed_at DESC);

CREATE INDEX IF NOT EXISTS idx_optimization_metrics_user 
ON optimization_metrics(performed_by, performed_at DESC);

-- Add indexes for archive tables
CREATE INDEX IF NOT EXISTS idx_diet_logs_archive_user_date 
ON diet_logs_archive(user_id, consumed_at DESC);

CREATE INDEX IF NOT EXISTS idx_symptoms_archive_user_date 
ON symptoms_archive(user_id, recorded_at DESC);

-- Optimize existing indexes for better performance
-- Add composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_diet_logs_user_meal_date 
ON diet_logs(user_id, meal_type, consumed_at DESC);

CREATE INDEX IF NOT EXISTS idx_symptoms_user_type_severity 
ON symptoms(user_id, symptom_type, severity, recorded_at DESC);

CREATE INDEX IF NOT EXISTS idx_ml_predictions_user_type_confidence 
ON ml_predictions(user_id, prediction_type, confidence DESC, predicted_at DESC);

-- Add partial indexes for active data
CREATE INDEX IF NOT EXISTS idx_diet_logs_recent 
ON diet_logs(user_id, consumed_at DESC) 
WHERE consumed_at >= NOW() - INTERVAL '90 days';

CREATE INDEX IF NOT EXISTS idx_symptoms_recent 
ON symptoms(user_id, recorded_at DESC) 
WHERE recorded_at >= NOW() - INTERVAL '90 days';

-- Create function to automatically populate daily nutrition summary
CREATE OR REPLACE FUNCTION populate_daily_nutrition_summary()
RETURNS TRIGGER AS $$
DECLARE
    summary_date DATE;
    user_uuid UUID;
BEGIN
    -- Get the date and user from the inserted/updated/deleted record
    IF TG_OP = 'DELETE' THEN
        summary_date := OLD.consumed_at::DATE;
        user_uuid := OLD.user_id;
    ELSE
        summary_date := NEW.consumed_at::DATE;
        user_uuid := NEW.user_id;
    END IF;

    -- Update or insert daily summary
    INSERT INTO daily_nutrition_summary (
        user_id, 
        date, 
        total_calories, 
        total_protein_g, 
        total_carbs_g, 
        total_fat_g, 
        total_fiber_g,
        total_sugar_g,
        total_sodium_mg,
        meals_count,
        updated_at
    )
    SELECT 
        user_uuid,
        summary_date,
        COALESCE(SUM(calories), 0),
        COALESCE(SUM(protein_g), 0),
        COALESCE(SUM(carbs_g), 0),
        COALESCE(SUM(fat_g), 0),
        COALESCE(SUM(fiber_g), 0),
        COALESCE(SUM(sugar_g), 0),
        COALESCE(SUM(sodium_mg), 0),
        COUNT(DISTINCT meal_type),
        NOW()
    FROM diet_logs 
    WHERE user_id = user_uuid 
    AND consumed_at::DATE = summary_date
    ON CONFLICT (user_id, date) 
    DO UPDATE SET
        total_calories = EXCLUDED.total_calories,
        total_protein_g = EXCLUDED.total_protein_g,
        total_carbs_g = EXCLUDED.total_carbs_g,
        total_fat_g = EXCLUDED.total_fat_g,
        total_fiber_g = EXCLUDED.total_fiber_g,
        total_sugar_g = EXCLUDED.total_sugar_g,
        total_sodium_mg = EXCLUDED.total_sodium_mg,
        meals_count = EXCLUDED.meals_count,
        updated_at = NOW();

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Create trigger for daily nutrition summary
DROP TRIGGER IF EXISTS trigger_daily_nutrition_summary ON diet_logs;
CREATE TRIGGER trigger_daily_nutrition_summary
    AFTER INSERT OR UPDATE OR DELETE ON diet_logs
    FOR EACH ROW
    EXECUTE FUNCTION populate_daily_nutrition_summary();

-- Create function to populate weekly symptom summary
CREATE OR REPLACE FUNCTION populate_weekly_symptom_summary()
RETURNS TRIGGER AS $$
DECLARE
    week_start_date DATE;
    week_end_date DATE;
    user_uuid UUID;
BEGIN
    -- Get the week start date and user from the inserted/updated/deleted record
    IF TG_OP = 'DELETE' THEN
        week_start_date := DATE_TRUNC('week', OLD.recorded_at)::DATE;
        week_end_date := week_start_date + INTERVAL '6 days';
        user_uuid := OLD.user_id;
    ELSE
        week_start_date := DATE_TRUNC('week', NEW.recorded_at)::DATE;
        week_end_date := week_start_date + INTERVAL '6 days';
        user_uuid := NEW.user_id;
    END IF;

    -- Update or insert weekly summary
    INSERT INTO weekly_symptom_summary (
        user_id,
        week_start,
        week_end,
        avg_severity,
        max_severity,
        most_common_type,
        symptom_days,
        total_symptoms,
        updated_at
    )
    SELECT 
        user_uuid,
        week_start_date,
        week_end_date,
        AVG(severity::NUMERIC),
        MAX(severity::NUMERIC),
        MODE() WITHIN GROUP (ORDER BY symptom_type),
        COUNT(DISTINCT recorded_at::DATE),
        COUNT(*),
        NOW()
    FROM symptoms 
    WHERE user_id = user_uuid 
    AND recorded_at >= week_start_date 
    AND recorded_at < week_end_date + INTERVAL '1 day'
    ON CONFLICT (user_id, week_start) 
    DO UPDATE SET
        avg_severity = EXCLUDED.avg_severity,
        max_severity = EXCLUDED.max_severity,
        most_common_type = EXCLUDED.most_common_type,
        symptom_days = EXCLUDED.symptom_days,
        total_symptoms = EXCLUDED.total_symptoms,
        updated_at = NOW();

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Create trigger for weekly symptom summary
DROP TRIGGER IF EXISTS trigger_weekly_symptom_summary ON symptoms;
CREATE TRIGGER trigger_weekly_symptom_summary
    AFTER INSERT OR UPDATE OR DELETE ON symptoms
    FOR EACH ROW
    EXECUTE FUNCTION populate_weekly_symptom_summary();

-- Create function for database maintenance
CREATE OR REPLACE FUNCTION run_optimization_maintenance()
RETURNS TABLE(
    operation VARCHAR(100),
    records_affected INTEGER,
    execution_time_ms INTEGER
) AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    affected_rows INTEGER;
BEGIN
    -- Vacuum and analyze critical tables
    start_time := clock_timestamp();
    EXECUTE 'VACUUM ANALYZE diet_logs';
    end_time := clock_timestamp();
    
    operation := 'VACUUM ANALYZE diet_logs';
    records_affected := 0;
    execution_time_ms := EXTRACT(MILLISECONDS FROM (end_time - start_time))::INTEGER;
    RETURN NEXT;

    -- Vacuum and analyze symptoms table
    start_time := clock_timestamp();
    EXECUTE 'VACUUM ANALYZE symptoms';
    end_time := clock_timestamp();
    
    operation := 'VACUUM ANALYZE symptoms';
    records_affected := 0;
    execution_time_ms := EXTRACT(MILLISECONDS FROM (end_time - start_time))::INTEGER;
    RETURN NEXT;

    -- Update table statistics
    start_time := clock_timestamp();
    EXECUTE 'ANALYZE daily_nutrition_summary, weekly_symptom_summary, optimization_metrics';
    end_time := clock_timestamp();
    
    operation := 'ANALYZE summary tables';
    records_affected := 0;
    execution_time_ms := EXTRACT(MILLISECONDS FROM (end_time - start_time))::INTEGER;
    RETURN NEXT;

    RETURN;
END;
$$ LANGUAGE plpgsql;

-- Insert audit log entry
INSERT INTO audit_logs (
    table_name,
    operation,
    old_values,
    new_values,
    user_id,
    timestamp
) VALUES (
    'database_schema',
    'CREATE',
    '{}',
    '{"migration": "004_add_optimization_tables", "description": "Added optimization tables and indexes"}',
    NULL,
    NOW()
);

COMMIT;

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 004_add_optimization_tables completed successfully';
    RAISE NOTICE 'Created tables: daily_nutrition_summary, weekly_symptom_summary, optimization_metrics';
    RAISE NOTICE 'Created archive tables: diet_logs_archive, symptoms_archive';
    RAISE NOTICE 'Added optimization indexes and triggers';
END $$;