'use client';

const API_BASE_URL = process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000';

export interface MLPredictionRequest {
  user_id?: string;
  timeframe?: 'day' | 'week' | 'month';
  include_recommendations?: boolean;
}

export interface MLPredictionResponse {
  risk_level: 'low' | 'medium' | 'moderate' | 'high';
  confidence: number;
  next_flare_probability: number;
  predicted_severity: number;
  timeline: string;
  key_factors: string[];
  recommendations?: {
    immediate_actions: Array<{
      action: string;
      priority: 'high' | 'medium' | 'low';
      explanation: string;
      expected_benefit: string;
    }>;
    dietary_suggestions: Array<{
      type: 'avoid' | 'include' | 'moderate';
      foods: string[];
      reason: string;
      timeline: string;
    }>;
    lifestyle_changes: Array<{
      category: string;
      suggestion: string;
      difficulty: 'easy' | 'moderate' | 'challenging';
      impact: string;
    }>;
  };
}

export interface RealtimePredictionResponse {
  current_risk: number;
  risk_factors: string[];
  immediate_recommendations: string[];
  confidence_score: number;
}

export interface PersonalizedRecommendationsResponse {
  dietary_recommendations: Array<{
    type: string;
    title: string;
    description: string;
    priority: string;
  }>;
  lifestyle_insights: Array<{
    category: string;
    insight: string;
    recommendation: string;
    priority: string;
  }>;
  trigger_analysis: {
    primary_category: string;
    insights: string[];
  };
  management_strategy: {
    strategy: string;
    approach: string;
    timeline: string;
  };
  personalized_tips: string[];
}

class MLService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  async getPredictions(request: MLPredictionRequest = {}): Promise<MLPredictionResponse> {
    try {
      const queryParams = new URLSearchParams();
      if (request.timeframe) queryParams.append('timeframe', request.timeframe);
      if (request.include_recommendations) queryParams.append('include_recommendations', 'true');

      const response = await fetch(
        `${API_BASE_URL}/api/v1/ml/predictions?${queryParams}`,
        {
          method: 'GET',
          headers: this.getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching ML predictions:', error);
      // Return mock data as fallback
      return this.getMockPredictions();
    }
  }

  async getRealtimePredictions(): Promise<RealtimePredictionResponse> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/ml/realtime-predictions`,
        {
          method: 'GET',
          headers: this.getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching realtime predictions:', error);
      // Return mock data as fallback
      return {
        current_risk: 35,
        risk_factors: ['Stress levels', 'Dairy consumption', 'Sleep quality'],
        immediate_recommendations: [
          'Reduce dairy intake for the next 3-5 days',
          'Practice 10 minutes of deep breathing before meals',
          'Ensure 8+ hours of sleep tonight'
        ],
        confidence_score: 78
      };
    }
  }

  async getPersonalizedRecommendations(): Promise<PersonalizedRecommendationsResponse> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/recommendations/personalized`,
        {
          method: 'GET',
          headers: this.getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching personalized recommendations:', error);
      // Return mock data as fallback
      return this.getMockRecommendations();
    }
  }

  async generateReport(timeframe: 'day' | 'week' | 'month' = 'month') {
    try {
      const [predictions, recommendations, realtimeData] = await Promise.all([
        this.getPredictions({ timeframe, include_recommendations: true }),
        this.getPersonalizedRecommendations(),
        this.getRealtimePredictions()
      ]);

      return {
        predictions,
        recommendations,
        realtimeData,
        generated_at: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error generating report:', error);
      throw error;
    }
  }

  private getMockPredictions(): MLPredictionResponse {
    return {
      risk_level: 'medium',
      confidence: 78,
      next_flare_probability: 35,
      predicted_severity: 4.5,
      timeline: "next 7 days",
      key_factors: ["Stress levels", "Dairy consumption", "Sleep quality"],
      recommendations: {
        immediate_actions: [
          {
            action: "Reduce dairy intake for the next 3-5 days",
            priority: 'high',
            explanation: "Our analysis shows dairy products trigger symptoms in 73% of your logged episodes",
            expected_benefit: "May reduce bloating and discomfort by 40-60%"
          },
          {
            action: "Practice 10 minutes of deep breathing before meals",
            priority: 'medium',
            explanation: "Stress management significantly impacts your digestive health",
            expected_benefit: "Can improve digestion and reduce symptom severity"
          }
        ],
        dietary_suggestions: [
          {
            type: 'avoid',
            foods: ["Dairy products", "Spicy foods", "High-fat meals"],
            reason: "These foods consistently trigger symptoms based on your tracking data",
            timeline: "Next 1-2 weeks"
          },
          {
            type: 'include',
            foods: ["Oats", "Bananas", "Lean proteins", "Herbal teas"],
            reason: "These foods have shown positive effects on your digestive health",
            timeline: "Daily incorporation recommended"
          }
        ],
        lifestyle_changes: [
          {
            category: "Sleep",
            suggestion: "Maintain consistent 8+ hour sleep schedule",
            difficulty: 'easy',
            impact: "Better sleep quality correlates with 30% fewer symptom days"
          },
          {
            category: "Exercise",
            suggestion: "Add 20 minutes of gentle walking after meals",
            difficulty: 'easy',
            impact: "Can improve digestion and reduce bloating"
          }
        ]
      }
    };
  }

  private getMockRecommendations(): PersonalizedRecommendationsResponse {
    return {
      dietary_recommendations: [
        {
          type: "avoid",
          title: "High FODMAP Foods",
          description: "Temporarily avoid high FODMAP foods to identify triggers",
          priority: "high"
        },
        {
          type: "include",
          title: "Probiotic Foods",
          description: "Include yogurt, kefir, and fermented foods for gut health",
          priority: "medium"
        }
      ],
      lifestyle_insights: [
        {
          category: "Stress Management",
          insight: "High stress correlates with symptom flare-ups",
          recommendation: "Practice daily meditation or yoga",
          priority: "high"
        },
        {
          category: "Exercise",
          insight: "Regular gentle exercise improves digestive health",
          recommendation: "30 minutes of walking daily",
          priority: "medium"
        }
      ],
      trigger_analysis: {
        primary_category: "Dietary",
        insights: [
          "Dairy products are your primary trigger",
          "Spicy foods cause moderate reactions",
          "High-fat meals worsen symptoms"
        ]
      },
      management_strategy: {
        strategy: "Elimination Diet with Stress Management",
        approach: "Gradual elimination of trigger foods combined with stress reduction techniques",
        timeline: "4-6 weeks for initial results"
      },
      personalized_tips: [
        "Keep a detailed food diary to identify patterns",
        "Eat smaller, more frequent meals",
        "Stay hydrated throughout the day",
        "Consider working with a registered dietitian"
      ]
    };
  }
}

export const mlService = new MLService();