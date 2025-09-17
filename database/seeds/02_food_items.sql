-- Seed data for food_items table
-- Common foods with nutritional information and FODMAP levels

INSERT INTO food_items (
    id,
    name,
    category,
    fodmap_level,
    calories_per_100g,
    fiber_per_100g,
    fat_per_100g,
    protein_per_100g,
    carbs_per_100g,
    common_triggers,
    created_at
) VALUES 

-- Fruits
('650e8400-e29b-41d4-a716-446655440001', 'Apple', 'Fruits', 'high', 52, 2.4, 0.2, 0.3, 14.0, true, NOW()),
('650e8400-e29b-41d4-a716-446655440002', 'Banana', 'Fruits', 'low', 89, 2.6, 0.3, 1.1, 23.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440003', 'Orange', 'Fruits', 'low', 47, 2.4, 0.1, 0.9, 12.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440004', 'Grapes', 'Fruits', 'low', 62, 0.9, 0.2, 0.6, 16.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440005', 'Strawberries', 'Fruits', 'low', 32, 2.0, 0.3, 0.7, 8.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440006', 'Watermelon', 'Fruits', 'high', 30, 0.4, 0.2, 0.6, 8.0, true, NOW()),
('650e8400-e29b-41d4-a716-446655440007', 'Mango', 'Fruits', 'high', 60, 1.6, 0.4, 0.8, 15.0, true, NOW()),

-- Vegetables
('650e8400-e29b-41d4-a716-446655440008', 'Broccoli', 'Vegetables', 'low', 34, 2.6, 0.4, 2.8, 7.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440009', 'Carrots', 'Vegetables', 'low', 41, 2.8, 0.2, 0.9, 10.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440010', 'Spinach', 'Vegetables', 'low', 23, 2.2, 0.4, 2.9, 3.6, false, NOW()),
('650e8400-e29b-41d4-a716-446655440011', 'Onion', 'Vegetables', 'high', 40, 1.7, 0.1, 1.1, 9.3, true, NOW()),
('650e8400-e29b-41d4-a716-446655440012', 'Garlic', 'Vegetables', 'high', 149, 2.1, 0.5, 6.4, 33.0, true, NOW()),
('650e8400-e29b-41d4-a716-446655440013', 'Bell Pepper', 'Vegetables', 'low', 31, 2.5, 0.3, 1.0, 7.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440014', 'Cauliflower', 'Vegetables', 'moderate', 25, 2.0, 0.3, 1.9, 5.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440015', 'Cabbage', 'Vegetables', 'moderate', 25, 2.5, 0.1, 1.3, 6.0, false, NOW()),

-- Grains
('650e8400-e29b-41d4-a716-446655440016', 'White Rice', 'Grains', 'low', 130, 0.4, 0.3, 2.7, 28.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440017', 'Brown Rice', 'Grains', 'low', 111, 1.8, 0.9, 2.6, 23.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440018', 'Oats', 'Grains', 'low', 389, 10.6, 6.9, 16.9, 66.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440019', 'Wheat Bread', 'Grains', 'high', 265, 2.7, 3.2, 9.0, 49.0, true, NOW()),
('650e8400-e29b-41d4-a716-446655440020', 'Quinoa', 'Grains', 'low', 368, 7.0, 6.1, 14.1, 64.0, false, NOW()),

-- Proteins
('650e8400-e29b-41d4-a716-446655440021', 'Chicken Breast', 'Proteins', 'low', 165, 0.0, 3.6, 31.0, 0.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440022', 'Salmon', 'Proteins', 'low', 208, 0.0, 12.4, 22.1, 0.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440023', 'Eggs', 'Proteins', 'low', 155, 0.0, 11.0, 13.0, 1.1, false, NOW()),
('650e8400-e29b-41d4-a716-446655440024', 'Tofu', 'Proteins', 'low', 76, 0.9, 4.8, 8.1, 1.9, false, NOW()),
('650e8400-e29b-41d4-a716-446655440025', 'Beans (Black)', 'Proteins', 'high', 132, 8.7, 0.5, 8.9, 23.0, true, NOW()),
('650e8400-e29b-41d4-a716-446655440026', 'Lentils', 'Proteins', 'high', 116, 7.9, 0.4, 9.0, 20.0, true, NOW()),

-- Dairy
('650e8400-e29b-41d4-a716-446655440027', 'Milk (Whole)', 'Dairy', 'high', 61, 0.0, 3.3, 3.2, 4.8, true, NOW()),
('650e8400-e29b-41d4-a716-446655440028', 'Lactose-Free Milk', 'Dairy', 'low', 50, 0.0, 1.5, 3.4, 5.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440029', 'Cheddar Cheese', 'Dairy', 'low', 403, 0.0, 33.0, 25.0, 1.3, false, NOW()),
('650e8400-e29b-41d4-a716-446655440030', 'Greek Yogurt', 'Dairy', 'moderate', 59, 0.0, 0.4, 10.0, 3.6, false, NOW()),

-- Nuts and Seeds
('650e8400-e29b-41d4-a716-446655440031', 'Almonds', 'Nuts', 'moderate', 579, 12.5, 49.9, 21.2, 22.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440032', 'Walnuts', 'Nuts', 'low', 654, 6.7, 65.2, 15.2, 14.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440033', 'Peanuts', 'Nuts', 'low', 567, 8.5, 49.2, 25.8, 16.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440034', 'Chia Seeds', 'Seeds', 'low', 486, 34.4, 30.7, 16.5, 42.0, false, NOW()),

-- Beverages
('650e8400-e29b-41d4-a716-446655440035', 'Coffee', 'Beverages', 'low', 2, 0.0, 0.0, 0.3, 0.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440036', 'Green Tea', 'Beverages', 'low', 1, 0.0, 0.0, 0.0, 0.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440037', 'Orange Juice', 'Beverages', 'moderate', 45, 0.2, 0.2, 0.7, 10.4, false, NOW()),

-- Processed Foods
('650e8400-e29b-41d4-a716-446655440038', 'Pizza', 'Processed', 'high', 266, 2.3, 10.4, 11.0, 33.0, true, NOW()),
('650e8400-e29b-41d4-a716-446655440039', 'Ice Cream', 'Processed', 'high', 207, 0.7, 11.0, 3.5, 24.0, true, NOW()),
('650e8400-e29b-41d4-a716-446655440040', 'Dark Chocolate', 'Processed', 'low', 546, 7.0, 31.0, 4.9, 61.0, false, NOW());