-- Comprehensive cleanup script for IBS Wellness Companion test data
-- This script removes all test data in the correct order to handle foreign key constraints

\echo 'Starting comprehensive test data cleanup...'

-- Step 1: Delete dependent records first (tables with NO ACTION foreign keys)
\echo 'Step 1: Cleaning up dependent records...'

-- Delete food reactions
DELETE FROM food_reactions WHERE user_id IN (SELECT id FROM users);
\echo 'Deleted food reactions'

-- Delete diet logs
DELETE FROM diet_logs WHERE user_id IN (SELECT id FROM users);
\echo 'Deleted diet logs'

-- Delete medication logs  
DELETE FROM medication_logs WHERE user_id IN (SELECT id FROM users);
\echo 'Deleted medication logs'

-- Delete symptom logs
DELETE FROM symptom_logs WHERE user_id IN (SELECT id FROM users);
\echo 'Deleted symptom logs'

-- Step 2: Delete records with CASCADE (these will be deleted automatically, but doing explicitly for clarity)
\echo 'Step 2: Cleaning up CASCADE records...'

-- Delete chat messages (CASCADE)
DELETE FROM chat_messages WHERE user_id IN (SELECT id FROM users);
\echo 'Deleted chat messages'

-- Delete chat sessions (CASCADE)
DELETE FROM chat_sessions WHERE user_id IN (SELECT id FROM users);
\echo 'Deleted chat sessions'

-- Delete user preferences (CASCADE)
DELETE FROM user_preferences WHERE user_id IN (SELECT id FROM users);
\echo 'Deleted user preferences'

-- Delete user profile completion (CASCADE)
DELETE FROM user_profile_completion WHERE user_id IN (SELECT id FROM users);
\echo 'Deleted user profile completion'

-- Delete user dietary profiles (CASCADE)
DELETE FROM user_dietary_profiles WHERE user_id IN (SELECT id FROM users);
\echo 'Deleted user dietary profiles'

-- Delete user medical profiles (CASCADE)
DELETE FROM user_medical_profiles WHERE user_id IN (SELECT id FROM users);
\echo 'Deleted user medical profiles'

-- Step 3: Delete user sessions
\echo 'Step 3: Cleaning up user sessions...'
DELETE FROM user_sessions WHERE user_id IN (SELECT id FROM users);
\echo 'Deleted user sessions'

-- Step 4: Delete notifications
\echo 'Step 4: Cleaning up notifications...'
DELETE FROM notifications WHERE user_id IN (SELECT id FROM users);
\echo 'Deleted notifications'

-- Step 5: Finally delete all users
\echo 'Step 5: Deleting all users...'
DELETE FROM users;
\echo 'Deleted all users'

-- Step 6: Reset sequences if they exist
\echo 'Step 6: Resetting sequences...'
-- Note: PostgreSQL with UUIDs doesn't typically use sequences, but including for completeness

-- Step 7: Verify cleanup
\echo 'Step 7: Verifying cleanup...'
SELECT 'Users remaining: ' || COUNT(*) FROM users;
SELECT 'Symptom logs remaining: ' || COUNT(*) FROM symptom_logs;
SELECT 'Diet logs remaining: ' || COUNT(*) FROM diet_logs;
SELECT 'Medication logs remaining: ' || COUNT(*) FROM medication_logs;
SELECT 'Food reactions remaining: ' || COUNT(*) FROM food_reactions;
SELECT 'Chat sessions remaining: ' || COUNT(*) FROM chat_sessions;
SELECT 'Chat messages remaining: ' || COUNT(*) FROM chat_messages;

\echo 'Comprehensive cleanup completed successfully!'
\echo 'All test data has been removed from the database.'