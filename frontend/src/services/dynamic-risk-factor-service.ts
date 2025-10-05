'use client';

import { mlService } from './ml-service';
import { stressCorrelationDataService } from './stress-correlation-data-service';
import { sleepQualityDataService } from './sleep-quality-data-service';
import { exerciseToleranceDataService } from './exercise-tolerance-data-service';
import { apiService } from '@/lib/api';

export interface RiskFactor {
  factor: string;
  value: number;
  impact: 'low' | 'moderate' | 'high' | 'critical';
  description: string;
  recommendation: string;
  confidence: number;
}

export interface DynamicRiskAssessment {
  overallRiskScore: number;
  riskLevel: 'low' | 'moderate' | 'high' | 'critical';
  riskFactors: RiskFactor[];
  primaryTriggers: string[];
  recommendations: string[];
  confidence: number;
  lastUpdated: string;
}

export interface UserRiskData {
  stress_level: number;
  sleep_quality: number;
  sleep_hours: number;
  exercise_frequency: number;
  diet_adherence: number;
  medication_adherence: number;
  recent_symptom_severity: number;
  trigger_food_exposure: number;
  lifestyle_consistency: number;
}

class DynamicRiskFactorService {
  private readonly RISK_WEIGHTS = {
    stress: 0.25,
    sleep: 0.20,
    diet: 0.20,
    exercise: 0.15,
    medication: 0.10,
    symptoms: 0.10
  };

  private readonly IMPACT_THRESHOLDS = {
    low: 0.3,
    moderate: 0.5,
    high: 0.7,
    critical: 0.85
  };

  /**
   * Calculate comprehensive risk assessment based on user data
   */
  async calculateDynamicRiskFactors(): Promise<DynamicRiskAssessment> {
    try {
      // Gather data from multiple sources
      const [
        userRiskData,
        stressCorrelationData,
        sleepQualityData,
        exerciseToleranceData,
        recentSymptoms
      ] = await Promise.all([
        this.getUserRiskData(),
        stressCorrelationDataService.fetchUserStressSymptomData(30),
        sleepQualityDataService.fetchUserSleepSymptomData(30),
        exerciseToleranceDataService.fetchUserExerciseSymptomData(30),
        this.getRecentSymptoms()
      ]);

      // Calculate individual risk factors
      const riskFactors = await this.calculateIndividualRiskFactors(
        userRiskData,
        stressCorrelationData,
        sleepQualityData,
        exerciseToleranceData,
        recentSymptoms
      );

      // Calculate overall risk score
      const overallRiskScore = this.calculateOverallRiskScore(riskFactors);
      const riskLevel = this.determineRiskLevel(overallRiskScore);

      // Generate recommendations
      const recommendations = this.generateRecommendations(riskFactors, riskLevel);
      const primaryTriggers = this.identifyPrimaryTriggers(riskFactors);

      // Calculate confidence based on data quality
      const confidence = this.calculateConfidence(riskFactors);

      return {
        overallRiskScore: Math.round(overallRiskScore * 100) / 100,
        riskLevel,
        riskFactors,
        primaryTriggers,
        recommendations,
        confidence,
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error calculating dynamic risk factors:', error);
      return this.getFallbackRiskAssessment();
    }
  }

  /**
   * Calculate individual risk factors
   */
  private async calculateIndividualRiskFactors(
    userRiskData: UserRiskData,
    stressData: any,
    sleepData: any,
    exerciseData: any,
    recentSymptoms: any[]
  ): Promise<RiskFactor[]> {
    const riskFactors: RiskFactor[] = [];

    // Stress Risk Factor
    const stressRisk = this.calculateStressRisk(userRiskData.stress_level, stressData);
    riskFactors.push({
      factor: 'Stress Level',
      value: stressRisk.value,
      impact: stressRisk.impact,
      description: `Current stress level: ${userRiskData.stress_level}/10`,
      recommendation: stressRisk.recommendation,
      confidence: stressRisk.confidence
    });

    // Sleep Risk Factor
    const sleepRisk = this.calculateSleepRisk(userRiskData.sleep_quality, userRiskData.sleep_hours, sleepData);
    riskFactors.push({
      factor: 'Sleep Quality',
      value: sleepRisk.value,
      impact: sleepRisk.impact,
      description: `Sleep quality: ${userRiskData.sleep_quality}/10, Hours: ${userRiskData.sleep_hours}`,
      recommendation: sleepRisk.recommendation,
      confidence: sleepRisk.confidence
    });

    // Diet Risk Factor
    const dietRisk = this.calculateDietRisk(userRiskData.diet_adherence, userRiskData.trigger_food_exposure);
    riskFactors.push({
      factor: 'Dietary Adherence',
      value: dietRisk.value,
      impact: dietRisk.impact,
      description: `Diet adherence: ${Math.round(userRiskData.diet_adherence * 100)}%`,
      recommendation: dietRisk.recommendation,
      confidence: dietRisk.confidence
    });

    // Exercise Risk Factor
    const exerciseRisk = this.calculateExerciseRisk(userRiskData.exercise_frequency, exerciseData);
    riskFactors.push({
      factor: 'Exercise Pattern',
      value: exerciseRisk.value,
      impact: exerciseRisk.impact,
      description: `Exercise frequency: ${userRiskData.exercise_frequency} times/week`,
      recommendation: exerciseRisk.recommendation,
      confidence: exerciseRisk.confidence
    });

    // Medication Risk Factor
    const medicationRisk = this.calculateMedicationRisk(userRiskData.medication_adherence);
    riskFactors.push({
      factor: 'Medication Adherence',
      value: medicationRisk.value,
      impact: medicationRisk.impact,
      description: `Medication adherence: ${Math.round(userRiskData.medication_adherence * 100)}%`,
      recommendation: medicationRisk.recommendation,
      confidence: medicationRisk.confidence
    });

    // Symptom Severity Risk Factor
    const symptomRisk = this.calculateSymptomRisk(userRiskData.recent_symptom_severity, recentSymptoms);
    riskFactors.push({
      factor: 'Recent Symptoms',
      value: symptomRisk.value,
      impact: symptomRisk.impact,
      description: `Recent average severity: ${userRiskData.recent_symptom_severity}/10`,
      recommendation: symptomRisk.recommendation,
      confidence: symptomRisk.confidence
    });

    return riskFactors;
  }

  /**
   * Calculate stress-related risk
   */
  private calculateStressRisk(stressLevel: number, stressData: any): {
    value: number;
    impact: 'low' | 'moderate' | 'high' | 'critical';
    recommendation: string;
    confidence: number;
  } {
    // Normalize stress level (0-10 scale to 0-1)
    const normalizedStress = Math.min(1, Math.max(0, stressLevel / 10));
    
    // Factor in correlation with symptoms if available
    let correlationMultiplier = 1;
    if (stressData?.average_stress && stressData?.average_severity) {
      const correlation = Math.abs(stressData.average_stress - stressData.average_severity) / 10;
      correlationMultiplier = 1 + (correlation * 0.3);
    }

    const riskValue = normalizedStress * correlationMultiplier;
    const impact = this.getImpactLevel(riskValue);

    let recommendation = 'Continue current stress management practices';
    if (riskValue > 0.7) {
      recommendation = 'Implement immediate stress reduction techniques - consider meditation, deep breathing, or professional support';
    } else if (riskValue > 0.5) {
      recommendation = 'Focus on stress management - try regular exercise, mindfulness, or relaxation techniques';
    } else if (riskValue > 0.3) {
      recommendation = 'Monitor stress levels and maintain healthy coping strategies';
    }

    return {
      value: riskValue,
      impact,
      recommendation,
      confidence: stressData?.data_points ? Math.min(0.9, stressData.data_points / 30) : 0.6
    };
  }

  /**
   * Calculate sleep-related risk
   */
  private calculateSleepRisk(sleepQuality: number, sleepHours: number, sleepData: any): {
    value: number;
    impact: 'low' | 'moderate' | 'high' | 'critical';
    recommendation: string;
    confidence: number;
  } {
    // Calculate sleep quality risk (inverse of quality)
    const qualityRisk = Math.max(0, (10 - sleepQuality) / 10);
    
    // Calculate sleep duration risk
    const optimalHours = 8;
    const hoursDiff = Math.abs(sleepHours - optimalHours);
    const durationRisk = Math.min(1, hoursDiff / 4); // Max risk if 4+ hours off optimal

    // Combine risks
    const riskValue = (qualityRisk * 0.6) + (durationRisk * 0.4);
    const impact = this.getImpactLevel(riskValue);

    let recommendation = 'Maintain good sleep hygiene practices';
    if (riskValue > 0.7) {
      recommendation = 'Prioritize sleep improvement - establish consistent bedtime routine and aim for 7-9 hours';
    } else if (riskValue > 0.5) {
      recommendation = 'Focus on improving sleep quality and duration consistency';
    } else if (riskValue > 0.3) {
      recommendation = 'Monitor sleep patterns and maintain regular sleep schedule';
    }

    return {
      value: riskValue,
      impact,
      recommendation,
      confidence: sleepData?.averageSleepQuality ? 0.8 : 0.6
    };
  }

  /**
   * Calculate diet-related risk
   */
  private calculateDietRisk(dietAdherence: number, triggerFoodExposure: number): {
    value: number;
    impact: 'low' | 'moderate' | 'high' | 'critical';
    recommendation: string;
    confidence: number;
  } {
    // Calculate adherence risk (inverse of adherence)
    const adherenceRisk = Math.max(0, 1 - dietAdherence);
    
    // Calculate trigger exposure risk
    const exposureRisk = Math.min(1, triggerFoodExposure);

    // Combine risks with higher weight on trigger exposure
    const riskValue = (adherenceRisk * 0.4) + (exposureRisk * 0.6);
    const impact = this.getImpactLevel(riskValue);

    let recommendation = 'Continue following your dietary plan';
    if (riskValue > 0.7) {
      recommendation = 'Strictly avoid trigger foods and improve diet adherence - consider working with a dietitian';
    } else if (riskValue > 0.5) {
      recommendation = 'Focus on reducing trigger food exposure and improving diet consistency';
    } else if (riskValue > 0.3) {
      recommendation = 'Monitor food intake and maintain awareness of trigger foods';
    }

    return {
      value: riskValue,
      impact,
      recommendation,
      confidence: 0.7
    };
  }

  /**
   * Calculate exercise-related risk
   */
  private calculateExerciseRisk(exerciseFrequency: number, exerciseData: any): {
    value: number;
    impact: 'low' | 'moderate' | 'high' | 'critical';
    recommendation: string;
    confidence: number;
  } {
    // Optimal exercise frequency is 3-5 times per week
    const optimalFrequency = 4;
    const frequencyDiff = Math.abs(exerciseFrequency - optimalFrequency);
    const riskValue = Math.min(1, frequencyDiff / 4);

    const impact = this.getImpactLevel(riskValue);

    let recommendation = 'Maintain current exercise routine';
    if (exerciseFrequency < 2) {
      recommendation = 'Gradually increase physical activity - start with light walking or yoga';
    } else if (exerciseFrequency > 6) {
      recommendation = 'Consider reducing exercise intensity to avoid overexertion';
    } else if (riskValue > 0.3) {
      recommendation = 'Aim for 3-5 moderate exercise sessions per week';
    }

    return {
      value: riskValue,
      impact,
      recommendation,
      confidence: exerciseData?.toleranceScore ? 0.8 : 0.6
    };
  }

  /**
   * Calculate medication-related risk
   */
  private calculateMedicationRisk(medicationAdherence: number): {
    value: number;
    impact: 'low' | 'moderate' | 'high' | 'critical';
    recommendation: string;
    confidence: number;
  } {
    const riskValue = Math.max(0, 1 - medicationAdherence);
    const impact = this.getImpactLevel(riskValue);

    let recommendation = 'Continue current medication routine';
    if (riskValue > 0.7) {
      recommendation = 'Improve medication adherence - consider setting reminders or discussing with healthcare provider';
    } else if (riskValue > 0.5) {
      recommendation = 'Focus on taking medications as prescribed consistently';
    } else if (riskValue > 0.3) {
      recommendation = 'Monitor medication adherence and maintain consistency';
    }

    return {
      value: riskValue,
      impact,
      recommendation,
      confidence: 0.9
    };
  }

  /**
   * Calculate symptom severity risk
   */
  private calculateSymptomRisk(recentSeverity: number, recentSymptoms: any[]): {
    value: number;
    impact: 'low' | 'moderate' | 'high' | 'critical';
    recommendation: string;
    confidence: number;
  } {
    const riskValue = Math.min(1, recentSeverity / 10);
    const impact = this.getImpactLevel(riskValue);

    let recommendation = 'Continue monitoring symptoms';
    if (riskValue > 0.7) {
      recommendation = 'High symptom severity detected - consider consulting healthcare provider';
    } else if (riskValue > 0.5) {
      recommendation = 'Focus on symptom management strategies and trigger avoidance';
    } else if (riskValue > 0.3) {
      recommendation = 'Maintain current management approach and monitor for changes';
    }

    return {
      value: riskValue,
      impact,
      recommendation,
      confidence: recentSymptoms.length > 5 ? 0.8 : 0.6
    };
  }

  /**
   * Calculate overall risk score from individual factors
   */
  private calculateOverallRiskScore(riskFactors: RiskFactor[]): number {
    let weightedSum = 0;
    let totalWeight = 0;

    riskFactors.forEach(factor => {
      const weight = this.getFactorWeight(factor.factor);
      weightedSum += factor.value * weight * factor.confidence;
      totalWeight += weight * factor.confidence;
    });

    return totalWeight > 0 ? weightedSum / totalWeight : 0;
  }

  /**
   * Get weight for specific risk factor
   */
  private getFactorWeight(factorName: string): number {
    const lowerName = factorName.toLowerCase();
    if (lowerName.includes('stress')) return this.RISK_WEIGHTS.stress;
    if (lowerName.includes('sleep')) return this.RISK_WEIGHTS.sleep;
    if (lowerName.includes('diet')) return this.RISK_WEIGHTS.diet;
    if (lowerName.includes('exercise')) return this.RISK_WEIGHTS.exercise;
    if (lowerName.includes('medication')) return this.RISK_WEIGHTS.medication;
    if (lowerName.includes('symptom')) return this.RISK_WEIGHTS.symptoms;
    return 0.1; // Default weight
  }

  /**
   * Determine risk level from overall score
   */
  private determineRiskLevel(score: number): 'low' | 'moderate' | 'high' | 'critical' {
    if (score >= this.IMPACT_THRESHOLDS.critical) return 'critical';
    if (score >= this.IMPACT_THRESHOLDS.high) return 'high';
    if (score >= this.IMPACT_THRESHOLDS.moderate) return 'moderate';
    return 'low';
  }

  /**
   * Get impact level from risk value
   */
  private getImpactLevel(value: number): 'low' | 'moderate' | 'high' | 'critical' {
    if (value >= this.IMPACT_THRESHOLDS.critical) return 'critical';
    if (value >= this.IMPACT_THRESHOLDS.high) return 'high';
    if (value >= this.IMPACT_THRESHOLDS.moderate) return 'moderate';
    return 'low';
  }

  /**
   * Generate recommendations based on risk factors
   */
  private generateRecommendations(riskFactors: RiskFactor[], riskLevel: string): string[] {
    const recommendations: string[] = [];
    
    // Add high-impact factor recommendations
    const highRiskFactors = riskFactors.filter(f => f.impact === 'high' || f.impact === 'critical');
    highRiskFactors.forEach(factor => {
      recommendations.push(factor.recommendation);
    });

    // Add general recommendations based on overall risk level
    if (riskLevel === 'critical') {
      recommendations.push('Consider immediate consultation with healthcare provider');
      recommendations.push('Implement all recommended lifestyle modifications immediately');
    } else if (riskLevel === 'high') {
      recommendations.push('Focus on addressing the highest risk factors first');
      recommendations.push('Consider scheduling a healthcare provider consultation');
    } else if (riskLevel === 'moderate') {
      recommendations.push('Gradually implement recommended lifestyle changes');
      recommendations.push('Monitor symptoms closely for any changes');
    }

    return Array.from(new Set(recommendations)); // Remove duplicates
  }

  /**
   * Identify primary triggers from risk factors
   */
  private identifyPrimaryTriggers(riskFactors: RiskFactor[]): string[] {
    return riskFactors
      .filter(f => f.impact === 'high' || f.impact === 'critical')
      .map(f => f.factor)
      .slice(0, 3); // Top 3 triggers
  }

  /**
   * Calculate confidence based on data quality
   */
  private calculateConfidence(riskFactors: RiskFactor[]): number {
    const avgConfidence = riskFactors.reduce((sum, f) => sum + f.confidence, 0) / riskFactors.length;
    return Math.round(avgConfidence * 100) / 100;
  }

  /**
   * Get user risk data from various sources
   */
  private async getUserRiskData(): Promise<UserRiskData> {
    try {
      // This would typically fetch from user profile, recent logs, etc.
      // For now, using mock data that would be replaced with actual API calls
      return {
        stress_level: 6.5,
        sleep_quality: 7.2,
        sleep_hours: 7.5,
        exercise_frequency: 3,
        diet_adherence: 0.8,
        medication_adherence: 0.9,
        recent_symptom_severity: 4.2,
        trigger_food_exposure: 0.3,
        lifestyle_consistency: 0.75
      };
    } catch (error) {
      console.error('Error fetching user risk data:', error);
      // Return fallback data
      return {
        stress_level: 5,
        sleep_quality: 7,
        sleep_hours: 8,
        exercise_frequency: 3,
        diet_adherence: 0.8,
        medication_adherence: 0.85,
        recent_symptom_severity: 4,
        trigger_food_exposure: 0.2,
        lifestyle_consistency: 0.7
      };
    }
  }

  /**
   * Get recent symptoms data
   */
  private async getRecentSymptoms(): Promise<any[]> {
    try {
      const response = await apiService.getSymptomLogs();
      if (response && response.items) {
        return response.items.slice(0, 10); // Last 10 entries
      }
      return [];
    } catch (error) {
      console.error('Error fetching recent symptoms:', error);
      return [];
    }
  }

  /**
   * Get fallback risk assessment when calculation fails
   */
  private getFallbackRiskAssessment(): DynamicRiskAssessment {
    return {
      overallRiskScore: 0.4,
      riskLevel: 'moderate',
      riskFactors: [
        {
          factor: 'General Risk',
          value: 0.4,
          impact: 'moderate',
          description: 'Unable to calculate detailed risk factors',
          recommendation: 'Continue monitoring symptoms and maintaining healthy lifestyle',
          confidence: 0.5
        }
      ],
      primaryTriggers: ['Data unavailable'],
      recommendations: [
        'Continue logging symptoms regularly',
        'Maintain consistent lifestyle habits',
        'Consult healthcare provider if symptoms worsen'
      ],
      confidence: 0.5,
      lastUpdated: new Date().toISOString()
    };
  }
}

export const dynamicRiskFactorService = new DynamicRiskFactorService();