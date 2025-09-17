/**
 * Shared TypeScript interfaces for IBS Wellness Companion
 * These types ensure consistency between frontend and backend
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum SeverityLevel {
  NONE = 'none',
  MILD = 'mild',
  MODERATE = 'moderate',
  SEVERE = 'severe'
}

export enum GenderType {
  MALE = 'male',
  FEMALE = 'female',
  OTHER = 'other',
  PREFER_NOT_TO_SAY = 'prefer_not_to_say'
}

export enum IBSType {
  IBS_D = 'ibs_d',  // Diarrhea-predominant
  IBS_C = 'ibs_c',  // Constipation-predominant
  IBS_M = 'ibs_m',  // Mixed
  IBS_U = 'ibs_u'   // Unsubtyped
}

export enum BristolStoolType {
  TYPE_1 = 1,
  TYPE_2 = 2,
  TYPE_3 = 3,
  TYPE_4 = 4,
  TYPE_5 = 5,
  TYPE_6 = 6,
  TYPE_7 = 7
}

export enum MealType {
  BREAKFAST = 'breakfast',
  LUNCH = 'lunch',
  DINNER = 'dinner',
  SNACK = 'snack'
}

export enum MedicationType {
  ANTISPASMODIC = 'antispasmodic',
  ANTIDIARRHEAL = 'antidiarrheal',
  LAXATIVE = 'laxative',
  PROBIOTIC = 'probiotic',
  FIBER_SUPPLEMENT = 'fiber_supplement',
  PAIN_RELIEVER = 'pain_reliever',
  OTHER = 'other'
}

// ============================================================================
// BASE INTERFACES
// ============================================================================

export interface BaseEntity {
  id: string | number;
  created_at: string;
  updated_at: string;
}

export interface TimestampedEntity {
  created_at: string;
  updated_at?: string;
}

// ============================================================================
// USER INTERFACES
// ============================================================================

export interface UserBase {
  email: string;
  first_name: string;
  last_name: string;
}

export interface UserProfile extends UserBase, BaseEntity {
  full_name: string;
  phone_number?: string;
  date_of_birth?: string;
  age?: number;
  gender?: GenderType;
  height_cm?: number;
  weight_kg?: number;
  bmi?: number;
  ibs_type?: IBSType;
  diagnosis_date?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  is_active: boolean;
  is_verified: boolean;
  last_login?: string;
}

export interface UserStats {
  total_symptom_logs: number;
  total_diet_logs: number;
  total_medication_logs: number;
  days_since_registration: number;
  last_symptom_log?: string;
  last_diet_log?: string;
  last_medication_log?: string;
  average_symptom_severity?: number;
  most_common_symptoms: string[];
  most_common_triggers: string[];
}

// ============================================================================
// SYMPTOM INTERFACES
// ============================================================================

export interface SymptomLogBase {
  severity: SeverityLevel;
  symptoms: string[];
  pain_location?: string;
  bristol_scale?: BristolStoolType;
  mood_rating?: number;
  stress_level?: number;
  sleep_quality?: number;
  notes?: string;
  logged_at?: string;
  // Additional fields for compatibility with existing forms
  symptom_id?: number;
  bristol_stool_type?: BristolStoolType;
  bowel_movement_frequency?: number;
  pain_type?: string;
  exercise_minutes?: number;
  potential_triggers?: string;
}

export interface SymptomLog extends SymptomLogBase, BaseEntity {
  user_id: string | number;
}

export interface SymptomStats {
  total_logs: number;
  average_severity: number;
  most_common_symptoms: string[];
  severity_distribution: Record<string, number>;
  bristol_distribution: Record<string, number>;
  pain_locations: Record<string, number>;
  weekly_trends: Record<string, number>;
}

export interface SymptomAnalytics {
  symptom_trends: TrendData[];
  severity_patterns: PatternData[];
  trigger_correlations: CorrelationData[];
  predictions: PredictionData[];
}

// ============================================================================
// DIET INTERFACES
// ============================================================================

export interface FoodReactionBase {
  food_name: string;
  severity: SeverityLevel;
  symptoms: string[];
  onset_time?: number;
  duration_minutes?: number;
  notes?: string;
  consumed_at?: string;
}

export interface FoodReaction extends FoodReactionBase, BaseEntity {
  user_id: string | number;
}

export interface DietLogBase {
  meal_type: MealType;
  foods: string[];
  portion_size?: string;
  calories?: number;
  notes?: string;
  consumed_at?: string;
}

export interface DietLog extends DietLogBase, BaseEntity {
  user_id: string | number;
}

export interface FoodStats {
  total_reactions: number;
  most_problematic_foods: string[];
  safe_foods: string[];
  reaction_patterns: Record<string, number>;
  severity_by_food: Record<string, number>;
}

export interface DietStats {
  total_logs: number;
  meal_distribution: Record<string, number>;
  average_calories: number;
  most_common_foods: string[];
  nutritional_balance: NutritionalData;
}

// ============================================================================
// MEDICATION INTERFACES
// ============================================================================

export interface MedicationLogBase {
  medication_name: string;
  medication_type: MedicationType;
  dosage: string;
  frequency: string;
  taken_at?: string;
  effectiveness_rating?: number;
  side_effects?: string[];
  notes?: string;
}

export interface MedicationLog extends MedicationLogBase, BaseEntity {
  user_id: string | number;
}

export interface MedicationStats {
  total_logs: number;
  adherence_rate: number;
  most_effective_medications: string[];
  common_side_effects: string[];
  effectiveness_trends: Record<string, number>;
}

// ============================================================================
// ANALYTICS & VISUALIZATION INTERFACES
// ============================================================================

export interface TrendData {
  date: string;
  symptom_severity: number;
  mood_rating: number;
  bristol_scale: number;
}

export interface PatternData {
  pattern_type: string;
  frequency: number;
  severity: number;
  confidence: number;
}

export interface CorrelationData {
  factor: string;
  correlation_strength: number;
  p_value: number;
  description: string;
}

export interface PredictionData {
  date: string;
  predicted_severity: number;
  confidence_interval: [number, number];
  contributing_factors: string[];
}

export interface FoodReactionPattern {
  food_name: string;
  reaction_count: number;
  avg_severity: number;
  common_symptoms: string[];
}

export interface WeeklySummary {
  week: string;
  total_symptoms: number;
  avg_severity: number;
  total_meals: number;
  reactions: number;
}

export interface VisualizationData {
  symptom_trends: TrendData[];
  food_reaction_patterns: FoodReactionPattern[];
  weekly_summary: WeeklySummary[];
}

export interface NutritionalData {
  protein: number;
  carbohydrates: number;
  fat: number;
  fiber: number;
  calories: number;
}

// ============================================================================
// API RESPONSE INTERFACES
// ============================================================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
}

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ListResponse<T = any> extends ApiResponse<PaginatedResponse<T>> {}

// ============================================================================
// FORM INTERFACES
// ============================================================================

export interface SymptomLogFormData extends Omit<SymptomLogBase, 'logged_at'> {
  logged_at?: Date | string;
}

export interface FoodReactionFormData extends Omit<FoodReactionBase, 'consumed_at'> {
  consumed_at?: Date | string;
}

export interface DietLogFormData extends Omit<DietLogBase, 'consumed_at'> {
  consumed_at?: Date | string;
}

export interface MedicationLogFormData extends Omit<MedicationLogBase, 'taken_at'> {
  taken_at?: Date | string;
}

// ============================================================================
// AUTHENTICATION INTERFACES
// ============================================================================

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends UserBase {
  password: string;
  confirm_password: string;
}

export interface AuthToken {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthUser extends UserProfile {
  permissions: string[];
  roles: string[];
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type CreateRequest<T> = Omit<T, keyof BaseEntity>;
export type UpdateRequest<T> = Partial<Omit<T, keyof BaseEntity>>;
export type ID = string | number;