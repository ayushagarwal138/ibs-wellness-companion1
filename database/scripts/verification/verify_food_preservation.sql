-- Food Items Preservation Verification Script
-- This script verifies that food_items data is preserved during user cleanup
-- Run this BEFORE and AFTER the user data cleanup to ensure no data loss

\echo 'Food Items Preservation Verification'
\echo '===================================='

-- Check current food items count and sample data
SELECT 
    'FOOD_ITEMS_COUNT' as metric,
    COUNT(*)::TEXT as value
FROM food_items;

SELECT 
    'FOOD_ITEMS_CATEGORIES' as metric,
    COUNT(DISTINCT category)::TEXT as value
FROM food_items 
WHERE category IS NOT NULL;

-- Show sample food items for manual verification
\echo ''
\echo 'Sample Food Items (first 10):'
\echo '----------------------------'
SELECT 
    name,
    category,
    fodmap_level,
    calories_per_100g
FROM food_items 
ORDER BY name 
LIMIT 10;

-- Check for any potential foreign key references to food_items
\echo ''
\echo 'Checking for references to food_items:'
\echo '------------------------------------'

-- Check if any diet_logs reference food_items in their JSONB data
-- This is a complex check since food_items are stored as JSONB arrays
SELECT 
    'DIET_LOGS_WITH_FOOD_REFERENCES' as check_type,
    COUNT(*) as count
FROM diet_logs 
WHERE food_items IS NOT NULL 
  AND jsonb_array_length(food_items) > 0;

-- Verify food_items table structure
\echo ''
\echo 'Food Items Table Structure:'
\echo '-------------------------'
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'food_items' 
  AND table_schema = 'public'
ORDER BY ordinal_position;

-- Check for any constraints on food_items
\echo ''
\echo 'Food Items Constraints:'
\echo '---------------------'
SELECT 
    constraint_name,
    constraint_type
FROM information_schema.table_constraints 
WHERE table_name = 'food_items' 
  AND table_schema = 'public';

-- Summary statistics
\echo ''
\echo 'Food Items Summary Statistics:'
\echo '----------------------------'
SELECT 
    COUNT(*) as total_items,
    COUNT(DISTINCT category) as unique_categories,
    COUNT(CASE WHEN fodmap_level = 'low' THEN 1 END) as low_fodmap_items,
    COUNT(CASE WHEN fodmap_level = 'moderate' THEN 1 END) as moderate_fodmap_items,
    COUNT(CASE WHEN fodmap_level = 'high' THEN 1 END) as high_fodmap_items,
    COUNT(CASE WHEN common_triggers = true THEN 1 END) as common_trigger_foods,
    AVG(calories_per_100g) as avg_calories_per_100g
FROM food_items;

\echo ''
\echo 'Verification completed. Save this output for comparison after cleanup.'