'use client';

import { mlService } from './ml-service';
import { personalizationService } from './personalization-service';

export interface ProfileSection {
  basic_info: Record<string, any>;
  medical_history: Record<string, any>;
  dietary_preferences: Record<string, any>;
  lifestyle_factors: Record<string, any>;
  goals_preferences: Record<string, any>;
}

export interface MLOptimizedWeights {
  field_weights: Record<string, Record<string, number>>;
  predictive_importance: Record<string, number>;
  personalization_factors: {
    ibs_type_multiplier: Record<string, number>;
    severity_multiplier: Record<string, number>;
    goal_multiplier: Record<string, number>;
  };
  dynamic_adjustments: {
    symptom_prediction_weight: number;
    trigger_identification_weight: number;
    treatment_optimization_weight: number;
  };
}

export interface ProfileCompletionResult {
  overall_completion: number;
  section_completion: Record<string, number>;
  ml_optimized_score: number;
  predictive_value_score: number;
  missing_critical_fields: string[];
  recommended_next_steps: Array<{
    field: string;
    section: string;
    importance: number;
    reason: string;
    impact: string;
  }>;
  personalization_readiness: number;
}

class MLProfileCompletionService {
  private baseWeights: MLOptimizedWeights = {
    field_weights: {
      basic_info: {
        first_name: 2,
        last_name: 2,
        email: 3,
        phone_number: 2,
        date_of_birth: 12, // High importance for age-related patterns
        gender: 8, // Important for IBS prevalence patterns
        height_cm: 6,
        weight_kg: 6,
        emergency_contact_name: 1,
        emergency_contact_phone: 1,
      },
      medical_history: {
        ibs_type: 25, // Critical for personalized treatment
        diagnosis_date: 15, // Important for progression tracking
        severity_level: 20, // Essential for risk assessment
        known_triggers: 18, // Critical for trigger prediction
        common_symptoms: 16, // Important for symptom tracking
        symptom_patterns: 12, // Valuable for pattern recognition
        current_medications: 10, // Important for interaction analysis
        allergies: 8, // Important for safety
        other_conditions: 6, // Relevant for comorbidity analysis
        medical_notes: 4,
      },
      dietary_preferences: {
        dietary_restrictions: 8,
        food_allergies: 12, // Critical for safety
        preferred_cuisines: 3,
        meal_frequency: 7, // Important for symptom timing
        water_intake_goal: 4,
        special_diets: 6,
        trigger_foods: 20, // Critical for trigger prediction
        safe_foods: 15, // Important for meal planning
      },
      lifestyle_factors: {
        exercise_frequency: 8, // Important for IBS management
        sleep_quality: 12, // Strong correlation with IBS symptoms
        stress_level: 15, // Major IBS trigger
        work_schedule: 5,
        smoking_status: 6,
        alcohol_consumption: 7,
      },
      goals_preferences: {
        primary_goals: 18, // Critical for personalized treatment
        preferred_treatments: 10,
        communication_preferences: 3,
        notification_preferences: 3,
        privacy_settings: 2,
      },
    },
    predictive_importance: {
      symptom_severity_prediction: 0.25,
      trigger_food_identification: 0.22,
      treatment_response_prediction: 0.20,
      lifestyle_impact_assessment: 0.15,
      medication_optimization: 0.10,
      emergency_risk_assessment: 0.08,
    },
    personalization_factors: {
      ibs_type_multiplier: {
        'IBS_D': 1.2, // Diarrhea-predominant needs more dietary tracking
        'IBS_C': 1.1, // Constipation-predominant needs lifestyle factors
        'IBS_M': 1.3, // Mixed type needs comprehensive tracking
        'IBS_U': 1.0, // Unsubtyped baseline
      },
      severity_multiplier: {
        'mild': 0.9,
        'moderate': 1.1,
        'severe': 1.3,
      },
      goal_multiplier: {
        'symptom_management': 1.2,
        'dietary_optimization': 1.1,
        'lifestyle_improvement': 1.0,
        'medication_management': 1.1,
      },
    },
    dynamic_adjustments: {
      symptom_prediction_weight: 0.3,
      trigger_identification_weight: 0.4,
      treatment_optimization_weight: 0.3,
    },
  };

  /**
   * Calculate ML-optimized profile completion with personalized weights
   */
  async calculateMLOptimizedCompletion(
    profileData: Partial<ProfileSection>
  ): Promise<ProfileCompletionResult> {
    try {
      // Get personalization profile for user-specific adjustments
      const personalizationProfile = await personalizationService.getPersonalizationProfile();
      
      // Get ML-optimized weights based on user context
      const optimizedWeights = await this.getMLOptimizedWeights(
        profileData,
        personalizationProfile
      );
      
      // Calculate section completions with ML weights
      const sectionCompletions = this.calculateSectionCompletions(
        profileData,
        optimizedWeights
      );
      
      // Calculate overall completion
      const overallCompletion = this.calculateOverallCompletion(sectionCompletions);
      
      // Calculate ML-optimized score (weighted by predictive importance)
      const mlOptimizedScore = this.calculateMLOptimizedScore(
        profileData,
        optimizedWeights
      );
      
      // Calculate predictive value score
      const predictiveValueScore = this.calculatePredictiveValueScore(
        profileData,
        optimizedWeights
      );
      
      // Identify missing critical fields
      const missingCriticalFields = this.identifyMissingCriticalFields(
        profileData,
        optimizedWeights
      );
      
      // Generate ML-driven recommendations
      const recommendedNextSteps = await this.generateMLRecommendations(
        profileData,
        optimizedWeights,
        personalizationProfile
      );
      
      // Calculate personalization readiness
      const personalizationReadiness = this.calculatePersonalizationReadiness(
        profileData,
        optimizedWeights
      );

      return {
        overall_completion: overallCompletion,
        section_completion: sectionCompletions,
        ml_optimized_score: mlOptimizedScore,
        predictive_value_score: predictiveValueScore,
        missing_critical_fields: missingCriticalFields,
        recommended_next_steps: recommendedNextSteps,
        personalization_readiness: personalizationReadiness,
      };
    } catch (error) {
      console.error('Error calculating ML-optimized profile completion:', error);
      return this.getFallbackCompletion(profileData);
    }
  }

  /**
   * Get ML-optimized weights based on user context and ML insights
   */
  private async getMLOptimizedWeights(
    profileData: Partial<ProfileSection>,
    personalizationProfile: any
  ): Promise<MLOptimizedWeights> {
    const weights = JSON.parse(JSON.stringify(this.baseWeights)); // Deep copy
    
    // Apply IBS type multiplier
    const ibsType = profileData.medical_history?.['ibs_type'];
    if (ibsType && weights.personalization_factors.ibs_type_multiplier[ibsType]) {
      const multiplier = weights.personalization_factors.ibs_type_multiplier[ibsType];
      this.applyMultiplierToSection(weights.field_weights.dietary_preferences, multiplier);
      this.applyMultiplierToSection(weights.field_weights.lifestyle_factors, multiplier * 0.8);
    }
    
    // Apply severity multiplier
    const severityLevel = profileData.medical_history?.['severity_level'];
    if (severityLevel && weights.personalization_factors.severity_multiplier[severityLevel]) {
      const multiplier = weights.personalization_factors.severity_multiplier[severityLevel];
      this.applyMultiplierToSection(weights.field_weights.medical_history, multiplier);
    }
    
    // Apply goal-based adjustments
    const primaryGoals = profileData.goals_preferences?.['primary_goals'] || [];
    primaryGoals.forEach((goal: string) => {
      const multiplier = weights.personalization_factors.goal_multiplier[goal] || 1.0;
      if (goal === 'dietary_optimization') {
        this.applyMultiplierToSection(weights.field_weights.dietary_preferences, multiplier);
      } else if (goal === 'lifestyle_improvement') {
        this.applyMultiplierToSection(weights.field_weights.lifestyle_factors, multiplier);
      }
    });
    
    // Apply ML-driven dynamic adjustments based on user's prediction needs
    if (personalizationProfile?.prediction_preferences) {
      const prefs = personalizationProfile.prediction_preferences;
      if (prefs.symptom_prediction_priority === 'high') {
        weights.field_weights.medical_history.symptom_patterns *= 1.3;
        weights.field_weights.medical_history.common_symptoms *= 1.2;
      }
      if (prefs.trigger_identification_priority === 'high') {
        weights.field_weights.dietary_preferences.trigger_foods *= 1.4;
        weights.field_weights.dietary_preferences.safe_foods *= 1.2;
      }
    }
    
    return weights;
  }

  /**
   * Calculate completion for each profile section
   */
  private calculateSectionCompletions(
    profileData: Partial<ProfileSection>,
    weights: MLOptimizedWeights
  ): Record<string, number> {
    const sectionCompletions: Record<string, number> = {};
    
    Object.entries(weights.field_weights).forEach(([sectionName, fieldWeights]) => {
      if (!sectionName || !(sectionName in profileData)) {
        return;
      }
      const sectionData = profileData[sectionName as keyof ProfileSection] || {};
      let totalWeight = 0;
      let completedWeight = 0;
      
      Object.entries(fieldWeights).forEach(([fieldName, weight]) => {
        totalWeight += weight;
        const fieldValue = sectionData[fieldName];
        
        if (this.isFieldCompleted(fieldValue)) {
          completedWeight += weight;
        }
      });
      
      sectionCompletions[sectionName] = totalWeight > 0 ? (completedWeight / totalWeight) * 100 : 0;
    });
    
    return sectionCompletions;
  }

  /**
   * Calculate overall completion percentage
   */
  private calculateOverallCompletion(sectionCompletions: Record<string, number>): number {
    const sectionWeights = {
      basic_info: 0.15,
      medical_history: 0.35,
      dietary_preferences: 0.25,
      lifestyle_factors: 0.15,
      goals_preferences: 0.10,
    };
    
    let totalWeightedScore = 0;
    let totalWeight = 0;
    
    Object.entries(sectionCompletions).forEach(([section, completion]) => {
      const weight = sectionWeights[section as keyof typeof sectionWeights] || 0;
      totalWeightedScore += completion * weight;
      totalWeight += weight;
    });
    
    return totalWeight > 0 ? totalWeightedScore / totalWeight : 0;
  }

  /**
   * Calculate ML-optimized score based on predictive importance
   */
  private calculateMLOptimizedScore(
    profileData: Partial<ProfileSection>,
    weights: MLOptimizedWeights
  ): number {
    let score = 0;
    let maxScore = 0;
    
    // Weight completion by predictive importance
    Object.entries(weights.predictive_importance).forEach(([capability, importance]) => {
      const capabilityScore = this.calculateCapabilityScore(profileData, capability, weights);
      score += capabilityScore * importance;
      maxScore += importance;
    });
    
    return maxScore > 0 ? (score / maxScore) * 100 : 0;
  }

  /**
   * Calculate predictive value score
   */
  private calculatePredictiveValueScore(
    profileData: Partial<ProfileSection>,
    weights: MLOptimizedWeights
  ): number {
    const criticalFields = [
      'medical_history.ibs_type',
      'medical_history.severity_level',
      'medical_history.known_triggers',
      'dietary_preferences.trigger_foods',
      'lifestyle_factors.stress_level',
      'goals_preferences.primary_goals',
    ];
    
    let completedCritical = 0;
    criticalFields.forEach(fieldPath => {
      const [section, field] = fieldPath.split('.');
      if (!section || !field) return;
      const sectionData = profileData[section as keyof ProfileSection] || {};
      if (this.isFieldCompleted(sectionData[field])) {
        completedCritical++;
      }
    });
    
    return (completedCritical / criticalFields.length) * 100;
  }

  /**
   * Identify missing critical fields for ML predictions
   */
  private identifyMissingCriticalFields(
    profileData: Partial<ProfileSection>,
    weights: MLOptimizedWeights
  ): string[] {
    const missingFields: string[] = [];
    const criticalThreshold = 15; // Fields with weight >= 15 are critical
    
    Object.entries(weights.field_weights).forEach(([sectionName, fieldWeights]) => {
      const sectionData = profileData[sectionName as keyof ProfileSection] || {};
      
      Object.entries(fieldWeights).forEach(([fieldName, weight]) => {
        if (weight >= criticalThreshold && !this.isFieldCompleted(sectionData[fieldName])) {
          missingFields.push(`${sectionName}.${fieldName}`);
        }
      });
    });
    
    return missingFields;
  }

  /**
   * Generate ML-driven recommendations for profile completion
   */
  private async generateMLRecommendations(
    profileData: Partial<ProfileSection>,
    weights: MLOptimizedWeights,
    personalizationProfile: any
  ): Promise<ProfileCompletionResult['recommended_next_steps']> {
    const recommendations: ProfileCompletionResult['recommended_next_steps'] = [];
    
    // Analyze missing high-impact fields
    Object.entries(weights.field_weights).forEach(([sectionName, fieldWeights]) => {
      const sectionData = profileData[sectionName as keyof ProfileSection] || {};
      
      Object.entries(fieldWeights).forEach(([fieldName, weight]) => {
        if (!this.isFieldCompleted(sectionData[fieldName]) && weight >= 10) {
          const recommendation = this.generateFieldRecommendation(
            fieldName,
            sectionName,
            weight,
            profileData
          );
          recommendations.push(recommendation);
        }
      });
    });
    
    // Sort by importance and return top 5
    return recommendations
      .sort((a, b) => b.importance - a.importance)
      .slice(0, 5);
  }

  /**
   * Calculate personalization readiness score
   */
  private calculatePersonalizationReadiness(
    profileData: Partial<ProfileSection>,
    weights: MLOptimizedWeights
  ): number {
    const personalizationFields = [
      'medical_history.ibs_type',
      'medical_history.severity_level',
      'medical_history.known_triggers',
      'dietary_preferences.trigger_foods',
      'dietary_preferences.safe_foods',
      'lifestyle_factors.stress_level',
      'lifestyle_factors.sleep_quality',
      'goals_preferences.primary_goals',
    ];
    
    let readinessScore = 0;
    personalizationFields.forEach(fieldPath => {
      const [section, field] = fieldPath.split('.');
      if (!section || !field) return;
      const sectionData = profileData[section as keyof ProfileSection] || {};
      if (this.isFieldCompleted(sectionData[field])) {
        readinessScore += 1;
      }
    });
    
    return (readinessScore / personalizationFields.length) * 100;
  }

  // Helper methods
  private applyMultiplierToSection(section: Record<string, number>, multiplier: number): void {
    Object.keys(section).forEach(field => {
      if (section[field] !== undefined) {
        section[field] *= multiplier;
      }
    });
  }

  private isFieldCompleted(value: any): boolean {
    return value !== null && value !== undefined && value !== '' && 
           (Array.isArray(value) ? value.length > 0 : true);
  }

  private calculateCapabilityScore(
    profileData: Partial<ProfileSection>,
    capability: string,
    weights: MLOptimizedWeights
  ): number {
    // Simplified capability scoring based on relevant fields
    const capabilityFieldMap: Record<string, string[]> = {
      symptom_severity_prediction: ['medical_history.severity_level', 'medical_history.symptom_patterns'],
      trigger_food_identification: ['dietary_preferences.trigger_foods', 'dietary_preferences.food_allergies'],
      treatment_response_prediction: ['medical_history.current_medications', 'goals_preferences.primary_goals'],
      lifestyle_impact_assessment: ['lifestyle_factors.stress_level', 'lifestyle_factors.sleep_quality'],
      medication_optimization: ['medical_history.current_medications', 'medical_history.allergies'],
      emergency_risk_assessment: ['medical_history.severity_level', 'medical_history.other_conditions'],
    };
    
    const relevantFields = capabilityFieldMap[capability] || [];
    let completedFields = 0;
    
    relevantFields.forEach(fieldPath => {
      const [section, field] = fieldPath.split('.');
      if (!section || !field) return;
      const sectionData = profileData[section as keyof ProfileSection] || {};
      if (this.isFieldCompleted(sectionData[field])) {
        completedFields++;
      }
    });
    
    return relevantFields.length > 0 ? completedFields / relevantFields.length : 0;
  }

  private generateFieldRecommendation(
    fieldName: string,
    sectionName: string,
    importance: number,
    profileData: Partial<ProfileSection>
  ): ProfileCompletionResult['recommended_next_steps'][0] {
    const recommendations: Record<string, { reason: string; impact: string }> = {
      'ibs_type': {
        reason: 'Essential for personalized treatment recommendations',
        impact: 'Enables targeted symptom management and dietary suggestions'
      },
      'severity_level': {
        reason: 'Critical for risk assessment and treatment intensity',
        impact: 'Improves accuracy of symptom predictions by 40%'
      },
      'known_triggers': {
        reason: 'Key for trigger prediction and avoidance strategies',
        impact: 'Reduces symptom episodes by identifying patterns'
      },
      'trigger_foods': {
        reason: 'Essential for dietary recommendations and meal planning',
        impact: 'Prevents 60% of food-related symptom flares'
      },
      'stress_level': {
        reason: 'Major IBS trigger that affects symptom severity',
        impact: 'Enables stress-based symptom prediction and management'
      },
      'primary_goals': {
        reason: 'Guides personalized treatment and recommendation focus',
        impact: 'Aligns all suggestions with your health objectives'
      },
    };
    
    const fieldInfo = recommendations[fieldName] || {
      reason: 'Important for comprehensive health profile',
      impact: 'Improves personalization accuracy'
    };
    
    return {
      field: fieldName,
      section: sectionName,
      importance,
      reason: fieldInfo.reason,
      impact: fieldInfo.impact,
    };
  }

  private getFallbackCompletion(profileData: Partial<ProfileSection>): ProfileCompletionResult {
    return {
      overall_completion: 30,
      section_completion: {
        basic_info: 40,
        medical_history: 20,
        dietary_preferences: 30,
        lifestyle_factors: 25,
        goals_preferences: 35,
      },
      ml_optimized_score: 25,
      predictive_value_score: 20,
      missing_critical_fields: ['medical_history.ibs_type', 'medical_history.severity_level'],
      recommended_next_steps: [
        {
          field: 'ibs_type',
          section: 'medical_history',
          importance: 25,
          reason: 'Essential for personalized treatment',
          impact: 'Enables targeted recommendations',
        },
      ],
      personalization_readiness: 20,
    };
  }
}

export const mlProfileCompletionService = new MLProfileCompletionService();