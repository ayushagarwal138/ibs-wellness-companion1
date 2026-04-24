-- Migration: 003_add_data_retention_policies.sql
-- Description: Add comprehensive data retention policies and cleanup procedures
-- Created: 2024-01-15
-- Author: IBS Wellness Companion

-- Create function to clean up old data based on retention policies
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS TABLE(
    table_name TEXT,
    records_deleted BIGINT,
    cleanup_date TIMESTAMP
) AS $$
DECLARE
    deleted_count BIGINT;
    cleanup_timestamp TIMESTAMP := NOW();
BEGIN
    -- Clean up old audit logs (keep 1 year)
    DELETE FROM audit_logs 
    WHERE created_at < NOW() - INTERVAL '1 year';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    table_name := 'audit_logs';
    records_deleted := deleted_count;
    cleanup_date := cleanup_timestamp;
    RETURN NEXT;
    
    -- Clean up old ML predictions (keep 6 months)
    DELETE FROM ml_predictions 
    WHERE predicted_at < NOW() - INTERVAL '6 months';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    table_name := 'ml_predictions';
    records_deleted := deleted_count;
    cleanup_date := cleanup_timestamp;
    RETURN NEXT;
    
    -- Clean up old diet logs (keep 1 year)
    DELETE FROM diet_logs 
    WHERE logged_at < NOW() - INTERVAL '1 year';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    table_name := 'diet_logs';
    records_deleted := deleted_count;
    cleanup_date := cleanup_timestamp;
    RETURN NEXT;
    
    -- Clean up old medication logs (keep 2 years)
    DELETE FROM medication_logs 
    WHERE taken_at < NOW() - INTERVAL '2 years';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    table_name := 'medication_logs';
    records_deleted := deleted_count;
    cleanup_date := cleanup_timestamp;
    RETURN NEXT;
    
    -- Clean up old symptoms (keep 2 years)
    DELETE FROM symptoms 
    WHERE recorded_at < NOW() - INTERVAL '2 years';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    table_name := 'symptoms';
    records_deleted := deleted_count;
    cleanup_date := cleanup_timestamp;
    RETURN NEXT;
    
    -- Clean up old chat sessions and messages (keep 6 months)
    DELETE FROM chat_messages 
    WHERE created_at < NOW() - INTERVAL '6 months';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    table_name := 'chat_messages';
    records_deleted := deleted_count;
    cleanup_date := cleanup_timestamp;
    RETURN NEXT;
    
    DELETE FROM chat_sessions 
    WHERE created_at < NOW() - INTERVAL '6 months';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    table_name := 'chat_sessions';
    records_deleted := deleted_count;
    cleanup_date := cleanup_timestamp;
    RETURN NEXT;
    
    -- Clean up old notifications (keep sent notifications for 3 months)
    DELETE FROM notifications 
    WHERE sent_at IS NOT NULL 
    AND sent_at < NOW() - INTERVAL '3 months';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    table_name := 'notifications';
    records_deleted := deleted_count;
    cleanup_date := cleanup_timestamp;
    RETURN NEXT;
    
    -- Clean up expired user sessions (keep 30 days)
    DELETE FROM user_sessions 
    WHERE expires_at < NOW() - INTERVAL '30 days';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    table_name := 'user_sessions';
    records_deleted := deleted_count;
    cleanup_date := cleanup_timestamp;
    RETURN NEXT;
    
    -- Log cleanup operation
    INSERT INTO audit_logs (
        user_id, 
        action_type, 
        table_name, 
        details, 
        created_at
    ) VALUES (
        NULL,
        'DATA_CLEANUP',
        'SYSTEM',
        json_build_object(
            'cleanup_timestamp', cleanup_timestamp,
            'retention_policy', 'automated_cleanup'
        ),
        cleanup_timestamp
    );
    
END;
$$ LANGUAGE plpgsql;

-- Create function to archive old data before deletion
CREATE OR REPLACE FUNCTION archive_old_data(archive_table_suffix TEXT DEFAULT NULL)
RETURNS TABLE(
    table_name TEXT,
    records_archived BIGINT,
    archive_date TIMESTAMP
) AS $$
DECLARE
    deleted_count BIGINT;
    archive_timestamp TIMESTAMP := NOW();
    suffix TEXT := COALESCE(archive_table_suffix, to_char(NOW(), 'YYYY_MM'));
BEGIN
    -- Archive old symptoms data (older than 1 year)
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS symptoms_archive_%s (LIKE symptoms INCLUDING ALL);
    ', suffix);
    
    EXECUTE format('
        INSERT INTO symptoms_archive_%s 
        SELECT * FROM symptoms 
        WHERE recorded_at < NOW() - INTERVAL ''1 year''
        AND recorded_at >= NOW() - INTERVAL ''2 years'';
    ', suffix);
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    table_name := 'symptoms_archive_' || suffix;
    records_archived := deleted_count;
    archive_date := archive_timestamp;
    RETURN NEXT;
    
    -- Archive old diet logs (older than 6 months)
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS diet_logs_archive_%s (LIKE diet_logs INCLUDING ALL);
    ', suffix);
    
    EXECUTE format('
        INSERT INTO diet_logs_archive_%s 
        SELECT * FROM diet_logs 
        WHERE logged_at < NOW() - INTERVAL ''6 months''
        AND logged_at >= NOW() - INTERVAL ''1 year'';
    ', suffix);
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    table_name := 'diet_logs_archive_' || suffix;
    records_archived := deleted_count;
    archive_date := archive_timestamp;
    RETURN NEXT;
    
    -- Archive old ML predictions (older than 3 months)
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS ml_predictions_archive_%s (LIKE ml_predictions INCLUDING ALL);
    ', suffix);
    
    EXECUTE format('
        INSERT INTO ml_predictions_archive_%s 
        SELECT * FROM ml_predictions 
        WHERE predicted_at < NOW() - INTERVAL ''3 months''
        AND predicted_at >= NOW() - INTERVAL ''6 months'';
    ', suffix);
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    table_name := 'ml_predictions_archive_' || suffix;
    records_archived := deleted_count;
    archive_date := archive_timestamp;
    RETURN NEXT;
    
    -- Log archival operation
    INSERT INTO audit_logs (
        user_id, 
        action_type, 
        table_name, 
        details, 
        created_at
    ) VALUES (
        NULL,
        'DATA_ARCHIVE',
        'SYSTEM',
        json_build_object(
            'archive_timestamp', archive_timestamp,
            'archive_suffix', suffix,
            'retention_policy', 'automated_archive'
        ),
        archive_timestamp
    );
    
END;
$$ LANGUAGE plpgsql;

-- Create function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS TABLE(
    view_name TEXT,
    refresh_status TEXT,
    refresh_date TIMESTAMP
) AS $$
DECLARE
    refresh_timestamp TIMESTAMP := NOW();
BEGIN
    -- Refresh user summary stats
    BEGIN
        REFRESH MATERIALIZED VIEW user_summary_stats;
        view_name := 'user_summary_stats';
        refresh_status := 'SUCCESS';
        refresh_date := refresh_timestamp;
        RETURN NEXT;
    EXCEPTION WHEN OTHERS THEN
        view_name := 'user_summary_stats';
        refresh_status := 'ERROR: ' || SQLERRM;
        refresh_date := refresh_timestamp;
        RETURN NEXT;
    END;
    
    -- Log refresh operation
    INSERT INTO audit_logs (
        user_id, 
        action_type, 
        table_name, 
        details, 
        created_at
    ) VALUES (
        NULL,
        'VIEW_REFRESH',
        'SYSTEM',
        json_build_object(
            'refresh_timestamp', refresh_timestamp,
            'operation', 'materialized_view_refresh'
        ),
        refresh_timestamp
    );
    
END;
$$ LANGUAGE plpgsql;

-- Create function to analyze table statistics
CREATE OR REPLACE FUNCTION analyze_table_statistics()
RETURNS TABLE(
    table_name TEXT,
    row_count BIGINT,
    table_size TEXT,
    index_size TEXT,
    last_analyzed TIMESTAMP
) AS $$
DECLARE
    analyze_timestamp TIMESTAMP := NOW();
BEGIN
    -- Analyze all main tables
    ANALYZE symptoms;
    ANALYZE diet_logs;
    ANALYZE medication_logs;
    ANALYZE ml_predictions;
    ANALYZE users;
    ANALYZE notifications;
    ANALYZE chat_sessions;
    ANALYZE chat_messages;
    ANALYZE audit_logs;
    
    -- Return statistics for main tables
    RETURN QUERY
    SELECT 
        schemaname||'.'||tablename as table_name,
        n_tup_ins + n_tup_upd - n_tup_del as row_count,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size,
        pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as index_size,
        analyze_timestamp as last_analyzed
    FROM pg_stat_user_tables 
    WHERE schemaname = 'public'
    AND tablename IN ('symptoms', 'diet_logs', 'medication_logs', 'ml_predictions', 
                      'users', 'notifications', 'chat_sessions', 'chat_messages', 'audit_logs')
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
    
    -- Log analysis operation
    INSERT INTO audit_logs (
        user_id, 
        action_type, 
        table_name, 
        details, 
        created_at
    ) VALUES (
        NULL,
        'TABLE_ANALYSIS',
        'SYSTEM',
        json_build_object(
            'analysis_timestamp', analyze_timestamp,
            'operation', 'table_statistics_analysis'
        ),
        analyze_timestamp
    );
    
END;
$$ LANGUAGE plpgsql;

-- Create function for database maintenance
CREATE OR REPLACE FUNCTION perform_database_maintenance()
RETURNS TABLE(
    operation TEXT,
    status TEXT,
    details TEXT,
    execution_time INTERVAL
) AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    maintenance_timestamp TIMESTAMP := NOW();
BEGIN
    -- Vacuum and analyze main tables
    start_time := clock_timestamp();
    
    VACUUM ANALYZE symptoms;
    VACUUM ANALYZE diet_logs;
    VACUUM ANALYZE medication_logs;
    VACUUM ANALYZE ml_predictions;
    VACUUM ANALYZE users;
    
    end_time := clock_timestamp();
    
    operation := 'VACUUM_ANALYZE';
    status := 'SUCCESS';
    details := 'Vacuumed and analyzed main tables';
    execution_time := end_time - start_time;
    RETURN NEXT;
    
    -- Reindex critical indexes
    start_time := clock_timestamp();
    
    REINDEX INDEX idx_symptoms_user_date;
    REINDEX INDEX idx_diet_logs_user_date;
    REINDEX INDEX idx_ml_predictions_user_type_date;
    
    end_time := clock_timestamp();
    
    operation := 'REINDEX';
    status := 'SUCCESS';
    details := 'Reindexed critical performance indexes';
    execution_time := end_time - start_time;
    RETURN NEXT;
    
    -- Update table statistics
    start_time := clock_timestamp();
    
    PERFORM analyze_table_statistics();
    
    end_time := clock_timestamp();
    
    operation := 'UPDATE_STATISTICS';
    status := 'SUCCESS';
    details := 'Updated table statistics';
    execution_time := end_time - start_time;
    RETURN NEXT;
    
    -- Refresh materialized views
    start_time := clock_timestamp();
    
    PERFORM refresh_materialized_views();
    
    end_time := clock_timestamp();
    
    operation := 'REFRESH_VIEWS';
    status := 'SUCCESS';
    details := 'Refreshed materialized views';
    execution_time := end_time - start_time;
    RETURN NEXT;
    
    -- Log maintenance operation
    INSERT INTO audit_logs (
        user_id, 
        action_type, 
        table_name, 
        details, 
        created_at
    ) VALUES (
        NULL,
        'DATABASE_MAINTENANCE',
        'SYSTEM',
        json_build_object(
            'maintenance_timestamp', maintenance_timestamp,
            'operation', 'full_database_maintenance'
        ),
        maintenance_timestamp
    );
    
END;
$$ LANGUAGE plpgsql;

-- Add comments for documentation
COMMENT ON FUNCTION cleanup_old_data() IS 'Automated cleanup of old data based on retention policies';
COMMENT ON FUNCTION archive_old_data(TEXT) IS 'Archive old data before deletion for compliance';
COMMENT ON FUNCTION refresh_materialized_views() IS 'Refresh all materialized views for performance';
COMMENT ON FUNCTION analyze_table_statistics() IS 'Analyze and update table statistics for query optimization';
COMMENT ON FUNCTION perform_database_maintenance() IS 'Comprehensive database maintenance routine';

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
    '{"migration": "003_add_data_retention_policies", "description": "Added comprehensive data retention policies and cleanup procedures"}',
    NOW()
);