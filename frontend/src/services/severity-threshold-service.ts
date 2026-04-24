import { personalizationService } from './personalization-service';

export interface SeverityThresholds {
  low: number;
  moderate: number;
  high: number;
  severe: number;
}

export interface ConfidenceThresholds {
  low: number;
  medium: number;
  high: number;
  excellent: number;
}

export interface RiskThresholds {
  low: number;
  medium: number;
  high: number;
  critical: number;
}

export interface UserContext {
  userId?: string;
  ibsType?: string;
  severityLevel?: string;
  symptomHistory?: Array<{ severity: number; date: string }>;
  medicationHistory?: Array<{ effectiveness: number; medication: string }>;
  personalFactors?: {
    age?: number;
    stressLevel?: number;
    sleepQuality?: number;
    exerciseFrequency?: number;
  };
}

class SeverityThresholdService {
  private defaultSeverityThresholds: SeverityThresholds = {
    low: 3.0,
    moderate: 5.0,
    high: 7.0,
    severe: 8.5
  };

  private defaultConfidenceThresholds: ConfidenceThresholds = {
    low: 0.6,
    medium: 0.75,
    high: 0.85,
    excellent: 0.95
  };

  private defaultRiskThresholds: RiskThresholds = {
    low: 0.3,
    medium: 0.5,
    high: 0.7,
    critical: 0.85
  };

  /**
   * Calculate personalized severity thresholds based on user context
   */
  async calculateSeverityThresholds(userContext: UserContext = {}): Promise<SeverityThresholds> {
    try {
      const personalizationProfile = await personalizationService.getPersonalizationProfile();
      const baseThresholds = { ...this.defaultSeverityThresholds };

      // Adjust based on user's historical severity patterns
      if (userContext.symptomHistory && userContext.symptomHistory.length > 0) {
        const avgSeverity = userContext.symptomHistory.reduce((sum, log) => sum + log.severity, 0) / userContext.symptomHistory.length;
        const severityVariance = this.calculateVariance(userContext.symptomHistory.map(log => log.severity));
        
        // Adjust thresholds based on user's typical severity range
        const adjustment = (avgSeverity - 5.0) * 0.3; // Scale adjustment
        baseThresholds.low = Math.max(1.0, baseThresholds.low + adjustment);
        baseThresholds.moderate = Math.max(baseThresholds.low + 1.0, baseThresholds.moderate + adjustment);
        baseThresholds.high = Math.max(baseThresholds.moderate + 1.0, baseThresholds.high + adjustment);
        baseThresholds.severe = Math.max(baseThresholds.high + 1.0, baseThresholds.severe + adjustment);

        // Adjust for variance - users with high variance need wider ranges
        if (severityVariance > 2.0) {
          baseThresholds.moderate += 0.5;
          baseThresholds.high += 0.3;
        }
      }

      // Adjust based on IBS type
      if (userContext.ibsType) {
        switch (userContext.ibsType.toLowerCase()) {
          case 'ibs-d':
            // IBS-D typically has more acute episodes
            baseThresholds.high -= 0.5;
            baseThresholds.severe -= 0.3;
            break;
          case 'ibs-c':
            // IBS-C tends to have more chronic, steady symptoms
            baseThresholds.moderate += 0.3;
            baseThresholds.high += 0.5;
            break;
          case 'ibs-m':
            // Mixed type - use default with slight adjustment for unpredictability
            baseThresholds.moderate += 0.2;
            break;
        }
      }

      // Adjust based on personal factors
      if (userContext.personalFactors) {
        const { stressLevel, sleepQuality, age } = userContext.personalFactors;
        
        if (stressLevel && stressLevel > 7) {
          // High stress lowers tolerance thresholds
          baseThresholds.moderate -= 0.3;
          baseThresholds.high -= 0.5;
        }
        
        if (sleepQuality && sleepQuality < 6) {
          // Poor sleep affects symptom perception
          baseThresholds.low -= 0.2;
          baseThresholds.moderate -= 0.3;
        }
        
        if (age && age > 60) {
          // Older adults may have different pain tolerance
          baseThresholds.moderate += 0.2;
          baseThresholds.high += 0.3;
        }
      }

      // Apply ML-driven personalization adjustments
      const mlAdjustment = personalizationProfile.ml_thresholds.severity_threshold - 0.5;
      Object.keys(baseThresholds).forEach(key => {
        baseThresholds[key as keyof SeverityThresholds] += mlAdjustment;
      });

      return this.validateThresholds(baseThresholds);
    } catch (error) {
      console.error('Error calculating severity thresholds:', error);
      return this.defaultSeverityThresholds;
    }
  }

  /**
   * Calculate personalized confidence thresholds
   */
  async calculateConfidenceThresholds(userContext: UserContext = {}): Promise<ConfidenceThresholds> {
    try {
      const personalizationProfile = await personalizationService.getPersonalizationProfile();
      const baseThresholds = { ...this.defaultConfidenceThresholds };

      // Adjust based on medication effectiveness history
      if (userContext.medicationHistory && userContext.medicationHistory.length > 0) {
        const avgEffectiveness = userContext.medicationHistory.reduce((sum, med) => sum + med.effectiveness, 0) / userContext.medicationHistory.length;
        
        // Users with historically effective treatments can have higher confidence thresholds
        if (avgEffectiveness > 0.8) {
          baseThresholds.medium += 0.05;
          baseThresholds.high += 0.03;
        } else if (avgEffectiveness < 0.6) {
          baseThresholds.medium -= 0.05;
          baseThresholds.high -= 0.03;
        }
      }

      // Apply personalization profile adjustments
      const confidenceAdjustment = personalizationProfile.adaptive_settings.confidence_threshold - 0.6;
      Object.keys(baseThresholds).forEach(key => {
        baseThresholds[key as keyof ConfidenceThresholds] = Math.max(0.1, Math.min(0.99, 
          baseThresholds[key as keyof ConfidenceThresholds] + confidenceAdjustment
        ));
      });

      return baseThresholds;
    } catch (error) {
      console.error('Error calculating confidence thresholds:', error);
      return this.defaultConfidenceThresholds;
    }
  }

  /**
   * Calculate personalized risk thresholds
   */
  async calculateRiskThresholds(userContext: UserContext = {}): Promise<RiskThresholds> {
    try {
      const personalizationProfile = await personalizationService.getPersonalizationProfile();
      const baseThresholds = { ...this.defaultRiskThresholds };

      // Adjust based on user's risk profile
      const riskAdjustment = personalizationProfile.ml_thresholds.high_risk_threshold - 0.7;
      baseThresholds.high = Math.max(0.1, Math.min(0.9, baseThresholds.high + riskAdjustment));
      baseThresholds.medium = Math.max(0.1, Math.min(baseThresholds.high - 0.1, baseThresholds.medium + riskAdjustment * 0.7));
      baseThresholds.low = Math.max(0.1, Math.min(baseThresholds.medium - 0.1, baseThresholds.low + riskAdjustment * 0.5));
      baseThresholds.critical = Math.max(baseThresholds.high + 0.1, Math.min(0.95, baseThresholds.critical + riskAdjustment * 0.5));

      return baseThresholds;
    } catch (error) {
      console.error('Error calculating risk thresholds:', error);
      return this.defaultRiskThresholds;
    }
  }

  /**
   * Get severity category based on personalized thresholds
   */
  async getSeverityCategory(severity: number, userContext: UserContext = {}): Promise<string> {
    const thresholds = await this.calculateSeverityThresholds(userContext);
    
    if (severity >= thresholds.severe) return 'severe';
    if (severity >= thresholds.high) return 'high';
    if (severity >= thresholds.moderate) return 'moderate';
    return 'low';
  }

  /**
   * Get confidence category based on personalized thresholds
   */
  async getConfidenceCategory(confidence: number, userContext: UserContext = {}): Promise<string> {
    const thresholds = await this.calculateConfidenceThresholds(userContext);
    
    if (confidence >= thresholds.excellent) return 'excellent';
    if (confidence >= thresholds.high) return 'high';
    if (confidence >= thresholds.medium) return 'medium';
    return 'low';
  }

  /**
   * Get risk category based on personalized thresholds
   */
  async getRiskCategory(risk: number, userContext: UserContext = {}): Promise<string> {
    const thresholds = await this.calculateRiskThresholds(userContext);
    
    if (risk >= thresholds.critical) return 'critical';
    if (risk >= thresholds.high) return 'high';
    if (risk >= thresholds.medium) return 'medium';
    return 'low';
  }

  /**
   * Get color coding for severity levels
   */
  getSeverityColor(category: string): string {
    switch (category.toLowerCase()) {
      case 'severe': return 'text-red-800 bg-red-100 border-red-200';
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'moderate': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  }

  /**
   * Get color coding for confidence levels
   */
  getConfidenceColor(category: string): string {
    switch (category.toLowerCase()) {
      case 'excellent': return 'text-green-600 bg-green-100';
      case 'high': return 'text-blue-600 bg-blue-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  }

  /**
   * Get color coding for risk levels
   */
  getRiskColor(category: string): string {
    switch (category.toLowerCase()) {
      case 'critical': return 'border-red-500 bg-red-100';
      case 'high': return 'border-red-300 bg-red-50';
      case 'medium': return 'border-yellow-300 bg-yellow-50';
      case 'low': return 'border-green-300 bg-green-50';
      default: return 'border-gray-300 bg-gray-50';
    }
  }

  private calculateVariance(values: number[]): number {
    if (values.length === 0) return 0;
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const squaredDiffs = values.map(val => Math.pow(val - mean, 2));
    return squaredDiffs.reduce((sum, diff) => sum + diff, 0) / values.length;
  }

  private validateThresholds(thresholds: SeverityThresholds): SeverityThresholds {
    // Ensure thresholds are in ascending order and within valid ranges
    const validated = { ...thresholds };
    
    validated.low = Math.max(1.0, Math.min(4.0, validated.low));
    validated.moderate = Math.max(validated.low + 0.5, Math.min(6.0, validated.moderate));
    validated.high = Math.max(validated.moderate + 0.5, Math.min(8.0, validated.high));
    validated.severe = Math.max(validated.high + 0.5, Math.min(10.0, validated.severe));
    
    return validated;
  }
}

export const severityThresholdService = new SeverityThresholdService();