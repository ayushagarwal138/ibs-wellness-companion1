-- Safe test deletion script for current database state
-- Only deletes from existing tables: users and symptoms

BEGIN;

-- Check current data before deletion
SELECT 'BEFORE DELETION:' as status;
SELECT COUNT(*) as user_count FROM users;
SELECT COUNT(*) as symptoms_count FROM symptoms;

-- Delete symptoms first (has foreign key to users)
DELETE FROM symptoms;

-- Delete users
DELETE FROM users;

-- Check data after deletion
SELECT 'AFTER DELETION:' as status;
SELECT COUNT(*) as user_count FROM users;
SELECT COUNT(*) as symptoms_count FROM symptoms;

-- Rollback for safety (remove this line to actually execute)
ROLLBACK;

-- Uncomment the line below to actually commit the deletion
-- COMMIT;
