'use client';

const API_BASE_URL = process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000';

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
    this.baseUrl = `${API_BASE_URL}/api/v1/personalization`;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = localStorage.getItem('authToken');
    
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

  // Get user's personalization profile
  async getPersonalizationProfile(): Promise<PersonalizationProfile> {
    try {
      return await this.makeRequest<PersonalizationProfile>('/profile');
    } catch (error) {
      console.error('Error fetching personalization profile:', error);
      // Return default profile on error
      return {
        user_id: 'unknown',
        ml_thresholds: {
          high_risk_threshold: 0.7,
          medium_risk_threshold: 0.4,
          flare_prediction_threshold: 0.6,
          severity_threshold: 0.5,
        },
        learning_patterns: {
          trigger_foods: [],
          effective_interventions: [],
          symptom_correlations: {},
          time_patterns: {},
        },
        adaptive_settings: {
          recommendation_frequency: 'daily',
          intervention_aggressiveness: 'moderate',
          learning_rate: 0.1,
          confidence_threshold: 0.6,
        },
        personalization_score: 0.5,
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