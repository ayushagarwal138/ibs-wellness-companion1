-- Seed data for symptoms table
-- Realistic symptom logs for sample users over the past month

INSERT INTO symptoms (
    id,
    user_id,
    recorded_at,
    abdominal_pain,
    bloating,
    gas,
    diarrhea,
    constipation,
    urgency,
    incomplete_evacuation,
    nausea,
    fatigue,
    headache,
    anxiety,
    overall_severity,
    flare_status,
    notes,
    mood_score,
    stress_level,
    sleep_quality,
    created_at,
    updated_at
) VALUES 

-- John Doe (IBS-D) - Recent symptoms
('850e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', NOW() - INTERVAL '1 hour', 'moderate', 'mild', 'moderate', 'severe', 'none', 'severe', 'mild', 'mild', 'moderate', 'none', 'mild', 'moderate', 'moderate', 'Bad flare after lunch meeting', 4, 8, 6, NOW() - INTERVAL '1 hour', NOW() - INTERVAL '1 hour'),

('850e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440001', NOW() - INTERVAL '1 day', 'mild', 'mild', 'mild', 'moderate', 'none', 'moderate', 'none', 'none', 'mild', 'none', 'none', 'mild', 'mild', 'Better day overall', 7, 4, 7, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),

('850e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440001', NOW() - INTERVAL '2 days', 'severe', 'severe', 'severe', 'severe', 'none', 'severe', 'moderate', 'moderate', 'severe', 'mild', 'moderate', 'severe', 'severe', 'Worst flare in weeks - stress at work', 2, 9, 3, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),

('850e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440001', NOW() - INTERVAL '3 days', 'none', 'none', 'mild', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'none', 'Great day! Feeling normal', 9, 2, 8, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),

('850e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440001', NOW() - INTERVAL '5 days', 'moderate', 'moderate', 'moderate', 'moderate', 'none', 'moderate', 'mild', 'none', 'mild', 'none', 'mild', 'moderate', 'mild', 'Typical symptoms after eating out', 6, 5, 6, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days'),

-- Jane Smith (IBS-C) - Recent symptoms
('850e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440002', NOW() - INTERVAL '2 hours', 'moderate', 'severe', 'moderate', 'none', 'moderate', 'none', 'severe', 'mild', 'moderate', 'mild', 'mild', 'moderate', 'moderate', 'Bloated and uncomfortable', 5, 6, 5, NOW() - INTERVAL '2 hours', NOW() - INTERVAL '2 hours'),

('850e8400-e29b-41d4-a716-446655440007', '550e8400-e29b-41d4-a716-446655440002', NOW() - INTERVAL '1 day', 'mild', 'moderate', 'mild', 'none', 'mild', 'none', 'moderate', 'none', 'mild', 'none', 'none', 'mild', 'mild', 'Fiber supplement helping', 7, 3, 7, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),

('850e8400-e29b-41d4-a716-446655440008', '550e8400-e29b-41d4-a716-446655440002', NOW() - INTERVAL '3 days', 'severe', 'severe', 'severe', 'none', 'severe', 'none', 'severe', 'moderate', 'severe', 'moderate', 'moderate', 'severe', 'severe', 'Havent had BM in 4 days', 3, 8, 4, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),

('850e8400-e29b-41d4-a716-446655440009', '550e8400-e29b-41d4-a716-446655440002', NOW() - INTERVAL '4 days', 'mild', 'mild', 'mild', 'none', 'mild', 'none', 'mild', 'none', 'none', 'none', 'none', 'mild', 'none', 'Medication adjustment working', 8, 3, 8, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),

('850e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440002', NOW() - INTERVAL '6 days', 'moderate', 'severe', 'moderate', 'none', 'moderate', 'none', 'moderate', 'mild', 'moderate', 'none', 'mild', 'moderate', 'moderate', 'Typical constipation pattern', 5, 5, 6, NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days'),

-- Mike Johnson (IBS-M) - Recent symptoms
('850e8400-e29b-41d4-a716-446655440011', '550e8400-e29b-41d4-a716-446655440003', NOW() - INTERVAL '30 minutes', 'mild', 'moderate', 'mild', 'mild', 'none', 'mild', 'none', 'none', 'mild', 'none', 'none', 'mild', 'mild', 'Mixed symptoms today', 6, 4, 7, NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes'),

('850e8400-e29b-41d4-a716-446655440012', '550e8400-e29b-41d4-a716-446655440003', NOW() - INTERVAL '2 days', 'moderate', 'moderate', 'moderate', 'none', 'moderate', 'none', 'mild', 'mild', 'mild', 'mild', 'mild', 'moderate', 'mild', 'Constipation phase', 6, 5, 6, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),

('850e8400-e29b-41d4-a716-446655440013', '550e8400-e29b-41d4-a716-446655440003', NOW() - INTERVAL '4 days', 'moderate', 'mild', 'moderate', 'moderate', 'none', 'moderate', 'mild', 'none', 'mild', 'none', 'none', 'moderate', 'moderate', 'Diarrhea phase - alternating pattern', 5, 6, 5, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),

('850e8400-e29b-41d4-a716-446655440014', '550e8400-e29b-41d4-a716-446655440003', NOW() - INTERVAL '7 days', 'severe', 'severe', 'severe', 'severe', 'mild', 'severe', 'moderate', 'moderate', 'severe', 'moderate', 'severe', 'severe', 'severe', 'Major flare - both D and C symptoms', 2, 9, 3, NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days'),

-- Sarah Wilson (IBS-U) - Recent symptoms
('850e8400-e29b-41d4-a716-446655440015', '550e8400-e29b-41d4-a716-446655440004', NOW() - INTERVAL '15 minutes', 'moderate', 'moderate', 'moderate', 'mild', 'mild', 'mild', 'mild', 'mild', 'moderate', 'mild', 'moderate', 'moderate', 'mild', 'Unpredictable symptoms as usual', 5, 6, 6, NOW() - INTERVAL '15 minutes', NOW() - INTERVAL '15 minutes'),

('850e8400-e29b-41d4-a716-446655440016', '550e8400-e29b-41d4-a716-446655440004', NOW() - INTERVAL '1 day', 'mild', 'mild', 'mild', 'none', 'mild', 'none', 'mild', 'none', 'mild', 'none', 'mild', 'mild', 'none', 'Better day', 7, 4, 7, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),

('850e8400-e29b-41d4-a716-446655440017', '550e8400-e29b-41d4-a716-446655440004', NOW() - INTERVAL '3 days', 'severe', 'moderate', 'moderate', 'moderate', 'moderate', 'moderate', 'moderate', 'moderate', 'moderate', 'moderate', 'moderate', 'moderate', 'moderate', 'Confusing mix of symptoms', 4, 7, 5, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),

-- Historical data (older entries for pattern analysis)
('850e8400-e29b-41d4-a716-446655440018', '550e8400-e29b-41d4-a716-446655440001', NOW() - INTERVAL '10 days', 'moderate', 'moderate', 'moderate', 'moderate', 'none', 'moderate', 'mild', 'mild', 'moderate', 'none', 'mild', 'moderate', 'moderate', 'Regular IBS-D symptoms', 5, 6, 6, NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days'),

('850e8400-e29b-41d4-a716-446655440019', '550e8400-e29b-41d4-a716-446655440002', NOW() - INTERVAL '12 days', 'moderate', 'severe', 'mild', 'none', 'moderate', 'none', 'moderate', 'mild', 'moderate', 'mild', 'mild', 'moderate', 'moderate', 'Constipation episode', 4, 7, 5, NOW() - INTERVAL '12 days', NOW() - INTERVAL '12 days'),

('850e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440003', NOW() - INTERVAL '15 days', 'mild', 'mild', 'mild', 'mild', 'mild', 'mild', 'mild', 'none', 'mild', 'none', 'none', 'mild', 'mild', 'Stable period', 7, 3, 8, NOW() - INTERVAL '15 days', NOW() - INTERVAL '15 days');