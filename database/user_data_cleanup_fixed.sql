-- User Data Cleanup Script (Fixed Version)
-- This script permanently deletes all user accounts and associated data
-- while preserving food_items and database structure

BEGIN;

-- Step 1: Delete time-series data first (oldest data)
DO $$
BEGIN
    RAISE NOTICE 'Step 1: Deleting time-series data...';
END $$;

DELETE FROM daily_nutrition_summary WHERE user_id IS NOT NULL;
DELETE FROM weekly_symptom_summary WHERE user_id IS NOT NULL;

-- Step 2: Delete archive tables
DO $$
BEGIN
    RAISE NOTICE 'Step 2: Deleting archive data...';
END $$;

DELETE FROM diet_logs_archive WHERE user_id IS NOT NULL;
DELETE FROM symptoms_archive WHERE user_id IS NOT NULL;

-- Step 3: Delete communication and session data
DO $$
BEGIN
    RAISE NOTICE 'Step 3: Deleting communication data...';
END $$;

DELETE FROM chat_messages WHERE chat_session_id IN (SELECT id FROM chat_sessions WHERE user_id IS NOT NULL);
DELETE FROM chat_sessions WHERE user_id IS NOT NULL;
DELETE FROM notifications WHERE user_id IS NOT NULL;

-- Step 4: Delete ML predictions and analysis data
DO $$
BEGIN
    RAISE NOTICE 'Step 4: Deleting ML predictions...';
END $$;

DELETE FROM ml_predictions WHERE user_id IS NOT NULL;

-- Step 5: Delete diet and symptom logs
DO $$
BEGIN
    RAISE NOTICE 'Step 5: Deleting diet and symptom logs...';
END $$;

DELETE FROM diet_logs WHERE user_id IS NOT NULL;
DELETE FROM symptoms WHERE user_id IS NOT NULL;

-- Step 6: Delete medications
DO $$
BEGIN
    RAISE NOTICE 'Step 6: Deleting medications...';
END $$;

DELETE FROM medications WHERE user_id IS NOT NULL;

-- Step 7: Delete audit logs
DO $$
BEGIN
    RAISE NOTICE 'Step 7: Deleting audit logs...';
END $$;

DELETE FROM audit_logs WHERE user_id IS NOT NULL;

-- Step 8: Delete user sessions
DO $$
BEGIN
    RAISE NOTICE 'Step 8: Deleting user sessions...';
END $$;

DELETE FROM user_sessions WHERE user_id IS NOT NULL;

-- Step 9: Finally delete user accounts
DO $$
BEGIN
    RAISE NOTICE 'Step 9: Deleting user accounts...';
END $$;

DELETE FROM users;

-- Step 10: Verify food_items are preserved
DO $$
DECLARE
    food_count INTEGER;
BEGIN
    RAISE NOTICE 'Step 10: Final verification...';
    
    SELECT COUNT(*) INTO food_count FROM food_items;
    
    IF food_count = 0 THEN
        RAISE EXCEPTION 'CRITICAL ERROR: Food items were deleted! Rolling back transaction.';
    ELSE
        RAISE NOTICE 'SUCCESS: % food items preserved', food_count;
    END IF;
END $$;

-- Step 11: Database optimization
DO $$
BEGIN
    RAISE NOTICE 'Step 11: Optimizing database...';
END $$;

VACUUM ANALYZE users;
VACUUM ANALYZE symptoms;
VACUUM ANALYZE diet_logs;
VACUUM ANALYZE ml_predictions;
VACUUM ANALYZE notifications;
VACUUM ANALYZE chat_sessions;
VACUUM ANALYZE chat_messages;
VACUUM ANALYZE user_sessions;
VACUUM ANALYZE audit_logs;
VACUUM ANALYZE medications;
VACUUM ANALYZE daily_nutrition_summary;
VACUUM ANALYZE weekly_symptom_summary;

-- Commit the transaction
COMMIT;

-- Final success message
DO $$
BEGIN
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'USER DATA CLEANUP COMPLETED SUCCESSFULLY';
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'All user accounts and associated data have been permanently deleted.';
    RAISE NOTICE 'Food items and database structure have been preserved.';
    RAISE NOTICE 'The system is ready for new user registrations.';
    RAISE NOTICE '==========================================';
END $$;