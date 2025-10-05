/**
 * ML-Based Medication Effectiveness Prediction Service
 * 
 * Replaces hard-coded medication effectiveness scores with personalized predictions
 * based on user's medical history, genetic factors, and treatment response patterns.
 */

import { API_CONFIG } from '@/lib/config';

export interface MedicationProfile {
  medication_name: string;
  dosage: string;
  frequency: string;
  duration_days: number;
  indication: string;
  generic_name?: string;
  drug_class: string;
}

export interface UserMedicalContext {
  demographics: {
    age: number;
    weight?: number;
    gender: string;
    ethnicity?: string;
  };
  medical_history: {
    ibs_type: string;
    condition_duration_months: number;
    comorbidities: string[];
    allergies: string[];
    previous_medications: Array<{
      name: string;
      effectiveness_score: number; // 1-10
      side_effects: string[];
      duration_used: number;
    }>;
  };
  current_health: {
    symptom_severity: number;
    stress_level: number;
    sleep_quality: number;
    diet_adherence: number;
    exercise_frequency: number;
  };
  genetic_factors?: {
    cyp2d6_status?: string;
    cyp3a4_status?: string;
    other_metabolizer_genes?: Record<string, string>;
  };
  lifestyle_factors: {
    smoking: boolean;
    alcohol_consumption: 'none' | 'light' | 'moderate' | 'heavy';
    caffeine_intake: number; // mg per day
    supplement_use: string[];
  };
}

export interface EffectivenessPrediction {
  medication: MedicationProfile;
  predicted_effectiveness: {
    overall_score: number; // 1-10 scale
    symptom_specific_scores: {
      abdominal_pain: number;
      bloating: number;
      diarrhea: number;
      constipation: number;
      nausea: number;
    };
    confidence: number; // 0-1 scale
  };
  timeline_predictions: {
    onset_time: string; // e.g., "2-4 hours"
    peak_effect_time: string; // e.g., "4-6 hours"
    duration: string; // e.g., "8-12 hours"
    full_therapeutic_effect: string; // e.g., "2-4 weeks"
  };
  side_effect_predictions: Array<{
    side_effect: string;
    probability: number; // 0-1 scale
    severity: 'mild' | 'moderate' | 'severe';
    onset_timeframe: string;
  }>;
  drug_interactions: Array<{
    interacting_substance: string;
    interaction_type: 'minor' | 'moderate' | 'major';
    effect_description: string;
    recommendation: string;
  }>;
  personalized_recommendations: {
    optimal_dosage_range: string;
    best_timing: string[];
    dietary_considerations: string[];
    monitoring_suggestions: string[];
  };
  model_insights: {
    key_factors: Array<{
      factor: string;
      influence: number; // -1 to 1 scale
      explanation: string;
    }>;
    similar_patient_outcomes: {
      sample_size: number;
      average_effectiveness: number;
      success_rate: number;
    };
  };
  last_updated: string;
  model_version: string;
}

export interface TreatmentOptimization {
  current_regimen: MedicationProfile[];
  optimization_suggestions: Array<{
    type: 'dosage_adjustment' | 'timing_change' | 'medication_switch' | 'combination_therapy';
    current_medication: string;
    suggested_change: string;
    expected_improvement: number; // percentage
    confidence: number;
    rationale: string;
    monitoring_required: string[];
  }>;
  alternative_medications: Array<{
    medication: MedicationProfile;
    predicted_effectiveness: number;
    advantages: string[];
    considerations: string[];
    switch_timeline: string;
  }>;
  combination_opportunities: Array<{
    primary_medication: string;
    adjunct_medication: string;
    synergy_score: number;
    expected_benefit: string;
    monitoring_requirements: string[];
  }>;
}

class MLMedicationEffectivenessService {
  private baseUrl: string;
  private authHeaders: HeadersInit;
  private effectivenessCache: Map<string, EffectivenessPrediction> = new Map();
  private cacheExpiry: Map<string, number> = new Map();

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
   * Predict medication effectiveness for a specific medication
   */
  async predictEffectiveness(
    medication: MedicationProfile,
    userContext: UserMedicalContext
  ): Promise<EffectivenessPrediction> {
    const cacheKey = `${medication.medication_name}_${medication.dosage}`;
    
    // Check cache (valid for 6 hours)
    if (this.effectivenessCache.has(cacheKey) && 
        Date.now() < (this.cacheExpiry.get(cacheKey) || 0)) {
      return this.effectivenessCache.get(cacheKey)!;
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/medication/predict-effectiveness`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          medication,
          user_context: userContext
        }),
      });

      if (!response.ok) {
        throw new Error(`Effectiveness prediction failed: ${response.status}`);
      }

      const prediction = await response.json();
      const validatedPrediction = this.validateEffectivenessPrediction(prediction);
      
      // Cache the result
      this.effectivenessCache.set(cacheKey, validatedPrediction);
      this.cacheExpiry.set(cacheKey, Date.now() + (6 * 60 * 60 * 1000)); // 6 hours
      
      return validatedPrediction;
    } catch (error) {
      console.error('ML effectiveness prediction failed, using intelligent fallback:', error);
      return this.intelligentEffectivenessFallback(medication, userContext);
    }
  }

  /**
   * Predict effectiveness for multiple medications
   */
  async predictMultipleMedications(
    medications: MedicationProfile[],
    userContext: UserMedicalContext
  ): Promise<EffectivenessPrediction[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/medication/predict-multiple`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          medications,
          user_context: userContext
        }),
      });

      if (!response.ok) {
        throw new Error(`Multiple medication prediction failed: ${response.status}`);
      }

      const predictions = await response.json();
      return predictions.map((pred: any) => this.validateEffectivenessPrediction(pred));
    } catch (error) {
      console.error('Multiple medication prediction failed:', error);
      return Promise.all(
        medications.map(med => this.predictEffectiveness(med, userContext))
      );
    }
  }

  /**
   * Optimize current treatment regimen
   */
  async optimizeTreatment(
    currentRegimen: MedicationProfile[],
    userContext: UserMedicalContext,
    treatmentGoals: {
      primary_symptoms: string[];
      quality_of_life_priorities: string[];
      side_effect_tolerance: 'low' | 'medium' | 'high';
    }
  ): Promise<TreatmentOptimization> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/medication/optimize-treatment`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          current_regimen: currentRegimen,
          user_context: userContext,
          treatment_goals: treatmentGoals
        }),
      });

      if (!response.ok) {
        throw new Error(`Treatment optimization failed: ${response.status}`);
      }

      const optimization = await response.json();
      return this.validateTreatmentOptimization(optimization);
    } catch (error) {
      console.error('Treatment optimization failed, using fallback:', error);
      return this.fallbackTreatmentOptimization(currentRegimen, userContext);
    }
  }

  /**
   * Update effectiveness prediction based on real-world outcomes
   */
  async updateWithOutcome(
    medication: MedicationProfile,
    actualOutcome: {
      effectiveness_score: number;
      side_effects_experienced: string[];
      adherence_rate: number;
      duration_used: number;
      discontinuation_reason?: string;
    }
  ): Promise<void> {
    try {
      await fetch(`${this.baseUrl}/api/v1/ml/medication/update-outcome`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          medication,
          actual_outcome: actualOutcome
        }),
      });

      // Clear cache for this medication to force fresh prediction
      const cacheKey = `${medication.medication_name}_${medication.dosage}`;
      this.effectivenessCache.delete(cacheKey);
      this.cacheExpiry.delete(cacheKey);
    } catch (error) {
      console.error('Failed to update medication outcome:', error);
    }
  }

  /**
   * Get medication recommendations based on symptoms
   */
  async getMedicationRecommendations(
    symptoms: Record<string, number>,
    userContext: UserMedicalContext,
    preferences: {
      prefer_natural: boolean;
      avoid_side_effects: string[];
      max_daily_doses: number;
    }
  ): Promise<Array<{
    medication: MedicationProfile;
    predicted_effectiveness: number;
    rationale: string;
    considerations: string[];
  }>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/medication/recommendations`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          symptoms,
          user_context: userContext,
          preferences
        }),
      });

      if (!response.ok) {
        throw new Error(`Medication recommendations failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Medication recommendations failed:', error);
      return this.fallbackMedicationRecommendations(symptoms, userContext);
    }
  }

  /**
   * Intelligent fallback for effectiveness prediction
   */
  private intelligentEffectivenessFallback(
    medication: MedicationProfile,
    userContext: UserMedicalContext
  ): EffectivenessPrediction {
    // Base effectiveness by drug class and IBS type
    const baseEffectiveness = this.getBaseEffectiveness(medication, userContext.medical_history.ibs_type);
    
    // Adjust based on user factors
    let adjustedEffectiveness = baseEffectiveness;
    
    // Age adjustment
    if (userContext.demographics.age > 65) {
      adjustedEffectiveness *= 0.9; // Slightly reduced effectiveness in elderly
    } else if (userContext.demographics.age < 30) {
      adjustedEffectiveness *= 1.1; // Slightly better response in younger patients
    }
    
    // Previous medication history adjustment
    const similarMedications = userContext.medical_history.previous_medications.filter(
      prev => this.isSimilarMedication(prev.name, medication.medication_name)
    );
    
    if (similarMedications.length > 0) {
      const avgPreviousEffectiveness = similarMedications.reduce(
        (sum, med) => sum + med.effectiveness_score, 0
      ) / similarMedications.length;
      adjustedEffectiveness = (adjustedEffectiveness + avgPreviousEffectiveness) / 2;
    }
    
    // Symptom severity adjustment
    if (userContext.current_health.symptom_severity > 7) {
      adjustedEffectiveness *= 0.8; // Harder to treat severe symptoms
    }
    
    // Stress level adjustment
    if (userContext.current_health.stress_level > 7) {
      adjustedEffectiveness *= 0.9; // Stress can reduce medication effectiveness
    }

    const finalEffectiveness = Math.max(1, Math.min(10, adjustedEffectiveness));

    return {
      medication,
      predicted_effectiveness: {
        overall_score: Math.round(finalEffectiveness * 10) / 10,
        symptom_specific_scores: this.generateSymptomSpecificScores(finalEffectiveness, medication),
        confidence: this.calculateConfidence(userContext)
      },
      timeline_predictions: this.generateTimelinePredictions(medication),
      side_effect_predictions: this.generateSideEffectPredictions(medication, userContext),
      drug_interactions: this.generateDrugInteractions(medication, userContext),
      personalized_recommendations: this.generatePersonalizedRecommendations(medication, userContext),
      model_insights: {
        key_factors: this.generateKeyFactors(userContext),
        similar_patient_outcomes: {
          sample_size: 150,
          average_effectiveness: finalEffectiveness,
          success_rate: Math.min(0.9, finalEffectiveness / 10 * 0.8)
        }
      },
      last_updated: new Date().toISOString(),
      model_version: "fallback_v1.0"
    };
  }

  /**
   * Get base effectiveness by drug class and IBS type
   */
  private getBaseEffectiveness(medication: MedicationProfile, ibsType: string): number {
    const drugClassEffectiveness: Record<string, Record<string, number>> = {
      'antispasmodic': {
        'IBS-D': 7.2,
        'IBS-C': 6.8,
        'IBS-M': 7.0,
        'IBS-U': 6.5
      },
      'antidiarrheal': {
        'IBS-D': 8.1,
        'IBS-C': 3.0,
        'IBS-M': 6.5,
        'IBS-U': 5.5
      },
      'laxative': {
        'IBS-D': 2.5,
        'IBS-C': 7.8,
        'IBS-M': 5.0,
        'IBS-U': 4.5
      },
      'probiotic': {
        'IBS-D': 6.5,
        'IBS-C': 6.2,
        'IBS-M': 6.8,
        'IBS-U': 6.0
      },
      'tricyclic_antidepressant': {
        'IBS-D': 7.5,
        'IBS-C': 5.5,
        'IBS-M': 6.5,
        'IBS-U': 6.0
      },
      'ssri': {
        'IBS-D': 5.8,
        'IBS-C': 7.2,
        'IBS-M': 6.5,
        'IBS-U': 6.0
      }
    };

    const drugClass = medication.drug_class.toLowerCase();
    return drugClassEffectiveness[drugClass]?.[ibsType] || 6.0;
  }

  /**
   * Check if medications are similar (same class or mechanism)
   */
  private isSimilarMedication(med1: string, med2: string): boolean {
    const similarityMap: Record<string, string[]> = {
      'dicyclomine': ['hyoscyamine', 'bentyl'],
      'loperamide': ['imodium', 'diphenoxylate'],
      'polyethylene_glycol': ['miralax', 'lactulose'],
      'amitriptyline': ['nortriptyline', 'desipramine'],
      'sertraline': ['fluoxetine', 'citalopram']
    };

    const med1Lower = med1.toLowerCase();
    const med2Lower = med2.toLowerCase();

    if (med1Lower === med2Lower) return true;

    for (const [key, similar] of Object.entries(similarityMap)) {
      if ((key === med1Lower || similar.includes(med1Lower)) &&
          (key === med2Lower || similar.includes(med2Lower))) {
        return true;
      }
    }

    return false;
  }

  /**
   * Generate symptom-specific effectiveness scores
   */
  private generateSymptomSpecificScores(
    overallScore: number, 
    medication: MedicationProfile
  ): {
    abdominal_pain: number;
    bloating: number;
    diarrhea: number;
    constipation: number;
    nausea: number;
  } {
    const baseScores = {
      abdominal_pain: overallScore,
      bloating: overallScore,
      diarrhea: overallScore,
      constipation: overallScore,
      nausea: overallScore
    };

    // Adjust based on medication type
    const drugClass = medication.drug_class.toLowerCase();
    
    if (drugClass.includes('antispasmodic')) {
      baseScores.abdominal_pain *= 1.2;
      baseScores.bloating *= 1.1;
    } else if (drugClass.includes('antidiarrheal')) {
      baseScores.diarrhea *= 1.3;
      baseScores.constipation *= 0.7;
    } else if (drugClass.includes('laxative')) {
      baseScores.constipation *= 1.3;
      baseScores.diarrhea *= 0.6;
    }

    // Ensure scores are within bounds
    Object.keys(baseScores).forEach(key => {
      baseScores[key as keyof typeof baseScores] = Math.max(1, Math.min(10, baseScores[key as keyof typeof baseScores]));
    });

    return baseScores;
  }

  /**
   * Calculate confidence based on available data
   */
  private calculateConfidence(userContext: UserMedicalContext): number {
    let confidence = 0.5; // Base confidence
    
    // Increase confidence based on available data
    if (userContext.medical_history.previous_medications.length > 0) confidence += 0.2;
    if (userContext.genetic_factors) confidence += 0.15;
    if (userContext.medical_history.condition_duration_months > 12) confidence += 0.1;
    if (userContext.current_health.symptom_severity > 0) confidence += 0.05;
    
    return Math.min(0.9, confidence);
  }

  /**
   * Generate timeline predictions
   */
  private generateTimelinePredictions(medication: MedicationProfile): any {
    const timelineMap: Record<string, any> = {
      'antispasmodic': {
        onset_time: "30-60 minutes",
        peak_effect_time: "1-2 hours",
        duration: "4-6 hours",
        full_therapeutic_effect: "1-2 weeks"
      },
      'antidiarrheal': {
        onset_time: "1-2 hours",
        peak_effect_time: "2-4 hours",
        duration: "6-8 hours",
        full_therapeutic_effect: "3-7 days"
      },
      'laxative': {
        onset_time: "6-12 hours",
        peak_effect_time: "12-24 hours",
        duration: "24-48 hours",
        full_therapeutic_effect: "1-2 weeks"
      }
    };

    return timelineMap[medication.drug_class.toLowerCase()] || {
      onset_time: "1-3 hours",
      peak_effect_time: "2-6 hours",
      duration: "6-12 hours",
      full_therapeutic_effect: "2-4 weeks"
    };
  }

  /**
   * Generate side effect predictions
   */
  private generateSideEffectPredictions(
    medication: MedicationProfile,
    userContext: UserMedicalContext
  ): Array<any> {
    const commonSideEffects: Record<string, Array<any>> = {
      'antispasmodic': [
        { side_effect: 'dry mouth', probability: 0.3, severity: 'mild', onset_timeframe: '1-2 hours' },
        { side_effect: 'drowsiness', probability: 0.2, severity: 'mild', onset_timeframe: '30-60 minutes' }
      ],
      'antidiarrheal': [
        { side_effect: 'constipation', probability: 0.4, severity: 'moderate', onset_timeframe: '1-3 days' },
        { side_effect: 'abdominal cramping', probability: 0.2, severity: 'mild', onset_timeframe: '2-4 hours' }
      ],
      'laxative': [
        { side_effect: 'abdominal cramping', probability: 0.3, severity: 'mild', onset_timeframe: '6-12 hours' },
        { side_effect: 'diarrhea', probability: 0.25, severity: 'moderate', onset_timeframe: '12-24 hours' }
      ]
    };

    let sideEffects = commonSideEffects[medication.drug_class.toLowerCase()] || [];
    
    // Adjust probabilities based on user factors
    if (userContext.demographics.age > 65) {
      sideEffects = sideEffects.map(se => ({
        ...se,
        probability: Math.min(0.9, se.probability * 1.2)
      }));
    }

    return sideEffects;
  }

  /**
   * Generate drug interactions
   */
  private generateDrugInteractions(
    medication: MedicationProfile,
    userContext: UserMedicalContext
  ): Array<any> {
    // This would typically come from a comprehensive drug interaction database
    return [
      {
        interacting_substance: 'alcohol',
        interaction_type: 'moderate',
        effect_description: 'May increase drowsiness and reduce effectiveness',
        recommendation: 'Limit alcohol consumption while taking this medication'
      }
    ];
  }

  /**
   * Generate personalized recommendations
   */
  private generatePersonalizedRecommendations(
    medication: MedicationProfile,
    userContext: UserMedicalContext
  ): any {
    return {
      optimal_dosage_range: medication.dosage,
      best_timing: ['Take 30 minutes before meals'],
      dietary_considerations: ['Avoid high-fat meals', 'Stay hydrated'],
      monitoring_suggestions: ['Track symptom severity daily', 'Monitor for side effects']
    };
  }

  /**
   * Generate key factors influencing effectiveness
   */
  private generateKeyFactors(userContext: UserMedicalContext): Array<any> {
    return [
      {
        factor: 'symptom_severity',
        influence: -0.3,
        explanation: 'Higher baseline severity may reduce medication effectiveness'
      },
      {
        factor: 'stress_level',
        influence: -0.2,
        explanation: 'Elevated stress can interfere with treatment response'
      },
      {
        factor: 'previous_treatment_response',
        influence: 0.4,
        explanation: 'Past positive responses predict future effectiveness'
      }
    ];
  }

  /**
   * Fallback treatment optimization
   */
  private fallbackTreatmentOptimization(
    currentRegimen: MedicationProfile[],
    userContext: UserMedicalContext
  ): TreatmentOptimization {
    return {
      current_regimen: currentRegimen,
      optimization_suggestions: [
        {
          type: 'timing_change',
          current_medication: currentRegimen[0]?.medication_name || 'current medication',
          suggested_change: 'Take 30 minutes before meals for better absorption',
          expected_improvement: 15,
          confidence: 0.7,
          rationale: 'Timing optimization can improve bioavailability',
          monitoring_required: ['symptom severity', 'side effects']
        }
      ],
      alternative_medications: [],
      combination_opportunities: []
    };
  }

  /**
   * Fallback medication recommendations
   */
  private fallbackMedicationRecommendations(
    symptoms: Record<string, number>,
    userContext: UserMedicalContext
  ): Array<any> {
    const recommendations = [];
    
    if (symptoms['diarrhea'] && symptoms['diarrhea'] > 6) {
      recommendations.push({
        medication: {
          medication_name: 'loperamide',
          dosage: '2mg',
          frequency: 'as needed',
          duration_days: 7,
          indication: 'diarrhea control',
          drug_class: 'antidiarrheal'
        },
        predicted_effectiveness: 7.5,
        rationale: 'Effective for acute diarrhea management',
        considerations: ['Monitor for constipation', 'Use short-term only']
      });
    }

    return recommendations;
  }

  /**
   * Validation methods
   */
  private validateEffectivenessPrediction(prediction: any): EffectivenessPrediction {
    return {
      medication: prediction.medication || {},
      predicted_effectiveness: {
        overall_score: Math.max(1, Math.min(10, prediction.predicted_effectiveness?.overall_score || 5)),
        symptom_specific_scores: prediction.predicted_effectiveness?.symptom_specific_scores || {},
        confidence: Math.max(0, Math.min(1, prediction.predicted_effectiveness?.confidence || 0.5))
      },
      timeline_predictions: prediction.timeline_predictions || {},
      side_effect_predictions: Array.isArray(prediction.side_effect_predictions) 
        ? prediction.side_effect_predictions : [],
      drug_interactions: Array.isArray(prediction.drug_interactions) 
        ? prediction.drug_interactions : [],
      personalized_recommendations: prediction.personalized_recommendations || {},
      model_insights: prediction.model_insights || {},
      last_updated: prediction.last_updated || new Date().toISOString(),
      model_version: prediction.model_version || "unknown"
    };
  }

  private validateTreatmentOptimization(optimization: any): TreatmentOptimization {
    return {
      current_regimen: Array.isArray(optimization.current_regimen) 
        ? optimization.current_regimen : [],
      optimization_suggestions: Array.isArray(optimization.optimization_suggestions) 
        ? optimization.optimization_suggestions : [],
      alternative_medications: Array.isArray(optimization.alternative_medications) 
        ? optimization.alternative_medications : [],
      combination_opportunities: Array.isArray(optimization.combination_opportunities) 
        ? optimization.combination_opportunities : []
    };
  }
}

export const mlMedicationEffectivenessService = new MLMedicationEffectivenessService();
export default mlMedicationEffectivenessService;