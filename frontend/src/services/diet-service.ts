'use client';

import { API_CONFIG } from '@/lib/config';

export interface DietStats {
  total_meals_logged: number;
  meals_by_type: { [key: string]: number };
  average_daily_calories?: number;
  mood_correlation: { [key: string]: number };
  most_consumed_foods: string[];
}

export interface FoodStats {
  total_reactions: number;
  most_problematic_foods: string[];
  reaction_severity_distribution: { [key: string]: number };
  reaction_types_distribution: { [key: string]: number };
  safe_foods: string[];
  trigger_foods: string[];
}

export interface NutritionalAnalysis {
  analysis_period_days: number;
  average_daily_calories: number;
  nutritional_breakdown: { [key: string]: number };
  deficiency_warnings: string[];
  dietary_recommendations: string[];
  ibs_specific_insights: string[];
}

class DietService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
  }

  private async makeRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
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

  /**
   * Get diet statistics for the current user
   */
  async getDietStats(days: number = 30): Promise<DietStats> {
    try {
      const data = await this.makeRequest(`/api/v1/diet/stats/diet?days=${days}`);
      return data;
    } catch (error) {
      console.error('Error fetching diet stats:', error);
      throw error;
    }
  }

  /**
   * Get food statistics including reactions and trigger foods
   */
  async getFoodStats(days: number = 30): Promise<FoodStats> {
    try {
      const data = await this.makeRequest(`/api/v1/diet/stats/food?days=${days}`);
      return data;
    } catch (error) {
      console.error('Error fetching food stats:', error);
      throw error;
    }
  }

  /**
   * Get nutritional analysis for the current user
   */
  async getNutritionalAnalysis(days: number = 30): Promise<NutritionalAnalysis> {
    try {
      const data = await this.makeRequest(`/api/v1/diet/analysis/nutritional?days=${days}`);
      return data;
    } catch (error) {
      console.error('Error fetching nutritional analysis:', error);
      throw error;
    }
  }

  /**
   * Get daily nutrition summary for a specific date
   */
  async getDailyNutritionSummary(date: string): Promise<any> {
    try {
      const data = await this.makeRequest(`/api/v1/diet/nutrition/daily/${date}`);
      return data;
    } catch (error) {
      console.error('Error fetching daily nutrition summary:', error);
      throw error;
    }
  }

  /**
   * Get nutrition trends over a period
   */
  async getNutritionTrends(days: number = 30): Promise<any> {
    try {
      const data = await this.makeRequest(`/api/v1/diet/nutrition/trends?days=${days}`);
      return data;
    } catch (error) {
      console.error('Error fetching nutrition trends:', error);
      throw error;
    }
  }

  /**
   * Calculate nutrition for a list of food items
   */
  async calculateMealNutrition(foodItems: string[], portionSize?: string): Promise<any> {
    try {
      const requestBody: any = { food_items: foodItems };
      if (portionSize) {
        requestBody.portion_size = portionSize;
      }

      const data = await this.makeRequest('/api/v1/diet/nutrition/calculate', {
        method: 'POST',
        body: JSON.stringify(requestBody),
      });
      return data;
    } catch (error) {
      console.error('Error calculating meal nutrition:', error);
      throw error;
    }
  }

  /**
   * Get nutrition data for a specific food
   */
  async getFoodNutritionData(foodName: string, portionSize: string = '100g'): Promise<any> {
    try {
      const data = await this.makeRequest(
        `/api/v1/diet/nutrition/food/${encodeURIComponent(foodName)}?portion_size=${encodeURIComponent(portionSize)}`
      );
      return data;
    } catch (error) {
      console.error('Error fetching food nutrition data:', error);
      throw error;
    }
  }

  /**
   * Get food suggestions for autocomplete
   */
  async getFoodSuggestions(query: string = '', limit: number = 10): Promise<any> {
    try {
      const data = await this.makeRequest(
        `/api/v1/diet/food-suggestions?query=${encodeURIComponent(query)}&limit=${limit}`
      );
      return data;
    } catch (error) {
      console.error('Error fetching food suggestions:', error);
      throw error;
    }
  }
}

export const dietService = new DietService();
export default dietService;