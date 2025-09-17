-- Seed data for diet_logs table
-- Realistic meal entries for sample users

INSERT INTO diet_logs (
    id,
    user_id,
    logged_at,
    meal_type,
    food_items,
    calories,
    fiber_grams,
    fat_grams,
    protein_grams,
    carbs_grams,
    fodmap_level,
    trigger_foods,
    satisfaction_rating,
    digestive_comfort,
    notes,
    created_at
) VALUES 

-- John Doe (IBS-D) - Recent meals
('950e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', NOW() - INTERVAL '2 hours', 'lunch', 
'[{"name": "Grilled Chicken Breast", "quantity": "150g"}, {"name": "White Rice", "quantity": "100g"}, {"name": "Carrots", "quantity": "80g"}, {"name": "Green Tea", "quantity": "1 cup"}]', 
420, 3.2, 8.5, 38.2, 45.0, 'low', '{}', 4, 4, 'Safe meal choice', NOW() - INTERVAL '2 hours'),

('950e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440001', NOW() - INTERVAL '14 hours', 'breakfast', 
'[{"name": "Oats", "quantity": "50g"}, {"name": "Banana", "quantity": "1 medium"}, {"name": "Lactose-Free Milk", "quantity": "200ml"}, {"name": "Coffee", "quantity": "1 cup"}]', 
385, 6.8, 8.2, 12.4, 58.0, 'low', '{}', 5, 5, 'Good start to the day', NOW() - INTERVAL '14 hours'),

('950e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440001', NOW() - INTERVAL '1 day 2 hours', 'dinner', 
'[{"name": "Salmon", "quantity": "120g"}, {"name": "Quinoa", "quantity": "80g"}, {"name": "Spinach", "quantity": "100g"}, {"name": "Bell Pepper", "quantity": "60g"}]', 
485, 8.5, 18.2, 32.8, 42.0, 'low', '{}', 5, 4, 'Nutritious and well-tolerated', NOW() - INTERVAL '1 day 2 hours'),

('950e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440001', NOW() - INTERVAL '2 days 6 hours', 'lunch', 
'[{"name": "Pizza", "quantity": "2 slices"}, {"name": "Orange Juice", "quantity": "250ml"}]', 
645, 4.6, 20.8, 22.0, 78.5, 'high', '{"Pizza"}', 3, 1, 'Bad choice - triggered symptoms', NOW() - INTERVAL '2 days 6 hours'),

-- Jane Smith (IBS-C) - Recent meals
('950e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440002', NOW() - INTERVAL '3 hours', 'lunch', 
'[{"name": "Brown Rice", "quantity": "120g"}, {"name": "Broccoli", "quantity": "100g"}, {"name": "Tofu", "quantity": "100g"}, {"name": "Almonds", "quantity": "20g"}]', 
465, 12.8, 14.2, 18.5, 52.0, 'low', '{}', 4, 4, 'High fiber meal for constipation', NOW() - INTERVAL '3 hours'),

('950e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440002', NOW() - INTERVAL '15 hours', 'breakfast', 
'[{"name": "Oats", "quantity": "60g"}, {"name": "Strawberries", "quantity": "100g"}, {"name": "Chia Seeds", "quantity": "15g"}, {"name": "Greek Yogurt", "quantity": "150g"}]', 
425, 15.2, 12.8, 18.5, 48.0, 'moderate', '{}', 5, 4, 'Fiber-rich breakfast', NOW() - INTERVAL '15 hours'),

('950e8400-e29b-41d4-a716-446655440007', '550e8400-e29b-41d4-a716-446655440002', NOW() - INTERVAL '1 day 4 hours', 'dinner', 
'[{"name": "Lentils", "quantity": "100g"}, {"name": "Carrots", "quantity": "80g"}, {"name": "Spinach", "quantity": "100g"}, {"name": "Olive Oil", "quantity": "10ml"}]', 
285, 12.5, 5.2, 12.8, 35.0, 'high', '{"Lentils"}', 3, 2, 'High FODMAP - caused bloating', NOW() - INTERVAL '1 day 4 hours'),

-- Mike Johnson (IBS-M) - Recent meals
('950e8400-e29b-41d4-a716-446655440008', '550e8400-e29b-41d4-a716-446655440003', NOW() - INTERVAL '1 hour', 'snack', 
'[{"name": "Walnuts", "quantity": "25g"}, {"name": "Dark Chocolate", "quantity": "20g"}]', 
272, 3.1, 19.2, 6.8, 15.0, 'low', '{}', 4, 4, 'Afternoon snack', NOW() - INTERVAL '1 hour'),

('950e8400-e29b-41d4-a716-446655440009', '550e8400-e29b-41d4-a716-446655440003', NOW() - INTERVAL '6 hours', 'breakfast', 
'[{"name": "Eggs", "quantity": "2 large"}, {"name": "White Rice", "quantity": "80g"}, {"name": "Bell Pepper", "quantity": "50g"}, {"name": "Coffee", "quantity": "1 cup"}]', 
385, 2.8, 12.5, 18.2, 28.0, 'low', '{}', 5, 5, 'Simple and safe', NOW() - INTERVAL '6 hours'),

('950e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440003', NOW() - INTERVAL '1 day 8 hours', 'dinner', 
'[{"name": "Chicken Breast", "quantity": "140g"}, {"name": "Cauliflower", "quantity": "120g"}, {"name": "Carrots", "quantity": "60g"}]', 
295, 6.8, 6.2, 38.5, 18.0, 'moderate', '{}', 4, 3, 'Cauliflower caused some gas', NOW() - INTERVAL '1 day 8 hours'),

-- Sarah Wilson (IBS-U) - Recent meals
('950e8400-e29b-41d4-a716-446655440011', '550e8400-e29b-41d4-a716-446655440004', NOW() - INTERVAL '30 minutes', 'snack', 
'[{"name": "Banana", "quantity": "1 medium"}, {"name": "Peanuts", "quantity": "20g"}]', 
202, 4.3, 10.2, 6.8, 25.0, 'low', '{}', 4, 4, 'Quick snack', NOW() - INTERVAL '30 minutes'),

('950e8400-e29b-41d4-a716-446655440012', '550e8400-e29b-41d4-a716-446655440004', NOW() - INTERVAL '7 hours', 'breakfast', 
'[{"name": "Oats", "quantity": "45g"}, {"name": "Orange", "quantity": "1 medium"}, {"name": "Lactose-Free Milk", "quantity": "150ml"}]', 
285, 5.8, 4.2, 8.5, 42.0, 'low', '{}', 4, 4, 'Standard breakfast', NOW() - INTERVAL '7 hours'),

('950e8400-e29b-41d4-a716-446655440013', '550e8400-e29b-41d4-a716-446655440004', NOW() - INTERVAL '1 day 5 hours', 'lunch', 
'[{"name": "Apple", "quantity": "1 medium"}, {"name": "Cheddar Cheese", "quantity": "30g"}, {"name": "Wheat Bread", "quantity": "2 slices"}]', 
485, 5.8, 13.2, 15.8, 68.0, 'high', '{"Apple", "Wheat Bread"}', 2, 2, 'High FODMAP meal - felt unwell after', NOW() - INTERVAL '1 day 5 hours'),

-- Additional historical entries
('950e8400-e29b-41d4-a716-446655440014', '550e8400-e29b-41d4-a716-446655440001', NOW() - INTERVAL '3 days', 'breakfast', 
'[{"name": "Quinoa", "quantity": "60g"}, {"name": "Grapes", "quantity": "100g"}, {"name": "Lactose-Free Milk", "quantity": "200ml"}]', 
385, 4.8, 6.2, 12.5, 58.0, 'low', '{}', 5, 5, 'Great breakfast option', NOW() - INTERVAL '3 days'),

('950e8400-e29b-41d4-a716-446655440015', '550e8400-e29b-41d4-a716-446655440002', NOW() - INTERVAL '4 days', 'dinner', 
'[{"name": "Salmon", "quantity": "130g"}, {"name": "Brown Rice", "quantity": "100g"}, {"name": "Broccoli", "quantity": "120g"}]', 
485, 8.2, 16.8, 32.5, 38.0, 'low', '{}', 5, 4, 'Excellent meal for IBS-C', NOW() - INTERVAL '4 days'),

('950e8400-e29b-41d4-a716-446655440016', '550e8400-e29b-41d4-a716-446655440003', NOW() - INTERVAL '5 days', 'lunch', 
'[{"name": "Garlic", "quantity": "2 cloves"}, {"name": "Onion", "quantity": "50g"}, {"name": "Chicken Breast", "quantity": "120g"}, {"name": "White Rice", "quantity": "80g"}]', 
425, 2.8, 5.2, 28.5, 35.0, 'high', '{"Garlic", "Onion"}', 2, 1, 'Major trigger foods - big mistake', NOW() - INTERVAL '5 days'),

('950e8400-e29b-41d4-a716-446655440017', '550e8400-e29b-41d4-a716-446655440004', NOW() - INTERVAL '6 days', 'breakfast', 
'[{"name": "Oats", "quantity": "50g"}, {"name": "Watermelon", "quantity": "150g"}, {"name": "Greek Yogurt", "quantity": "100g"}]', 
285, 4.2, 2.8, 12.5, 42.0, 'high', '{"Watermelon"}', 3, 2, 'Watermelon triggered symptoms', NOW() - INTERVAL '6 days'),

('950e8400-e29b-41d4-a716-446655440018', '550e8400-e29b-41d4-a716-446655440001', NOW() - INTERVAL '7 days', 'dinner', 
'[{"name": "Tofu", "quantity": "120g"}, {"name": "Quinoa", "quantity": "90g"}, {"name": "Spinach", "quantity": "100g"}, {"name": "Bell Pepper", "quantity": "70g"}]', 
385, 8.5, 8.2, 18.8, 48.0, 'low', '{}', 5, 5, 'Perfect IBS-friendly meal', NOW() - INTERVAL '7 days'),

('950e8400-e29b-41d4-a716-446655440019', '550e8400-e29b-41d4-a716-446655440002', NOW() - INTERVAL '8 days', 'snack', 
'[{"name": "Strawberries", "quantity": "150g"}, {"name": "Cheddar Cheese", "quantity": "25g"}]', 
148, 3.0, 8.5, 6.8, 14.0, 'low', '{}', 4, 4, 'Light afternoon snack', NOW() - INTERVAL '8 days'),

('950e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440003', NOW() - INTERVAL '10 days', 'breakfast', 
'[{"name": "Eggs", "quantity": "2 large"}, {"name": "Spinach", "quantity": "80g"}, {"name": "Cheddar Cheese", "quantity": "20g"}, {"name": "Coffee", "quantity": "1 cup"}]', 
285, 2.8, 18.2, 22.5, 4.0, 'low', '{}', 5, 5, 'Low-carb breakfast worked well', NOW() - INTERVAL '10 days');