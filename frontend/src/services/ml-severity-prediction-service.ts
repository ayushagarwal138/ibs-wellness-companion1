/**
 * ML-Based Severity Prediction Service
 * 
 * Replaces hard-coded severity values with dynamic AI/ML predictions
 * based on user's historical data, current symptoms, and contextual factors.
 */

import { API_CONFIG } from '@/lib/config';

export interface SeverityPredictionInput {
  currentSymptoms: {
    abdominal_pain?: number;
    bloating?: number;
    diarrhea?: number;
    constipation?: number;
    nausea?: number;
    fatigue?: number;
  };
  contextualFactors: {
    stress_level?: number;
    sleep_quality?: number;
    recent_meals?: string[];
    medications?: string[];
    time_of_day?: string;
    menstrual_cycle_phase?: string;
  };
  historicalData?: {
    average_severity?: number;
    severity_variance?: number;
    recent_trend?: 'improving' | 'stable' | 'worsening';
  };
  userProfile?: {
    ibs_type?: string;
    age?: number;
    duration_of_condition?: number;
    sensitivity_level?: 'low' | 'medium' | 'high';
  };
}

export interface SeverityPredictionResult {
  predicted_severity: number; // 1-10 scale
  confidence: number; // 0-1 scale
  severity_category: 'mild' | 'moderate' | 'severe' | 'critical';
  contributing_factors: Array<{
    factor: string;
    impact: number; // -1 to 1 scale
    confidence: number;
  }>;
  recommendations: string[];
  prediction_horizon: string; // e.g., "next 2-4 hours"
  model_version: string;
}

export interface PersonalizedThresholds {
  mild_threshold: number;
  moderate_threshold: number;
  severe_threshold: number;
  critical_threshold: number;
  confidence: number;
}

class MLSeverityPredictionService {
  private baseUrl: string;
  private authHeaders: HeadersInit;

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
   * Predict severity based on current symptoms and context
   */
  async predictSeverity(input: SeverityPredictionInput): Promise<SeverityPredictionResult> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/predict/severity-advanced`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(input),
      });

      if (!response.ok) {
        throw new Error(`Severity prediction failed: ${response.status}`);
      }

      const result = await response.json();
      return this.validateSeverityPrediction(result);
    } catch (error) {
      console.error('ML severity prediction failed, using intelligent fallback:', error);
      return this.intelligentFallbackPrediction(input);
    }
  }

  /**
   * Get personalized severity thresholds for the user
   */
  async getPersonalizedThresholds(): Promise<PersonalizedThresholds> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/user/severity-thresholds`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`Threshold retrieval failed: ${response.status}`);
      }

      const thresholds = await response.json();
      return this.validateThresholds(thresholds);
    } catch (error) {
      console.error('Failed to get personalized thresholds, using adaptive defaults:', error);
      return this.getAdaptiveDefaultThresholds();
    }
  }

  /**
   * Predict severity progression over time
   */
  async predictSeverityProgression(
    input: SeverityPredictionInput,
    timeHorizon: number = 24 // hours
  ): Promise<Array<{ timestamp: string; predicted_severity: number; confidence: number }>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/predict/severity-progression`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ ...input, time_horizon_hours: timeHorizon }),
      });

      if (!response.ok) {
        throw new Error(`Severity progression prediction failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Severity progression prediction failed:', error);
      return this.generateProgressionFallback(input, timeHorizon);
    }
  }

  /**
   * Intelligent fallback when ML service is unavailable
   */
  private intelligentFallbackPrediction(input: SeverityPredictionInput): SeverityPredictionResult {
    // Calculate base severity from current symptoms
    const symptoms = input.currentSymptoms;
    const symptomValues = Object.values(symptoms).filter(v => v !== undefined) as number[];
    const avgSymptomSeverity = symptomValues.length > 0 
      ? symptomValues.reduce((sum, val) => sum + val, 0) / symptomValues.length 
      : 5;

    // Apply contextual adjustments
    let adjustedSeverity = avgSymptomSeverity;
    const factors: Array<{ factor: string; impact: number; confidence: number }> = [];

    // Stress impact
    if (input.contextualFactors.stress_level) {
      const stressImpact = (input.contextualFactors.stress_level - 5) * 0.3;
      adjustedSeverity += stressImpact;
      factors.push({
        factor: 'stress_level',
        impact: stressImpact / 10,
        confidence: 0.8
      });
    }

    // Sleep quality impact
    if (input.contextualFactors.sleep_quality) {
      const sleepImpact = (5 - input.contextualFactors.sleep_quality) * 0.2;
      adjustedSeverity += sleepImpact;
      factors.push({
        factor: 'sleep_quality',
        impact: sleepImpact / 10,
        confidence: 0.7
      });
    }

    // Historical trend impact
    if (input.historicalData?.recent_trend) {
      let trendImpact = 0;
      switch (input.historicalData.recent_trend) {
        case 'improving':
          trendImpact = -0.5;
          break;
        case 'worsening':
          trendImpact = 0.5;
          break;
        default:
          trendImpact = 0;
      }
      adjustedSeverity += trendImpact;
      factors.push({
        factor: 'historical_trend',
        impact: trendImpact / 10,
        confidence: 0.6
      });
    }

    // Ensure severity is within bounds
    const finalSeverity = Math.max(1, Math.min(10, adjustedSeverity));

    // Determine category
    let category: 'mild' | 'moderate' | 'severe' | 'critical';
    if (finalSeverity <= 3) category = 'mild';
    else if (finalSeverity <= 6) category = 'moderate';
    else if (finalSeverity <= 8) category = 'severe';
    else category = 'critical';

    // Calculate confidence based on data availability
    const dataPoints = [
      input.currentSymptoms,
      input.contextualFactors,
      input.historicalData,
      input.userProfile
    ].filter(data => data && Object.keys(data).length > 0).length;
    
    const confidence = Math.min(0.9, 0.4 + (dataPoints * 0.1));

    return {
      predicted_severity: Math.round(finalSeverity * 10) / 10,
      confidence,
      severity_category: category,
      contributing_factors: factors,
      recommendations: this.generateRecommendations(finalSeverity, factors),
      prediction_horizon: "next 2-4 hours",
      model_version: "fallback_v1.0"
    };
  }

  /**
   * Generate adaptive default thresholds based on available user data
   */
  private async getAdaptiveDefaultThresholds(): Promise<PersonalizedThresholds> {
    try {
      // Try to get user's historical data to adapt thresholds
      const response = await fetch(`${this.baseUrl}/api/v1/user/symptom-history`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (response.ok) {
        const history = await response.json();
        return this.calculateAdaptiveThresholds(history);
      }
    } catch (error) {
      console.log('Using default thresholds due to data unavailability');
    }

    // Default thresholds
    return {
      mild_threshold: 3.0,
      moderate_threshold: 5.0,
      severe_threshold: 7.5,
      critical_threshold: 9.0,
      confidence: 0.5
    };
  }

  /**
   * Get static default thresholds
   */
  private getStaticDefaultThresholds(): PersonalizedThresholds {
    return {
      mild_threshold: 3.0,
      moderate_threshold: 5.0,
      severe_threshold: 7.5,
      critical_threshold: 9.0,
      confidence: 0.5
    };
  }

  /**
   * Calculate adaptive thresholds based on user's historical data
   */
  private calculateAdaptiveThresholds(history: any): PersonalizedThresholds {
    if (!history.symptom_logs || history.symptom_logs.length === 0) {
      return this.getStaticDefaultThresholds();
    }

    const severities = history.symptom_logs.map((log: any) => log.severity || 5);
    const avgSeverity = severities.reduce((sum: number, s: number) => sum + s, 0) / severities.length;
    const variance = severities.reduce((sum: number, s: number) => sum + Math.pow(s - avgSeverity, 2), 0) / severities.length;

    // Adjust thresholds based on user's typical severity range
    const adjustment = (avgSeverity - 5) * 0.3;
    const varianceAdjustment = Math.sqrt(variance) * 0.2;

    return {
      mild_threshold: Math.max(1, 3.0 + adjustment - varianceAdjustment),
      moderate_threshold: Math.max(2, 5.0 + adjustment),
      severe_threshold: Math.max(4, 7.5 + adjustment + varianceAdjustment),
      critical_threshold: Math.max(6, 9.0 + adjustment + varianceAdjustment),
      confidence: Math.min(0.9, 0.6 + (severities.length / 100))
    };
  }

  /**
   * Generate contextual recommendations based on severity and factors
   */
  private generateRecommendations(severity: number, factors: Array<{ factor: string; impact: number }>): string[] {
    const recommendations: string[] = [];

    if (severity >= 8) {
      recommendations.push("Consider contacting your healthcare provider");
      recommendations.push("Rest and avoid trigger foods");
    } else if (severity >= 6) {
      recommendations.push("Take prescribed medications as needed");
      recommendations.push("Apply heat therapy for comfort");
    } else if (severity >= 4) {
      recommendations.push("Monitor symptoms closely");
      recommendations.push("Stay hydrated and eat bland foods");
    } else {
      recommendations.push("Continue current management plan");
      recommendations.push("Maintain regular meal schedule");
    }

    // Add factor-specific recommendations
    factors.forEach(factor => {
      if (factor.impact > 0.1) {
        switch (factor.factor) {
          case 'stress_level':
            recommendations.push("Practice stress reduction techniques");
            break;
          case 'sleep_quality':
            recommendations.push("Prioritize better sleep hygiene");
            break;
        }
      }
    });

    return recommendations.slice(0, 4); // Limit to 4 recommendations
  }

  /**
   * Validate ML prediction response
   */
  private validateSeverityPrediction(result: any): SeverityPredictionResult {
    return {
      predicted_severity: Math.max(1, Math.min(10, result.predicted_severity || 5)),
      confidence: Math.max(0, Math.min(1, result.confidence || 0.5)),
      severity_category: ['mild', 'moderate', 'severe', 'critical'].includes(result.severity_category) 
        ? result.severity_category : 'moderate',
      contributing_factors: Array.isArray(result.contributing_factors) ? result.contributing_factors : [],
      recommendations: Array.isArray(result.recommendations) ? result.recommendations : [],
      prediction_horizon: result.prediction_horizon || "next 2-4 hours",
      model_version: result.model_version || "unknown"
    };
  }

  /**
   * Validate threshold response
   */
  private validateThresholds(thresholds: any): PersonalizedThresholds {
    return {
      mild_threshold: Math.max(1, Math.min(4, thresholds.mild_threshold || 3)),
      moderate_threshold: Math.max(2, Math.min(6, thresholds.moderate_threshold || 5)),
      severe_threshold: Math.max(4, Math.min(8, thresholds.severe_threshold || 7.5)),
      critical_threshold: Math.max(6, Math.min(10, thresholds.critical_threshold || 9)),
      confidence: Math.max(0, Math.min(1, thresholds.confidence || 0.5))
    };
  }

  /**
   * Generate fallback progression data
   */
  private generateProgressionFallback(
    input: SeverityPredictionInput, 
    timeHorizon: number
  ): Array<{ timestamp: string; predicted_severity: number; confidence: number }> {
    const progression = [];
    const baseSeverity = Object.values(input.currentSymptoms).reduce((sum, val) => sum + (val || 0), 0) / 
                        Object.values(input.currentSymptoms).filter(val => val !== undefined).length || 5;

    for (let i = 0; i < timeHorizon; i += 2) {
      const timestamp = new Date(Date.now() + i * 60 * 60 * 1000).toISOString();
      const variation = (Math.random() - 0.5) * 1.5; // ±0.75 variation
      const predicted_severity = Math.max(1, Math.min(10, baseSeverity + variation));
      const confidence = Math.max(0.3, 0.8 - (i / timeHorizon) * 0.3); // Decreasing confidence over time

      progression.push({
        timestamp,
        predicted_severity: Math.round(predicted_severity * 10) / 10,
        confidence: Math.round(confidence * 100) / 100
      });
    }

    return progression;
  }
}

export const mlSeverityPredictionService = new MLSeverityPredictionService();
export default mlSeverityPredictionService;