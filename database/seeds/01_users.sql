-- Seed data for users table
-- Password for all test users is 'password123' (hashed with bcrypt)

INSERT INTO users (
    id,
    email,
    username,
    password_hash,
    first_name,
    last_name,
    date_of_birth,
    gender,
    role,
    is_active,
    is_verified,
    timezone,
    height_cm,
    weight_kg,
    diagnosis_date,
    ibs_subtype,
    notification_preferences,
    privacy_settings,
    created_at,
    updated_at
) VALUES 
-- Admin user
(
    '550e8400-e29b-41d4-a716-446655440000',
    'admin@ibswellness.com',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/A5/jF3kkS', -- password123
    'Admin',
    'User',
    '1985-01-01',
    'other',
    'admin',
    true,
    true,
    'UTC',
    NULL,
    NULL,
    NULL,
    NULL,
    '{"email": true, "push": true, "sms": false}',
    '{"profile_public": false, "data_sharing": false}',
    NOW() - INTERVAL '30 days',
    NOW() - INTERVAL '1 day'
),

-- Sample patients
(
    '550e8400-e29b-41d4-a716-446655440001',
    'john.doe@email.com',
    'johndoe',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/A5/jF3kkS', -- password123
    'John',
    'Doe',
    '1990-05-15',
    'male',
    'patient',
    true,
    true,
    'America/New_York',
    175,
    70.5,
    '2020-03-15',
    'IBS-D',
    '{"email": true, "push": true, "sms": true}',
    '{"profile_public": false, "data_sharing": true}',
    NOW() - INTERVAL '25 days',
    NOW() - INTERVAL '2 hours'
),

(
    '550e8400-e29b-41d4-a716-446655440002',
    'jane.smith@email.com',
    'janesmith',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/A5/jF3kkS', -- password123
    'Jane',
    'Smith',
    '1988-09-22',
    'female',
    'patient',
    true,
    true,
    'America/Los_Angeles',
    162,
    58.0,
    '2019-11-08',
    'IBS-C',
    '{"email": true, "push": false, "sms": false}',
    '{"profile_public": false, "data_sharing": true}',
    NOW() - INTERVAL '20 days',
    NOW() - INTERVAL '1 hour'
),

(
    '550e8400-e29b-41d4-a716-446655440003',
    'mike.johnson@email.com',
    'mikejohnson',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/A5/jF3kkS', -- password123
    'Mike',
    'Johnson',
    '1992-12-03',
    'male',
    'patient',
    true,
    true,
    'Europe/London',
    180,
    82.3,
    '2021-07-20',
    'IBS-M',
    '{"email": true, "push": true, "sms": true}',
    '{"profile_public": false, "data_sharing": false}',
    NOW() - INTERVAL '15 days',
    NOW() - INTERVAL '30 minutes'
),

(
    '550e8400-e29b-41d4-a716-446655440004',
    'sarah.wilson@email.com',
    'sarahwilson',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/A5/jF3kkS', -- password123
    'Sarah',
    'Wilson',
    '1995-04-18',
    'female',
    'patient',
    true,
    true,
    'Australia/Sydney',
    168,
    62.8,
    '2022-01-12',
    'IBS-U',
    '{"email": false, "push": true, "sms": false}',
    '{"profile_public": true, "data_sharing": true}',
    NOW() - INTERVAL '10 days',
    NOW() - INTERVAL '15 minutes'
),

-- Doctor user
(
    '550e8400-e29b-41d4-a716-446655440005',
    'dr.brown@hospital.com',
    'drbrown',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/A5/jF3kkS', -- password123
    'Dr. Emily',
    'Brown',
    '1975-08-30',
    'female',
    'doctor',
    true,
    true,
    'America/Chicago',
    NULL,
    NULL,
    NULL,
    NULL,
    '{"email": true, "push": true, "sms": true}',
    '{"profile_public": false, "data_sharing": false}',
    NOW() - INTERVAL '5 days',
    NOW() - INTERVAL '5 minutes'
);