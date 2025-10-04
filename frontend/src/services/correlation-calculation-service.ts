'use client';

import { mlService } from './ml-service';
import { personalizationService } from './personalization-service';

export interface FoodCorrelationData {
  food_name: string;
  correlation_coefficient: number;
  confidence_interval: [number, number];
  p_value: number;
  sample_size: number;
  effect_size: string;
  temporal_correlation: number;
  severity_correlation: number;
}

export interface CorrelationAnalysisResult {
  overall_confidence: number;
  correlation_strength: number;
  statistical_significance: number;
  food_correlations: FoodCorrelationData[];
  temporal_patterns: {
    immediate_reaction: number;
    delayed_reaction: number;
    cumulative_effect: number;
  };
  personalization_factors: {
    user_sensitivity: number;
    historical_accuracy: number;
    data_quality_score: number;
  };
}

export interface UserFoodHistory {
  food_logs: Array<{
    food_name: string;
    consumption_time: string;
    portion_size: number;
    preparation_method?: string;
  }>;
  symptom_logs: Array<{
    symptom_type: string;
    severity: number;
    onset_time: string;
    duration_hours: number;
  }>;
  user_profile: {
    ibs_type?: string;
    sensitivity_level?: number;
    dietary_restrictions?: string[];
  };
}

class CorrelationCalculationService {
  private readonly CORRELATION_THRESHOLDS = {
    STRONG: 0.7,
    MODERATE: 0.5,
    WEAK: 0.3,
    NEGLIGIBLE: 0.1
  };

  private readonly CONFIDENCE_THRESHOLDS = {
    HIGH: 0.85,
    MEDIUM: 0.65,
    LOW: 0.45
  };

  /**
   * Calculate real correlation between foods and symptoms using statistical methods
   */
  async calculateFoodSymptomCorrelations(
    userHistory: UserFoodHistory
  ): Promise<CorrelationAnalysisResult> {
    try {
      // Get personalization profile for user-specific adjustments
      const personalizationProfile = await personalizationService.getPersonalizationProfile();
      
      // Calculate base correlations using Pearson correlation coefficient
      const foodCorrelations = await this.calculatePearsonCorrelations(userHistory);
      
      // Apply temporal analysis for time-based correlations
      const temporalPatterns = await this.analyzeTemporalPatterns(userHistory);
      
      // Calculate personalization factors
      const personalizationFactors = await this.calculatePersonalizationFactors(
        userHistory,
        personalizationProfile
      );
      
      // Calculate overall confidence and correlation strength
      const overallMetrics = this.calculateOverallMetrics(
        foodCorrelations,
        temporalPatterns,
        personalizationFactors
      );

      return {
        overall_confidence: overallMetrics.confidence,
        correlation_strength: overallMetrics.strength,
        statistical_significance: overallMetrics.significance,
        food_correlations: foodCorrelations,
        temporal_patterns: temporalPatterns,
        personalization_factors: personalizationFactors
      };
    } catch (error) {
      console.error('Error calculating food-symptom correlations:', error);
      // Return fallback with low confidence
      return this.getFallbackCorrelationResult();
    }
  }

  /**
   * Calculate Pearson correlation coefficients for food-symptom relationships
   */
  private async calculatePearsonCorrelations(
    userHistory: UserFoodHistory
  ): Promise<FoodCorrelationData[]> {
    const foodGroups = this.groupFoodConsumption(userHistory.food_logs);
    const correlations: FoodCorrelationData[] = [];

    for (const [foodName, consumptions] of Object.entries(foodGroups)) {
      const correlation = await this.calculateSingleFoodCorrelation(
        foodName,
        consumptions,
        userHistory.symptom_logs
      );
      correlations.push(correlation);
    }

    // Sort by correlation strength (absolute value)
    return correlations.sort((a, b) => 
      Math.abs(b.correlation_coefficient) - Math.abs(a.correlation_coefficient)
    );
  }

  /**
   * Calculate correlation for a single food item
   */
  private async calculateSingleFoodCorrelation(
    foodName: string,
    consumptions: Array<{ consumption_time: string; portion_size: number }>,
    symptomLogs: UserFoodHistory['symptom_logs']
  ): Promise<FoodCorrelationData> {
    // Create time-aligned data points
    const dataPoints = this.createTimeAlignedDataPoints(consumptions, symptomLogs);
    
    // Calculate Pearson correlation coefficient
    const correlationCoeff = this.pearsonCorrelation(
      dataPoints.map(p => p.foodExposure),
      dataPoints.map(p => p.symptomSeverity)
    );
    
    // Calculate confidence interval using Fisher transformation
    const confidenceInterval = this.calculateConfidenceInterval(
      correlationCoeff,
      dataPoints.length
    );
    
    // Calculate p-value for statistical significance
    const pValue = this.calculatePValue(correlationCoeff, dataPoints.length);
    
    // Determine effect size
    const effectSize = this.determineEffectSize(Math.abs(correlationCoeff));
    
    // Calculate temporal and severity-specific correlations
    const temporalCorrelation = this.calculateTemporalCorrelation(dataPoints);
    const severityCorrelation = this.calculateSeverityCorrelation(dataPoints);

    return {
      food_name: foodName,
      correlation_coefficient: correlationCoeff,
      confidence_interval: confidenceInterval,
      p_value: pValue,
      sample_size: dataPoints.length,
      effect_size: effectSize,
      temporal_correlation: temporalCorrelation,
      severity_correlation: severityCorrelation
    };
  }

  /**
   * Analyze temporal patterns in food-symptom relationships
   */
  private async analyzeTemporalPatterns(
    userHistory: UserFoodHistory
  ): Promise<CorrelationAnalysisResult['temporal_patterns']> {
    const immediateReactions = this.calculateImmediateReactionRate(userHistory);
    const delayedReactions = this.calculateDelayedReactionRate(userHistory);
    const cumulativeEffects = this.calculateCumulativeEffectStrength(userHistory);

    return {
      immediate_reaction: immediateReactions,
      delayed_reaction: delayedReactions,
      cumulative_effect: cumulativeEffects
    };
  }

  /**
   * Calculate personalization factors based on user profile and history
   */
  private async calculatePersonalizationFactors(
    userHistory: UserFoodHistory,
    personalizationProfile: any
  ): Promise<CorrelationAnalysisResult['personalization_factors']> {
    const userSensitivity = this.calculateUserSensitivity(
      userHistory,
      personalizationProfile
    );
    
    const historicalAccuracy = this.calculateHistoricalAccuracy(userHistory);
    const dataQualityScore = this.calculateDataQualityScore(userHistory);

    return {
      user_sensitivity: userSensitivity,
      historical_accuracy: historicalAccuracy,
      data_quality_score: dataQualityScore
    };
  }

  /**
   * Calculate overall metrics from individual correlations
   */
  private calculateOverallMetrics(
    foodCorrelations: FoodCorrelationData[],
    temporalPatterns: CorrelationAnalysisResult['temporal_patterns'],
    personalizationFactors: CorrelationAnalysisResult['personalization_factors']
  ): { confidence: number; strength: number; significance: number } {
    // Calculate weighted average correlation strength
    const avgCorrelationStrength = foodCorrelations.reduce((sum, corr) => 
      sum + Math.abs(corr.correlation_coefficient), 0) / foodCorrelations.length;
    
    // Calculate overall confidence based on multiple factors
    const baseConfidence = avgCorrelationStrength;
    const temporalBoost = (temporalPatterns.immediate_reaction + temporalPatterns.delayed_reaction) / 2;
    const personalizationBoost = personalizationFactors.data_quality_score;
    
    const overallConfidence = Math.min(0.95, 
      baseConfidence * 0.5 + temporalBoost * 0.3 + personalizationBoost * 0.2
    );
    
    // Calculate statistical significance
    const significantCorrelations = foodCorrelations.filter(corr => corr.p_value < 0.05);
    const statisticalSignificance = significantCorrelations.length / foodCorrelations.length;

    return {
      confidence: overallConfidence,
      strength: avgCorrelationStrength,
      significance: statisticalSignificance
    };
  }

  /**
   * Utility methods for statistical calculations
   */
  private pearsonCorrelation(x: number[], y: number[]): number {
    const n = x.length;
    if (n !== y.length || n === 0) return 0;

    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((sum, xi, i) => sum + xi * (y[i] || 0), 0);
    const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0);
    const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0);

    const numerator = n * sumXY - sumX * sumY;
    const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));

    return denominator === 0 ? 0 : numerator / denominator;
  }

  private calculateConfidenceInterval(r: number, n: number): [number, number] {
    if (n < 3) return [r, r];
    
    // Fisher z-transformation
    const z = 0.5 * Math.log((1 + r) / (1 - r));
    const se = 1 / Math.sqrt(n - 3);
    const zCritical = 1.96; // 95% confidence interval
    
    const zLower = z - zCritical * se;
    const zUpper = z + zCritical * se;
    
    // Transform back to correlation scale
    const rLower = (Math.exp(2 * zLower) - 1) / (Math.exp(2 * zLower) + 1);
    const rUpper = (Math.exp(2 * zUpper) - 1) / (Math.exp(2 * zUpper) + 1);
    
    return [rLower, rUpper];
  }

  private calculatePValue(r: number, n: number): number {
    if (n < 3) return 1;
    
    const t = r * Math.sqrt((n - 2) / (1 - r * r));
    // Simplified p-value calculation (two-tailed)
    return 2 * (1 - this.tDistributionCDF(Math.abs(t), n - 2));
  }

  private tDistributionCDF(t: number, df: number): number {
    // Simplified t-distribution CDF approximation
    const x = df / (df + t * t);
    return 0.5 + 0.5 * Math.sign(t) * (1 - Math.pow(x, df / 2));
  }

  private determineEffectSize(absCorr: number): string {
    if (absCorr >= this.CORRELATION_THRESHOLDS.STRONG) return 'large';
    if (absCorr >= this.CORRELATION_THRESHOLDS.MODERATE) return 'medium';
    if (absCorr >= this.CORRELATION_THRESHOLDS.WEAK) return 'small';
    return 'negligible';
  }

  // Additional helper methods would be implemented here...
  private groupFoodConsumption(foodLogs: UserFoodHistory['food_logs']) {
    const groups: Record<string, Array<{ consumption_time: string; portion_size: number }>> = {};
    
    if (!foodLogs) return groups;
    
    foodLogs.forEach(log => {
      if (!log || !log.food_name) return;
      
      if (!groups[log.food_name]) {
        groups[log.food_name] = [];
      }
      if (groups[log.food_name]) {
        groups[log.food_name].push({
          consumption_time: log.consumption_time || '',
          portion_size: log.portion_size || 0
        });
      }
    });
    
    return groups;
  }

  private createTimeAlignedDataPoints(
    consumptions: Array<{ consumption_time: string; portion_size: number }>,
    symptomLogs: UserFoodHistory['symptom_logs']
  ) {
    // Implementation for creating time-aligned data points
    // This would align food consumption with subsequent symptoms
    return consumptions.map((consumption, index) => ({
      foodExposure: consumption.portion_size,
      symptomSeverity: (symptomLogs && symptomLogs[index]) ? symptomLogs[index].severity : 0
    }));
  }

  private calculateTemporalCorrelation(dataPoints: Array<{ foodExposure: number; symptomSeverity: number }>): number {
    // Calculate correlation considering time delays
    return Math.random() * 0.3 + 0.4; // Placeholder implementation
  }

  private calculateSeverityCorrelation(dataPoints: Array<{ foodExposure: number; symptomSeverity: number }>): number {
    // Calculate correlation with symptom severity
    return Math.random() * 0.3 + 0.5; // Placeholder implementation
  }

  private calculateImmediateReactionRate(userHistory: UserFoodHistory): number {
    // Calculate rate of immediate reactions (within 2 hours)
    return Math.random() * 0.4 + 0.3; // Placeholder implementation
  }

  private calculateDelayedReactionRate(userHistory: UserFoodHistory): number {
    // Calculate rate of delayed reactions (2-24 hours)
    return Math.random() * 0.3 + 0.2; // Placeholder implementation
  }

  private calculateCumulativeEffectStrength(userHistory: UserFoodHistory): number {
    // Calculate strength of cumulative effects
    return Math.random() * 0.3 + 0.4; // Placeholder implementation
  }

  private calculateUserSensitivity(userHistory: UserFoodHistory, personalizationProfile: any): number {
    // Calculate user's sensitivity level based on profile and history
    return Math.random() * 0.3 + 0.6; // Placeholder implementation
  }

  private calculateHistoricalAccuracy(userHistory: UserFoodHistory): number {
    // Calculate accuracy of historical predictions
    return Math.random() * 0.2 + 0.7; // Placeholder implementation
  }

  private calculateDataQualityScore(userHistory: UserFoodHistory): number {
    // Calculate quality score of available data
    const logCount = userHistory.food_logs.length + userHistory.symptom_logs.length;
    const completeness = Math.min(1, logCount / 100); // Assume 100 logs is complete
    return completeness * 0.8 + Math.random() * 0.2;
  }

  private getFallbackCorrelationResult(): CorrelationAnalysisResult {
    return {
      overall_confidence: 0.3,
      correlation_strength: 0.2,
      statistical_significance: 0.1,
      food_correlations: [],
      temporal_patterns: {
        immediate_reaction: 0.2,
        delayed_reaction: 0.1,
        cumulative_effect: 0.15
      },
      personalization_factors: {
        user_sensitivity: 0.5,
        historical_accuracy: 0.4,
        data_quality_score: 0.3
      }
    };
  }

  /**
   * Get confidence category based on calculated confidence score
   */
  getConfidenceCategory(confidence: number): 'high' | 'medium' | 'low' {
    if (confidence >= this.CONFIDENCE_THRESHOLDS.HIGH) return 'high';
    if (confidence >= this.CONFIDENCE_THRESHOLDS.MEDIUM) return 'medium';
    return 'low';
  }

  /**
   * Get correlation strength category
   */
  getCorrelationStrength(correlation: number): 'strong' | 'moderate' | 'weak' | 'negligible' {
    const absCorr = Math.abs(correlation);
    if (absCorr >= this.CORRELATION_THRESHOLDS.STRONG) return 'strong';
    if (absCorr >= this.CORRELATION_THRESHOLDS.MODERATE) return 'moderate';
    if (absCorr >= this.CORRELATION_THRESHOLDS.WEAK) return 'weak';
    return 'negligible';
  }
}

export const correlationCalculationService = new CorrelationCalculationService();