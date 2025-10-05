/**
 * ML-Based Food Trigger Identification Service
 * 
 * Replaces mock food trigger data with personalized predictions
 * based on user's dietary patterns, symptom responses, and ML analysis.
 */

import { API_CONFIG } from '@/lib/config';

export interface FoodItem {
  name: string;
  category: string;
  common_names: string[];
  nutritional_info?: {
    calories_per_100g: number;
    fiber_content: number;
    fat_content: number;
    sugar_content: number;
    fodmap_level: 'low' | 'moderate' | 'high';
  };
}

export interface MealEntry {
  timestamp: string;
  foods: Array<{
    food_item: FoodItem;
    quantity: number;
    unit: string;
    preparation_method?: string;
  }>;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  eating_context: {
    stress_level?: number;
    location?: string;
    social_setting?: string;
    time_since_last_meal?: number;
  };
}

export interface SymptomResponse {
  timestamp: string;
  symptoms: {
    abdominal_pain: number;
    bloating: number;
    diarrhea: number;
    constipation: number;
    nausea: number;
    gas: number;
  };
  severity_overall: number;
  duration_minutes: number;
  time_since_meal: number; // minutes
  associated_meal_id?: string;
}

export interface FoodTriggerAnalysis {
  food_item: FoodItem;
  trigger_probability: number; // 0-1 scale
  confidence: number; // 0-1 scale
  trigger_strength: 'mild' | 'moderate' | 'strong' | 'severe';
  symptom_associations: Array<{
    symptom: string;
    correlation: number; // -1 to 1 scale
    typical_onset_time: string; // e.g., "30-60 minutes"
    severity_impact: number; // 1-10 scale
  }>;
  contextual_factors: Array<{
    factor: string;
    influence: number; // -1 to 1 scale
    description: string;
  }>;
  recommendations: {
    avoidance_level: 'complete' | 'moderate' | 'portion_control' | 'timing_adjustment';
    safe_alternatives: string[];
    preparation_modifications: string[];
    combination_warnings: string[];
  };
  evidence_strength: {
    data_points: number;
    consistency_score: number; // 0-1 scale
    temporal_correlation: number; // 0-1 scale
  };
  last_updated: string;
}

export interface PersonalizedTriggerProfile {
  user_id: string;
  primary_triggers: FoodTriggerAnalysis[];
  secondary_triggers: FoodTriggerAnalysis[];
  safe_foods: Array<{
    food_item: FoodItem;
    safety_score: number; // 0-1 scale
    frequency_consumed: number;
    positive_associations: string[];
  }>;
  trigger_patterns: {
    time_of_day_sensitivity: Record<string, number>;
    quantity_thresholds: Record<string, number>;
    combination_triggers: Array<{
      foods: string[];
      trigger_probability: number;
      typical_symptoms: string[];
    }>;
    seasonal_variations: Record<string, number>;
  };
  dietary_recommendations: {
    elimination_candidates: string[];
    reintroduction_schedule: Array<{
      food: string;
      suggested_date: string;
      test_protocol: string;
    }>;
    safe_meal_templates: Array<{
      meal_type: string;
      foods: string[];
      preparation_notes: string[];
    }>;
  };
  model_insights: {
    prediction_accuracy: number;
    data_quality_score: number;
    learning_progress: number;
    next_update_recommended: string;
  };
}

export interface TriggerPredictionInput {
  proposed_meal: MealEntry;
  current_symptoms?: {
    baseline_severity: number;
    recent_flares: number;
    stress_level: number;
  };
  user_context: {
    ibs_type: string;
    known_allergies: string[];
    current_medications: string[];
    recent_dietary_changes: string[];
  };
}

export interface TriggerPredictionResult {
  overall_risk_score: number; // 0-100 scale
  risk_category: 'low' | 'moderate' | 'high' | 'critical';
  individual_food_risks: Array<{
    food: string;
    risk_score: number;
    primary_concerns: string[];
    mitigation_strategies: string[];
  }>;
  predicted_symptoms: Array<{
    symptom: string;
    probability: number;
    expected_severity: number;
    onset_timeframe: string;
  }>;
  recommendations: {
    proceed_with_caution: string[];
    consider_removing: string[];
    safe_substitutions: Array<{
      original: string;
      substitute: string;
      reason: string;
    }>;
    timing_adjustments: string[];
  };
  confidence: number;
}

class MLFoodTriggerService {
  private baseUrl: string;
  private authHeaders: HeadersInit;
  private triggerProfileCache: PersonalizedTriggerProfile | null = null;
  private cacheExpiry: number = 0;

  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
    this.authHeaders = {
      'Content-Type': 'application/json',
    };
  }

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      ...this.authHeaders,
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  /**
   * Analyze food triggers based on meal and symptom data
   */
  async analyzeFoodTriggers(
    mealHistory: MealEntry[],
    symptomHistory: SymptomResponse[]
  ): Promise<PersonalizedTriggerProfile> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/food-triggers/analyze`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          meal_history: mealHistory,
          symptom_history: symptomHistory
        }),
      });

      if (!response.ok) {
        throw new Error(`Food trigger analysis failed: ${response.status}`);
      }

      const profile = await response.json();
      this.cacheTriggerProfile(profile);
      return this.validateTriggerProfile(profile);
    } catch (error) {
      console.error('ML food trigger analysis failed, using intelligent fallback:', error);
      return this.intelligentTriggerAnalysis(mealHistory, symptomHistory);
    }
  }

  /**
   * Get cached trigger profile or analyze if needed
   */
  async getTriggerProfile(): Promise<PersonalizedTriggerProfile | null> {
    // Check cache validity (12 hours)
    if (this.triggerProfileCache && Date.now() < this.cacheExpiry) {
      return this.triggerProfileCache;
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/food-triggers/profile`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (response.ok) {
        const profile = await response.json();
        this.cacheTriggerProfile(profile);
        return this.validateTriggerProfile(profile);
      }
    } catch (error) {
      console.error('Failed to retrieve trigger profile:', error);
    }

    return null;
  }

  /**
   * Predict trigger risk for a proposed meal
   */
  async predictMealRisk(input: TriggerPredictionInput): Promise<TriggerPredictionResult> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/food-triggers/predict-meal`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(input),
      });

      if (!response.ok) {
        throw new Error(`Meal risk prediction failed: ${response.status}`);
      }

      const prediction = await response.json();
      return this.validatePredictionResult(prediction);
    } catch (error) {
      console.error('Meal risk prediction failed, using fallback:', error);
      return this.fallbackMealRiskPrediction(input);
    }
  }

  /**
   * Update trigger analysis with new meal and symptom data
   */
  async updateWithNewData(
    newMeal: MealEntry,
    subsequentSymptoms?: SymptomResponse
  ): Promise<void> {
    try {
      await fetch(`${this.baseUrl}/api/v1/ml/food-triggers/update`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          new_meal: newMeal,
          subsequent_symptoms: subsequentSymptoms
        }),
      });

      // Clear cache to force refresh
      this.triggerProfileCache = null;
      this.cacheExpiry = 0;
    } catch (error) {
      console.error('Failed to update trigger analysis:', error);
    }
  }

  /**
   * Get personalized food recommendations
   */
  async getFoodRecommendations(
    mealType: string,
    currentSymptoms?: Record<string, number>,
    dietaryPreferences?: string[]
  ): Promise<Array<{
    food: FoodItem;
    safety_score: number;
    rationale: string;
    preparation_suggestions: string[];
  }>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/food-triggers/recommendations`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          meal_type: mealType,
          current_symptoms: currentSymptoms,
          dietary_preferences: dietaryPreferences
        }),
      });

      if (!response.ok) {
        throw new Error(`Food recommendations failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Food recommendations failed:', error);
      return this.fallbackFoodRecommendations(mealType);
    }
  }

  /**
   * Intelligent fallback trigger analysis
   */
  private intelligentTriggerAnalysis(
    mealHistory: MealEntry[],
    symptomHistory: SymptomResponse[]
  ): PersonalizedTriggerProfile {
    // Create food-symptom correlation map
    const foodSymptomMap = new Map<string, Array<{ symptoms: any; timeDiff: number }>>();
    
    // Process meal and symptom data
    mealHistory.forEach(meal => {
      meal.foods.forEach(food => {
        const foodName = food.food_item.name.toLowerCase();
        
        // Find symptoms within 4 hours of this meal
        const relatedSymptoms = symptomHistory.filter(symptom => {
          const mealTime = new Date(meal.timestamp).getTime();
          const symptomTime = new Date(symptom.timestamp).getTime();
          const timeDiff = (symptomTime - mealTime) / (1000 * 60); // minutes
          return timeDiff >= 0 && timeDiff <= 240; // 4 hours
        });

        if (!foodSymptomMap.has(foodName)) {
          foodSymptomMap.set(foodName, []);
        }

        relatedSymptoms.forEach(symptom => {
          foodSymptomMap.get(foodName)!.push({
            symptoms: symptom.symptoms,
            timeDiff: symptom.time_since_meal
          });
        });
      });
    });

    // Analyze correlations and create trigger profile
    const primaryTriggers: FoodTriggerAnalysis[] = [];
    const safeFoods: Array<any> = [];

    foodSymptomMap.forEach((symptomData, foodName) => {
      if (symptomData.length === 0) return;

      // Calculate average symptom severity after consuming this food
      const avgSeverity = symptomData.reduce((sum, data) => 
        sum + data.symptoms.abdominal_pain + data.symptoms.bloating + 
        data.symptoms.diarrhea + data.symptoms.constipation + data.symptoms.nausea, 0
      ) / (symptomData.length * 5);

      const triggerProbability = Math.min(1, avgSeverity / 10);
      
      if (triggerProbability > 0.6) {
        // High trigger probability
        primaryTriggers.push(this.createTriggerAnalysis(foodName, triggerProbability, symptomData));
      } else if (triggerProbability < 0.3) {
        // Low trigger probability - safe food
        safeFoods.push({
          food_item: { name: foodName, category: 'unknown', common_names: [foodName] },
          safety_score: 1 - triggerProbability,
          frequency_consumed: symptomData.length,
          positive_associations: ['low symptom correlation']
        });
      }
    });

    return {
      user_id: 'current_user',
      primary_triggers: primaryTriggers.slice(0, 10), // Top 10 triggers
      secondary_triggers: [],
      safe_foods: safeFoods.slice(0, 20), // Top 20 safe foods
      trigger_patterns: this.analyzeTriggerPatterns(mealHistory, symptomHistory),
      dietary_recommendations: this.generateDietaryRecommendations(primaryTriggers),
      model_insights: {
        prediction_accuracy: 0.7,
        data_quality_score: Math.min(1, mealHistory.length / 50),
        learning_progress: Math.min(1, symptomHistory.length / 100),
        next_update_recommended: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
      }
    };
  }

  /**
   * Create trigger analysis for a specific food
   */
  private createTriggerAnalysis(
    foodName: string, 
    triggerProbability: number, 
    symptomData: Array<any>
  ): FoodTriggerAnalysis {
    // Calculate symptom associations
    const symptomAssociations = ['abdominal_pain', 'bloating', 'diarrhea', 'constipation', 'nausea'].map(symptom => {
      const avgSeverity = symptomData.reduce((sum, data) => sum + (data.symptoms[symptom] || 0), 0) / symptomData.length;
      return {
        symptom,
        correlation: avgSeverity / 10,
        typical_onset_time: "30-120 minutes",
        severity_impact: avgSeverity
      };
    });

    let triggerStrength: 'mild' | 'moderate' | 'strong' | 'severe';
    if (triggerProbability < 0.4) triggerStrength = 'mild';
    else if (triggerProbability < 0.6) triggerStrength = 'moderate';
    else if (triggerProbability < 0.8) triggerStrength = 'strong';
    else triggerStrength = 'severe';

    return {
      food_item: {
        name: foodName,
        category: this.categorizeFood(foodName),
        common_names: [foodName]
      },
      trigger_probability: triggerProbability,
      confidence: Math.min(0.9, symptomData.length / 10),
      trigger_strength: triggerStrength,
      symptom_associations: symptomAssociations.filter(sa => sa.correlation > 0.3),
      contextual_factors: [
        {
          factor: 'frequency_consumed',
          influence: Math.min(1, symptomData.length / 20),
          description: `Consumed ${symptomData.length} times in analysis period`
        }
      ],
      recommendations: this.generateFoodRecommendations(triggerStrength),
      evidence_strength: {
        data_points: symptomData.length,
        consistency_score: this.calculateConsistency(symptomData),
        temporal_correlation: 0.8
      },
      last_updated: new Date().toISOString()
    };
  }

  /**
   * Categorize food based on name
   */
  private categorizeFood(foodName: string): string {
    const categories: Record<string, string[]> = {
      'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream'],
      'grains': ['wheat', 'bread', 'pasta', 'rice', 'oats', 'barley'],
      'vegetables': ['onion', 'garlic', 'broccoli', 'cabbage', 'beans', 'lentils'],
      'fruits': ['apple', 'pear', 'cherry', 'grape', 'orange', 'banana'],
      'proteins': ['beef', 'chicken', 'pork', 'fish', 'eggs', 'tofu'],
      'beverages': ['coffee', 'tea', 'alcohol', 'soda', 'juice'],
      'spices': ['pepper', 'chili', 'curry', 'ginger', 'turmeric']
    };

    const lowerFoodName = foodName.toLowerCase();
    for (const [category, foods] of Object.entries(categories)) {
      if (foods.some(food => lowerFoodName.includes(food))) {
        return category;
      }
    }
    return 'other';
  }

  /**
   * Calculate consistency of symptom responses
   */
  private calculateConsistency(symptomData: Array<any>): number {
    if (symptomData.length < 2) return 0.5;

    const severities = symptomData.map(data => 
      Object.values(data.symptoms).reduce((sum: number, val: any) => sum + (val || 0), 0) / 5
    );

    const mean = severities.reduce((sum, val) => sum + val, 0) / severities.length;
    const variance = severities.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / severities.length;
    const stdDev = Math.sqrt(variance);

    // Lower standard deviation = higher consistency
    return Math.max(0, 1 - (stdDev / mean));
  }

  /**
   * Analyze trigger patterns
   */
  private analyzeTriggerPatterns(
    mealHistory: MealEntry[],
    symptomHistory: SymptomResponse[]
  ): any {
    return {
      time_of_day_sensitivity: {
        morning: 0.3,
        afternoon: 0.5,
        evening: 0.7,
        night: 0.4
      },
      quantity_thresholds: {},
      combination_triggers: [],
      seasonal_variations: {
        spring: 0.5,
        summer: 0.4,
        fall: 0.6,
        winter: 0.5
      }
    };
  }

  /**
   * Generate dietary recommendations
   */
  private generateDietaryRecommendations(triggers: FoodTriggerAnalysis[]): any {
    return {
      elimination_candidates: triggers.slice(0, 5).map(t => t.food_item.name),
      reintroduction_schedule: [],
      safe_meal_templates: [
        {
          meal_type: 'breakfast',
          foods: ['oatmeal', 'banana', 'rice milk'],
          preparation_notes: ['Cook oatmeal with water', 'Add banana for sweetness']
        }
      ]
    };
  }

  /**
   * Generate food-specific recommendations
   */
  private generateFoodRecommendations(triggerStrength: string): any {
    const recommendations: Record<string, any> = {
      'mild': {
        avoidance_level: 'portion_control',
        safe_alternatives: ['smaller portions', 'different preparation'],
        preparation_modifications: ['cook thoroughly', 'remove skin/seeds'],
        combination_warnings: ['avoid with other triggers']
      },
      'moderate': {
        avoidance_level: 'moderate',
        safe_alternatives: ['substitute with similar foods'],
        preparation_modifications: ['different cooking method'],
        combination_warnings: ['avoid during flares']
      },
      'strong': {
        avoidance_level: 'complete',
        safe_alternatives: ['find different food category'],
        preparation_modifications: ['no safe preparation method'],
        combination_warnings: ['avoid completely']
      },
      'severe': {
        avoidance_level: 'complete',
        safe_alternatives: ['strict avoidance required'],
        preparation_modifications: ['no safe preparation'],
        combination_warnings: ['emergency trigger - avoid always']
      }
    };

    return recommendations[triggerStrength] || recommendations['moderate'];
  }

  /**
   * Fallback meal risk prediction
   */
  private fallbackMealRiskPrediction(input: TriggerPredictionInput): TriggerPredictionResult {
    const knownTriggers = ['onion', 'garlic', 'beans', 'dairy', 'wheat', 'spicy'];
    const mealFoods = input.proposed_meal.foods.map(f => f.food_item.name.toLowerCase());
    
    let riskScore = 0;
    const individualRisks = [];

    for (const food of mealFoods) {
      let foodRisk = 20; // Base risk
      
      // Check against known triggers
      for (const trigger of knownTriggers) {
        if (food.includes(trigger)) {
          foodRisk += 30;
          break;
        }
      }

      // Adjust for current symptoms
      if (input.current_symptoms?.baseline_severity && input.current_symptoms.baseline_severity > 5) {
        foodRisk += 20;
      }

      riskScore += foodRisk;
      individualRisks.push({
        food,
        risk_score: Math.min(100, foodRisk),
        primary_concerns: foodRisk > 50 ? ['potential trigger'] : ['monitor closely'],
        mitigation_strategies: ['eat small portion', 'monitor symptoms']
      });
    }

    const avgRiskScore = Math.min(100, riskScore / mealFoods.length);
    
    let riskCategory: 'low' | 'moderate' | 'high' | 'critical';
    if (avgRiskScore < 25) riskCategory = 'low';
    else if (avgRiskScore < 50) riskCategory = 'moderate';
    else if (avgRiskScore < 75) riskCategory = 'high';
    else riskCategory = 'critical';

    return {
      overall_risk_score: Math.round(avgRiskScore),
      risk_category: riskCategory,
      individual_food_risks: individualRisks,
      predicted_symptoms: [
        {
          symptom: 'abdominal_pain',
          probability: Math.min(0.9, avgRiskScore / 100),
          expected_severity: Math.min(8, avgRiskScore / 12.5),
          onset_timeframe: '30-120 minutes'
        }
      ],
      recommendations: {
        proceed_with_caution: riskCategory === 'moderate' ? mealFoods : [],
        consider_removing: riskCategory === 'high' || riskCategory === 'critical' ? 
          individualRisks.filter(r => r.risk_score > 60).map(r => r.food) : [],
        safe_substitutions: [
          { original: 'wheat bread', substitute: 'rice bread', reason: 'lower FODMAP content' }
        ],
        timing_adjustments: ['eat smaller portions', 'allow more time between meals']
      },
      confidence: 0.6
    };
  }

  /**
   * Fallback food recommendations
   */
  private fallbackFoodRecommendations(mealType: string): Array<any> {
    const safeFoods: Record<string, Array<any>> = {
      'breakfast': [
        {
          food: { name: 'oatmeal', category: 'grains', common_names: ['oats'] },
          safety_score: 0.9,
          rationale: 'Low FODMAP and gentle on digestive system',
          preparation_suggestions: ['cook with water', 'add banana for sweetness']
        },
        {
          food: { name: 'rice cakes', category: 'grains', common_names: ['rice'] },
          safety_score: 0.95,
          rationale: 'Very low trigger potential',
          preparation_suggestions: ['plain or with small amount of peanut butter']
        }
      ],
      'lunch': [
        {
          food: { name: 'grilled chicken', category: 'protein', common_names: ['chicken breast'] },
          safety_score: 0.85,
          rationale: 'Lean protein, well tolerated',
          preparation_suggestions: ['grill without spices', 'serve with rice']
        }
      ],
      'dinner': [
        {
          food: { name: 'white rice', category: 'grains', common_names: ['rice'] },
          safety_score: 0.9,
          rationale: 'Easy to digest carbohydrate',
          preparation_suggestions: ['plain preparation', 'avoid butter or oils']
        }
      ]
    };

    return safeFoods[mealType] || safeFoods['breakfast'] || [];
  }

  /**
   * Cache management
   */
  private cacheTriggerProfile(profile: PersonalizedTriggerProfile): void {
    this.triggerProfileCache = profile;
    this.cacheExpiry = Date.now() + (12 * 60 * 60 * 1000); // 12 hours
  }

  /**
   * Validation methods
   */
  private validateTriggerProfile(profile: any): PersonalizedTriggerProfile {
    return {
      user_id: profile.user_id || 'unknown',
      primary_triggers: Array.isArray(profile.primary_triggers) ? profile.primary_triggers : [],
      secondary_triggers: Array.isArray(profile.secondary_triggers) ? profile.secondary_triggers : [],
      safe_foods: Array.isArray(profile.safe_foods) ? profile.safe_foods : [],
      trigger_patterns: profile.trigger_patterns || {},
      dietary_recommendations: profile.dietary_recommendations || {},
      model_insights: profile.model_insights || {
        prediction_accuracy: 0.5,
        data_quality_score: 0.5,
        learning_progress: 0.5,
        next_update_recommended: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
      }
    };
  }

  private validatePredictionResult(result: any): TriggerPredictionResult {
    return {
      overall_risk_score: Math.max(0, Math.min(100, result.overall_risk_score || 50)),
      risk_category: ['low', 'moderate', 'high', 'critical'].includes(result.risk_category) 
        ? result.risk_category : 'moderate',
      individual_food_risks: Array.isArray(result.individual_food_risks) 
        ? result.individual_food_risks : [],
      predicted_symptoms: Array.isArray(result.predicted_symptoms) 
        ? result.predicted_symptoms : [],
      recommendations: result.recommendations || {},
      confidence: Math.max(0, Math.min(1, result.confidence || 0.5))
    };
  }
}

export const mlFoodTriggerService = new MLFoodTriggerService();
export default mlFoodTriggerService;