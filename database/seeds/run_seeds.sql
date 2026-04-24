-- Master seed script to populate the IBS Wellness Companion database
-- Run this script to populate the database with sample data

-- Ensure we're using the correct database
\echo 'Starting database seeding...'

-- Run seed files in dependency order
\echo 'Seeding users...'
\i 01_users.sql

\echo 'Seeding food items...'
\i 02_food_items.sql

\echo 'Seeding medications...'
\i 03_medications.sql

\echo 'Seeding symptoms...'
\i 04_symptoms.sql

\echo 'Seeding diet logs...'
\i 05_diet_logs.sql

\echo 'Database seeding completed successfully!'
\echo 'Sample data includes:'
\echo '- 6 users (1 admin, 1 doctor, 4 patients)'
\echo '- 40 food items with FODMAP classifications'
\echo '- 14 medications for various IBS types'
\echo '- 20 symptom log entries'
\echo '- 20 diet log entries'