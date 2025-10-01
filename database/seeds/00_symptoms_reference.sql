-- Seed data for symptoms reference table
-- This table contains the available symptom types that users can log

INSERT INTO symptoms (name, description, category, is_active) VALUES
-- Digestive symptoms
('Abdominal Pain', 'Pain or discomfort in the abdominal area', 'digestive', true),
('Bloating', 'Feeling of fullness or swelling in the abdomen', 'digestive', true),
('Gas', 'Excessive gas or flatulence', 'digestive', true),
('Diarrhea', 'Loose or watery bowel movements', 'digestive', true),
('Constipation', 'Difficulty passing stool or infrequent bowel movements', 'digestive', true),
('Urgency', 'Sudden, strong urge to have a bowel movement', 'digestive', true),
('Incomplete Evacuation', 'Feeling that bowel movement is not complete', 'digestive', true),
('Nausea', 'Feeling of sickness or urge to vomit', 'digestive', true),
('Cramping', 'Sharp, sudden abdominal pain', 'digestive', true),
('Stomach Gurgling', 'Audible sounds from the digestive system', 'digestive', true),

-- Pain symptoms
('Lower Abdominal Pain', 'Pain in the lower part of the abdomen', 'pain', true),
('Upper Abdominal Pain', 'Pain in the upper part of the abdomen', 'pain', true),
('Back Pain', 'Pain in the back area', 'pain', true),
('Pelvic Pain', 'Pain in the pelvic region', 'pain', true),

-- Systemic symptoms
('Fatigue', 'Feeling of tiredness or lack of energy', 'systemic', true),
('Headache', 'Pain in the head or neck area', 'systemic', true),
('Muscle Aches', 'Pain or soreness in muscles', 'systemic', true),
('Joint Pain', 'Pain in joints', 'systemic', true),

-- Mood and psychological symptoms
('Anxiety', 'Feeling of worry, nervousness, or unease', 'mood', true),
('Depression', 'Feeling of sadness or low mood', 'mood', true),
('Irritability', 'Feeling easily annoyed or frustrated', 'mood', true),
('Stress', 'Feeling overwhelmed or under pressure', 'mood', true),

-- Sleep and energy symptoms
('Insomnia', 'Difficulty falling or staying asleep', 'sleep', true),
('Poor Sleep Quality', 'Non-restful or interrupted sleep', 'sleep', true),
('Daytime Sleepiness', 'Excessive sleepiness during the day', 'sleep', true),

-- Other symptoms
('Loss of Appetite', 'Reduced desire to eat', 'other', true),
('Food Intolerance', 'Adverse reaction to certain foods', 'other', true),
('Heartburn', 'Burning sensation in the chest', 'other', true),
('Acid Reflux', 'Stomach acid backing up into the esophagus', 'other', true);