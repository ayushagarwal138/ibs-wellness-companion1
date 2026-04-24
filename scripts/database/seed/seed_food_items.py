"""
Script to seed food items data into the database.
"""

import asyncio
import uuid
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.models.food_item import FoodItem


async def seed_food_items():
    """Seed food items data."""
    
    # Sample food items data
    foods = [
        {'id': '650e8400-e29b-41d4-a716-446655440001', 'name': 'Apple', 'category': 'Fruits', 'fodmap_level': 'high', 'calories_per_100g': 52, 'fiber_per_100g': 2.4, 'fat_per_100g': 0.2, 'protein_per_100g': 0.3, 'carbs_per_100g': 14.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440002', 'name': 'Banana', 'category': 'Fruits', 'fodmap_level': 'low', 'calories_per_100g': 89, 'fiber_per_100g': 2.6, 'fat_per_100g': 0.3, 'protein_per_100g': 1.1, 'carbs_per_100g': 23.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440003', 'name': 'Orange', 'category': 'Fruits', 'fodmap_level': 'low', 'calories_per_100g': 47, 'fiber_per_100g': 2.4, 'fat_per_100g': 0.1, 'protein_per_100g': 0.9, 'carbs_per_100g': 12.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440004', 'name': 'Grapes', 'category': 'Fruits', 'fodmap_level': 'low', 'calories_per_100g': 62, 'fiber_per_100g': 0.9, 'fat_per_100g': 0.2, 'protein_per_100g': 0.6, 'carbs_per_100g': 16.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440005', 'name': 'Strawberries', 'category': 'Fruits', 'fodmap_level': 'low', 'calories_per_100g': 32, 'fiber_per_100g': 2.0, 'fat_per_100g': 0.3, 'protein_per_100g': 0.7, 'carbs_per_100g': 8.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440008', 'name': 'Broccoli', 'category': 'Vegetables', 'fodmap_level': 'low', 'calories_per_100g': 34, 'fiber_per_100g': 2.6, 'fat_per_100g': 0.4, 'protein_per_100g': 2.8, 'carbs_per_100g': 7.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440009', 'name': 'Carrots', 'category': 'Vegetables', 'fodmap_level': 'low', 'calories_per_100g': 41, 'fiber_per_100g': 2.8, 'fat_per_100g': 0.2, 'protein_per_100g': 0.9, 'carbs_per_100g': 10.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440010', 'name': 'Spinach', 'category': 'Vegetables', 'fodmap_level': 'low', 'calories_per_100g': 23, 'fiber_per_100g': 2.2, 'fat_per_100g': 0.4, 'protein_per_100g': 2.9, 'carbs_per_100g': 3.6, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440011', 'name': 'Onion', 'category': 'Vegetables', 'fodmap_level': 'high', 'calories_per_100g': 40, 'fiber_per_100g': 1.7, 'fat_per_100g': 0.1, 'protein_per_100g': 1.1, 'carbs_per_100g': 9.3, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440016', 'name': 'White Rice', 'category': 'Grains', 'fodmap_level': 'low', 'calories_per_100g': 130, 'fiber_per_100g': 0.4, 'fat_per_100g': 0.3, 'protein_per_100g': 2.7, 'carbs_per_100g': 28.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440017', 'name': 'Brown Rice', 'category': 'Grains', 'fodmap_level': 'low', 'calories_per_100g': 111, 'fiber_per_100g': 1.8, 'fat_per_100g': 0.9, 'protein_per_100g': 2.6, 'carbs_per_100g': 23.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440018', 'name': 'Oats', 'category': 'Grains', 'fodmap_level': 'low', 'calories_per_100g': 389, 'fiber_per_100g': 10.6, 'fat_per_100g': 6.9, 'protein_per_100g': 16.9, 'carbs_per_100g': 66.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440021', 'name': 'Chicken Breast', 'category': 'Proteins', 'fodmap_level': 'low', 'calories_per_100g': 165, 'fiber_per_100g': 0.0, 'fat_per_100g': 3.6, 'protein_per_100g': 31.0, 'carbs_per_100g': 0.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440022', 'name': 'Salmon', 'category': 'Proteins', 'fodmap_level': 'low', 'calories_per_100g': 208, 'fiber_per_100g': 0.0, 'fat_per_100g': 12.4, 'protein_per_100g': 22.1, 'carbs_per_100g': 0.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440023', 'name': 'Eggs', 'category': 'Proteins', 'fodmap_level': 'low', 'calories_per_100g': 155, 'fiber_per_100g': 0.0, 'fat_per_100g': 11.0, 'protein_per_100g': 13.0, 'carbs_per_100g': 1.1, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440024', 'name': 'Tofu', 'category': 'Proteins', 'fodmap_level': 'low', 'calories_per_100g': 76, 'fiber_per_100g': 0.9, 'fat_per_100g': 4.8, 'protein_per_100g': 8.1, 'carbs_per_100g': 1.9, 'common_triggers': False},
        
        # Breakfast Dishes
        {'id': '650e8400-e29b-41d4-a716-446655440025', 'name': 'Pancakes', 'category': 'Breakfast', 'fodmap_level': 'medium', 'calories_per_100g': 227, 'fiber_per_100g': 1.5, 'fat_per_100g': 9.0, 'protein_per_100g': 6.0, 'carbs_per_100g': 28.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440026', 'name': 'Scrambled Eggs', 'category': 'Breakfast', 'fodmap_level': 'low', 'calories_per_100g': 168, 'fiber_per_100g': 0.0, 'fat_per_100g': 12.0, 'protein_per_100g': 14.0, 'carbs_per_100g': 1.5, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440027', 'name': 'French Toast', 'category': 'Breakfast', 'fodmap_level': 'medium', 'calories_per_100g': 166, 'fiber_per_100g': 1.2, 'fat_per_100g': 7.0, 'protein_per_100g': 6.0, 'carbs_per_100g': 20.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440028', 'name': 'Omelette', 'category': 'Breakfast', 'fodmap_level': 'low', 'calories_per_100g': 154, 'fiber_per_100g': 0.2, 'fat_per_100g': 11.0, 'protein_per_100g': 11.0, 'carbs_per_100g': 2.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440029', 'name': 'Cereal with Milk', 'category': 'Breakfast', 'fodmap_level': 'medium', 'calories_per_100g': 379, 'fiber_per_100g': 7.0, 'fat_per_100g': 4.0, 'protein_per_100g': 8.0, 'carbs_per_100g': 84.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440030', 'name': 'Toast with Butter', 'category': 'Breakfast', 'fodmap_level': 'medium', 'calories_per_100g': 313, 'fiber_per_100g': 2.3, 'fat_per_100g': 5.0, 'protein_per_100g': 9.0, 'carbs_per_100g': 58.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440031', 'name': 'Waffles', 'category': 'Breakfast', 'fodmap_level': 'medium', 'calories_per_100g': 291, 'fiber_per_100g': 1.5, 'fat_per_100g': 8.0, 'protein_per_100g': 7.0, 'carbs_per_100g': 48.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440032', 'name': 'Bagel with Cream Cheese', 'category': 'Breakfast', 'fodmap_level': 'medium', 'calories_per_100g': 277, 'fiber_per_100g': 1.7, 'fat_per_100g': 5.0, 'protein_per_100g': 11.0, 'carbs_per_100g': 53.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440033', 'name': 'Yogurt with Granola', 'category': 'Breakfast', 'fodmap_level': 'medium', 'calories_per_100g': 134, 'fiber_per_100g': 2.0, 'fat_per_100g': 3.5, 'protein_per_100g': 7.0, 'carbs_per_100g': 19.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440034', 'name': 'Smoothie Bowl', 'category': 'Breakfast', 'fodmap_level': 'medium', 'calories_per_100g': 89, 'fiber_per_100g': 3.0, 'fat_per_100g': 1.5, 'protein_per_100g': 2.0, 'carbs_per_100g': 20.0, 'common_triggers': False},
        
        # Lunch/Dinner Dishes
        {'id': '650e8400-e29b-41d4-a716-446655440035', 'name': 'Spaghetti Bolognese', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 131, 'fiber_per_100g': 1.8, 'fat_per_100g': 4.9, 'protein_per_100g': 6.1, 'carbs_per_100g': 16.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440036', 'name': 'Margherita Pizza', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 266, 'fiber_per_100g': 2.3, 'fat_per_100g': 10.0, 'protein_per_100g': 12.0, 'carbs_per_100g': 33.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440037', 'name': 'Cheeseburger', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 295, 'fiber_per_100g': 2.1, 'fat_per_100g': 14.0, 'protein_per_100g': 17.0, 'carbs_per_100g': 25.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440038', 'name': 'Caesar Salad', 'category': 'Salads', 'fodmap_level': 'medium', 'calories_per_100g': 158, 'fiber_per_100g': 2.3, 'fat_per_100g': 13.0, 'protein_per_100g': 7.0, 'carbs_per_100g': 5.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440039', 'name': 'Chicken Noodle Soup', 'category': 'Soups', 'fodmap_level': 'medium', 'calories_per_100g': 62, 'fiber_per_100g': 0.5, 'fat_per_100g': 2.0, 'protein_per_100g': 3.0, 'carbs_per_100g': 8.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440040', 'name': 'Fish and Chips', 'category': 'Main Course', 'fodmap_level': 'medium', 'calories_per_100g': 232, 'fiber_per_100g': 2.2, 'fat_per_100g': 11.0, 'protein_per_100g': 13.0, 'carbs_per_100g': 22.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440041', 'name': 'Stir Fry', 'category': 'Main Course', 'fodmap_level': 'low', 'calories_per_100g': 112, 'fiber_per_100g': 2.8, 'fat_per_100g': 4.0, 'protein_per_100g': 8.0, 'carbs_per_100g': 12.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440042', 'name': 'Grilled Chicken Salad', 'category': 'Salads', 'fodmap_level': 'low', 'calories_per_100g': 128, 'fiber_per_100g': 2.1, 'fat_per_100g': 3.0, 'protein_per_100g': 20.0, 'carbs_per_100g': 6.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440043', 'name': 'Beef Tacos', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 226, 'fiber_per_100g': 3.1, 'fat_per_100g': 11.0, 'protein_per_100g': 13.0, 'carbs_per_100g': 20.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440044', 'name': 'Vegetable Curry', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 93, 'fiber_per_100g': 3.2, 'fat_per_100g': 4.0, 'protein_per_100g': 3.0, 'carbs_per_100g': 12.0, 'common_triggers': True},
        
        # Snacks
        {'id': '650e8400-e29b-41d4-a716-446655440045', 'name': 'Potato Chips', 'category': 'Snacks', 'fodmap_level': 'low', 'calories_per_100g': 536, 'fiber_per_100g': 4.8, 'fat_per_100g': 35.0, 'protein_per_100g': 6.0, 'carbs_per_100g': 50.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440046', 'name': 'Mixed Nuts', 'category': 'Snacks', 'fodmap_level': 'medium', 'calories_per_100g': 607, 'fiber_per_100g': 8.0, 'fat_per_100g': 54.0, 'protein_per_100g': 20.0, 'carbs_per_100g': 13.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440047', 'name': 'Crackers', 'category': 'Snacks', 'fodmap_level': 'medium', 'calories_per_100g': 502, 'fiber_per_100g': 2.1, 'fat_per_100g': 25.0, 'protein_per_100g': 6.0, 'carbs_per_100g': 62.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440048', 'name': 'Greek Yogurt', 'category': 'Snacks', 'fodmap_level': 'medium', 'calories_per_100g': 97, 'fiber_per_100g': 0.0, 'fat_per_100g': 5.0, 'protein_per_100g': 9.0, 'carbs_per_100g': 6.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440049', 'name': 'Popcorn', 'category': 'Snacks', 'fodmap_level': 'low', 'calories_per_100g': 387, 'fiber_per_100g': 14.5, 'fat_per_100g': 5.0, 'protein_per_100g': 12.0, 'carbs_per_100g': 78.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440050', 'name': 'Cheese and Crackers', 'category': 'Snacks', 'fodmap_level': 'medium', 'calories_per_100g': 491, 'fiber_per_100g': 2.0, 'fat_per_100g': 32.0, 'protein_per_100g': 18.0, 'carbs_per_100g': 38.0, 'common_triggers': True},
        
        # Desserts
        {'id': '650e8400-e29b-41d4-a716-446655440051', 'name': 'Chocolate Ice Cream', 'category': 'Desserts', 'fodmap_level': 'high', 'calories_per_100g': 216, 'fiber_per_100g': 1.2, 'fat_per_100g': 11.0, 'protein_per_100g': 3.8, 'carbs_per_100g': 28.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440052', 'name': 'Chocolate Chip Cookies', 'category': 'Desserts', 'fodmap_level': 'high', 'calories_per_100g': 488, 'fiber_per_100g': 2.0, 'fat_per_100g': 21.0, 'protein_per_100g': 5.0, 'carbs_per_100g': 71.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440053', 'name': 'Cheesecake', 'category': 'Desserts', 'fodmap_level': 'high', 'calories_per_100g': 321, 'fiber_per_100g': 0.8, 'fat_per_100g': 23.0, 'protein_per_100g': 5.5, 'carbs_per_100g': 25.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440054', 'name': 'Apple Pie', 'category': 'Desserts', 'fodmap_level': 'high', 'calories_per_100g': 237, 'fiber_per_100g': 1.6, 'fat_per_100g': 11.0, 'protein_per_100g': 2.0, 'carbs_per_100g': 34.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440055', 'name': 'Dark Chocolate', 'category': 'Desserts', 'fodmap_level': 'medium', 'calories_per_100g': 546, 'fiber_per_100g': 10.9, 'fat_per_100g': 31.0, 'protein_per_100g': 7.8, 'carbs_per_100g': 61.0, 'common_triggers': False},
        
        # Indian Main Dishes - Rice Based
        {'id': '650e8400-e29b-41d4-a716-446655440100', 'name': 'Biryani (Chicken)', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 185, 'fiber_per_100g': 1.2, 'fat_per_100g': 6.8, 'protein_per_100g': 12.5, 'carbs_per_100g': 22.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440101', 'name': 'Biryani (Mutton)', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 210, 'fiber_per_100g': 1.3, 'fat_per_100g': 9.2, 'protein_per_100g': 14.8, 'carbs_per_100g': 20.5, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440102', 'name': 'Vegetable Biryani', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 165, 'fiber_per_100g': 2.8, 'fat_per_100g': 5.5, 'protein_per_100g': 4.2, 'carbs_per_100g': 28.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440103', 'name': 'Pulao (Vegetable)', 'category': 'Main Course', 'fodmap_level': 'medium', 'calories_per_100g': 142, 'fiber_per_100g': 1.8, 'fat_per_100g': 4.2, 'protein_per_100g': 3.5, 'carbs_per_100g': 24.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440104', 'name': 'Jeera Rice', 'category': 'Main Course', 'fodmap_level': 'low', 'calories_per_100g': 138, 'fiber_per_100g': 0.6, 'fat_per_100g': 3.2, 'protein_per_100g': 2.8, 'carbs_per_100g': 26.5, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440105', 'name': 'Lemon Rice', 'category': 'Main Course', 'fodmap_level': 'low', 'calories_per_100g': 145, 'fiber_per_100g': 0.8, 'fat_per_100g': 3.8, 'protein_per_100g': 2.9, 'carbs_per_100g': 27.0, 'common_triggers': False},
        
        # Indian Curries and Gravies
        {'id': '650e8400-e29b-41d4-a716-446655440106', 'name': 'Butter Chicken', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 180, 'fiber_per_100g': 1.2, 'fat_per_100g': 12.5, 'protein_per_100g': 15.8, 'carbs_per_100g': 6.2, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440107', 'name': 'Chicken Tikka Masala', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 175, 'fiber_per_100g': 1.5, 'fat_per_100g': 11.2, 'protein_per_100g': 16.5, 'carbs_per_100g': 7.8, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440108', 'name': 'Dal Tadka', 'category': 'Main Course', 'fodmap_level': 'medium', 'calories_per_100g': 108, 'fiber_per_100g': 4.2, 'fat_per_100g': 3.8, 'protein_per_100g': 8.5, 'carbs_per_100g': 12.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440109', 'name': 'Dal Makhani', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 145, 'fiber_per_100g': 3.8, 'fat_per_100g': 8.2, 'protein_per_100g': 9.2, 'carbs_per_100g': 11.5, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440110', 'name': 'Rajma (Kidney Bean Curry)', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 125, 'fiber_per_100g': 6.2, 'fat_per_100g': 2.8, 'protein_per_100g': 8.8, 'carbs_per_100g': 18.5, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440111', 'name': 'Chole (Chickpea Curry)', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 135, 'fiber_per_100g': 5.8, 'fat_per_100g': 3.5, 'protein_per_100g': 7.2, 'carbs_per_100g': 20.2, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440112', 'name': 'Palak Paneer', 'category': 'Main Course', 'fodmap_level': 'medium', 'calories_per_100g': 155, 'fiber_per_100g': 2.8, 'fat_per_100g': 11.2, 'protein_per_100g': 8.5, 'carbs_per_100g': 6.8, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440113', 'name': 'Paneer Makhani', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 185, 'fiber_per_100g': 1.8, 'fat_per_100g': 14.5, 'protein_per_100g': 9.8, 'carbs_per_100g': 8.2, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440114', 'name': 'Aloo Gobi', 'category': 'Main Course', 'fodmap_level': 'medium', 'calories_per_100g': 85, 'fiber_per_100g': 3.2, 'fat_per_100g': 2.8, 'protein_per_100g': 2.5, 'carbs_per_100g': 15.2, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440115', 'name': 'Bhindi Masala', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 95, 'fiber_per_100g': 4.5, 'fat_per_100g': 4.2, 'protein_per_100g': 2.8, 'carbs_per_100g': 12.5, 'common_triggers': True},
        
        # Indian Breads
        {'id': '650e8400-e29b-41d4-a716-446655440116', 'name': 'Naan', 'category': 'Grains', 'fodmap_level': 'high', 'calories_per_100g': 310, 'fiber_per_100g': 2.2, 'fat_per_100g': 8.5, 'protein_per_100g': 9.2, 'carbs_per_100g': 52.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440117', 'name': 'Garlic Naan', 'category': 'Grains', 'fodmap_level': 'high', 'calories_per_100g': 325, 'fiber_per_100g': 2.5, 'fat_per_100g': 9.2, 'protein_per_100g': 9.8, 'carbs_per_100g': 53.5, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440118', 'name': 'Roti (Chapati)', 'category': 'Grains', 'fodmap_level': 'medium', 'calories_per_100g': 297, 'fiber_per_100g': 3.8, 'fat_per_100g': 3.2, 'protein_per_100g': 11.0, 'carbs_per_100g': 58.5, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440119', 'name': 'Paratha (Plain)', 'category': 'Grains', 'fodmap_level': 'medium', 'calories_per_100g': 320, 'fiber_per_100g': 3.5, 'fat_per_100g': 12.8, 'protein_per_100g': 8.5, 'carbs_per_100g': 45.2, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440120', 'name': 'Aloo Paratha', 'category': 'Grains', 'fodmap_level': 'medium', 'calories_per_100g': 285, 'fiber_per_100g': 4.2, 'fat_per_100g': 10.5, 'protein_per_100g': 7.8, 'carbs_per_100g': 42.5, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440121', 'name': 'Puri', 'category': 'Grains', 'fodmap_level': 'medium', 'calories_per_100g': 375, 'fiber_per_100g': 2.8, 'fat_per_100g': 18.5, 'protein_per_100g': 8.2, 'carbs_per_100g': 45.8, 'common_triggers': False},
        
        # South Indian Dishes
        {'id': '650e8400-e29b-41d4-a716-446655440122', 'name': 'Dosa (Plain)', 'category': 'Breakfast', 'fodmap_level': 'low', 'calories_per_100g': 168, 'fiber_per_100g': 1.8, 'fat_per_100g': 3.2, 'protein_per_100g': 4.5, 'carbs_per_100g': 32.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440123', 'name': 'Masala Dosa', 'category': 'Breakfast', 'fodmap_level': 'medium', 'calories_per_100g': 185, 'fiber_per_100g': 2.2, 'fat_per_100g': 4.8, 'protein_per_100g': 5.2, 'carbs_per_100g': 34.5, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440124', 'name': 'Idli', 'category': 'Breakfast', 'fodmap_level': 'low', 'calories_per_100g': 158, 'fiber_per_100g': 1.2, 'fat_per_100g': 1.8, 'protein_per_100g': 4.8, 'carbs_per_100g': 32.5, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440125', 'name': 'Vada', 'category': 'Snacks', 'fodmap_level': 'medium', 'calories_per_100g': 245, 'fiber_per_100g': 3.5, 'fat_per_100g': 12.8, 'protein_per_100g': 8.2, 'carbs_per_100g': 28.5, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440126', 'name': 'Uttapam', 'category': 'Breakfast', 'fodmap_level': 'medium', 'calories_per_100g': 175, 'fiber_per_100g': 2.8, 'fat_per_100g': 4.2, 'protein_per_100g': 5.5, 'carbs_per_100g': 31.2, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440127', 'name': 'Sambar', 'category': 'Main Course', 'fodmap_level': 'medium', 'calories_per_100g': 95, 'fiber_per_100g': 4.8, 'fat_per_100g': 2.5, 'protein_per_100g': 5.2, 'carbs_per_100g': 15.8, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440128', 'name': 'Rasam', 'category': 'Main Course', 'fodmap_level': 'medium', 'calories_per_100g': 45, 'fiber_per_100g': 1.8, 'fat_per_100g': 1.2, 'protein_per_100g': 2.2, 'carbs_per_100g': 8.5, 'common_triggers': False},
        
        # Indian Snacks and Street Food
        {'id': '650e8400-e29b-41d4-a716-446655440129', 'name': 'Samosa', 'category': 'Snacks', 'fodmap_level': 'high', 'calories_per_100g': 262, 'fiber_per_100g': 3.2, 'fat_per_100g': 13.8, 'protein_per_100g': 5.8, 'carbs_per_100g': 32.5, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440130', 'name': 'Pakora (Mixed Vegetable)', 'category': 'Snacks', 'fodmap_level': 'high', 'calories_per_100g': 285, 'fiber_per_100g': 4.5, 'fat_per_100g': 18.2, 'protein_per_100g': 6.8, 'carbs_per_100g': 25.5, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440131', 'name': 'Chaat (Bhel Puri)', 'category': 'Snacks', 'fodmap_level': 'high', 'calories_per_100g': 165, 'fiber_per_100g': 3.8, 'fat_per_100g': 5.2, 'protein_per_100g': 4.5, 'carbs_per_100g': 28.5, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440132', 'name': 'Pani Puri', 'category': 'Snacks', 'fodmap_level': 'high', 'calories_per_100g': 185, 'fiber_per_100g': 2.8, 'fat_per_100g': 6.5, 'protein_per_100g': 4.2, 'carbs_per_100g': 32.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440133', 'name': 'Dhokla', 'category': 'Snacks', 'fodmap_level': 'low', 'calories_per_100g': 160, 'fiber_per_100g': 2.5, 'fat_per_100g': 3.8, 'protein_per_100g': 6.2, 'carbs_per_100g': 28.5, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440134', 'name': 'Kachori', 'category': 'Snacks', 'fodmap_level': 'high', 'calories_per_100g': 315, 'fiber_per_100g': 4.2, 'fat_per_100g': 16.8, 'protein_per_100g': 7.5, 'carbs_per_100g': 38.5, 'common_triggers': True},
        
        # Indian Desserts
        {'id': '650e8400-e29b-41d4-a716-446655440135', 'name': 'Gulab Jamun', 'category': 'Desserts', 'fodmap_level': 'high', 'calories_per_100g': 387, 'fiber_per_100g': 1.2, 'fat_per_100g': 12.5, 'protein_per_100g': 6.8, 'carbs_per_100g': 65.2, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440136', 'name': 'Rasgulla', 'category': 'Desserts', 'fodmap_level': 'high', 'calories_per_100g': 186, 'fiber_per_100g': 0.5, 'fat_per_100g': 4.2, 'protein_per_100g': 7.5, 'carbs_per_100g': 35.8, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440137', 'name': 'Kheer (Rice Pudding)', 'category': 'Desserts', 'fodmap_level': 'high', 'calories_per_100g': 97, 'fiber_per_100g': 0.8, 'fat_per_100g': 2.8, 'protein_per_100g': 3.2, 'carbs_per_100g': 16.5, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440138', 'name': 'Halwa (Carrot)', 'category': 'Desserts', 'fodmap_level': 'high', 'calories_per_100g': 185, 'fiber_per_100g': 2.8, 'fat_per_100g': 8.5, 'protein_per_100g': 4.2, 'carbs_per_100g': 28.5, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440139', 'name': 'Jalebi', 'category': 'Desserts', 'fodmap_level': 'high', 'calories_per_100g': 415, 'fiber_per_100g': 1.5, 'fat_per_100g': 15.2, 'protein_per_100g': 4.8, 'carbs_per_100g': 68.5, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440140', 'name': 'Kulfi', 'category': 'Desserts', 'fodmap_level': 'high', 'calories_per_100g': 168, 'fiber_per_100g': 0.2, 'fat_per_100g': 8.5, 'protein_per_100g': 4.8, 'carbs_per_100g': 20.5, 'common_triggers': True},
        
        # Indian Beverages
        {'id': '650e8400-e29b-41d4-a716-446655440141', 'name': 'Masala Chai', 'category': 'Beverages', 'fodmap_level': 'high', 'calories_per_100g': 42, 'fiber_per_100g': 0.2, 'fat_per_100g': 1.8, 'protein_per_100g': 1.5, 'carbs_per_100g': 6.8, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440142', 'name': 'Lassi (Sweet)', 'category': 'Beverages', 'fodmap_level': 'high', 'calories_per_100g': 89, 'fiber_per_100g': 0.1, 'fat_per_100g': 2.5, 'protein_per_100g': 3.2, 'carbs_per_100g': 15.8, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440143', 'name': 'Lassi (Salted)', 'category': 'Beverages', 'fodmap_level': 'high', 'calories_per_100g': 58, 'fiber_per_100g': 0.1, 'fat_per_100g': 2.2, 'protein_per_100g': 3.5, 'carbs_per_100g': 6.8, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440144', 'name': 'Nimbu Paani (Lemonade)', 'category': 'Beverages', 'fodmap_level': 'low', 'calories_per_100g': 25, 'fiber_per_100g': 0.2, 'fat_per_100g': 0.1, 'protein_per_100g': 0.2, 'carbs_per_100g': 6.5, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440145', 'name': 'Coconut Water', 'category': 'Beverages', 'fodmap_level': 'low', 'calories_per_100g': 19, 'fiber_per_100g': 1.1, 'fat_per_100g': 0.2, 'protein_per_100g': 0.7, 'carbs_per_100g': 3.7, 'common_triggers': False},
        
        # Regional Specialties
        {'id': '650e8400-e29b-41d4-a716-446655440146', 'name': 'Poha', 'category': 'Breakfast', 'fodmap_level': 'medium', 'calories_per_100g': 158, 'fiber_per_100g': 2.2, 'fat_per_100g': 4.5, 'protein_per_100g': 3.8, 'carbs_per_100g': 28.5, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440147', 'name': 'Upma', 'category': 'Breakfast', 'fodmap_level': 'medium', 'calories_per_100g': 145, 'fiber_per_100g': 2.8, 'fat_per_100g': 3.8, 'protein_per_100g': 4.2, 'carbs_per_100g': 26.5, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440148', 'name': 'Misal Pav', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 185, 'fiber_per_100g': 5.2, 'fat_per_100g': 6.8, 'protein_per_100g': 8.5, 'carbs_per_100g': 25.8, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440149', 'name': 'Vada Pav', 'category': 'Snacks', 'fodmap_level': 'high', 'calories_per_100g': 235, 'fiber_per_100g': 3.2, 'fat_per_100g': 8.5, 'protein_per_100g': 6.8, 'carbs_per_100g': 38.5, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440150', 'name': 'Pav Bhaji', 'category': 'Main Course', 'fodmap_level': 'high', 'calories_per_100g': 165, 'fiber_per_100g': 4.2, 'fat_per_100g': 6.8, 'protein_per_100g': 4.5, 'carbs_per_100g': 24.5, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440056', 'name': 'Vanilla Pudding', 'category': 'Desserts', 'fodmap_level': 'high', 'calories_per_100g': 111, 'fiber_per_100g': 0.0, 'fat_per_100g': 2.8, 'protein_per_100g': 2.5, 'carbs_per_100g': 20.0, 'common_triggers': True},
        
        # Beverages
        {'id': '650e8400-e29b-41d4-a716-446655440057', 'name': 'Coffee', 'category': 'Beverages', 'fodmap_level': 'low', 'calories_per_100g': 1, 'fiber_per_100g': 0.0, 'fat_per_100g': 0.0, 'protein_per_100g': 0.1, 'carbs_per_100g': 0.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440058', 'name': 'Green Tea', 'category': 'Beverages', 'fodmap_level': 'low', 'calories_per_100g': 1, 'fiber_per_100g': 0.0, 'fat_per_100g': 0.0, 'protein_per_100g': 0.2, 'carbs_per_100g': 0.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440059', 'name': 'Orange Juice', 'category': 'Beverages', 'fodmap_level': 'low', 'calories_per_100g': 45, 'fiber_per_100g': 0.2, 'fat_per_100g': 0.2, 'protein_per_100g': 0.7, 'carbs_per_100g': 10.4, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440060', 'name': 'Coca Cola', 'category': 'Beverages', 'fodmap_level': 'high', 'calories_per_100g': 42, 'fiber_per_100g': 0.0, 'fat_per_100g': 0.0, 'protein_per_100g': 0.0, 'carbs_per_100g': 10.6, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440061', 'name': 'Smoothie', 'category': 'Beverages', 'fodmap_level': 'medium', 'calories_per_100g': 56, 'fiber_per_100g': 1.8, 'fat_per_100g': 0.3, 'protein_per_100g': 1.0, 'carbs_per_100g': 13.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440062', 'name': 'Beer', 'category': 'Beverages', 'fodmap_level': 'high', 'calories_per_100g': 43, 'fiber_per_100g': 0.0, 'fat_per_100g': 0.0, 'protein_per_100g': 0.5, 'carbs_per_100g': 3.6, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440063', 'name': 'Red Wine', 'category': 'Beverages', 'fodmap_level': 'low', 'calories_per_100g': 85, 'fiber_per_100g': 0.0, 'fat_per_100g': 0.0, 'protein_per_100g': 0.1, 'carbs_per_100g': 2.6, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440064', 'name': 'Latte', 'category': 'Beverages', 'fodmap_level': 'medium', 'calories_per_100g': 42, 'fiber_per_100g': 0.0, 'fat_per_100g': 1.6, 'protein_per_100g': 2.1, 'carbs_per_100g': 5.0, 'common_triggers': True},
        
        # Indian Curry Dishes
        {'id': '650e8400-e29b-41d4-a716-446655440065', 'name': 'Dal Tadka', 'category': 'Indian Curries', 'fodmap_level': 'medium', 'calories_per_100g': 108, 'fiber_per_100g': 4.2, 'fat_per_100g': 3.5, 'protein_per_100g': 6.8, 'carbs_per_100g': 14.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440066', 'name': 'Butter Chicken', 'category': 'Indian Curries', 'fodmap_level': 'high', 'calories_per_100g': 180, 'fiber_per_100g': 1.2, 'fat_per_100g': 12.0, 'protein_per_100g': 15.0, 'carbs_per_100g': 6.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440067', 'name': 'Paneer Makhani', 'category': 'Indian Curries', 'fodmap_level': 'high', 'calories_per_100g': 195, 'fiber_per_100g': 1.5, 'fat_per_100g': 15.0, 'protein_per_100g': 11.0, 'carbs_per_100g': 7.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440068', 'name': 'Palak Paneer', 'category': 'Indian Curries', 'fodmap_level': 'medium', 'calories_per_100g': 142, 'fiber_per_100g': 2.8, 'fat_per_100g': 10.0, 'protein_per_100g': 8.5, 'carbs_per_100g': 6.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440069', 'name': 'Rajma', 'category': 'Indian Curries', 'fodmap_level': 'high', 'calories_per_100g': 127, 'fiber_per_100g': 6.4, 'fat_per_100g': 0.8, 'protein_per_100g': 8.7, 'carbs_per_100g': 22.8, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440070', 'name': 'Chole', 'category': 'Indian Curries', 'fodmap_level': 'high', 'calories_per_100g': 164, 'fiber_per_100g': 7.6, 'fat_per_100g': 2.6, 'protein_per_100g': 8.9, 'carbs_per_100g': 27.4, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440071', 'name': 'Aloo Gobi', 'category': 'Indian Curries', 'fodmap_level': 'medium', 'calories_per_100g': 89, 'fiber_per_100g': 3.2, 'fat_per_100g': 3.5, 'protein_per_100g': 2.8, 'carbs_per_100g': 13.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440072', 'name': 'Chicken Tikka Masala', 'category': 'Indian Curries', 'fodmap_level': 'high', 'calories_per_100g': 163, 'fiber_per_100g': 1.0, 'fat_per_100g': 10.2, 'protein_per_100g': 14.8, 'carbs_per_100g': 5.2, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440073', 'name': 'Sambar', 'category': 'Indian Curries', 'fodmap_level': 'medium', 'calories_per_100g': 95, 'fiber_per_100g': 3.8, 'fat_per_100g': 2.5, 'protein_per_100g': 4.2, 'carbs_per_100g': 15.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440074', 'name': 'Kadhi', 'category': 'Indian Curries', 'fodmap_level': 'medium', 'calories_per_100g': 78, 'fiber_per_100g': 1.2, 'fat_per_100g': 4.5, 'protein_per_100g': 3.8, 'carbs_per_100g': 7.0, 'common_triggers': False},
        
        # Indian Rice Dishes
        {'id': '650e8400-e29b-41d4-a716-446655440075', 'name': 'Chicken Biryani', 'category': 'Indian Rice', 'fodmap_level': 'high', 'calories_per_100g': 185, 'fiber_per_100g': 0.8, 'fat_per_100g': 6.5, 'protein_per_100g': 12.0, 'carbs_per_100g': 23.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440076', 'name': 'Vegetable Biryani', 'category': 'Indian Rice', 'fodmap_level': 'high', 'calories_per_100g': 165, 'fiber_per_100g': 2.1, 'fat_per_100g': 5.2, 'protein_per_100g': 4.8, 'carbs_per_100g': 28.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440077', 'name': 'Jeera Rice', 'category': 'Indian Rice', 'fodmap_level': 'low', 'calories_per_100g': 142, 'fiber_per_100g': 0.6, 'fat_per_100g': 3.2, 'protein_per_100g': 2.8, 'carbs_per_100g': 28.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440078', 'name': 'Pulao', 'category': 'Indian Rice', 'fodmap_level': 'medium', 'calories_per_100g': 158, 'fiber_per_100g': 1.2, 'fat_per_100g': 4.0, 'protein_per_100g': 3.5, 'carbs_per_100g': 27.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440079', 'name': 'Lemon Rice', 'category': 'Indian Rice', 'fodmap_level': 'low', 'calories_per_100g': 148, 'fiber_per_100g': 0.8, 'fat_per_100g': 3.8, 'protein_per_100g': 2.9, 'carbs_per_100g': 28.5, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440080', 'name': 'Curd Rice', 'category': 'Indian Rice', 'fodmap_level': 'medium', 'calories_per_100g': 98, 'fiber_per_100g': 0.2, 'fat_per_100g': 2.1, 'protein_per_100g': 3.8, 'carbs_per_100g': 17.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440081', 'name': 'Coconut Rice', 'category': 'Indian Rice', 'fodmap_level': 'low', 'calories_per_100g': 168, 'fiber_per_100g': 1.2, 'fat_per_100g': 6.8, 'protein_per_100g': 3.2, 'carbs_per_100g': 25.0, 'common_triggers': False},
        
        # Indian Breads
        {'id': '650e8400-e29b-41d4-a716-446655440082', 'name': 'Roti', 'category': 'Indian Breads', 'fodmap_level': 'medium', 'calories_per_100g': 297, 'fiber_per_100g': 11.0, 'fat_per_100g': 3.7, 'protein_per_100g': 11.0, 'carbs_per_100g': 58.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440083', 'name': 'Naan', 'category': 'Indian Breads', 'fodmap_level': 'high', 'calories_per_100g': 310, 'fiber_per_100g': 2.7, 'fat_per_100g': 7.5, 'protein_per_100g': 9.0, 'carbs_per_100g': 56.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440084', 'name': 'Paratha', 'category': 'Indian Breads', 'fodmap_level': 'medium', 'calories_per_100g': 320, 'fiber_per_100g': 3.8, 'fat_per_100g': 12.0, 'protein_per_100g': 8.5, 'carbs_per_100g': 48.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440085', 'name': 'Dosa', 'category': 'Indian Breads', 'fodmap_level': 'low', 'calories_per_100g': 168, 'fiber_per_100g': 1.2, 'fat_per_100g': 3.8, 'protein_per_100g': 4.1, 'carbs_per_100g': 32.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440086', 'name': 'Idli', 'category': 'Indian Breads', 'fodmap_level': 'low', 'calories_per_100g': 58, 'fiber_per_100g': 0.3, 'fat_per_100g': 0.3, 'protein_per_100g': 2.0, 'carbs_per_100g': 12.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440087', 'name': 'Uttapam', 'category': 'Indian Breads', 'fodmap_level': 'low', 'calories_per_100g': 85, 'fiber_per_100g': 1.8, 'fat_per_100g': 1.2, 'protein_per_100g': 3.2, 'carbs_per_100g': 16.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440088', 'name': 'Bhatura', 'category': 'Indian Breads', 'fodmap_level': 'high', 'calories_per_100g': 385, 'fiber_per_100g': 2.5, 'fat_per_100g': 18.0, 'protein_per_100g': 8.2, 'carbs_per_100g': 48.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440089', 'name': 'Poori', 'category': 'Indian Breads', 'fodmap_level': 'medium', 'calories_per_100g': 375, 'fiber_per_100g': 3.2, 'fat_per_100g': 17.5, 'protein_per_100g': 7.8, 'carbs_per_100g': 50.0, 'common_triggers': False},
        
        # Indian Snacks
        {'id': '650e8400-e29b-41d4-a716-446655440090', 'name': 'Samosa', 'category': 'Indian Snacks', 'fodmap_level': 'high', 'calories_per_100g': 308, 'fiber_per_100g': 3.5, 'fat_per_100g': 17.0, 'protein_per_100g': 5.8, 'carbs_per_100g': 35.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440091', 'name': 'Pakora', 'category': 'Indian Snacks', 'fodmap_level': 'medium', 'calories_per_100g': 285, 'fiber_per_100g': 4.2, 'fat_per_100g': 15.0, 'protein_per_100g': 8.5, 'carbs_per_100g': 32.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440092', 'name': 'Pani Puri', 'category': 'Indian Snacks', 'fodmap_level': 'high', 'calories_per_100g': 329, 'fiber_per_100g': 2.8, 'fat_per_100g': 12.0, 'protein_per_100g': 6.2, 'carbs_per_100g': 52.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440093', 'name': 'Bhel Puri', 'category': 'Indian Snacks', 'fodmap_level': 'medium', 'calories_per_100g': 168, 'fiber_per_100g': 3.8, 'fat_per_100g': 4.2, 'protein_per_100g': 4.8, 'carbs_per_100g': 32.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440094', 'name': 'Dhokla', 'category': 'Indian Snacks', 'fodmap_level': 'low', 'calories_per_100g': 160, 'fiber_per_100g': 2.1, 'fat_per_100g': 3.8, 'protein_per_100g': 6.2, 'carbs_per_100g': 28.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440095', 'name': 'Kachori', 'category': 'Indian Snacks', 'fodmap_level': 'high', 'calories_per_100g': 418, 'fiber_per_100g': 4.5, 'fat_per_100g': 25.0, 'protein_per_100g': 8.2, 'carbs_per_100g': 42.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440096', 'name': 'Vada Pav', 'category': 'Indian Snacks', 'fodmap_level': 'high', 'calories_per_100g': 265, 'fiber_per_100g': 2.8, 'fat_per_100g': 12.0, 'protein_per_100g': 6.5, 'carbs_per_100g': 35.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440097', 'name': 'Aloo Tikki', 'category': 'Indian Snacks', 'fodmap_level': 'medium', 'calories_per_100g': 198, 'fiber_per_100g': 2.5, 'fat_per_100g': 8.5, 'protein_per_100g': 3.8, 'carbs_per_100g': 28.0, 'common_triggers': False},
        
        # Indian Sweets
        {'id': '650e8400-e29b-41d4-a716-446655440098', 'name': 'Gulab Jamun', 'category': 'Indian Sweets', 'fodmap_level': 'high', 'calories_per_100g': 387, 'fiber_per_100g': 0.8, 'fat_per_100g': 12.0, 'protein_per_100g': 6.8, 'carbs_per_100g': 65.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440099', 'name': 'Rasgulla', 'category': 'Indian Sweets', 'fodmap_level': 'high', 'calories_per_100g': 186, 'fiber_per_100g': 0.0, 'fat_per_100g': 4.0, 'protein_per_100g': 7.0, 'carbs_per_100g': 35.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440100', 'name': 'Laddu', 'category': 'Indian Sweets', 'fodmap_level': 'medium', 'calories_per_100g': 418, 'fiber_per_100g': 2.8, 'fat_per_100g': 15.0, 'protein_per_100g': 8.5, 'carbs_per_100g': 68.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440101', 'name': 'Jalebi', 'category': 'Indian Sweets', 'fodmap_level': 'high', 'calories_per_100g': 150, 'fiber_per_100g': 0.5, 'fat_per_100g': 1.0, 'protein_per_100g': 1.0, 'carbs_per_100g': 37.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440102', 'name': 'Kheer', 'category': 'Indian Sweets', 'fodmap_level': 'high', 'calories_per_100g': 97, 'fiber_per_100g': 0.2, 'fat_per_100g': 2.8, 'protein_per_100g': 3.2, 'carbs_per_100g': 16.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440103', 'name': 'Halwa', 'category': 'Indian Sweets', 'fodmap_level': 'medium', 'calories_per_100g': 416, 'fiber_per_100g': 3.2, 'fat_per_100g': 18.0, 'protein_per_100g': 6.8, 'carbs_per_100g': 62.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440104', 'name': 'Barfi', 'category': 'Indian Sweets', 'fodmap_level': 'high', 'calories_per_100g': 451, 'fiber_per_100g': 1.2, 'fat_per_100g': 20.0, 'protein_per_100g': 9.5, 'carbs_per_100g': 62.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440105', 'name': 'Kulfi', 'category': 'Indian Sweets', 'fodmap_level': 'high', 'calories_per_100g': 223, 'fiber_per_100g': 0.0, 'fat_per_100g': 9.8, 'protein_per_100g': 4.2, 'carbs_per_100g': 32.0, 'common_triggers': True},
        
        # Indian Proteins
        {'id': '650e8400-e29b-41d4-a716-446655440106', 'name': 'Tandoori Chicken', 'category': 'Indian Proteins', 'fodmap_level': 'low', 'calories_per_100g': 148, 'fiber_per_100g': 0.0, 'fat_per_100g': 4.2, 'protein_per_100g': 26.8, 'carbs_per_100g': 2.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440107', 'name': 'Fish Curry', 'category': 'Indian Proteins', 'fodmap_level': 'medium', 'calories_per_100g': 165, 'fiber_per_100g': 1.2, 'fat_per_100g': 8.5, 'protein_per_100g': 18.5, 'carbs_per_100g': 6.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440108', 'name': 'Mutton Curry', 'category': 'Indian Proteins', 'fodmap_level': 'high', 'calories_per_100g': 195, 'fiber_per_100g': 1.0, 'fat_per_100g': 12.0, 'protein_per_100g': 19.5, 'carbs_per_100g': 4.5, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440109', 'name': 'Paneer Tikka', 'category': 'Indian Proteins', 'fodmap_level': 'low', 'calories_per_100g': 265, 'fiber_per_100g': 0.5, 'fat_per_100g': 20.0, 'protein_per_100g': 18.0, 'carbs_per_100g': 3.5, 'common_triggers': False},
        
        # Indian Vegetables
        {'id': '650e8400-e29b-41d4-a716-446655440110', 'name': 'Bhindi Masala', 'category': 'Indian Vegetables', 'fodmap_level': 'low', 'calories_per_100g': 78, 'fiber_per_100g': 3.2, 'fat_per_100g': 3.5, 'protein_per_100g': 2.8, 'carbs_per_100g': 12.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440111', 'name': 'Baingan Bharta', 'category': 'Indian Vegetables', 'fodmap_level': 'medium', 'calories_per_100g': 85, 'fiber_per_100g': 4.2, 'fat_per_100g': 4.0, 'protein_per_100g': 2.5, 'carbs_per_100g': 11.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440112', 'name': 'Methi Sabzi', 'category': 'Indian Vegetables', 'fodmap_level': 'low', 'calories_per_100g': 68, 'fiber_per_100g': 4.8, 'fat_per_100g': 2.5, 'protein_per_100g': 4.2, 'carbs_per_100g': 8.5, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440113', 'name': 'Karela Sabzi', 'category': 'Indian Vegetables', 'fodmap_level': 'low', 'calories_per_100g': 52, 'fiber_per_100g': 2.8, 'fat_per_100g': 2.0, 'protein_per_100g': 2.2, 'carbs_per_100g': 8.0, 'common_triggers': False},
        
        # Indian Healthy Options
        {'id': '650e8400-e29b-41d4-a716-446655440114', 'name': 'Moong Dal', 'category': 'Indian Proteins', 'fodmap_level': 'medium', 'calories_per_100g': 105, 'fiber_per_100g': 8.2, 'fat_per_100g': 0.4, 'protein_per_100g': 7.0, 'carbs_per_100g': 19.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440115', 'name': 'Masoor Dal', 'category': 'Indian Proteins', 'fodmap_level': 'high', 'calories_per_100g': 116, 'fiber_per_100g': 7.9, 'fat_per_100g': 0.4, 'protein_per_100g': 9.0, 'carbs_per_100g': 20.0, 'common_triggers': True},
        {'id': '650e8400-e29b-41d4-a716-446655440116', 'name': 'Quinoa Upma', 'category': 'Indian Rice', 'fodmap_level': 'low', 'calories_per_100g': 158, 'fiber_per_100g': 2.8, 'fat_per_100g': 4.2, 'protein_per_100g': 5.8, 'carbs_per_100g': 26.0, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440117', 'name': 'Oats Idli', 'category': 'Indian Breads', 'fodmap_level': 'low', 'calories_per_100g': 68, 'fiber_per_100g': 1.8, 'fat_per_100g': 1.2, 'protein_per_100g': 3.2, 'carbs_per_100g': 12.5, 'common_triggers': False},
        {'id': '650e8400-e29b-41d4-a716-446655440118', 'name': 'Ragi Dosa', 'category': 'Indian Breads', 'fodmap_level': 'low', 'calories_per_100g': 78, 'fiber_per_100g': 2.2, 'fat_per_100g': 1.8, 'protein_per_100g': 3.8, 'carbs_per_100g': 14.0, 'common_triggers': False},
        
        # Indian Snacks
        {'id': str(uuid.uuid4()), 'name': 'Samosa', 'category': 'Indian Snacks', 'fodmap_level': 'high', 'calories_per_100g': 262, 'fiber_per_100g': 3.5, 'fat_per_100g': 17.8, 'protein_per_100g': 5.6, 'carbs_per_100g': 23.0, 'common_triggers': True},
        {'id': str(uuid.uuid4()), 'name': 'Pakora', 'category': 'Indian Snacks', 'fodmap_level': 'medium', 'calories_per_100g': 215, 'fiber_per_100g': 2.8, 'fat_per_100g': 12.5, 'protein_per_100g': 4.2, 'carbs_per_100g': 22.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Dhokla', 'category': 'Indian Snacks', 'fodmap_level': 'low', 'calories_per_100g': 160, 'fiber_per_100g': 1.5, 'fat_per_100g': 4.2, 'protein_per_100g': 3.8, 'carbs_per_100g': 27.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Idli Sambhar', 'category': 'Indian Snacks', 'fodmap_level': 'medium', 'calories_per_100g': 58, 'fiber_per_100g': 1.2, 'fat_per_100g': 0.8, 'protein_per_100g': 2.5, 'carbs_per_100g': 11.0, 'common_triggers': False},
        
        # Additional Popular Indian Dishes
        # Paratha Varieties
        {'id': str(uuid.uuid4()), 'name': 'Gobi Paratha', 'category': 'Indian Breads', 'fodmap_level': 'medium', 'calories_per_100g': 295, 'fiber_per_100g': 4.2, 'fat_per_100g': 11.5, 'protein_per_100g': 8.2, 'carbs_per_100g': 42.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Paneer Paratha', 'category': 'Indian Breads', 'fodmap_level': 'medium', 'calories_per_100g': 315, 'fiber_per_100g': 3.8, 'fat_per_100g': 13.2, 'protein_per_100g': 12.5, 'carbs_per_100g': 38.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Methi Paratha', 'category': 'Indian Breads', 'fodmap_level': 'low', 'calories_per_100g': 285, 'fiber_per_100g': 5.2, 'fat_per_100g': 10.8, 'protein_per_100g': 9.5, 'carbs_per_100g': 40.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Mooli Paratha', 'category': 'Indian Breads', 'fodmap_level': 'low', 'calories_per_100g': 275, 'fiber_per_100g': 4.8, 'fat_per_100g': 9.5, 'protein_per_100g': 8.0, 'carbs_per_100g': 41.0, 'common_triggers': False},
        
        # Street Food & Popular Dishes
        {'id': str(uuid.uuid4()), 'name': 'Pav Bhaji', 'category': 'Indian Street Food', 'fodmap_level': 'high', 'calories_per_100g': 185, 'fiber_per_100g': 3.5, 'fat_per_100g': 8.2, 'protein_per_100g': 4.8, 'carbs_per_100g': 25.0, 'common_triggers': True},
        {'id': str(uuid.uuid4()), 'name': 'Poha', 'category': 'Indian Breakfast', 'fodmap_level': 'low', 'calories_per_100g': 158, 'fiber_per_100g': 1.8, 'fat_per_100g': 4.2, 'protein_per_100g': 3.5, 'carbs_per_100g': 28.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Upma', 'category': 'Indian Breakfast', 'fodmap_level': 'low', 'calories_per_100g': 145, 'fiber_per_100g': 2.2, 'fat_per_100g': 3.8, 'protein_per_100g': 4.2, 'carbs_per_100g': 26.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Misal Pav', 'category': 'Indian Street Food', 'fodmap_level': 'high', 'calories_per_100g': 195, 'fiber_per_100g': 4.8, 'fat_per_100g': 6.5, 'protein_per_100g': 8.2, 'carbs_per_100g': 28.0, 'common_triggers': True},
        {'id': str(uuid.uuid4()), 'name': 'Dabeli', 'category': 'Indian Street Food', 'fodmap_level': 'medium', 'calories_per_100g': 225, 'fiber_per_100g': 3.2, 'fat_per_100g': 7.8, 'protein_per_100g': 5.5, 'carbs_per_100g': 35.0, 'common_triggers': False},
        
        # South Indian Specialties
        {'id': str(uuid.uuid4()), 'name': 'Masala Dosa', 'category': 'Indian Breads', 'fodmap_level': 'medium', 'calories_per_100g': 185, 'fiber_per_100g': 2.2, 'fat_per_100g': 5.8, 'protein_per_100g': 4.8, 'carbs_per_100g': 32.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Rava Dosa', 'category': 'Indian Breads', 'fodmap_level': 'low', 'calories_per_100g': 165, 'fiber_per_100g': 1.5, 'fat_per_100g': 4.2, 'protein_per_100g': 3.8, 'carbs_per_100g': 30.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Medu Vada', 'category': 'Indian Snacks', 'fodmap_level': 'medium', 'calories_per_100g': 245, 'fiber_per_100g': 3.8, 'fat_per_100g': 12.5, 'protein_per_100g': 8.2, 'carbs_per_100g': 28.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Rasam', 'category': 'Indian Soups', 'fodmap_level': 'medium', 'calories_per_100g': 45, 'fiber_per_100g': 1.8, 'fat_per_100g': 1.2, 'protein_per_100g': 2.2, 'carbs_per_100g': 8.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Appam', 'category': 'Indian Breads', 'fodmap_level': 'low', 'calories_per_100g': 95, 'fiber_per_100g': 0.8, 'fat_per_100g': 1.2, 'protein_per_100g': 2.5, 'carbs_per_100g': 20.0, 'common_triggers': False},
        
        # North Indian Specialties
        {'id': str(uuid.uuid4()), 'name': 'Makki di Roti', 'category': 'Indian Breads', 'fodmap_level': 'low', 'calories_per_100g': 342, 'fiber_per_100g': 7.3, 'fat_per_100g': 3.9, 'protein_per_100g': 8.7, 'carbs_per_100g': 74.3, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Sarson da Saag', 'category': 'Indian Vegetables', 'fodmap_level': 'low', 'calories_per_100g': 85, 'fiber_per_100g': 4.2, 'fat_per_100g': 3.8, 'protein_per_100g': 4.5, 'carbs_per_100g': 10.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Kulcha', 'category': 'Indian Breads', 'fodmap_level': 'high', 'calories_per_100g': 295, 'fiber_per_100g': 2.8, 'fat_per_100g': 7.5, 'protein_per_100g': 8.2, 'carbs_per_100g': 52.0, 'common_triggers': True},
        {'id': str(uuid.uuid4()), 'name': 'Lassi (Sweet)', 'category': 'Indian Beverages', 'fodmap_level': 'high', 'calories_per_100g': 89, 'fiber_per_100g': 0.0, 'fat_per_100g': 2.5, 'protein_per_100g': 3.2, 'carbs_per_100g': 14.0, 'common_triggers': True},
        {'id': str(uuid.uuid4()), 'name': 'Lassi (Salted)', 'category': 'Indian Beverages', 'fodmap_level': 'high', 'calories_per_100g': 65, 'fiber_per_100g': 0.0, 'fat_per_100g': 2.8, 'protein_per_100g': 3.5, 'carbs_per_100g': 8.0, 'common_triggers': True},
        
        # Bengali & Eastern Specialties
        {'id': str(uuid.uuid4()), 'name': 'Machher Jhol', 'category': 'Indian Curries', 'fodmap_level': 'medium', 'calories_per_100g': 125, 'fiber_per_100g': 1.5, 'fat_per_100g': 6.2, 'protein_per_100g': 14.5, 'carbs_per_100g': 4.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Aloo Posto', 'category': 'Indian Vegetables', 'fodmap_level': 'low', 'calories_per_100g': 165, 'fiber_per_100g': 3.2, 'fat_per_100g': 8.5, 'protein_per_100g': 4.8, 'carbs_per_100g': 18.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Shorshe Ilish', 'category': 'Indian Proteins', 'fodmap_level': 'low', 'calories_per_100g': 185, 'fiber_per_100g': 0.5, 'fat_per_100g': 12.5, 'protein_per_100g': 18.2, 'carbs_per_100g': 2.0, 'common_triggers': False},
        
        # Gujarati Specialties
        {'id': str(uuid.uuid4()), 'name': 'Thepla', 'category': 'Indian Breads', 'fodmap_level': 'low', 'calories_per_100g': 285, 'fiber_per_100g': 4.8, 'fat_per_100g': 9.2, 'protein_per_100g': 8.5, 'carbs_per_100g': 42.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Khakhra', 'category': 'Indian Snacks', 'fodmap_level': 'low', 'calories_per_100g': 395, 'fiber_per_100g': 6.2, 'fat_per_100g': 8.5, 'protein_per_100g': 12.0, 'carbs_per_100g': 72.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Handvo', 'category': 'Indian Snacks', 'fodmap_level': 'medium', 'calories_per_100g': 185, 'fiber_per_100g': 3.5, 'fat_per_100g': 6.8, 'protein_per_100g': 5.2, 'carbs_per_100g': 28.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Undhiyu', 'category': 'Indian Vegetables', 'fodmap_level': 'medium', 'calories_per_100g': 125, 'fiber_per_100g': 4.8, 'fat_per_100g': 5.2, 'protein_per_100g': 3.8, 'carbs_per_100g': 18.0, 'common_triggers': False},
        
        # Rajasthani Specialties
        {'id': str(uuid.uuid4()), 'name': 'Dal Baati Churma', 'category': 'Indian Main Course', 'fodmap_level': 'medium', 'calories_per_100g': 285, 'fiber_per_100g': 5.2, 'fat_per_100g': 12.5, 'protein_per_100g': 8.8, 'carbs_per_100g': 38.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Gatte ki Sabzi', 'category': 'Indian Vegetables', 'fodmap_level': 'medium', 'calories_per_100g': 145, 'fiber_per_100g': 3.8, 'fat_per_100g': 6.2, 'protein_per_100g': 5.5, 'carbs_per_100g': 18.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Ker Sangri', 'category': 'Indian Vegetables', 'fodmap_level': 'low', 'calories_per_100g': 95, 'fiber_per_100g': 4.5, 'fat_per_100g': 3.2, 'protein_per_100g': 3.8, 'carbs_per_100g': 14.0, 'common_triggers': False},
        
        # Additional Breakfast Items
        {'id': str(uuid.uuid4()), 'name': 'Aloo Poha', 'category': 'Indian Breakfast', 'fodmap_level': 'low', 'calories_per_100g': 175, 'fiber_per_100g': 2.2, 'fat_per_100g': 5.8, 'protein_per_100g': 4.2, 'carbs_per_100g': 28.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Sabudana Khichdi', 'category': 'Indian Breakfast', 'fodmap_level': 'low', 'calories_per_100g': 185, 'fiber_per_100g': 0.8, 'fat_per_100g': 6.5, 'protein_per_100g': 2.2, 'carbs_per_100g': 32.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Vermicelli Upma', 'category': 'Indian Breakfast', 'fodmap_level': 'low', 'calories_per_100g': 165, 'fiber_per_100g': 1.8, 'fat_per_100g': 4.5, 'protein_per_100g': 4.8, 'carbs_per_100g': 28.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Rava Idli', 'category': 'Indian Breakfast', 'fodmap_level': 'low', 'calories_per_100g': 85, 'fiber_per_100g': 1.2, 'fat_per_100g': 1.8, 'protein_per_100g': 3.2, 'carbs_per_100g': 16.0, 'common_triggers': False},
        
        # Additional Sweets & Desserts
        {'id': str(uuid.uuid4()), 'name': 'Sandesh', 'category': 'Indian Sweets', 'fodmap_level': 'high', 'calories_per_100g': 186, 'fiber_per_100g': 0.0, 'fat_per_100g': 4.2, 'protein_per_100g': 7.8, 'carbs_per_100g': 32.0, 'common_triggers': True},
        {'id': str(uuid.uuid4()), 'name': 'Mysore Pak', 'category': 'Indian Sweets', 'fodmap_level': 'medium', 'calories_per_100g': 518, 'fiber_per_100g': 1.8, 'fat_per_100g': 28.5, 'protein_per_100g': 6.2, 'carbs_per_100g': 62.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Kaju Katli', 'category': 'Indian Sweets', 'fodmap_level': 'low', 'calories_per_100g': 435, 'fiber_per_100g': 2.2, 'fat_per_100g': 22.5, 'protein_per_100g': 12.8, 'carbs_per_100g': 52.0, 'common_triggers': False},
        {'id': str(uuid.uuid4()), 'name': 'Ras Malai', 'category': 'Indian Sweets', 'fodmap_level': 'high', 'calories_per_100g': 186, 'fiber_per_100g': 0.0, 'fat_per_100g': 6.8, 'protein_per_100g': 6.2, 'carbs_per_100g': 28.0, 'common_triggers': True}
    ]

    async with AsyncSessionLocal() as db:
        try:
            for food_data in foods:
                # Use INSERT OR IGNORE to avoid duplicate key errors
                food_item = FoodItem(**food_data)
                db.add(food_item)
                try:
                    await db.flush()  # Try to flush this individual item
                except Exception as e:
                    # If there's a duplicate key error, rollback this item and continue
                    await db.rollback()
                    print(f'Skipping duplicate food item: {food_data["name"]}')
                    continue
            
            await db.commit()
            print('Food items seeded successfully!')
            
        except Exception as e:
            print(f'Error seeding food items: {e}')
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(seed_food_items())