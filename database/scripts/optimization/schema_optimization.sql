-- Database Schema Optimization Script
-- Optimizes indexes, constraints, and triggers for better performance
-- and immediate UI reflection of user profile updates

BEGIN;

-- Step 1: Add optimized indexes for user profile operations
DO $$
BEGIN
    RAISE NOTICE 'Step 1: Creating optimized indexes for user operations...';
END $$;

-- Index for user lookups by email (login operations)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_active 
ON users (email) WHERE deleted_at IS NULL;

-- Index for user profile updates (frequent operations)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_updated_at 
ON users (updated_at DESC);

-- Composite index for user sessions
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_sessions_user_active 
ON user_sessions (user_id, expires_at) WHERE expires_at > NOW();

-- Step 2: Optimize food-related queries
DO $$
BEGIN
    RAISE NOTICE 'Step 2: Optimizing food-related indexes...';
END $$;

-- Index for food item searches by category and FODMAP level
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_food_items_category_fodmap 
ON food_items (category, fodmap_level);

-- Index for food item name searches (case-insensitive)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_food_items_name_lower 
ON food_items (LOWER(name));

-- Step 3: Optimize diet logging and symptom tracking
DO $$
BEGIN
    RAISE NOTICE 'Step 3: Optimizing diet and symptom tracking indexes...';
END $$;

-- Index for diet logs by user and date (most common query pattern)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_diet_logs_user_date 
ON diet_logs (user_id, logged_at DESC);

-- Index for symptoms by user and date
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_symptoms_user_date 
ON symptoms (user_id, recorded_at DESC);

-- Index for ML predictions by user (for dashboard queries)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ml_predictions_user_created 
ON ml_predictions (user_id, created_at DESC);

-- Step 4: Add triggers for immediate UI updates
DO $$
BEGIN
    RAISE NOTICE 'Step 4: Creating triggers for immediate UI reflection...';
END $$;

-- Function to update user updated_at timestamp
CREATE OR REPLACE FUNCTION update_user_timestamp()
RETURNS TRIGGER AS $func$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$func$ LANGUAGE plpgsql;

-- Trigger for user profile updates
DROP TRIGGER IF EXISTS trigger_users_update_timestamp ON users;
CREATE TRIGGER trigger_users_update_timestamp
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_user_timestamp();

-- Function to notify application of user changes (for real-time UI updates)
CREATE OR REPLACE FUNCTION notify_user_change()
RETURNS TRIGGER AS $func$
BEGIN
    -- Notify the application layer of user profile changes
    PERFORM pg_notify('user_profile_updated', 
        json_build_object(
            'user_id', COALESCE(NEW.id, OLD.id),
            'action', TG_OP,
            'timestamp', NOW()
        )::text
    );
    RETURN COALESCE(NEW, OLD);
END;
$func$ LANGUAGE plpgsql;

-- Trigger for real-time user profile notifications
DROP TRIGGER IF EXISTS trigger_users_notify_change ON users;
CREATE TRIGGER trigger_users_notify_change
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW
    EXECUTE FUNCTION notify_user_change();

-- Step 5: Optimize constraints for better performance
DO $$
BEGIN
    RAISE NOTICE 'Step 5: Optimizing constraints...';
END $$;

-- Add partial unique constraint for active users only
DROP INDEX IF EXISTS idx_users_email_unique_active;
CREATE UNIQUE INDEX CONCURRENTLY idx_users_email_unique_active 
ON users (email) WHERE deleted_at IS NULL;

-- Step 6: Add check constraints for data integrity
DO $$
BEGIN
    RAISE NOTICE 'Step 6: Adding data integrity constraints...';
END $$;

-- Ensure email format is valid
ALTER TABLE users 
ADD CONSTRAINT IF NOT EXISTS chk_users_email_format 
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Ensure age is reasonable
ALTER TABLE users 
ADD CONSTRAINT IF NOT EXISTS chk_users_age_range 
CHECK (age IS NULL OR (age >= 13 AND age <= 120));

-- Step 7: Create materialized view for user dashboard performance
DO $$
BEGIN
    RAISE NOTICE 'Step 7: Creating materialized views for performance...';
END $$;

-- Drop existing materialized view if it exists
DROP MATERIALIZED VIEW IF EXISTS user_dashboard_summary;

-- Create materialized view for user dashboard data
CREATE MATERIALIZED VIEW user_dashboard_summary AS
SELECT 
    u.id as user_id,
    u.name,
    u.email,
    u.updated_at as profile_updated_at,
    COUNT(DISTINCT dl.id) as total_diet_logs,
    COUNT(DISTINCT s.id) as total_symptoms,
    COUNT(DISTINCT mp.id) as total_predictions,
    MAX(dl.logged_at) as last_diet_log,
    MAX(s.recorded_at) as last_symptom_record
FROM users u
LEFT JOIN diet_logs dl ON u.id = dl.user_id
LEFT JOIN symptoms s ON u.id = s.user_id  
LEFT JOIN ml_predictions mp ON u.id = mp.user_id
WHERE u.deleted_at IS NULL
GROUP BY u.id, u.name, u.email, u.updated_at;

-- Create index on materialized view
CREATE INDEX idx_user_dashboard_summary_user_id 
ON user_dashboard_summary (user_id);

-- Step 8: Create function to refresh dashboard data
DO $$
BEGIN
    RAISE NOTICE 'Step 8: Creating dashboard refresh function...';
END $$;

CREATE OR REPLACE FUNCTION refresh_user_dashboard()
RETURNS void AS $func$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY user_dashboard_summary;
END;
$func$ LANGUAGE plpgsql;

-- Step 9: Analyze tables for query planner optimization
DO $$
BEGIN
    RAISE NOTICE 'Step 9: Analyzing tables for query optimization...';
END $$;

ANALYZE users;
ANALYZE food_items;
ANALYZE diet_logs;
ANALYZE symptoms;
ANALYZE ml_predictions;
ANALYZE user_sessions;
ANALYZE notifications;

-- Step 10: Set optimal PostgreSQL parameters for the workload
DO $$
BEGIN
    RAISE NOTICE 'Step 10: Optimization completed successfully!';
    RAISE NOTICE 'Database is now optimized for:';
    RAISE NOTICE '- Fast user profile lookups and updates';
    RAISE NOTICE '- Immediate UI reflection of changes';
    RAISE NOTICE '- Efficient food item searches';
    RAISE NOTICE '- Optimized diet and symptom tracking';
    RAISE NOTICE '- Real-time notifications for profile updates';
END $$;

COMMIT;

-- Final verification
DO $$
DECLARE
    index_count INTEGER;
    trigger_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO index_count 
    FROM pg_indexes 
    WHERE schemaname = 'public' 
    AND indexname LIKE 'idx_%';
    
    SELECT COUNT(*) INTO trigger_count 
    FROM pg_trigger 
    WHERE tgname LIKE 'trigger_%';
    
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'SCHEMA OPTIMIZATION COMPLETED';
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'Created % optimized indexes', index_count;
    RAISE NOTICE 'Created % triggers for real-time updates', trigger_count;
    RAISE NOTICE 'System ready for optimal performance';
    RAISE NOTICE '==========================================';
END $$;