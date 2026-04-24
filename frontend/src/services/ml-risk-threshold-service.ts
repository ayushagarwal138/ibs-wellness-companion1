/**
 * ML-Based Risk Threshold Calculation Service
 * 
 * Replaces static risk thresholds with personalized, dynamic calculations
 * based on user's medical history, current health status, and ML predictions.
 */

import { API_CONFIG } from '@/lib/config';

export interface RiskFactorInput {
  userProfile: {
    age: number;
    ibs_type: string;
    condition_duration_months: number;
    comorbidities: string[];
    medication_history: string[];
    family_history: boolean;
  };
  currentHealth: {
    recent_flare_frequency: number;
    average_symptom_severity: number;
    stress_level: number;
    sleep_quality: number;
    diet_adherence: number;
    exercise_frequency: number;
  };
  environmentalFactors: {
    season: string;
    location_climate: string;
    work_stress_level: number;
    social_support_level: number;
  };
  recentTriggers: {
    food_triggers: string[];
    stress_events: string[];
    medication_changes: string[];
    lifestyle_changes: string[];
  };
}

export interface PersonalizedRiskThresholds {
  flare_risk: {
    low: number;
    moderate: number;
    high: number;
    critical: number;
  };
  symptom_severity: {
    mild: number;
    moderate: number;
    severe: number;
    emergency: number;
  };
  medication_effectiveness: {
    poor: number;
    fair: number;
    good: number;
    excellent: number;
  };
  lifestyle_impact: {
    minimal: number;
    moderate: number;
    significant: number;
    severe: number;
  };
  confidence_scores: {
    flare_prediction: number;
    severity_assessment: number;
    treatment_response: number;
    lifestyle_recommendations: number;
  };
  last_updated: string;
  model_version: string;
}

export interface RiskAssessmentResult {
  overall_risk_score: number; // 0-100 scale
  risk_category: 'low' | 'moderate' | 'high' | 'critical';
  primary_risk_factors: Array<{
    factor: string;
    contribution: number; // 0-1 scale
    modifiable: boolean;
    recommendation: string;
  }>;
  predicted_outcomes: {
    flare_probability_7d: number;
    flare_probability_30d: number;
    expected_severity_range: [number, number];
    recovery_time_estimate: string;
  };
  personalized_thresholds: PersonalizedRiskThresholds;
  recommendations: {
    immediate_actions: string[];
    preventive_measures: string[];
    monitoring_suggestions: string[];
  };
}

class MLRiskThresholdService {
  private baseUrl: string;
  private authHeaders: HeadersInit;
  private cachedThresholds: PersonalizedRiskThresholds | null = null;
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
   * Calculate personalized risk thresholds using ML
   */
  async calculatePersonalizedThresholds(input: RiskFactorInput): Promise<PersonalizedRiskThresholds> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/risk/personalized-thresholds`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(input),
      });

      if (!response.ok) {
        throw new Error(`Risk threshold calculation failed: ${response.status}`);
      }

      const thresholds = await response.json();
      this.cacheThresholds(thresholds);
      return this.validateThresholds(thresholds);
    } catch (error) {
      console.error('ML risk threshold calculation failed, using adaptive fallback:', error);
      return this.adaptiveFallbackThresholds(input);
    }
  }

  /**
   * Get cached thresholds or calculate new ones
   */
  async getPersonalizedThresholds(input?: RiskFactorInput): Promise<PersonalizedRiskThresholds> {
    // Check cache validity (24 hours)
    if (this.cachedThresholds && Date.now() < this.cacheExpiry) {
      return this.cachedThresholds;
    }

    if (input) {
      return this.calculatePersonalizedThresholds(input);
    }

    // Try to get from server
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/risk/user-thresholds`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (response.ok) {
        const thresholds = await response.json();
        this.cacheThresholds(thresholds);
        return this.validateThresholds(thresholds);
      }
    } catch (error) {
      console.error('Failed to retrieve cached thresholds:', error);
    }

    // Fallback to default adaptive thresholds
    return this.getDefaultAdaptiveThresholds();
  }

  /**
   * Perform comprehensive risk assessment
   */
  async assessRisk(input: RiskFactorInput): Promise<RiskAssessmentResult> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/risk/comprehensive-assessment`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(input),
      });

      if (!response.ok) {
        throw new Error(`Risk assessment failed: ${response.status}`);
      }

      const assessment = await response.json();
      return this.validateRiskAssessment(assessment);
    } catch (error) {
      console.error('ML risk assessment failed, using intelligent fallback:', error);
      return this.intelligentRiskAssessment(input);
    }
  }

  /**
   * Update thresholds based on new user data
   */
  async updateThresholdsWithNewData(
    newData: Partial<RiskFactorInput>,
    outcomeData?: {
      actual_flare_occurred: boolean;
      actual_severity: number;
      treatment_effectiveness: number;
    }
  ): Promise<PersonalizedRiskThresholds> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/risk/update-thresholds`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ new_data: newData, outcome_data: outcomeData }),
      });

      if (!response.ok) {
        throw new Error(`Threshold update failed: ${response.status}`);
      }

      const updatedThresholds = await response.json();
      this.cacheThresholds(updatedThresholds);
      return this.validateThresholds(updatedThresholds);
    } catch (error) {
      console.error('Failed to update thresholds with new data:', error);
      // Return current thresholds if update fails
      return this.cachedThresholds || this.getDefaultAdaptiveThresholds();
    }
  }

  /**
   * Adaptive fallback when ML service is unavailable
   */
  private adaptiveFallbackThresholds(input: RiskFactorInput): PersonalizedRiskThresholds {
    // Calculate base risk factors
    const ageRisk = this.calculateAgeRisk(input.userProfile.age);
    const durationRisk = this.calculateDurationRisk(input.userProfile.condition_duration_months);
    const severityRisk = this.calculateSeverityRisk(input.currentHealth.average_symptom_severity);
    const stressRisk = this.calculateStressRisk(input.currentHealth.stress_level);

    // Combine risk factors
    const overallRisk = (ageRisk + durationRisk + severityRisk + stressRisk) / 4;

    // Adjust thresholds based on overall risk
    const riskAdjustment = (overallRisk - 0.5) * 0.3; // -0.15 to +0.15 adjustment

    return {
      flare_risk: {
        low: Math.max(0.05, 0.15 + riskAdjustment),
        moderate: Math.max(0.15, 0.35 + riskAdjustment),
        high: Math.max(0.35, 0.65 + riskAdjustment),
        critical: Math.max(0.65, 0.85 + riskAdjustment),
      },
      symptom_severity: {
        mild: Math.max(1, 3 + (riskAdjustment * 5)),
        moderate: Math.max(2, 5 + (riskAdjustment * 5)),
        severe: Math.max(4, 7 + (riskAdjustment * 5)),
        emergency: Math.max(6, 9 + (riskAdjustment * 5)),
      },
      medication_effectiveness: {
        poor: Math.max(0.1, 0.3 - riskAdjustment),
        fair: Math.max(0.3, 0.5 - riskAdjustment),
        good: Math.max(0.5, 0.7 - riskAdjustment),
        excellent: Math.max(0.7, 0.9 - riskAdjustment),
      },
      lifestyle_impact: {
        minimal: Math.max(0.1, 0.25 + riskAdjustment),
        moderate: Math.max(0.25, 0.5 + riskAdjustment),
        significant: Math.max(0.5, 0.75 + riskAdjustment),
        severe: Math.max(0.75, 0.9 + riskAdjustment),
      },
      confidence_scores: {
        flare_prediction: 0.6,
        severity_assessment: 0.7,
        treatment_response: 0.5,
        lifestyle_recommendations: 0.6,
      },
      last_updated: new Date().toISOString(),
      model_version: "adaptive_fallback_v1.0"
    };
  }

  /**
   * Intelligent risk assessment fallback
   */
  private intelligentRiskAssessment(input: RiskFactorInput): RiskAssessmentResult {
    const thresholds = this.adaptiveFallbackThresholds(input);
    
    // Calculate overall risk score
    const riskFactors = [
      this.calculateAgeRisk(input.userProfile.age),
      this.calculateDurationRisk(input.userProfile.condition_duration_months),
      this.calculateSeverityRisk(input.currentHealth.average_symptom_severity),
      this.calculateStressRisk(input.currentHealth.stress_level),
      this.calculateFlareFrequencyRisk(input.currentHealth.recent_flare_frequency),
    ];

    const overallRiskScore = (riskFactors.reduce((sum, risk) => sum + risk, 0) / riskFactors.length) * 100;

    // Determine risk category
    let riskCategory: 'low' | 'moderate' | 'high' | 'critical';
    if (overallRiskScore < 25) riskCategory = 'low';
    else if (overallRiskScore < 50) riskCategory = 'moderate';
    else if (overallRiskScore < 75) riskCategory = 'high';
    else riskCategory = 'critical';

    // Generate primary risk factors
    const primaryRiskFactors = [
      {
        factor: 'symptom_severity',
        contribution: this.calculateSeverityRisk(input.currentHealth.average_symptom_severity),
        modifiable: true,
        recommendation: 'Monitor symptoms closely and follow treatment plan'
      },
      {
        factor: 'stress_level',
        contribution: this.calculateStressRisk(input.currentHealth.stress_level),
        modifiable: true,
        recommendation: 'Practice stress management techniques'
      },
      {
        factor: 'flare_frequency',
        contribution: this.calculateFlareFrequencyRisk(input.currentHealth.recent_flare_frequency),
        modifiable: true,
        recommendation: 'Identify and avoid trigger patterns'
      }
    ].sort((a, b) => b.contribution - a.contribution);

    return {
      overall_risk_score: Math.round(overallRiskScore),
      risk_category: riskCategory,
      primary_risk_factors: primaryRiskFactors,
      predicted_outcomes: {
        flare_probability_7d: Math.min(0.9, overallRiskScore / 100 * 0.3),
        flare_probability_30d: Math.min(0.9, overallRiskScore / 100 * 0.6),
        expected_severity_range: [
          Math.max(1, input.currentHealth.average_symptom_severity - 1),
          Math.min(10, input.currentHealth.average_symptom_severity + 2)
        ],
        recovery_time_estimate: this.estimateRecoveryTime(overallRiskScore)
      },
      personalized_thresholds: thresholds,
      recommendations: this.generateRiskRecommendations(riskCategory, primaryRiskFactors)
    };
  }

  // Risk calculation helper methods
  private calculateAgeRisk(age: number): number {
    if (age < 30) return 0.3;
    if (age < 50) return 0.5;
    if (age < 70) return 0.7;
    return 0.8;
  }

  private calculateDurationRisk(months: number): number {
    if (months < 12) return 0.4;
    if (months < 60) return 0.6;
    if (months < 120) return 0.7;
    return 0.8;
  }

  private calculateSeverityRisk(severity: number): number {
    return Math.min(1, severity / 10);
  }

  private calculateStressRisk(stressLevel: number): number {
    return Math.min(1, stressLevel / 10);
  }

  private calculateFlareFrequencyRisk(frequency: number): number {
    if (frequency < 1) return 0.2;
    if (frequency < 3) return 0.4;
    if (frequency < 6) return 0.6;
    if (frequency < 10) return 0.8;
    return 1.0;
  }

  private estimateRecoveryTime(riskScore: number): string {
    if (riskScore < 25) return "1-3 days";
    if (riskScore < 50) return "3-7 days";
    if (riskScore < 75) return "1-2 weeks";
    return "2-4 weeks";
  }

  private generateRiskRecommendations(
    category: string, 
    riskFactors: Array<{ factor: string; modifiable: boolean }>
  ) {
    const recommendations = {
      immediate_actions: [] as string[],
      preventive_measures: [] as string[],
      monitoring_suggestions: [] as string[]
    };

    if (category === 'critical' || category === 'high') {
      recommendations.immediate_actions.push("Contact healthcare provider");
      recommendations.immediate_actions.push("Review and adjust current medications");
    }

    if (riskFactors.some(f => f.factor === 'stress_level')) {
      recommendations.preventive_measures.push("Implement daily stress management routine");
    }

    if (riskFactors.some(f => f.factor === 'symptom_severity')) {
      recommendations.monitoring_suggestions.push("Track symptoms daily");
    }

    recommendations.preventive_measures.push("Maintain consistent meal schedule");
    recommendations.monitoring_suggestions.push("Monitor trigger patterns");

    return recommendations;
  }

  private getDefaultAdaptiveThresholds(): PersonalizedRiskThresholds {
    return {
      flare_risk: {
        low: 0.15,
        moderate: 0.35,
        high: 0.65,
        critical: 0.85,
      },
      symptom_severity: {
        mild: 3,
        moderate: 5,
        severe: 7,
        emergency: 9,
      },
      medication_effectiveness: {
        poor: 0.3,
        fair: 0.5,
        good: 0.7,
        excellent: 0.9,
      },
      lifestyle_impact: {
        minimal: 0.25,
        moderate: 0.5,
        significant: 0.75,
        severe: 0.9,
      },
      confidence_scores: {
        flare_prediction: 0.5,
        severity_assessment: 0.6,
        treatment_response: 0.5,
        lifestyle_recommendations: 0.6,
      },
      last_updated: new Date().toISOString(),
      model_version: "default_v1.0"
    };
  }

  private cacheThresholds(thresholds: PersonalizedRiskThresholds): void {
    this.cachedThresholds = thresholds;
    this.cacheExpiry = Date.now() + (24 * 60 * 60 * 1000); // 24 hours
  }

  private validateThresholds(thresholds: any): PersonalizedRiskThresholds {
    return {
      flare_risk: {
        low: Math.max(0, Math.min(1, thresholds.flare_risk?.low || 0.15)),
        moderate: Math.max(0, Math.min(1, thresholds.flare_risk?.moderate || 0.35)),
        high: Math.max(0, Math.min(1, thresholds.flare_risk?.high || 0.65)),
        critical: Math.max(0, Math.min(1, thresholds.flare_risk?.critical || 0.85)),
      },
      symptom_severity: {
        mild: Math.max(1, Math.min(10, thresholds.symptom_severity?.mild || 3)),
        moderate: Math.max(1, Math.min(10, thresholds.symptom_severity?.moderate || 5)),
        severe: Math.max(1, Math.min(10, thresholds.symptom_severity?.severe || 7)),
        emergency: Math.max(1, Math.min(10, thresholds.symptom_severity?.emergency || 9)),
      },
      medication_effectiveness: {
        poor: Math.max(0, Math.min(1, thresholds.medication_effectiveness?.poor || 0.3)),
        fair: Math.max(0, Math.min(1, thresholds.medication_effectiveness?.fair || 0.5)),
        good: Math.max(0, Math.min(1, thresholds.medication_effectiveness?.good || 0.7)),
        excellent: Math.max(0, Math.min(1, thresholds.medication_effectiveness?.excellent || 0.9)),
      },
      lifestyle_impact: {
        minimal: Math.max(0, Math.min(1, thresholds.lifestyle_impact?.minimal || 0.25)),
        moderate: Math.max(0, Math.min(1, thresholds.lifestyle_impact?.moderate || 0.5)),
        significant: Math.max(0, Math.min(1, thresholds.lifestyle_impact?.significant || 0.75)),
        severe: Math.max(0, Math.min(1, thresholds.lifestyle_impact?.severe || 0.9)),
      },
      confidence_scores: {
        flare_prediction: Math.max(0, Math.min(1, thresholds.confidence_scores?.flare_prediction || 0.5)),
        severity_assessment: Math.max(0, Math.min(1, thresholds.confidence_scores?.severity_assessment || 0.6)),
        treatment_response: Math.max(0, Math.min(1, thresholds.confidence_scores?.treatment_response || 0.5)),
        lifestyle_recommendations: Math.max(0, Math.min(1, thresholds.confidence_scores?.lifestyle_recommendations || 0.6)),
      },
      last_updated: thresholds.last_updated || new Date().toISOString(),
      model_version: thresholds.model_version || "unknown"
    };
  }

  private validateRiskAssessment(assessment: any): RiskAssessmentResult {
    return {
      overall_risk_score: Math.max(0, Math.min(100, assessment.overall_risk_score || 50)),
      risk_category: ['low', 'moderate', 'high', 'critical'].includes(assessment.risk_category) 
        ? assessment.risk_category : 'moderate',
      primary_risk_factors: Array.isArray(assessment.primary_risk_factors) 
        ? assessment.primary_risk_factors : [],
      predicted_outcomes: {
        flare_probability_7d: Math.max(0, Math.min(1, assessment.predicted_outcomes?.flare_probability_7d || 0.3)),
        flare_probability_30d: Math.max(0, Math.min(1, assessment.predicted_outcomes?.flare_probability_30d || 0.5)),
        expected_severity_range: Array.isArray(assessment.predicted_outcomes?.expected_severity_range) 
          ? assessment.predicted_outcomes.expected_severity_range : [3, 7],
        recovery_time_estimate: assessment.predicted_outcomes?.recovery_time_estimate || "3-7 days"
      },
      personalized_thresholds: this.validateThresholds(assessment.personalized_thresholds || {}),
      recommendations: {
        immediate_actions: Array.isArray(assessment.recommendations?.immediate_actions) 
          ? assessment.recommendations.immediate_actions : [],
        preventive_measures: Array.isArray(assessment.recommendations?.preventive_measures) 
          ? assessment.recommendations.preventive_measures : [],
        monitoring_suggestions: Array.isArray(assessment.recommendations?.monitoring_suggestions) 
          ? assessment.recommendations.monitoring_suggestions : []
      }
    };
  }
}

export const mlRiskThresholdService = new MLRiskThresholdService();
export default mlRiskThresholdService;