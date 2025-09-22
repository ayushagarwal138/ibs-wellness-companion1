-- IBS Wellness Companion: Complete User Data Cleanup Script
-- This script permanently deletes ALL user accounts and associated data
-- while preserving food_items and maintaining database integrity
-- 
-- IMPORTANT: This operation is IRREVERSIBLE
-- Ensure you have proper backups before execution
--
-- Created: $(date)
-- Purpose: Clean slate for production deployment

BEGIN;

-- Set transaction isolation level for consistency
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Disable triggers temporarily to improve performance
SET session_replication_role = replica;

-- Create a backup verification function
CREATE OR REPLACE FUNCTION verify_food_items_preservation()
RETURNS TABLE(
    total_food_items BIGINT,
    sample_food_names TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_food_items,
        ARRAY(SELECT name FROM food_items ORDER BY name LIMIT 10) as sample_food_names
    FROM food_items;
END;
$$ LANGUAGE plpgsql;

-- Store food items count before deletion for verification
CREATE TEMP TABLE food_items_backup_verification AS
SELECT * FROM verify_food_items_preservation();

-- Log the cleanup operation start
DO $$
BEGIN
    RAISE NOTICE 'Starting comprehensive user data cleanup at %', NOW();
    RAISE NOTICE 'Food items before cleanup: %', (SELECT total_food_items FROM food_items_backup_verification);
END $$;

-- Step 1: Delete time-series data (hypertables) first to avoid constraint issues
-- These tables have the most data and benefit from bulk deletion

RAISE NOTICE 'Step 1: Cleaning time-series data...';

-- Delete ML predictions (references users)
DELETE FROM ml_predictions;
RAISE NOTICE 'Deleted all ML predictions';

-- Delete audit logs (some may reference users, but we want to clean all for fresh start)
DELETE FROM audit_logs;
RAISE NOTICE 'Deleted all audit logs';

-- Delete symptoms data
DELETE FROM symptoms;
RAISE NOTICE 'Deleted all symptoms data';

-- Delete medication logs
DELETE FROM medication_logs;
RAISE NOTICE 'Deleted all medication logs';

-- Delete diet logs
DELETE FROM diet_logs;
RAISE NOTICE 'Deleted all diet logs';

-- Step 2: Delete archive tables
RAISE NOTICE 'Step 2: Cleaning archive tables...';

-- Delete archived data
DELETE FROM diet_logs_archive;
DELETE FROM symptoms_archive;
RAISE NOTICE 'Deleted all archived data';

-- Step 3: Delete optimization and summary tables
RAISE NOTICE 'Step 3: Cleaning optimization tables...';

-- Delete daily nutrition summaries
DELETE FROM daily_nutrition_summary;
RAISE NOTICE 'Deleted all daily nutrition summaries';

-- Delete weekly symptom summaries  
DELETE FROM weekly_symptom_summary;
RAISE NOTICE 'Deleted all weekly symptom summaries';

-- Delete optimization metrics (clean slate for new tracking)
DELETE FROM optimization_metrics;
RAISE NOTICE 'Deleted all optimization metrics';

-- Step 4: Delete chat and communication data
RAISE NOTICE 'Step 4: Cleaning communication data...';

-- Delete chat messages first (references chat_sessions)
DELETE FROM chat_messages;
RAISE NOTICE 'Deleted all chat messages';

-- Delete chat sessions
DELETE FROM chat_sessions;
RAISE NOTICE 'Deleted all chat sessions';

-- Delete notifications
DELETE FROM notifications;
RAISE NOTICE 'Deleted all notifications';

-- Step 5: Delete authentication and session data
RAISE NOTICE 'Step 5: Cleaning authentication data...';

-- Delete user sessions
DELETE FROM user_sessions;
RAISE NOTICE 'Deleted all user sessions';

-- Step 6: Delete medication data
RAISE NOTICE 'Step 6: Cleaning medication data...';

-- Delete medications (medication_logs already deleted)
DELETE FROM medications;
RAISE NOTICE 'Deleted all medications';

-- Step 7: Finally delete users table (this will cascade to any remaining references)
RAISE NOTICE 'Step 7: Deleting user accounts...';

-- Get count before deletion for logging
DO $$
DECLARE
    user_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    RAISE NOTICE 'Deleting % user accounts...', user_count;
END $$;

-- Delete all users (this will cascade delete any remaining references due to FK constraints)
DELETE FROM users;
RAISE NOTICE 'Deleted all user accounts';

-- Step 8: Verify food_items preservation
RAISE NOTICE 'Step 8: Verifying food items preservation...';

DO $$
DECLARE
    food_count_before BIGINT;
    food_count_after BIGINT;
BEGIN
    SELECT total_food_items INTO food_count_before FROM food_items_backup_verification;
    SELECT COUNT(*) INTO food_count_after FROM food_items;
    
    IF food_count_before != food_count_after THEN
        RAISE EXCEPTION 'CRITICAL ERROR: Food items count mismatch! Before: %, After: %', 
                       food_count_before, food_count_after;
    END IF;
    
    RAISE NOTICE 'SUCCESS: Food items preserved. Count: %', food_count_after;
END $$;

-- Step 9: Reset sequences and optimize database
RAISE NOTICE 'Step 9: Optimizing database...';

-- Reset any sequences that might have been affected
-- Note: We're using UUIDs, so no sequences to reset for primary keys

-- Update table statistics for query planner
ANALYZE users;
ANALYZE symptoms;
ANALYZE medications;
ANALYZE medication_logs;
ANALYZE diet_logs;
ANALYZE ml_predictions;
ANALYZE notifications;
ANALYZE chat_sessions;
ANALYZE chat_messages;
ANALYZE user_sessions;
ANALYZE audit_logs;
ANALYZE daily_nutrition_summary;
ANALYZE weekly_symptom_summary;
ANALYZE food_items;

-- Vacuum tables to reclaim space
VACUUM ANALYZE users;
VACUUM ANALYZE symptoms;
VACUUM ANALYZE medications;
VACUUM ANALYZE medication_logs;
VACUUM ANALYZE diet_logs;
VACUUM ANALYZE ml_predictions;
VACUUM ANALYZE notifications;
VACUUM ANALYZE chat_sessions;
VACUUM ANALYZE chat_messages;
VACUUM ANALYZE user_sessions;
VACUUM ANALYZE audit_logs;
VACUUM ANALYZE daily_nutrition_summary;
VACUUM ANALYZE weekly_symptom_summary;

-- Re-enable triggers
SET session_replication_role = DEFAULT;

-- Step 10: Final verification and logging
RAISE NOTICE 'Step 10: Final verification...';

-- Verify all user-related data is gone
DO $$
DECLARE
    remaining_users INTEGER;
    remaining_symptoms INTEGER;
    remaining_diet_logs INTEGER;
    remaining_medications INTEGER;
    remaining_sessions INTEGER;
    food_items_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO remaining_users FROM users;
    SELECT COUNT(*) INTO remaining_symptoms FROM symptoms;
    SELECT COUNT(*) INTO remaining_diet_logs FROM diet_logs;
    SELECT COUNT(*) INTO remaining_medications FROM medications;
    SELECT COUNT(*) INTO remaining_sessions FROM user_sessions;
    SELECT COUNT(*) INTO food_items_count FROM food_items;
    
    -- Verify complete cleanup
    IF remaining_users > 0 OR remaining_symptoms > 0 OR remaining_diet_logs > 0 
       OR remaining_medications > 0 OR remaining_sessions > 0 THEN
        RAISE EXCEPTION 'CLEANUP INCOMPLETE: Users: %, Symptoms: %, Diet Logs: %, Medications: %, Sessions: %',
                       remaining_users, remaining_symptoms, remaining_diet_logs, 
                       remaining_medications, remaining_sessions;
    END IF;
    
    -- Log success
    RAISE NOTICE '=== USER DATA CLEANUP COMPLETED SUCCESSFULLY ===';
    RAISE NOTICE 'All user accounts and associated data have been permanently deleted';
    RAISE NOTICE 'Food items preserved: % records', food_items_count;
    RAISE NOTICE 'Database is now ready for fresh user registrations';
    RAISE NOTICE 'Cleanup completed at: %', NOW();
END $$;

-- Clean up temporary objects
DROP FUNCTION verify_food_items_preservation();
DROP TABLE food_items_backup_verification;

-- Log final completion
INSERT INTO audit_logs (
    user_id,
    action,
    resource_type,
    resource_id,
    new_values,
    created_at
) VALUES (
    NULL,
    'SYSTEM_CLEANUP',
    'DATABASE',
    NULL,
    jsonb_build_object(
        'operation', 'complete_user_data_cleanup',
        'completed_at', NOW(),
        'status', 'SUCCESS',
        'description', 'All user data permanently deleted, food items preserved'
    ),
    NOW()
);

COMMIT;

-- Final message
\echo ''
\echo '=========================================='
\echo 'USER DATA CLEANUP COMPLETED SUCCESSFULLY'
\echo '=========================================='
\echo 'All user accounts and associated data have been permanently deleted.'
\echo 'Food items and database structure have been preserved.'
\echo 'The system is ready for new user registrations.'
\echo '=========================================='