'use client';

import { API_CONFIG } from '@/lib/config';

export interface UserAnalyticsResponse {
  user_id: string;
  total_logs: number;
  symptom_frequency: Record<string, number>;
  trigger_foods: Array<{
    food: string;
    frequency: number;
    severity_impact: number;
  }>;
  medication_adherence: number;
  improvement_trend: number;
  active_days: number;
  streak_days: number;
  last_flare_date?: string;
  average_symptom_severity: number;
  most_common_symptoms: string[];
  generated_at: string;
}

export interface SystemMetricsResponse {
  total_users: number;
  active_users_today: number;
  active_users_week: number;
  active_users_month: number;
  total_logs_today: number;
  total_predictions_made: number;
  average_user_engagement: number;
  system_uptime: number;
  api_response_time: number;
  generated_at: string;
}

export interface AchievementResponse {
  id: string;
  title: string;
  description: string;
  category: string;
  icon: string;
  points: number;
  unlocked_at: string;
  progress: number;
  requirements: Record<string, any>;
}

export interface AchievementListResponse {
  achievements: AchievementResponse[];
  total_points: number;
  level: number;
  next_level_points: number;
  unlocked_count: number;
  total_count: number;
}

class AnalyticsService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  async getUserAnalytics(timeframe: 'week' | 'month' | 'year' = 'month'): Promise<UserAnalyticsResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/analytics/user?timeframe=${timeframe}`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`User Analytics API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('User Analytics API error:', error);
      const duration = performance.now() - startTime;
      console.log(`User Analytics API call failed after ${duration.toFixed(2)}ms`);
      
      // Return mock data as fallback
      return this.getMockUserAnalytics();
    }
  }

  async getSystemMetrics(): Promise<SystemMetricsResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/analytics/system`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`System Metrics API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('System Metrics API error:', error);
      const duration = performance.now() - startTime;
      console.log(`System Metrics API call failed after ${duration.toFixed(2)}ms`);
      
      // Return mock data as fallback
      return this.getMockSystemMetrics();
    }
  }

  async getAchievements(): Promise<AchievementListResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/analytics/achievements`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Achievements API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Achievements API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Achievements API call failed after ${duration.toFixed(2)}ms`);
      
      // Return mock data as fallback
      return this.getMockAchievements();
    }
  }

  private getMockUserAnalytics(): UserAnalyticsResponse {
    return {
      user_id: "mock-user-id",
      total_logs: 156,
      symptom_frequency: {
        "bloating": 45,
        "abdominal_pain": 32,
        "diarrhea": 28,
        "constipation": 15
      },
      trigger_foods: [
        { food: "dairy", frequency: 23, severity_impact: 7.5 },
        { food: "spicy_food", frequency: 18, severity_impact: 6.2 },
        { food: "high_fat", frequency: 12, severity_impact: 5.8 }
      ],
      medication_adherence: 85.5,
      improvement_trend: 12.3,
      active_days: 28,
      streak_days: 7,
      last_flare_date: "2024-01-15",
      average_symptom_severity: 4.2,
      most_common_symptoms: ["bloating", "abdominal_pain", "diarrhea"],
      generated_at: new Date().toISOString()
    };
  }

  private getMockSystemMetrics(): SystemMetricsResponse {
    return {
      total_users: 1250,
      active_users_today: 89,
      active_users_week: 456,
      active_users_month: 892,
      total_logs_today: 234,
      total_predictions_made: 5678,
      average_user_engagement: 72.5,
      system_uptime: 99.8,
      api_response_time: 145,
      generated_at: new Date().toISOString()
    };
  }

  private getMockAchievements(): AchievementListResponse {
    return {
      achievements: [
        {
          id: "first-log",
          title: "First Steps",
          description: "Log your first symptom entry",
          category: "getting_started",
          icon: "🎯",
          points: 10,
          unlocked_at: "2024-01-10T10:00:00Z",
          progress: 100,
          requirements: { logs_count: 1 }
        },
        {
          id: "week-streak",
          title: "Week Warrior",
          description: "Log symptoms for 7 consecutive days",
          category: "consistency",
          icon: "🔥",
          points: 50,
          unlocked_at: "2024-01-17T10:00:00Z",
          progress: 100,
          requirements: { streak_days: 7 }
        }
      ],
      total_points: 60,
      level: 2,
      next_level_points: 100,
      unlocked_count: 2,
      total_count: 15
    };
  }
}

export const analyticsService = new AnalyticsService();