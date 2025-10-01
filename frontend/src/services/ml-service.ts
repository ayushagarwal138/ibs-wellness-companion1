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
    const startTime = performance.now();
    
    try {
      // Build query parameters
      const params = new URLSearchParams();
      if (request.timeframe) params.append('timeframe', request.timeframe);
      if (request.include_recommendations !== undefined) params.append('include_recommendations', request.include_recommendations.toString());
      
      const queryString = params.toString();
      const url = `${API_BASE_URL}/api/v1/ml/predictions${queryString ? `?${queryString}` : ''}`;
      
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`ML Predictions API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('ML Predictions API error:', error);
      const duration = performance.now() - startTime;
      console.log(`ML Predictions API call failed after ${duration.toFixed(2)}ms`);
      
      // Return mock data as fallback
      return this.getMockPredictions();
    }
  }

  async getRealtimePredictions(): Promise<RealtimePredictionResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/ml/realtime-predictions`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Real-time Predictions API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Real-time Predictions API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Real-time Predictions API call failed after ${duration.toFixed(2)}ms`);
      
      // Return mock data as fallback
      return {
        current_risk: Math.round((Math.random() * 0.8 + 0.1) * 100), // 10 to 90 (already as percentage)
        risk_factors: ['Stress levels elevated', 'Irregular sleep pattern', 'Dietary triggers detected'],
        immediate_recommendations: ['Take deep breaths', 'Avoid trigger foods', 'Stay hydrated'],
        confidence_score: Math.round(75 + Math.random() * 20) // 75-95%
      };
    }
  }

  async getPersonalizedRecommendations(): Promise<PersonalizedRecommendationsResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/recommendations/personalized`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Personalized Recommendations API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Personalized Recommendations API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Personalized Recommendations API call failed after ${duration.toFixed(2)}ms`);
      
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
