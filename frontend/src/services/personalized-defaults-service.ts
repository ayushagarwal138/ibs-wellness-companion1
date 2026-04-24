import { mlService } from './ml-service';
import { patternInsightsService } from './pattern-insights-service';
import { dynamicRiskFactorService } from './dynamic-risk-factor-service';

export interface PersonalizedSymptomDefaults {
  severity: number;
  stressLevel: number;
  sleepQuality: number;
  duration: number;
  mostLikelySymptom?: number;
}

export interface PersonalizedDietDefaults {
  moodBefore: number;
  moodAfter: number;
  hydrationLevel: number;
  eatingSpeed: 'slow' | 'normal' | 'fast';
  preferredMealTime: string;
  commonFoodCategories: string[];
  preferredPreparationMethod: string;
}

export interface UserPatternData {
  avgSeverity?: number;
  avgStressLevel?: number;
  avgSleepQuality?: number;
  avgDuration?: number;
  avgMoodBefore?: number;
  avgMoodAfter?: number;
  avgHydration?: number;
  commonEatingSpeed?: string;
  preferredMealTimes?: string[];
  frequentFoodCategories?: string[];
  preferredPreparation?: string;
  mostFrequentSymptom?: number;
}

class PersonalizedDefaultsService {
  private cache: Map<string, any> = new Map();
  private cacheExpiry: Map<string, number> = new Map();
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  private isCacheValid(key: string): boolean {
    const expiry = this.cacheExpiry.get(key);
    return expiry ? Date.now() < expiry : false;
  }

  private setCache(key: string, data: any): void {
    this.cache.set(key, data);
    this.cacheExpiry.set(key, Date.now() + this.CACHE_DURATION);
  }

  private getCache(key: string): any {
    if (this.isCacheValid(key)) {
      return this.cache.get(key);
    }
    this.cache.delete(key);
    this.cacheExpiry.delete(key);
    return null;
  }

  /**
   * Get personalized defaults for symptom logging form
   */
  async getSymptomDefaults(): Promise<PersonalizedSymptomDefaults> {
    const cacheKey = 'symptom_defaults';
    const cached = this.getCache(cacheKey);
    if (cached) return cached;

    try {
      // Get ML predictions and user patterns
      const [mlPredictions, patternInsights, riskAssessment] = await Promise.all([
        mlService.getRealtimePredictions().catch(() => null),
        patternInsightsService.getPatternInsights().catch(() => null),
        dynamicRiskFactorService.calculateDynamicRiskFactors().catch(() => null)
      ]);

      // Calculate intelligent defaults based on patterns and predictions
      const defaults: PersonalizedSymptomDefaults = {
        // Severity: Use predicted severity or user's typical severity
        severity: this.calculateDefaultSeverity(mlPredictions, patternInsights),
        
        // Stress Level: Use current stress prediction or user's typical stress
        stressLevel: this.calculateDefaultStressLevel(mlPredictions, riskAssessment, patternInsights),
        
        // Sleep Quality: Use recent sleep patterns or predicted impact
        sleepQuality: this.calculateDefaultSleepQuality(mlPredictions, patternInsights),
        
        // Duration: Use typical symptom duration based on patterns
        duration: this.calculateDefaultDuration(patternInsights),
        
        // Most likely symptom based on patterns and predictions
        mostLikelySymptom: this.calculateMostLikelySymptom(mlPredictions, patternInsights)
      };

      this.setCache(cacheKey, defaults);
      return defaults;
    } catch (error) {
      console.error('Error getting personalized symptom defaults:', error);
      return this.getFallbackSymptomDefaults();
    }
  }

  /**
   * Get personalized defaults for diet logging form
   */
  async getDietDefaults(): Promise<PersonalizedDietDefaults> {
    const cacheKey = 'diet_defaults';
    const cached = this.getCache(cacheKey);
    if (cached) return cached;

    try {
      // Get ML predictions and user patterns
      const [mlPredictions, patternInsights, riskAssessment] = await Promise.all([
        mlService.getRealtimePredictions().catch(() => null),
        patternInsightsService.getPatternInsights().catch(() => null),
        dynamicRiskFactorService.calculateDynamicRiskFactors().catch(() => null)
      ]);

      const defaults: PersonalizedDietDefaults = {
        // Mood levels based on current predictions and typical patterns
        moodBefore: this.calculateDefaultMoodBefore(mlPredictions, riskAssessment),
        moodAfter: this.calculateDefaultMoodAfter(mlPredictions, patternInsights),
        
        // Hydration based on user patterns and health recommendations
        hydrationLevel: this.calculateDefaultHydration(patternInsights, riskAssessment),
        
        // Eating speed based on user patterns and digestive health
        eatingSpeed: this.calculateDefaultEatingSpeed(patternInsights, riskAssessment),
        
        // Preferred meal time based on user patterns
        preferredMealTime: this.calculatePreferredMealTime(patternInsights),
        
        // Common food categories based on user's safe foods
        commonFoodCategories: this.calculateCommonFoodCategories(patternInsights),
        
        // Preferred preparation method based on digestive tolerance
        preferredPreparationMethod: this.calculatePreferredPreparation(patternInsights, riskAssessment)
      };

      this.setCache(cacheKey, defaults);
      return defaults;
    } catch (error) {
      console.error('Error getting personalized diet defaults:', error);
      return this.getFallbackDietDefaults();
    }
  }

  private calculateDefaultSeverity(mlPredictions: any, patternInsights: any): number {
    // Use predicted severity if available
    if (mlPredictions?.predicted_severity) {
      return Math.round(mlPredictions.predicted_severity * 10);
    }
    
    // Use pattern-based average severity
    if (patternInsights?.severity_patterns?.average_severity) {
      return Math.round(patternInsights.severity_patterns.average_severity);
    }
    
    // Default to moderate severity
    return 5;
  }

  private calculateDefaultStressLevel(mlPredictions: any, riskAssessment: any, patternInsights: any): number {
    // Use current stress prediction
    if (riskAssessment?.stress_level) {
      return Math.round(riskAssessment.stress_level * 10);
    }
    
    // Use ML stress correlation if available
    if (mlPredictions?.stress_correlation) {
      return Math.round(mlPredictions.stress_correlation * 10);
    }
    
    // Use pattern-based average
    if (patternInsights?.stress_patterns?.average_stress) {
      return Math.round(patternInsights.stress_patterns.average_stress);
    }
    
    return 5;
  }

  private calculateDefaultSleepQuality(mlPredictions: any, patternInsights: any): number {
    // Use sleep quality prediction if available
    if (mlPredictions?.sleep_quality_impact) {
      return Math.round((1 - mlPredictions.sleep_quality_impact) * 10);
    }
    
    // Use pattern-based sleep quality
    if (patternInsights?.sleep_patterns?.average_quality) {
      return Math.round(patternInsights.sleep_patterns.average_quality);
    }
    
    return 7; // Default to good sleep quality
  }

  private calculateDefaultDuration(patternInsights: any): number {
    // Use pattern-based average duration
    if (patternInsights?.symptom_patterns?.average_duration) {
      return Math.round(patternInsights.symptom_patterns.average_duration);
    }
    
    return 30; // Default 30 minutes
  }

  private calculateMostLikelySymptom(mlPredictions: any, patternInsights: any): number | undefined {
    // Use ML prediction for most likely symptom
    if (mlPredictions?.most_likely_symptom_id) {
      return mlPredictions.most_likely_symptom_id;
    }
    
    // Use pattern-based most frequent symptom
    if (patternInsights?.symptom_patterns?.most_frequent_symptom_id) {
      return patternInsights.symptom_patterns.most_frequent_symptom_id;
    }
    
    return undefined;
  }

  private calculateDefaultMoodBefore(mlPredictions: any, riskAssessment: any): number {
    // Use current mood prediction based on risk factors
    if (riskAssessment?.mood_impact) {
      return Math.round((1 - riskAssessment.mood_impact) * 10);
    }
    
    // Use ML mood correlation
    if (mlPredictions?.mood_correlation) {
      return Math.round(mlPredictions.mood_correlation * 10);
    }
    
    return 6; // Slightly positive default
  }

  private calculateDefaultMoodAfter(mlPredictions: any, patternInsights: any): number {
    // Typically mood after eating is slightly lower due to digestive concerns
    const moodBefore = this.calculateDefaultMoodBefore(mlPredictions, null);
    
    // Use pattern-based mood change if available
    if (patternInsights?.mood_patterns?.typical_mood_change) {
      return Math.max(1, Math.min(10, moodBefore + patternInsights.mood_patterns.typical_mood_change));
    }
    
    return Math.max(1, moodBefore - 1); // Slightly lower after eating
  }

  private calculateDefaultHydration(patternInsights: any, riskAssessment: any): number {
    // Use pattern-based hydration if available
    if (patternInsights?.hydration_patterns?.average_level) {
      return Math.round(patternInsights.hydration_patterns.average_level);
    }
    
    // Higher hydration recommended for digestive health
    return 7;
  }

  private calculateDefaultEatingSpeed(patternInsights: any, riskAssessment: any): 'slow' | 'normal' | 'fast' {
    // Use pattern-based eating speed
    if (patternInsights?.eating_patterns?.typical_speed) {
      return patternInsights.eating_patterns.typical_speed;
    }
    
    // Recommend slower eating for better digestion
    if (riskAssessment?.overallRiskScore > 0.6) {
      return 'slow';
    }
    
    return 'normal';
  }

  private calculatePreferredMealTime(patternInsights: any): string {
    // Use pattern-based preferred meal times
    if (patternInsights?.temporal_patterns?.length > 0) {
      const currentHour = new Date().getHours();
      const currentTime = new Date();
      currentTime.setMinutes(0, 0, 0);
      return currentTime.toISOString().slice(0, 16);
    }
    
    // Default to current time
    const now = new Date();
    now.setMinutes(0, 0, 0);
    return now.toISOString().slice(0, 16);
  }

  private calculateCommonFoodCategories(patternInsights: any): string[] {
    // Use pattern-based safe food categories
    if (patternInsights?.dietary_patterns?.safe_categories) {
      return patternInsights.dietary_patterns.safe_categories;
    }
    
    // Default to generally safe categories
    return ['Lean Proteins', 'Cooked Vegetables', 'Low FODMAP'];
  }

  private calculatePreferredPreparation(patternInsights: any, riskAssessment: any): string {
    // Use pattern-based preparation preference
    if (patternInsights?.dietary_patterns?.preferred_preparation) {
      return patternInsights.dietary_patterns.preferred_preparation;
    }
    
    // Recommend gentler preparation methods for higher risk
    if (riskAssessment?.overallRiskScore > 0.6) {
      return 'Steamed';
    }
    
    return 'Grilled';
  }

  private getFallbackSymptomDefaults(): PersonalizedSymptomDefaults {
    return {
      severity: 5,
      stressLevel: 5,
      sleepQuality: 7,
      duration: 30,
      mostLikelySymptom: undefined
    };
  }

  private getFallbackDietDefaults(): PersonalizedDietDefaults {
    return {
      moodBefore: 6,
      moodAfter: 5,
      hydrationLevel: 7,
      eatingSpeed: 'normal',
      preferredMealTime: new Date().toISOString().slice(0, 16),
      commonFoodCategories: ['Lean Proteins', 'Cooked Vegetables'],
      preferredPreparationMethod: 'Grilled'
    };
  }

  /**
   * Clear all cached defaults (useful when user patterns change significantly)
   */
  clearCache(): void {
    this.cache.clear();
    this.cacheExpiry.clear();
  }
}

export const personalizedDefaultsService = new PersonalizedDefaultsService();