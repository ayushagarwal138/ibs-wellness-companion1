-- Migration 005: Fix CASCADE DELETE constraints for user deletion
-- This migration updates all foreign key constraints referencing users.id to use CASCADE DELETE

BEGIN;

-- Drop and recreate foreign key constraints with CASCADE DELETE using actual constraint names

-- billing_addresses table
ALTER TABLE billing_addresses DROP CONSTRAINT fk_billing_addresses_user_id_users;
ALTER TABLE billing_addresses ADD CONSTRAINT fk_billing_addresses_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- challenge_participations table
ALTER TABLE challenge_participations DROP CONSTRAINT fk_challenge_participations_user_id_users;
ALTER TABLE challenge_participations ADD CONSTRAINT fk_challenge_participations_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- challenges table
ALTER TABLE challenges DROP CONSTRAINT fk_challenges_created_by_user_id_users;
ALTER TABLE challenges ADD CONSTRAINT fk_challenges_created_by_user_id_users 
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE CASCADE;

-- data_insights table
ALTER TABLE data_insights DROP CONSTRAINT fk_data_insights_user_id_users;
ALTER TABLE data_insights ADD CONSTRAINT fk_data_insights_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- device_tokens table
ALTER TABLE device_tokens DROP CONSTRAINT fk_device_tokens_user_id_users;
ALTER TABLE device_tokens ADD CONSTRAINT fk_device_tokens_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- diet_logs table
ALTER TABLE diet_logs DROP CONSTRAINT fk_diet_logs_user_id_users;
ALTER TABLE diet_logs ADD CONSTRAINT fk_diet_logs_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- food_reactions table
ALTER TABLE food_reactions DROP CONSTRAINT fk_food_reactions_user_id_users;
ALTER TABLE food_reactions ADD CONSTRAINT fk_food_reactions_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- goal_progress table
ALTER TABLE goal_progress DROP CONSTRAINT fk_goal_progress_user_id_users;
ALTER TABLE goal_progress ADD CONSTRAINT fk_goal_progress_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- invoices table
ALTER TABLE invoices DROP CONSTRAINT fk_invoices_user_id_users;
ALTER TABLE invoices ADD CONSTRAINT fk_invoices_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- medical_records table
ALTER TABLE medical_records DROP CONSTRAINT fk_medical_records_user_id_users;
ALTER TABLE medical_records ADD CONSTRAINT fk_medical_records_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- medication_costs table
ALTER TABLE medication_costs DROP CONSTRAINT fk_medication_costs_user_id_users;
ALTER TABLE medication_costs ADD CONSTRAINT fk_medication_costs_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- medication_logs table
ALTER TABLE medication_logs DROP CONSTRAINT fk_medication_logs_user_id_users;
ALTER TABLE medication_logs ADD CONSTRAINT fk_medication_logs_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- milestones table
ALTER TABLE milestones DROP CONSTRAINT fk_milestones_user_id_users;
ALTER TABLE milestones ADD CONSTRAINT fk_milestones_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- notification_preferences table
ALTER TABLE notification_preferences DROP CONSTRAINT fk_notification_preferences_user_id_users;
ALTER TABLE notification_preferences ADD CONSTRAINT fk_notification_preferences_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- notifications table
ALTER TABLE notifications DROP CONSTRAINT fk_notifications_user_id_users;
ALTER TABLE notifications ADD CONSTRAINT fk_notifications_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- payment_methods table
ALTER TABLE payment_methods DROP CONSTRAINT fk_payment_methods_user_id_users;
ALTER TABLE payment_methods ADD CONSTRAINT fk_payment_methods_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- report_generations table
ALTER TABLE report_generations DROP CONSTRAINT fk_report_generations_user_id_users;
ALTER TABLE report_generations ADD CONSTRAINT fk_report_generations_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- subscriptions table
ALTER TABLE subscriptions DROP CONSTRAINT fk_subscriptions_user_id_users;
ALTER TABLE subscriptions ADD CONSTRAINT fk_subscriptions_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- symptom_logs table
ALTER TABLE symptom_logs DROP CONSTRAINT fk_symptom_logs_user_id_users;
ALTER TABLE symptom_logs ADD CONSTRAINT fk_symptom_logs_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- transactions table
ALTER TABLE transactions DROP CONSTRAINT fk_transactions_user_id_users;
ALTER TABLE transactions ADD CONSTRAINT fk_transactions_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- user_achievements table
ALTER TABLE user_achievements DROP CONSTRAINT fk_user_achievements_user_id_users;
ALTER TABLE user_achievements ADD CONSTRAINT fk_user_achievements_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- user_analytics table
ALTER TABLE user_analytics DROP CONSTRAINT fk_user_analytics_user_id_users;
ALTER TABLE user_analytics ADD CONSTRAINT fk_user_analytics_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- user_goals table
ALTER TABLE user_goals DROP CONSTRAINT fk_user_goals_user_id_users;
ALTER TABLE user_goals ADD CONSTRAINT fk_user_goals_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- user_providers table
ALTER TABLE user_providers DROP CONSTRAINT fk_user_providers_user_id_users;
ALTER TABLE user_providers ADD CONSTRAINT fk_user_providers_user_id_users 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

COMMIT;

-- Verify the changes
SELECT 
    tc.table_name,
    tc.constraint_name,
    rc.delete_rule
FROM information_schema.table_constraints tc
JOIN information_schema.referential_constraints rc ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND rc.unique_constraint_name IN (
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'users' AND constraint_type = 'PRIMARY KEY'
    )
ORDER BY tc.table_name;