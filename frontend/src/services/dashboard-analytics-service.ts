'use client';

import { API_CONFIG } from '@/lib/config';

export interface DashboardAnalytics {
  totalSymptomLogs: number;
  mealsLogged: number;
  foodReactions: number;
  avgWellnessScore: number;
  symptomLogsChange: string;
  mealsLoggedChange: string;
  foodReactionsChange: string;
  wellnessScoreChange: string;
  recentActivity: Array<{
    type: string;
    description: string;
    timeAgo: string;
    color: string;
  }>;
}

class DashboardAnalyticsService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.warn('No access token found in localStorage');
    }
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  async getDashboardAnalytics(): Promise<DashboardAnalytics> {
    try {
      // Fetch data from multiple endpoints
      const [symptomLogs, dietLogs, foodReactions] = await Promise.all([
        this.fetchSymptomLogs(),
        this.fetchDietLogs(),
        this.fetchFoodReactions()
      ]);

      // Calculate analytics from the fetched data
      const analytics = this.calculateAnalytics(symptomLogs, dietLogs, foodReactions);
      
      return analytics;
    } catch (error) {
      console.error('Failed to fetch dashboard analytics:', error);
      // Return fallback analytics
      return this.getFallbackAnalytics();
    }
  }

  private async fetchSymptomLogs(): Promise<any[]> {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/symptom-logs/?days=30`, {
        headers: this.getAuthHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.data || [];
    } catch (error) {
      console.error('Failed to fetch symptom logs:', error);
      return [];
    }
  }

  private async fetchDietLogs(): Promise<any[]> {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/diet/logs?size=100`, {
        headers: this.getAuthHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.items || [];
    } catch (error) {
      console.error('Failed to fetch diet logs:', error);
      return [];
    }
  }

  private async fetchFoodReactions(): Promise<any[]> {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/diet/reactions?size=100`, {
        headers: this.getAuthHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.items || [];
    } catch (error) {
      console.error('Failed to fetch food reactions:', error);
      return [];
    }
  }

  private calculateAnalytics(symptomLogs: any[], dietLogs: any[], foodReactions: any[]): DashboardAnalytics {
    const now = new Date();
    const lastMonth = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    const previousMonth = new Date(now.getTime() - 60 * 24 * 60 * 60 * 1000);

    // Filter data for current and previous periods
    const currentSymptomLogs = symptomLogs.filter(log => new Date(log.created_at) >= lastMonth);
    const previousSymptomLogs = symptomLogs.filter(log => {
      const date = new Date(log.created_at);
      return date >= previousMonth && date < lastMonth;
    });

    const currentDietLogs = dietLogs.filter(log => new Date(log.consumed_at) >= lastMonth);
    const previousDietLogs = dietLogs.filter(log => {
      const date = new Date(log.consumed_at);
      return date >= previousMonth && date < lastMonth;
    });

    const currentFoodReactions = foodReactions.filter(log => new Date(log.created_at) >= lastMonth);
    const previousFoodReactions = foodReactions.filter(log => {
      const date = new Date(log.created_at);
      return date >= previousMonth && date < lastMonth;
    });

    // Calculate totals
    const totalSymptomLogs = currentSymptomLogs.length;
    const mealsLogged = currentDietLogs.length;
    const totalFoodReactions = currentFoodReactions.length;

    // Calculate wellness score (average of inverse symptom severity)
    const avgWellnessScore = currentSymptomLogs.length > 0 
      ? (10 - currentSymptomLogs.reduce((sum, log) => sum + this.severityToNumber(log.severity), 0) / currentSymptomLogs.length)
      : 8.0;

    // Calculate percentage changes
    const symptomLogsChange = this.calculatePercentageChange(totalSymptomLogs, previousSymptomLogs.length);
    const mealsLoggedChange = this.calculatePercentageChange(mealsLogged, previousDietLogs.length);
    const foodReactionsChange = this.calculatePercentageChange(totalFoodReactions, previousFoodReactions.length);
    const wellnessScoreChange = this.calculateWellnessScoreChange(currentSymptomLogs, previousSymptomLogs);

    // Generate recent activity
    const recentActivity = this.generateRecentActivity(symptomLogs, dietLogs, foodReactions);

    return {
      totalSymptomLogs,
      mealsLogged,
      foodReactions: totalFoodReactions,
      avgWellnessScore: Math.round(avgWellnessScore * 10) / 10,
      symptomLogsChange,
      mealsLoggedChange,
      foodReactionsChange,
      wellnessScoreChange,
      recentActivity
    };
  }

  private calculatePercentageChange(current: number, previous: number): string {
    if (previous === 0) {
      return current > 0 ? '+100%' : '+0%';
    }
    
    const change = ((current - previous) / previous) * 100;
    const sign = change >= 0 ? '+' : '';
    return `${sign}${Math.round(change)}%`;
  }

  private severityToNumber(severity: string): number {
    // Convert severity string to numeric value (1-5 scale)
    switch (severity?.toLowerCase()) {
      case 'none':
        return 0;
      case 'mild':
        return 1;
      case 'moderate':
        return 2;
      case 'severe':
        return 3;
      case 'very_severe':
        return 4;
      default:
        return 0; // Default to none if unknown
    }
  }

  private calculateWellnessScoreChange(currentLogs: any[], previousLogs: any[]): string {
    const currentAvg = currentLogs.length > 0 
      ? (10 - currentLogs.reduce((sum, log) => sum + this.severityToNumber(log.severity), 0) / currentLogs.length)
      : 8.0;
    
    const previousAvg = previousLogs.length > 0 
      ? (10 - previousLogs.reduce((sum, log) => sum + this.severityToNumber(log.severity), 0) / previousLogs.length)
      : 8.0;
    
    const change = currentAvg - previousAvg;
    const sign = change >= 0 ? '+' : '';
    return `${sign}${Math.round(change * 10) / 10}`;
  }

  private generateRecentActivity(symptomLogs: any[], dietLogs: any[], foodReactions: any[]): Array<{
    type: string;
    description: string;
    timeAgo: string;
    color: string;
  }> {
    const activities: Array<{
      type: string;
      description: string;
      timeAgo: string;
      color: string;
      timestamp: Date;
    }> = [];

    // Add recent symptom logs
    symptomLogs.slice(-5).forEach(log => {
      activities.push({
        type: 'symptom',
        description: `Logged ${log.severity ? `severity ${log.severity}` : 'mild'} symptoms`,
        timeAgo: this.getTimeAgo(new Date(log.created_at)),
        color: 'yellow',
        timestamp: new Date(log.created_at)
      });
    });

    // Add recent diet logs
    dietLogs.slice(-5).forEach(log => {
      activities.push({
        type: 'diet',
        description: `Logged ${log.meal_type || 'meal'}`,
        timeAgo: this.getTimeAgo(new Date(log.consumed_at)),
        color: 'blue',
        timestamp: new Date(log.consumed_at)
      });
    });

    // Add recent food reactions
    foodReactions.slice(-3).forEach(reaction => {
      activities.push({
        type: 'reaction',
        description: `Food reaction to ${reaction.food_name}`,
        timeAgo: this.getTimeAgo(new Date(reaction.created_at)),
        color: 'red',
        timestamp: new Date(reaction.created_at)
      });
    });

    // Sort by timestamp and return top 5
    return activities
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, 5)
      .map(({ timestamp, ...activity }) => activity);
  }

  private getTimeAgo(date: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) {
      return 'Just now';
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString();
    }
  }

  private getFallbackAnalytics(): DashboardAnalytics {
    return {
      totalSymptomLogs: 0,
      mealsLogged: 0,
      foodReactions: 0,
      avgWellnessScore: 8.0,
      symptomLogsChange: '+0%',
      mealsLoggedChange: '+0%',
      foodReactionsChange: '+0%',
      wellnessScoreChange: '+0.0',
      recentActivity: [
        {
          type: 'info',
          description: 'Start logging symptoms and meals to see analytics',
          timeAgo: 'Now',
          color: 'gray'
        }
      ]
    };
  }
}

export const dashboardAnalyticsService = new DashboardAnalyticsService();