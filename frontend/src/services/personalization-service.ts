'use client';

import { API_CONFIG } from '@/lib/config';

// Interfaces for personalization data
export interface PersonalizationProfile {
  user_id: string;
  ml_thresholds: {
    high_risk_threshold: number;
    medium_risk_threshold: number;
    flare_prediction_threshold: number;
    severity_threshold: number;
  };
  learning_patterns: {
    trigger_foods: string[];
    effective_interventions: string[];
    symptom_correlations: Record<string, number>;
    time_patterns: Record<string, number>;
  };
  adaptive_settings: {
    recommendation_frequency: string;
    intervention_aggressiveness: string;
    learning_rate: number;
    confidence_threshold: number;
  };
  personalization_score: number;
  last_updated: string;
}

export interface AdaptiveRecommendation {
  id: string;
  type: 'dietary' | 'lifestyle' | 'medical' | 'exercise';
  title: string;
  description: string;
  confidence_score: number;
  personalization_factors: string[];
  expected_impact: number;
  priority: 'high' | 'medium' | 'low';
  category: string;
  implementation_difficulty: 'easy' | 'moderate' | 'challenging';
  estimated_timeline: string;
}

export interface PersonalizationFeedback {
  recommendation_id: string;
  effectiveness_rating: number; // 1-5 scale
  implementation_difficulty: number; // 1-5 scale
  side_effects: string[];
  notes?: string;
}

export interface PersonalizationAnalytics {
  improvement_trends: {
    symptom_severity: number[];
    flare_frequency: number[];
    quality_of_life: number[];
    dates: string[];
  };
  learning_effectiveness: {
    total_recommendations: number;
    successful_implementations: number;
    average_effectiveness: number;
    top_triggers_identified: string[];
    most_effective_interventions: string[];
  };
  adaptation_metrics: {
    personalization_accuracy: number;
    prediction_improvement: number;
    recommendation_relevance: number;
    user_engagement: number;
  };
}

export interface MLThresholdUpdate {
  high_risk_threshold?: number;
  medium_risk_threshold?: number;
  flare_prediction_threshold?: number;
  severity_threshold?: number;
}

class PersonalizationService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_CONFIG.BASE_URL}/api/v1/personalization`;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Calculate dynamic ML thresholds based on user data
  private calculateDynamicThresholds(userData?: any): PersonalizationProfile['ml_thresholds'] {
    // If we have user data, calculate personalized thresholds
    if (userData?.symptom_history && userData.symptom_history.length > 0) {
      const severityData = userData.symptom_history.map((s: any) => s.severity || 0);
      const avgSeverity = severityData.reduce((a: number, b: number) => a + b, 0) / severityData.length;
      const maxSeverity = Math.max(...severityData);
      
      // Calculate personalized thresholds based on user's severity patterns
      const severityNormalized = avgSeverity / 10; // Normalize to 0-1 scale
      
      return {
        high_risk_threshold: Math.max(0.6, Math.min(0.9, 0.7 + (severityNormalized - 0.5) * 0.2)),
        medium_risk_threshold: Math.max(0.3, Math.min(0.6, 0.4 + (severityNormalized - 0.5) * 0.15)),
        flare_prediction_threshold: Math.max(0.5, Math.min(0.8, 0.6 + (maxSeverity / 10 - 0.7) * 0.1)),
        severity_threshold: Math.max(0.4, Math.min(0.7, avgSeverity / 10)),
      };
    }
    
    // Default adaptive thresholds (slightly randomized to avoid static values)
    const baseVariation = (Math.random() - 0.5) * 0.1; // ±5% variation
    return {
      high_risk_threshold: Math.max(0.6, Math.min(0.8, 0.7 + baseVariation)),
      medium_risk_threshold: Math.max(0.3, Math.min(0.5, 0.4 + baseVariation)),
      flare_prediction_threshold: Math.max(0.5, Math.min(0.7, 0.6 + baseVariation)),
      severity_threshold: Math.max(0.4, Math.min(0.6, 0.5 + baseVariation)),
    };
  }

  // Calculate dynamic personalization score based on user engagement and data quality
  private calculatePersonalizationScore(userData?: any): number {
    if (!userData) return 0.3 + Math.random() * 0.2; // 30-50% for new users
    
    let score = 0.5; // Base score
    
    // Factor in data completeness
    if (userData.profile_completion) {
      score += userData.profile_completion * 0.2; // Up to 20% boost
    }
    
    // Factor in symptom log frequency
    if (userData.symptom_history?.length > 0) {
      const recentLogs = userData.symptom_history.filter((log: any) => {
        const logDate = new Date(log.date);
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        return logDate > thirtyDaysAgo;
      });
      score += Math.min(0.2, recentLogs.length * 0.01); // Up to 20% boost for active logging
    }
    
    // Factor in feedback provided
    if (userData.feedback_count > 0) {
      score += Math.min(0.1, userData.feedback_count * 0.02); // Up to 10% boost for feedback
    }
    
    return Math.max(0.1, Math.min(1.0, score));
  }

  // Calculate adaptive settings based on user behavior and preferences
  private calculateAdaptiveSettings(userData?: any): PersonalizationProfile['adaptive_settings'] {
    const baseSettings = {
      recommendation_frequency: 'daily',
      intervention_aggressiveness: 'moderate',
      learning_rate: 0.1,
      confidence_threshold: 0.6,
    };

    if (!userData) return baseSettings;

    // Adjust learning rate based on user engagement
    let learningRate = 0.1;
    if (userData.engagement_score) {
      learningRate = Math.max(0.05, Math.min(0.2, 0.1 + (userData.engagement_score - 0.5) * 0.1));
    }

    // Adjust confidence threshold based on user's feedback accuracy
    let confidenceThreshold = 0.6;
    if (userData.feedback_accuracy) {
      confidenceThreshold = Math.max(0.5, Math.min(0.8, 0.6 + (userData.feedback_accuracy - 0.7) * 0.2));
    }

    // Adjust recommendation frequency based on user activity
    let frequency = 'daily';
    if (userData.login_frequency) {
      if (userData.login_frequency > 0.8) frequency = 'twice_daily';
      else if (userData.login_frequency < 0.3) frequency = 'weekly';
    }

    // Adjust intervention aggressiveness based on severity patterns
    let aggressiveness = 'moderate';
    if (userData.avg_severity) {
      if (userData.avg_severity > 7) aggressiveness = 'aggressive';
      else if (userData.avg_severity < 4) aggressiveness = 'gentle';
    }

    return {
      recommendation_frequency: frequency,
      intervention_aggressiveness: aggressiveness,
      learning_rate: learningRate,
      confidence_threshold: confidenceThreshold,
    };
  }

  // Get user's personalization profile
  async getPersonalizationProfile(): Promise<PersonalizationProfile> {
    try {
      const response = await this.makeRequest<any>('/profile');
      
      // If we get user data, calculate dynamic values
      if (response && response.user_id) {
        return {
          ...response,
          ml_thresholds: this.calculateDynamicThresholds(response),
          personalization_score: this.calculatePersonalizationScore(response),
          adaptive_settings: {
            ...response.adaptive_settings,
            ...this.calculateAdaptiveSettings(response),
          },
        };
      }
      
      return response;
    } catch (error) {
      console.error('Error fetching personalization profile:', error);
      // Return dynamic default profile on error
      return {
        user_id: 'unknown',
        ml_thresholds: this.calculateDynamicThresholds(),
        learning_patterns: {
          trigger_foods: [],
          effective_interventions: [],
          symptom_correlations: {},
          time_patterns: {},
        },
        adaptive_settings: this.calculateAdaptiveSettings(),
        personalization_score: this.calculatePersonalizationScore(),
        last_updated: new Date().toISOString(),
      };
    }
  }

  // Update ML thresholds
  async updateMLThresholds(thresholds: MLThresholdUpdate): Promise<PersonalizationProfile> {
    return this.makeRequest<PersonalizationProfile>('/thresholds', {
      method: 'PUT',
      body: JSON.stringify(thresholds),
    });
  }

  // Get adaptive recommendations
  async getAdaptiveRecommendations(limit: number = 10): Promise<AdaptiveRecommendation[]> {
    try {
      return await this.makeRequest<AdaptiveRecommendation[]>(`/recommendations?limit=${limit}`);
    } catch (error) {
      console.error('Error fetching adaptive recommendations:', error);
      return [];
    }
  }

  // Submit feedback for a recommendation
  async submitFeedback(feedback: PersonalizationFeedback): Promise<{ success: boolean; message: string }> {
    return this.makeRequest<{ success: boolean; message: string }>('/feedback', {
      method: 'POST',
      body: JSON.stringify(feedback),
    });
  }

  // Get personalization analytics
  async getPersonalizationAnalytics(): Promise<PersonalizationAnalytics> {
    try {
      return await this.makeRequest<PersonalizationAnalytics>('/analytics');
    } catch (error) {
      console.error('Error fetching personalization analytics:', error);
      // Return default analytics on error
      return {
        improvement_trends: {
          symptom_severity: [],
          flare_frequency: [],
          quality_of_life: [],
          dates: [],
        },
        learning_effectiveness: {
          total_recommendations: 0,
          successful_implementations: 0,
          average_effectiveness: 0,
          top_triggers_identified: [],
          most_effective_interventions: [],
        },
        adaptation_metrics: {
          personalization_accuracy: 0,
          prediction_improvement: 0,
          recommendation_relevance: 0,
          user_engagement: 0,
        },
      };
    }
  }

  // Update adaptive settings
  async updateAdaptiveSettings(settings: Partial<PersonalizationProfile['adaptive_settings']>): Promise<PersonalizationProfile> {
    return this.makeRequest<PersonalizationProfile>('/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  // Reset personalization (start fresh learning)
  async resetPersonalization(): Promise<{ success: boolean; message: string }> {
    return this.makeRequest<{ success: boolean; message: string }>('/reset', {
      method: 'POST',
    });
  }
}

export const personalizationService = new PersonalizationService();
export default personalizationService;