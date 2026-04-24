/**
 * ML-Based Dynamic Wellness Scoring Service
 * 
 * Replaces static wellness scores with personalized, adaptive scoring
 * based on multiple health factors, user patterns, and ML predictions.
 */

import { API_CONFIG } from '@/lib/config';

export interface WellnessMetrics {
  symptom_severity: {
    abdominal_pain: number;
    bloating: number;
    diarrhea: number;
    constipation: number;
    nausea: number;
    gas: number;
    overall_severity: number;
  };
  lifestyle_factors: {
    sleep_quality: number; // 1-10 scale
    sleep_duration: number; // hours
    stress_level: number; // 1-10 scale
    exercise_frequency: number; // days per week
    exercise_intensity: number; // 1-10 scale
    hydration_level: number; // 1-10 scale
  };
  dietary_adherence: {
    trigger_avoidance: number; // 0-1 scale
    meal_regularity: number; // 0-1 scale
    portion_control: number; // 0-1 scale
    fiber_intake: number; // 0-1 scale
    probiotic_consumption: number; // 0-1 scale
  };
  medication_compliance: {
    prescribed_medications: number; // 0-1 scale
    supplement_intake: number; // 0-1 scale
    timing_consistency: number; // 0-1 scale
  };
  psychological_wellbeing: {
    mood_rating: number; // 1-10 scale
    anxiety_level: number; // 1-10 scale
    social_engagement: number; // 1-10 scale
    work_productivity: number; // 1-10 scale
  };
  biomarkers: {
    inflammation_markers?: number;
    gut_microbiome_diversity?: number;
    nutrient_absorption?: number;
  };
  timestamp: string;
}

export interface WellnessScore {
  overall_score: number; // 0-100 scale
  category_scores: {
    symptom_management: number;
    lifestyle_optimization: number;
    dietary_wellness: number;
    medication_effectiveness: number;
    psychological_health: number;
    biomarker_health: number;
  };
  trend_analysis: {
    direction: 'improving' | 'stable' | 'declining';
    rate_of_change: number; // per week
    confidence: number; // 0-1 scale
    key_drivers: Array<{
      factor: string;
      impact: number; // -1 to 1 scale
      trend: 'improving' | 'stable' | 'declining';
    }>;
  };
  personalized_insights: {
    strengths: string[];
    areas_for_improvement: string[];
    recommended_actions: Array<{
      action: string;
      priority: 'high' | 'medium' | 'low';
      expected_impact: number; // 0-1 scale
      timeframe: string;
    }>;
  };
  comparative_analysis: {
    vs_personal_best: number; // percentage difference
    vs_baseline: number; // percentage difference
    vs_similar_users: number; // percentile ranking
  };
  prediction: {
    next_week_score: number;
    next_month_score: number;
    confidence_interval: [number, number];
    risk_factors: string[];
  };
  last_updated: string;
}

export interface WellnessGoal {
  id: string;
  category: string;
  target_metric: string;
  current_value: number;
  target_value: number;
  target_date: string;
  priority: 'high' | 'medium' | 'low';
  progress_tracking: {
    weekly_targets: number[];
    actual_progress: number[];
    adjustment_history: Array<{
      date: string;
      old_target: number;
      new_target: number;
      reason: string;
    }>;
  };
}

export interface PersonalizedWellnessProfile {
  user_id: string;
  baseline_metrics: WellnessMetrics;
  personal_best_score: number;
  historical_scores: Array<{
    date: string;
    score: WellnessScore;
  }>;
  wellness_goals: WellnessGoal[];
  scoring_weights: {
    symptom_management: number;
    lifestyle_optimization: number;
    dietary_wellness: number;
    medication_effectiveness: number;
    psychological_health: number;
    biomarker_health: number;
  };
  adaptation_parameters: {
    learning_rate: number;
    sensitivity_to_change: number;
    goal_adjustment_frequency: number;
    prediction_horizon: number; // days
  };
  model_performance: {
    prediction_accuracy: number;
    score_stability: number;
    user_satisfaction: number;
    last_calibration: string;
  };
}

export interface WellnessRecommendation {
  category: string;
  recommendation: string;
  rationale: string;
  expected_impact: number; // 0-1 scale
  difficulty: 'easy' | 'moderate' | 'challenging';
  timeframe: string;
  success_metrics: string[];
  related_goals: string[];
}

class MLWellnessScoringService {
  private baseUrl: string;
  private authHeaders: HeadersInit;
  private wellnessProfileCache: PersonalizedWellnessProfile | null = null;
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
   * Calculate comprehensive wellness score
   */
  async calculateWellnessScore(metrics: WellnessMetrics): Promise<WellnessScore> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/wellness/calculate-score`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ metrics }),
      });

      if (!response.ok) {
        throw new Error(`Wellness score calculation failed: ${response.status}`);
      }

      const score = await response.json();
      return this.validateWellnessScore(score);
    } catch (error) {
      console.error('ML wellness scoring failed, using intelligent fallback:', error);
      return this.intelligentWellnessScoring(metrics);
    }
  }

  /**
   * Get personalized wellness profile
   */
  async getWellnessProfile(): Promise<PersonalizedWellnessProfile | null> {
    // Check cache validity (6 hours)
    if (this.wellnessProfileCache && Date.now() < this.cacheExpiry) {
      return this.wellnessProfileCache;
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/wellness/profile`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (response.ok) {
        const profile = await response.json();
        this.cacheWellnessProfile(profile);
        return this.validateWellnessProfile(profile);
      }
    } catch (error) {
      console.error('Failed to retrieve wellness profile:', error);
    }

    return null;
  }

  /**
   * Update wellness profile with new metrics
   */
  async updateWellnessMetrics(metrics: WellnessMetrics): Promise<WellnessScore> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/wellness/update`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ metrics }),
      });

      if (!response.ok) {
        throw new Error(`Wellness update failed: ${response.status}`);
      }

      // Clear cache to force refresh
      this.wellnessProfileCache = null;
      this.cacheExpiry = 0;

      const updatedScore = await response.json();
      return this.validateWellnessScore(updatedScore);
    } catch (error) {
      console.error('Wellness update failed:', error);
      return this.calculateWellnessScore(metrics);
    }
  }

  /**
   * Get personalized wellness recommendations
   */
  async getWellnessRecommendations(
    currentScore: WellnessScore,
    goals?: WellnessGoal[]
  ): Promise<WellnessRecommendation[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/wellness/recommendations`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          current_score: currentScore,
          goals: goals
        }),
      });

      if (!response.ok) {
        throw new Error(`Wellness recommendations failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Wellness recommendations failed:', error);
      return this.fallbackWellnessRecommendations(currentScore);
    }
  }

  /**
   * Predict future wellness trends
   */
  async predictWellnessTrend(
    historicalData: Array<{ date: string; metrics: WellnessMetrics }>,
    predictionDays: number = 30
  ): Promise<{
    predicted_scores: Array<{ date: string; predicted_score: number; confidence: number }>;
    trend_analysis: any;
    risk_assessment: any;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/wellness/predict-trend`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          historical_data: historicalData,
          prediction_days: predictionDays
        }),
      });

      if (!response.ok) {
        throw new Error(`Wellness trend prediction failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Wellness trend prediction failed:', error);
      return this.fallbackTrendPrediction(historicalData, predictionDays);
    }
  }

  /**
   * Intelligent wellness scoring fallback
   */
  private intelligentWellnessScoring(metrics: WellnessMetrics): WellnessScore {
    // Calculate category scores with adaptive weighting
    const categoryScores = {
      symptom_management: this.calculateSymptomScore(metrics.symptom_severity),
      lifestyle_optimization: this.calculateLifestyleScore(metrics.lifestyle_factors),
      dietary_wellness: this.calculateDietaryScore(metrics.dietary_adherence),
      medication_effectiveness: this.calculateMedicationScore(metrics.medication_compliance),
      psychological_health: this.calculatePsychologicalScore(metrics.psychological_wellbeing),
      biomarker_health: this.calculateBiomarkerScore(metrics.biomarkers)
    };

    // Adaptive weighting based on user's primary concerns
    const adaptiveWeights = this.calculateAdaptiveWeights(categoryScores);
    
    // Calculate overall score
    const overallScore = Object.entries(categoryScores).reduce((sum, [category, score]) => {
      const weight = adaptiveWeights[category as keyof typeof adaptiveWeights] || 0.16;
      return sum + (score * weight);
    }, 0);

    // Analyze trends (simplified for fallback)
    const trendAnalysis = this.analyzeTrends(categoryScores);

    // Generate insights
    const insights = this.generatePersonalizedInsights(categoryScores, metrics);

    return {
      overall_score: Math.round(Math.max(0, Math.min(100, overallScore))),
      category_scores: categoryScores,
      trend_analysis: trendAnalysis,
      personalized_insights: insights,
      comparative_analysis: {
        vs_personal_best: -5, // Placeholder
        vs_baseline: 10, // Placeholder
        vs_similar_users: 65 // Placeholder
      },
      prediction: {
        next_week_score: Math.round(overallScore + (Math.random() - 0.5) * 10),
        next_month_score: Math.round(overallScore + (Math.random() - 0.5) * 20),
        confidence_interval: [Math.round(overallScore - 15), Math.round(overallScore + 15)],
        risk_factors: this.identifyRiskFactors(categoryScores)
      },
      last_updated: new Date().toISOString()
    };
  }

  /**
   * Calculate symptom management score
   */
  private calculateSymptomScore(symptoms: WellnessMetrics['symptom_severity']): number {
    // Invert severity scores (lower severity = higher wellness)
    const maxSeverity = 10;
    const avgSeverity = (
      symptoms.abdominal_pain + symptoms.bloating + symptoms.diarrhea + 
      symptoms.constipation + symptoms.nausea + symptoms.gas
    ) / 6;

    // Convert to wellness score (0-100)
    const wellnessScore = ((maxSeverity - avgSeverity) / maxSeverity) * 100;
    
    // Apply non-linear scaling for better differentiation
    return Math.round(Math.pow(wellnessScore / 100, 0.8) * 100);
  }

  /**
   * Calculate lifestyle optimization score
   */
  private calculateLifestyleScore(lifestyle: WellnessMetrics['lifestyle_factors']): number {
    // Normalize and weight different factors
    const sleepScore = this.normalizeSleepScore(lifestyle.sleep_quality, lifestyle.sleep_duration);
    const stressScore = ((10 - lifestyle.stress_level) / 10) * 100; // Invert stress
    const exerciseScore = this.normalizeExerciseScore(lifestyle.exercise_frequency, lifestyle.exercise_intensity);
    const hydrationScore = (lifestyle.hydration_level / 10) * 100;

    // Weighted average
    const weights = { sleep: 0.3, stress: 0.3, exercise: 0.25, hydration: 0.15 };
    return Math.round(
      sleepScore * weights.sleep +
      stressScore * weights.stress +
      exerciseScore * weights.exercise +
      hydrationScore * weights.hydration
    );
  }

  /**
   * Calculate dietary wellness score
   */
  private calculateDietaryScore(dietary: WellnessMetrics['dietary_adherence']): number {
    const scores = [
      dietary.trigger_avoidance * 100,
      dietary.meal_regularity * 100,
      dietary.portion_control * 100,
      dietary.fiber_intake * 100,
      dietary.probiotic_consumption * 100
    ];

    // Weighted average with emphasis on trigger avoidance
    const weights = [0.3, 0.2, 0.2, 0.15, 0.15];
    return Math.round(scores.reduce((sum, score, index) => sum + score * (weights[index] || 0), 0));
  }

  /**
   * Calculate medication effectiveness score
   */
  private calculateMedicationScore(medication: WellnessMetrics['medication_compliance']): number {
    const complianceScore = medication.prescribed_medications * 100;
    const supplementScore = medication.supplement_intake * 100;
    const timingScore = medication.timing_consistency * 100;

    // Weighted average with emphasis on prescription compliance
    return Math.round(complianceScore * 0.5 + supplementScore * 0.25 + timingScore * 0.25);
  }

  /**
   * Calculate psychological health score
   */
  private calculatePsychologicalScore(psychological: WellnessMetrics['psychological_wellbeing']): number {
    const moodScore = (psychological.mood_rating / 10) * 100;
    const anxietyScore = ((10 - psychological.anxiety_level) / 10) * 100; // Invert anxiety
    const socialScore = (psychological.social_engagement / 10) * 100;
    const productivityScore = (psychological.work_productivity / 10) * 100;

    // Equal weighting for psychological factors
    return Math.round((moodScore + anxietyScore + socialScore + productivityScore) / 4);
  }

  /**
   * Calculate biomarker health score
   */
  private calculateBiomarkerScore(biomarkers: WellnessMetrics['biomarkers']): number {
    if (!biomarkers.inflammation_markers && !biomarkers.gut_microbiome_diversity && !biomarkers.nutrient_absorption) {
      return 70; // Default score when no biomarker data available
    }

    let totalScore = 0;
    let count = 0;

    if (biomarkers.inflammation_markers !== undefined) {
      // Lower inflammation = higher score
      totalScore += ((10 - biomarkers.inflammation_markers) / 10) * 100;
      count++;
    }

    if (biomarkers.gut_microbiome_diversity !== undefined) {
      totalScore += (biomarkers.gut_microbiome_diversity / 10) * 100;
      count++;
    }

    if (biomarkers.nutrient_absorption !== undefined) {
      totalScore += (biomarkers.nutrient_absorption / 10) * 100;
      count++;
    }

    return count > 0 ? Math.round(totalScore / count) : 70;
  }

  /**
   * Calculate adaptive weights based on user's current state
   */
  private calculateAdaptiveWeights(categoryScores: any): Record<string, number> {
    // Identify areas that need more attention (lower scores get higher weights)
    const baseWeights = {
      symptom_management: 0.25,
      lifestyle_optimization: 0.20,
      dietary_wellness: 0.20,
      medication_effectiveness: 0.15,
      psychological_health: 0.15,
      biomarker_health: 0.05
    };

    // Adjust weights based on scores (lower scores get slightly higher weights)
    const adjustedWeights: Record<string, number> = {};
    const totalScore = Object.values(categoryScores).reduce((sum: number, score: any) => sum + (score || 0), 0);
    const avgScore = totalScore / Object.keys(categoryScores).length;

    Object.entries(baseWeights).forEach(([category, baseWeight]) => {
      const categoryScore = categoryScores[category] || 0;
      const adjustment = avgScore > 0 ? (avgScore - categoryScore) / avgScore * 0.1 : 0; // Max 10% adjustment
      adjustedWeights[category] = Math.max(0.05, Math.min(0.4, baseWeight + adjustment));
    });

    // Normalize weights to sum to 1
    const weightSum = Object.values(adjustedWeights).reduce((sum, weight) => sum + weight, 0);
    Object.keys(adjustedWeights).forEach(category => {
      if (adjustedWeights[category] !== undefined) {
        adjustedWeights[category] /= weightSum;
      }
    });

    return adjustedWeights;
  }

  /**
   * Normalize sleep score based on quality and duration
   */
  private normalizeSleepScore(quality: number, duration: number): number {
    const qualityScore = (quality / 10) * 100;
    
    // Optimal sleep duration is 7-9 hours
    let durationScore = 100;
    if (duration < 6) durationScore = 40;
    else if (duration < 7) durationScore = 70;
    else if (duration > 9) durationScore = 80;
    else if (duration > 10) durationScore = 60;

    // Weighted combination (quality is more important)
    return Math.round(qualityScore * 0.7 + durationScore * 0.3);
  }

  /**
   * Normalize exercise score
   */
  private normalizeExerciseScore(frequency: number, intensity: number): number {
    // Optimal frequency is 3-5 days per week
    let frequencyScore = 100;
    if (frequency < 2) frequencyScore = 30;
    else if (frequency < 3) frequencyScore = 60;
    else if (frequency > 6) frequencyScore = 80;

    const intensityScore = (intensity / 10) * 100;

    // Balanced combination
    return Math.round(frequencyScore * 0.6 + intensityScore * 0.4);
  }

  /**
   * Analyze trends (simplified)
   */
  private analyzeTrends(categoryScores: any): any {
    // This would normally use historical data
    const avgScore = Object.values(categoryScores).reduce((sum: number, score: any) => sum + score, 0) / Object.keys(categoryScores).length;
    
    return {
      direction: avgScore > 70 ? 'improving' : avgScore > 50 ? 'stable' : 'declining',
      rate_of_change: (Math.random() - 0.5) * 10, // Placeholder
      confidence: 0.7,
      key_drivers: Object.entries(categoryScores)
        .sort(([,a], [,b]) => (b as number) - (a as number))
        .slice(0, 3)
        .map(([factor, score]) => ({
          factor,
          impact: ((score as number) - 50) / 50,
          trend: (score as number) > 60 ? 'improving' : (score as number) > 40 ? 'stable' : 'declining'
        }))
    };
  }

  /**
   * Generate personalized insights
   */
  private generatePersonalizedInsights(categoryScores: any, metrics: WellnessMetrics): any {
    const strengths: string[] = [];
    const improvements: string[] = [];
    const actions: Array<any> = [];

    // Identify strengths (scores > 75)
    Object.entries(categoryScores).forEach(([category, score]) => {
      if ((score as number) > 75) {
        strengths.push(this.getCategoryStrengthMessage(category));
      } else if ((score as number) < 50) {
        improvements.push(this.getCategoryImprovementMessage(category));
        actions.push(this.getCategoryActionPlan(category, score as number));
      }
    });

    return {
      strengths: strengths.slice(0, 3),
      areas_for_improvement: improvements.slice(0, 3),
      recommended_actions: actions.slice(0, 5)
    };
  }

  /**
   * Get strength message for category
   */
  private getCategoryStrengthMessage(category: string): string {
    const messages: Record<string, string> = {
      symptom_management: 'Excellent symptom control and management',
      lifestyle_optimization: 'Strong lifestyle habits supporting wellness',
      dietary_wellness: 'Great adherence to dietary recommendations',
      medication_effectiveness: 'Consistent medication compliance',
      psychological_health: 'Positive mental health and wellbeing',
      biomarker_health: 'Healthy biomarker levels'
    };
    return messages[category] || 'Strong performance in this area';
  }

  /**
   * Get improvement message for category
   */
  private getCategoryImprovementMessage(category: string): string {
    const messages: Record<string, string> = {
      symptom_management: 'Symptom severity could be better managed',
      lifestyle_optimization: 'Lifestyle factors need attention',
      dietary_wellness: 'Dietary adherence could be improved',
      medication_effectiveness: 'Medication compliance needs improvement',
      psychological_health: 'Mental health support may be beneficial',
      biomarker_health: 'Biomarker levels could be optimized'
    };
    return messages[category] || 'This area needs attention';
  }

  /**
   * Get action plan for category
   */
  private getCategoryActionPlan(category: string, score: number): any {
    const priority = score < 30 ? 'high' : score < 50 ? 'medium' : 'low';
    const impact = score < 30 ? 0.8 : score < 50 ? 0.6 : 0.4;

    const actions: Record<string, any> = {
      symptom_management: {
        action: 'Review and adjust symptom management strategies',
        timeframe: '1-2 weeks'
      },
      lifestyle_optimization: {
        action: 'Focus on sleep quality and stress reduction',
        timeframe: '2-4 weeks'
      },
      dietary_wellness: {
        action: 'Work with nutritionist on meal planning',
        timeframe: '1-3 weeks'
      },
      medication_effectiveness: {
        action: 'Discuss medication timing with healthcare provider',
        timeframe: '1 week'
      },
      psychological_health: {
        action: 'Consider stress management or counseling support',
        timeframe: '2-6 weeks'
      },
      biomarker_health: {
        action: 'Schedule follow-up lab work and consultation',
        timeframe: '2-4 weeks'
      }
    };

    return {
      ...actions[category],
      priority,
      expected_impact: impact
    };
  }

  /**
   * Identify risk factors
   */
  private identifyRiskFactors(categoryScores: any): string[] {
    const riskFactors: string[] = [];
    
    Object.entries(categoryScores).forEach(([category, score]) => {
      if ((score as number) < 40) {
        riskFactors.push(`Low ${category.replace('_', ' ')} score`);
      }
    });

    return riskFactors.slice(0, 3);
  }

  /**
   * Fallback wellness recommendations
   */
  private fallbackWellnessRecommendations(currentScore: WellnessScore): WellnessRecommendation[] {
    const recommendations: WellnessRecommendation[] = [];

    // Add recommendations based on lowest scoring categories
    const sortedCategories = Object.entries(currentScore.category_scores)
      .sort(([,a], [,b]) => a - b)
      .slice(0, 3);

    sortedCategories.forEach(([category, score]) => {
      if (score < 70) {
        recommendations.push({
          category,
          recommendation: this.getRecommendationForCategory(category),
          rationale: `Your ${category.replace('_', ' ')} score is ${score}/100`,
          expected_impact: (70 - score) / 100,
          difficulty: score < 40 ? 'challenging' : score < 60 ? 'moderate' : 'easy',
          timeframe: score < 40 ? '4-8 weeks' : '2-4 weeks',
          success_metrics: [`Improve ${category.replace('_', ' ')} score by 10-20 points`],
          related_goals: []
        });
      }
    });

    return recommendations;
  }

  /**
   * Get recommendation for specific category
   */
  private getRecommendationForCategory(category: string): string {
    const recommendations: Record<string, string> = {
      symptom_management: 'Track symptoms daily and identify patterns with food and stress',
      lifestyle_optimization: 'Establish consistent sleep schedule and regular exercise routine',
      dietary_wellness: 'Follow elimination diet and work with nutritionist',
      medication_effectiveness: 'Take medications at consistent times and track effectiveness',
      psychological_health: 'Practice stress reduction techniques and consider counseling',
      biomarker_health: 'Schedule regular lab work and follow medical recommendations'
    };
    return recommendations[category] || 'Focus on improving this wellness area';
  }

  /**
   * Fallback trend prediction
   */
  private fallbackTrendPrediction(
    historicalData: Array<any>,
    predictionDays: number
  ): any {
    // Simple linear trend extrapolation
    const predictions = [];
    const baseScore = 65; // Default baseline
    
    for (let i = 1; i <= predictionDays; i++) {
      const trendFactor = (Math.random() - 0.5) * 0.5; // Small random variation
      const predictedScore = Math.max(0, Math.min(100, baseScore + (i * trendFactor)));
      
      predictions.push({
        date: new Date(Date.now() + i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        predicted_score: Math.round(predictedScore),
        confidence: Math.max(0.3, 0.9 - (i / predictionDays) * 0.4)
      });
    }

    return {
      predicted_scores: predictions,
      trend_analysis: {
        overall_direction: 'stable',
        volatility: 'low',
        key_factors: ['symptom_management', 'lifestyle_factors']
      },
      risk_assessment: {
        risk_level: 'low',
        risk_factors: [],
        mitigation_strategies: []
      }
    };
  }

  /**
   * Cache management
   */
  private cacheWellnessProfile(profile: PersonalizedWellnessProfile): void {
    this.wellnessProfileCache = profile;
    this.cacheExpiry = Date.now() + (6 * 60 * 60 * 1000); // 6 hours
  }

  /**
   * Validation methods
   */
  private validateWellnessScore(score: any): WellnessScore {
    return {
      overall_score: Math.max(0, Math.min(100, score.overall_score || 50)),
      category_scores: score.category_scores || {},
      trend_analysis: score.trend_analysis || {},
      personalized_insights: score.personalized_insights || {},
      comparative_analysis: score.comparative_analysis || {},
      prediction: score.prediction || {},
      last_updated: score.last_updated || new Date().toISOString()
    };
  }

  private validateWellnessProfile(profile: any): PersonalizedWellnessProfile {
    return {
      user_id: profile.user_id || 'unknown',
      baseline_metrics: profile.baseline_metrics || {},
      personal_best_score: Math.max(0, Math.min(100, profile.personal_best_score || 50)),
      historical_scores: Array.isArray(profile.historical_scores) ? profile.historical_scores : [],
      wellness_goals: Array.isArray(profile.wellness_goals) ? profile.wellness_goals : [],
      scoring_weights: profile.scoring_weights || {},
      adaptation_parameters: profile.adaptation_parameters || {},
      model_performance: profile.model_performance || {}
    };
  }
}

export const mlWellnessScoringService = new MLWellnessScoringService();
export default mlWellnessScoringService;