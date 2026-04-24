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
('650e8400-e29b-41d4-a716-446655440040', 'Dark Chocolate', 'Processed', 'low', 546, 7.0, 31.0, 4.9, 61.0, false, NOW()),

-- Indian Rice Dishes
('650e8400-e29b-41d4-a716-446655440041', 'Plain Rice', 'Indian Rice', 'low', 130, 0.4, 0.3, 2.7, 28.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440042', 'Jeera Rice', 'Indian Rice', 'low', 142, 0.6, 3.2, 2.8, 28.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440043', 'Lemon Rice', 'Indian Rice', 'low', 148, 0.8, 3.8, 2.9, 28.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440044', 'Curd Rice', 'Indian Rice', 'moderate', 135, 0.8, 2.5, 4.2, 26.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440045', 'Coconut Rice', 'Indian Rice', 'low', 165, 1.2, 6.8, 3.5, 25.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440046', 'Vegetable Pulao', 'Indian Rice', 'moderate', 158, 1.5, 4.0, 3.8, 27.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440047', 'Chicken Biryani', 'Indian Rice', 'high', 185, 0.8, 6.5, 12.0, 23.0, true, NOW()),
('650e8400-e29b-41d4-a716-446655440048', 'Vegetable Biryani', 'Indian Rice', 'high', 165, 2.1, 5.2, 4.8, 28.0, true, NOW()),

-- Indian Dal (Lentils)
('650e8400-e29b-41d4-a716-446655440049', 'Moong Dal', 'Indian Dal', 'low', 105, 8.2, 0.4, 7.0, 19.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440050', 'Masoor Dal', 'Indian Dal', 'moderate', 116, 7.9, 0.4, 9.0, 20.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440051', 'Toor Dal', 'Indian Dal', 'low', 118, 5.8, 0.7, 8.2, 22.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440052', 'Chana Dal', 'Indian Dal', 'moderate', 160, 9.9, 2.6, 8.9, 27.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440053', 'Urad Dal', 'Indian Dal', 'moderate', 341, 18.3, 1.6, 25.2, 58.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440054', 'Dal Tadka', 'Indian Dal', 'low', 125, 6.5, 3.2, 8.5, 18.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440055', 'Dal Fry', 'Indian Dal', 'moderate', 135, 7.2, 4.8, 8.8, 17.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440056', 'Sambhar', 'Indian Dal', 'high', 95, 4.2, 2.8, 6.5, 15.0, true, NOW()),

-- Indian Vegetables
('650e8400-e29b-41d4-a716-446655440057', 'Palak Paneer', 'Indian Vegetables', 'low', 120, 2.9, 8.5, 7.2, 6.8, false, NOW()),
('650e8400-e29b-41d4-a716-446655440058', 'Aloo Gobi', 'Indian Vegetables', 'moderate', 85, 2.8, 3.2, 2.5, 14.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440059', 'Bhindi Masala', 'Indian Vegetables', 'low', 65, 3.2, 2.8, 2.0, 11.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440060', 'Baingan Bharta', 'Indian Vegetables', 'low', 75, 3.0, 4.2, 1.8, 9.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440061', 'Lauki Sabzi', 'Indian Vegetables', 'low', 45, 2.5, 1.8, 1.2, 8.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440062', 'Turai Sabzi', 'Indian Vegetables', 'low', 42, 2.8, 1.5, 1.5, 7.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440063', 'Karela Sabzi', 'Indian Vegetables', 'low', 38, 2.6, 0.8, 1.8, 7.2, false, NOW()),
('650e8400-e29b-41d4-a716-446655440064', 'Methi Sabzi', 'Indian Vegetables', 'low', 55, 4.2, 1.2, 4.4, 8.5, false, NOW()),

-- Indian Breads
('650e8400-e29b-41d4-a716-446655440065', 'Chapati', 'Indian Breads', 'high', 297, 2.7, 3.7, 11.0, 58.0, true, NOW()),
('650e8400-e29b-41d4-a716-446655440066', 'Naan', 'Indian Breads', 'high', 310, 2.2, 9.5, 9.2, 50.0, true, NOW()),
('650e8400-e29b-41d4-a716-446655440067', 'Paratha', 'Indian Breads', 'high', 320, 3.1, 12.8, 8.5, 45.0, true, NOW()),
('650e8400-e29b-41d4-a716-446655440068', 'Roti', 'Indian Breads', 'high', 295, 2.8, 3.2, 10.8, 57.0, true, NOW()),
('650e8400-e29b-41d4-a716-446655440069', 'Missi Roti', 'Indian Breads', 'moderate', 285, 4.5, 4.2, 12.5, 52.0, false, NOW()),

-- South Indian Dishes
('650e8400-e29b-41d4-a716-446655440070', 'Idli', 'South Indian', 'low', 58, 1.2, 0.3, 2.5, 12.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440071', 'Dosa', 'South Indian', 'low', 168, 1.5, 3.8, 4.2, 32.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440072', 'Uttapam', 'South Indian', 'low', 145, 1.8, 2.5, 3.8, 28.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440073', 'Vada', 'South Indian', 'moderate', 285, 3.2, 18.5, 8.5, 22.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440074', 'Rasam', 'South Indian', 'low', 35, 1.8, 0.8, 1.2, 6.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440075', 'Upma', 'South Indian', 'low', 85, 1.9, 2.2, 2.8, 16.0, false, NOW()),

-- Indian Snacks
('650e8400-e29b-41d4-a716-446655440076', 'Dhokla', 'Indian Snacks', 'moderate', 160, 2.1, 4.5, 4.8, 28.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440077', 'Poha', 'Indian Snacks', 'low', 158, 1.3, 2.8, 3.2, 32.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440078', 'Khichdi', 'Indian Snacks', 'low', 120, 2.5, 2.2, 4.5, 22.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440079', 'Samosa', 'Indian Snacks', 'high', 308, 3.8, 17.8, 6.2, 32.0, true, NOW()),
('650e8400-e29b-41d4-a716-446655440080', 'Pakora', 'Indian Snacks', 'moderate', 285, 2.8, 18.2, 5.5, 25.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440081', 'Kachori', 'Indian Snacks', 'high', 420, 4.2, 28.5, 8.8, 35.0, true, NOW()),

-- Indian Dairy & Beverages
('650e8400-e29b-41d4-a716-446655440082', 'Lassi', 'Indian Dairy', 'moderate', 85, 0.1, 2.8, 3.5, 12.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440083', 'Buttermilk', 'Indian Dairy', 'low', 40, 0.1, 0.9, 3.1, 4.8, false, NOW()),
('650e8400-e29b-41d4-a716-446655440084', 'Paneer', 'Indian Dairy', 'low', 265, 0.0, 20.8, 18.3, 1.2, false, NOW()),
('650e8400-e29b-41d4-a716-446655440085', 'Chai', 'Indian Beverages', 'low', 45, 0.0, 1.8, 1.5, 6.2, false, NOW()),
('650e8400-e29b-41d4-a716-446655440086', 'Masala Chai', 'Indian Beverages', 'low', 52, 0.2, 2.2, 1.8, 7.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440087', 'Nimbu Paani', 'Indian Beverages', 'low', 25, 0.1, 0.0, 0.2, 6.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440088', 'Coconut Water', 'Indian Beverages', 'low', 19, 1.1, 0.2, 0.7, 3.7, false, NOW()),

-- Indian Sweets (Limited for IBS)
('650e8400-e29b-41d4-a716-446655440089', 'Kheer', 'Indian Sweets', 'moderate', 185, 0.8, 6.2, 4.5, 28.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440090', 'Halwa', 'Indian Sweets', 'moderate', 420, 2.5, 18.5, 6.8, 58.0, false, NOW()),

-- Indian Spices & Condiments
('650e8400-e29b-41d4-a716-446655440091', 'Turmeric', 'Indian Spices', 'low', 312, 22.7, 3.2, 9.7, 67.1, false, NOW()),
('650e8400-e29b-41d4-a716-446655440092', 'Cumin', 'Indian Spices', 'low', 375, 10.5, 22.3, 17.8, 44.2, false, NOW()),
('650e8400-e29b-41d4-a716-446655440093', 'Coriander', 'Indian Spices', 'low', 298, 41.9, 17.8, 12.4, 54.2, false, NOW()),
('650e8400-e29b-41d4-a716-446655440094', 'Ginger', 'Indian Spices', 'low', 80, 2.0, 0.8, 1.8, 18.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440095', 'Mint Chutney', 'Indian Condiments', 'low', 45, 2.8, 0.8, 2.2, 8.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440096', 'Coconut Chutney', 'Indian Condiments', 'low', 185, 9.0, 18.3, 2.0, 6.2, false, NOW()),
('650e8400-e29b-41d4-a716-446655440097', 'Pickle (Achar)', 'Indian Condiments', 'high', 125, 3.2, 8.5, 1.8, 12.0, true, NOW()),

-- Regional Specialties
('650e8400-e29b-41d4-a716-446655440098', 'Rajma', 'North Indian', 'high', 127, 6.4, 0.5, 8.7, 22.8, true, NOW()),
('650e8400-e29b-41d4-a716-446655440099', 'Chole', 'North Indian', 'high', 164, 7.6, 2.6, 8.9, 27.4, true, NOW()),
('650e8400-e29b-41d4-a716-446655440100', 'Pongal', 'South Indian', 'low', 145, 1.8, 3.2, 4.5, 26.0, false, NOW()),

-- Additional North Indian Dishes
('650e8400-e29b-41d4-a716-446655440101', 'Butter Chicken', 'North Indian', 'moderate', 285, 1.2, 22.5, 18.5, 8.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440102', 'Chicken Tikka Masala', 'North Indian', 'moderate', 265, 1.8, 18.2, 20.8, 12.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440103', 'Paneer Makhani', 'North Indian', 'low', 245, 1.5, 18.8, 12.5, 9.2, false, NOW()),
('650e8400-e29b-41d4-a716-446655440104', 'Aloo Matar', 'North Indian', 'low', 95, 3.2, 2.8, 3.5, 16.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440105', 'Saag Paneer', 'North Indian', 'low', 135, 3.8, 9.5, 8.2, 7.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440106', 'Dal Makhani', 'North Indian', 'moderate', 185, 5.8, 8.5, 9.2, 22.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440107', 'Kadhi Pakora', 'North Indian', 'moderate', 165, 2.8, 8.2, 6.5, 18.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440108', 'Stuffed Paratha', 'North Indian', 'high', 385, 4.2, 15.8, 12.5, 52.0, true, NOW()),

-- Additional South Indian Dishes
('650e8400-e29b-41d4-a716-446655440109', 'Medu Vada', 'South Indian', 'moderate', 295, 3.5, 19.2, 9.8, 24.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440110', 'Rava Dosa', 'South Indian', 'low', 185, 2.2, 4.8, 5.2, 35.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440111', 'Coconut Chutney', 'South Indian', 'low', 195, 9.2, 19.5, 2.8, 7.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440112', 'Tomato Rice', 'South Indian', 'low', 155, 1.5, 4.2, 3.8, 28.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440113', 'Bisi Bele Bath', 'South Indian', 'moderate', 165, 3.2, 5.8, 6.5, 26.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440114', 'Mysore Pak', 'South Indian', 'moderate', 485, 1.2, 28.5, 6.8, 52.0, false, NOW()),
('650e8400-e29b-41d4-a716-446655440115', 'Filter Coffee', 'South Indian', 'low', 8, 0.0, 0.2, 0.5, 1.2, false, NOW()),

-- West Indian Dishes
('650e8400-e29b-41d4-a716-446655440116', 'Gujarati Thali', 'West Indian', 'moderate', 285, 8.5, 12.5, 12.8, 38.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440117', 'Pav Bhaji', 'West Indian', 'high', 195, 4.2, 8.5, 6.8, 26.5, true, NOW()),
('650e8400-e29b-41d4-a716-446655440118', 'Vada Pav', 'West Indian', 'high', 285, 3.8, 12.5, 8.2, 38.5, true, NOW()),
('650e8400-e29b-41d4-a716-446655440119', 'Bhel Puri', 'West Indian', 'moderate', 165, 3.5, 6.8, 5.2, 24.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440120', 'Khandvi', 'West Indian', 'low', 125, 2.8, 4.5, 6.8, 16.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440121', 'Undhiyu', 'West Indian', 'moderate', 145, 5.2, 6.8, 5.5, 18.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440122', 'Handvo', 'West Indian', 'moderate', 185, 4.2, 8.5, 7.2, 22.5, false, NOW()),

-- East Indian Dishes
('650e8400-e29b-41d4-a716-446655440123', 'Fish Curry Bengali', 'East Indian', 'low', 165, 1.8, 8.5, 18.5, 6.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440124', 'Luchi', 'East Indian', 'high', 385, 2.5, 18.5, 8.8, 48.5, true, NOW()),
('650e8400-e29b-41d4-a716-446655440125', 'Mishti Doi', 'East Indian', 'moderate', 125, 0.2, 4.8, 4.5, 18.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440126', 'Kosha Mangsho', 'East Indian', 'moderate', 285, 2.2, 18.5, 22.8, 8.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440127', 'Aloo Posto', 'East Indian', 'low', 165, 3.2, 8.5, 4.8, 18.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440128', 'Chingri Malai Curry', 'East Indian', 'low', 195, 1.5, 12.5, 16.8, 6.5, false, NOW()),

-- Traditional Indian Breakfast Items
('650e8400-e29b-41d4-a716-446655440129', 'Aloo Paratha', 'Indian Breakfast', 'moderate', 295, 3.8, 12.5, 8.5, 38.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440130', 'Methi Paratha', 'Indian Breakfast', 'low', 285, 5.2, 11.5, 9.8, 36.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440131', 'Besan Chilla', 'Indian Breakfast', 'low', 165, 4.8, 6.5, 8.8, 18.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440132', 'Rava Upma', 'Indian Breakfast', 'low', 95, 2.2, 2.8, 3.5, 16.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440133', 'Vermicelli Upma', 'Indian Breakfast', 'low', 105, 1.8, 3.2, 3.8, 18.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440134', 'Masala Oats', 'Indian Breakfast', 'low', 125, 4.5, 3.8, 5.2, 22.5, false, NOW()),

-- Indian Street Food (IBS-Friendly Options)
('650e8400-e29b-41d4-a716-446655440135', 'Corn Chaat', 'Indian Street Food', 'low', 125, 3.8, 2.5, 4.8, 24.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440136', 'Cucumber Chaat', 'Indian Street Food', 'low', 45, 2.8, 0.8, 1.5, 8.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440137', 'Sprouts Chaat', 'Indian Street Food', 'moderate', 95, 4.2, 1.8, 6.8, 16.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440138', 'Fruit Chaat', 'Indian Street Food', 'low', 65, 2.5, 0.5, 1.2, 15.5, false, NOW()),

-- Traditional Indian Desserts (IBS-Friendly)
('650e8400-e29b-41d4-a716-446655440139', 'Rice Kheer', 'Indian Desserts', 'moderate', 165, 0.8, 5.2, 4.8, 26.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440140', 'Carrot Halwa', 'Indian Desserts', 'low', 285, 3.2, 12.5, 6.8, 38.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440141', 'Coconut Laddu', 'Indian Desserts', 'low', 385, 8.5, 28.5, 4.8, 28.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440142', 'Banana Sheera', 'Indian Desserts', 'low', 195, 2.2, 6.8, 3.5, 32.5, false, NOW()),

-- Indian Beverages
('650e8400-e29b-41d4-a716-446655440143', 'Aam Panna', 'Indian Beverages', 'low', 45, 0.8, 0.2, 0.5, 11.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440144', 'Jaljeera', 'Indian Beverages', 'low', 25, 1.2, 0.2, 0.8, 5.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440145', 'Kokum Sharbat', 'Indian Beverages', 'low', 35, 1.5, 0.2, 0.5, 8.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440146', 'Thandai', 'Indian Beverages', 'moderate', 185, 2.8, 12.5, 6.8, 15.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440147', 'Sattu Drink', 'Indian Beverages', 'low', 85, 3.2, 1.8, 6.8, 14.5, false, NOW()),

-- Indian Fermented Foods (Probiotic-Rich)
('650e8400-e29b-41d4-a716-446655440148', 'Idli Sambhar', 'Indian Fermented', 'moderate', 125, 3.2, 2.8, 5.5, 22.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440149', 'Dosa with Chutney', 'Indian Fermented', 'low', 185, 2.8, 5.2, 5.8, 32.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440150', 'Fermented Rice', 'Indian Fermented', 'low', 145, 1.2, 2.8, 3.5, 28.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440151', 'Kanji', 'Indian Fermented', 'moderate', 45, 2.8, 0.5, 1.8, 8.5, false, NOW()),

-- Indian Healthy Snacks
('650e8400-e29b-41d4-a716-446655440152', 'Roasted Chana', 'Indian Healthy Snacks', 'moderate', 385, 12.5, 6.8, 18.5, 58.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440153', 'Makhana', 'Indian Healthy Snacks', 'low', 347, 14.5, 0.1, 9.7, 76.9, false, NOW()),
('650e8400-e29b-41d4-a716-446655440154', 'Murmura Chivda', 'Indian Healthy Snacks', 'low', 385, 2.8, 12.5, 8.5, 68.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440155', 'Til Laddu', 'Indian Healthy Snacks', 'low', 485, 11.8, 38.5, 18.5, 22.5, false, NOW()),

-- Indian Soups and Broths
('650e8400-e29b-41d4-a716-446655440156', 'Tomato Soup', 'Indian Soups', 'low', 45, 1.8, 1.2, 2.5, 8.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440157', 'Vegetable Clear Soup', 'Indian Soups', 'low', 35, 2.2, 0.8, 1.8, 6.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440158', 'Chicken Soup', 'Indian Soups', 'low', 85, 1.2, 2.8, 8.5, 6.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440159', 'Bone Broth', 'Indian Soups', 'low', 45, 0.0, 1.8, 6.8, 2.5, false, NOW()),
('650e8400-e29b-41d4-a716-446655440160', 'Moong Dal Soup', 'Indian Soups', 'low', 65, 4.2, 0.8, 5.5, 11.5, false, NOW());