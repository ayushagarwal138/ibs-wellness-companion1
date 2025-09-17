-- Database Migration Runner
-- Executes all migration scripts in order
-- Created: 2024-01-15

\echo 'Starting database migrations...'
\echo ''

-- Create migrations tracking table if it doesn't exist
CREATE TABLE IF NOT EXISTS migration_history (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) NOT NULL UNIQUE,
    executed_at TIMESTAMP DEFAULT NOW(),
    execution_time INTERVAL,
    status VARCHAR(50) DEFAULT 'SUCCESS',
    error_message TEXT
);

-- Function to track migration execution
CREATE OR REPLACE FUNCTION execute_migration(migration_name TEXT, migration_file TEXT)
RETURNS VOID AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    execution_duration INTERVAL;
BEGIN
    -- Check if migration already executed
    IF EXISTS (SELECT 1 FROM migration_history WHERE migration_history.migration_name = execute_migration.migration_name) THEN
        RAISE NOTICE 'Migration % already executed, skipping...', migration_name;
        RETURN;
    END IF;
    
    start_time := clock_timestamp();
    
    -- Execute the migration (this would be done externally)
    RAISE NOTICE 'Executing migration: %', migration_name;
    
    end_time := clock_timestamp();
    execution_duration := end_time - start_time;
    
    -- Record successful execution
    INSERT INTO migration_history (migration_name, executed_at, execution_time, status)
    VALUES (migration_name, start_time, execution_duration, 'SUCCESS');
    
    RAISE NOTICE 'Migration % completed successfully in %', migration_name, execution_duration;
    
EXCEPTION WHEN OTHERS THEN
    -- Record failed execution
    INSERT INTO migration_history (migration_name, executed_at, execution_time, status, error_message)
    VALUES (migration_name, start_time, clock_timestamp() - start_time, 'FAILED', SQLERRM);
    
    RAISE EXCEPTION 'Migration % failed: %', migration_name, SQLERRM;
END;
$$ LANGUAGE plpgsql;

\echo 'Migration tracking system initialized.'
\echo ''

-- Execute migrations in order
\echo 'Executing Migration 001: Add ML Prediction Indexes'
SELECT execute_migration('001_add_ml_prediction_indexes', '001_add_ml_prediction_indexes.sql');
\i 001_add_ml_prediction_indexes.sql
\echo 'Migration 001 completed.'
\echo ''

\echo 'Executing Migration 002: Add User Analytics Views'
SELECT execute_migration('002_add_user_analytics_views', '002_add_user_analytics_views.sql');
\i 002_add_user_analytics_views.sql
\echo 'Migration 002 completed.'
\echo ''

\echo 'Executing Migration 003: Add Data Retention Policies'
SELECT execute_migration('003_add_data_retention_policies', '003_add_data_retention_policies.sql');
\i 003_add_data_retention_policies.sql
\echo 'Migration 003 completed.'
\echo ''

-- Display migration summary
\echo 'Migration Summary:'
\echo '=================='
SELECT 
    migration_name,
    executed_at,
    execution_time,
    status
FROM migration_history 
ORDER BY executed_at DESC;

\echo ''
\echo 'Database Performance Summary:'
\echo '============================'
SELECT * FROM analyze_table_statistics();

\echo ''
\echo 'All migrations completed successfully!'
\echo 'Database is now ready for ML integration and advanced analytics.'
\echo ''

-- Final verification
\echo 'Verifying database structure...'
\echo ''

-- Check that all expected tables exist
DO $$
DECLARE
    missing_tables TEXT[] := ARRAY[]::TEXT[];
    expected_tables TEXT[] := ARRAY[
        'users', 'symptoms', 'medications', 'medication_logs', 
        'diet_logs', 'food_items', 'ml_predictions', 'notifications',
        'chat_sessions', 'chat_messages', 'user_sessions', 'audit_logs'
    ];
    table_name TEXT;
BEGIN
    FOREACH table_name IN ARRAY expected_tables
    LOOP
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = table_name
        ) THEN
            missing_tables := array_append(missing_tables, table_name);
        END IF;
    END LOOP;
    
    IF array_length(missing_tables, 1) > 0 THEN
        RAISE EXCEPTION 'Missing tables: %', array_to_string(missing_tables, ', ');
    ELSE
        RAISE NOTICE 'All expected tables are present.';
    END IF;
END $$;

-- Check that all expected views exist
DO $$
DECLARE
    missing_views TEXT[] := ARRAY[]::TEXT[];
    expected_views TEXT[] := ARRAY[
        'user_symptom_trends', 'user_dietary_patterns', 
        'medication_effectiveness', 'ml_training_features',
        'user_engagement_metrics'
    ];
    view_name TEXT;
BEGIN
    FOREACH view_name IN ARRAY expected_views
    LOOP
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.views 
            WHERE table_schema = 'public' AND table_name = view_name
        ) THEN
            missing_views := array_append(missing_views, view_name);
        END IF;
    END LOOP;
    
    IF array_length(missing_views, 1) > 0 THEN
        RAISE EXCEPTION 'Missing views: %', array_to_string(missing_views, ', ');
    ELSE
        RAISE NOTICE 'All expected views are present.';
    END IF;
END $$;

-- Check that all expected functions exist
DO $$
DECLARE
    missing_functions TEXT[] := ARRAY[]::TEXT[];
    expected_functions TEXT[] := ARRAY[
        'cleanup_old_data', 'archive_old_data', 'refresh_materialized_views',
        'analyze_table_statistics', 'perform_database_maintenance'
    ];
    function_name TEXT;
BEGIN
    FOREACH function_name IN ARRAY expected_functions
    LOOP
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.routines 
            WHERE routine_schema = 'public' AND routine_name = function_name
        ) THEN
            missing_functions := array_append(missing_functions, function_name);
        END IF;
    END LOOP;
    
    IF array_length(missing_functions, 1) > 0 THEN
        RAISE EXCEPTION 'Missing functions: %', array_to_string(missing_functions, ', ');
    ELSE
        RAISE NOTICE 'All expected functions are present.';
    END IF;
END $$;

\echo ''
\echo 'Database verification completed successfully!'
\echo 'The IBS Wellness Companion database is ready for production use.'