-- Seed data for medications table
-- Common IBS medications for sample users

INSERT INTO medications (
    id,
    user_id,
    name,
    dosage,
    frequency,
    medication_type,
    start_date,
    end_date,
    is_active,
    prescribing_doctor,
    notes,
    side_effects,
    created_at,
    updated_at
) VALUES 

-- Medications for John Doe (IBS-D)
('750e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 'Loperamide', '2mg', 'As needed', 'Antidiarrheal', '2023-01-15', NULL, true, 'Dr. Smith', 'Take when experiencing diarrhea', 'Mild constipation when overused', NOW() - INTERVAL '20 days', NOW() - INTERVAL '1 day'),

('750e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440001', 'Dicyclomine', '20mg', 'Twice daily', 'Antispasmodic', '2023-02-01', NULL, true, 'Dr. Smith', 'Take with meals to reduce cramping', 'Dry mouth, dizziness', NOW() - INTERVAL '15 days', NOW() - INTERVAL '1 day'),

('750e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440001', 'Probiotics', '10 billion CFU', 'Once daily', 'Probiotic', '2023-03-01', NULL, true, 'Dr. Smith', 'Take with breakfast', 'None reported', NOW() - INTERVAL '10 days', NOW() - INTERVAL '1 day'),

-- Medications for Jane Smith (IBS-C)
('750e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440002', 'Psyllium Husk', '5g', 'Twice daily', 'Fiber Supplement', '2023-01-20', NULL, true, 'Dr. Johnson', 'Mix with plenty of water', 'Initial bloating', NOW() - INTERVAL '18 days', NOW() - INTERVAL '2 hours'),

('750e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440002', 'Polyethylene Glycol', '17g', 'Once daily', 'Laxative', '2023-02-15', NULL, true, 'Dr. Johnson', 'Dissolve in 8oz of liquid', 'Mild nausea initially', NOW() - INTERVAL '12 days', NOW() - INTERVAL '2 hours'),

('750e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440002', 'Linaclotide', '290mcg', 'Once daily', 'Guanylate Cyclase Agonist', '2023-03-10', NULL, true, 'Dr. Johnson', 'Take on empty stomach', 'Diarrhea (mild)', NOW() - INTERVAL '8 days', NOW() - INTERVAL '2 hours'),

-- Medications for Mike Johnson (IBS-M)
('750e8400-e29b-41d4-a716-446655440007', '550e8400-e29b-41d4-a716-446655440003', 'Hyoscyamine', '0.125mg', 'As needed', 'Antispasmodic', '2023-02-20', NULL, true, 'Dr. Brown', 'Take before meals for cramping', 'Dry mouth, blurred vision', NOW() - INTERVAL '14 days', NOW() - INTERVAL '30 minutes'),

('750e8400-e29b-41d4-a716-446655440008', '550e8400-e29b-41d4-a716-446655440003', 'Rifaximin', '550mg', 'Three times daily', 'Antibiotic', '2023-01-10', '2023-01-24', false, 'Dr. Brown', '14-day course for SIBO treatment', 'Mild headache', NOW() - INTERVAL '25 days', NOW() - INTERVAL '20 days'),

('750e8400-e29b-41d4-a716-446655440009', '550e8400-e29b-41d4-a716-446655440003', 'Peppermint Oil', '0.2ml', 'Three times daily', 'Natural Antispasmodic', '2023-03-01', NULL, true, 'Dr. Brown', 'Enteric-coated capsules', 'Heartburn if not enteric-coated', NOW() - INTERVAL '10 days', NOW() - INTERVAL '30 minutes'),

-- Medications for Sarah Wilson (IBS-U)
('750e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440004', 'Alosetron', '0.5mg', 'Twice daily', 'Serotonin Antagonist', '2023-02-01', NULL, true, 'Dr. Davis', 'Monitor for constipation', 'Constipation, nausea', NOW() - INTERVAL '8 days', NOW() - INTERVAL '15 minutes'),

('750e8400-e29b-41d4-a716-446655440011', '550e8400-e29b-41d4-a716-446655440004', 'Simethicone', '40mg', 'Four times daily', 'Anti-gas', '2023-01-25', NULL, true, 'Dr. Davis', 'Take after meals and at bedtime', 'None reported', NOW() - INTERVAL '12 days', NOW() - INTERVAL '15 minutes'),

('750e8400-e29b-41d4-a716-446655440012', '550e8400-e29b-41d4-a716-446655440004', 'Lactobacillus', '5 billion CFU', 'Once daily', 'Probiotic', '2023-03-15', NULL, true, 'Dr. Davis', 'Refrigerate after opening', 'None reported', NOW() - INTERVAL '5 days', NOW() - INTERVAL '15 minutes'),

-- Additional medications (some discontinued)
('750e8400-e29b-41d4-a716-446655440013', '550e8400-e29b-41d4-a716-446655440001', 'Amitriptyline', '10mg', 'Once daily at bedtime', 'Tricyclic Antidepressant', '2022-12-01', '2023-01-15', false, 'Dr. Smith', 'Discontinued due to side effects', 'Drowsiness, weight gain', NOW() - INTERVAL '30 days', NOW() - INTERVAL '25 days'),

('750e8400-e29b-41d4-a716-446655440014', '550e8400-e29b-41d4-a716-446655440002', 'Lubiprostone', '24mcg', 'Twice daily', 'Chloride Channel Activator', '2022-11-15', '2023-01-20', false, 'Dr. Johnson', 'Switched to Linaclotide', 'Nausea, diarrhea', NOW() - INTERVAL '35 days', NOW() - INTERVAL '18 days');