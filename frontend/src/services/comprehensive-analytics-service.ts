'use client';

import { API_CONFIG } from '@/lib/config';

export interface TrendData {
  period: string;
  value: number;
  change: number;
}

export interface DietPattern {
  food: string;
  frequency: number;
  avgReaction: number;
}

export interface TriggerAnalysis {
  trigger: string;
  frequency: number;
  impact: number;
}

export interface WeeklyProgress {
  week: string;
  avgSeverity: number;
  goodDays: number;
}

export interface MonthlyInsights {
  bestMonth: string;
  worstMonth: string;
  improvementTrend: number;
  consistencyScore: number;
}

export interface ComprehensiveAnalyticsData {
  symptomTrends: TrendData[];
  dietPatterns: DietPattern[];
  triggerAnalysis: TriggerAnalysis[];
  weeklyProgress: WeeklyProgress[];
  monthlyInsights: MonthlyInsights;
}

class ComprehensiveAnalyticsService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  async getComprehensiveAnalytics(timeframe: 'week' | 'month' | 'year' = 'month'): Promise<ComprehensiveAnalyticsData> {
    try {
      // Fetch data from multiple endpoints in parallel
      const [symptomStats, dietReactions, userAnalytics, patternInsights] = await Promise.all([
        this.fetchSymptomStats(timeframe),
        this.fetchDietReactions(),
        this.fetchUserAnalytics(timeframe),
        this.fetchPatternInsights()
      ]);

      // Transform the data into the required format
      return {
        symptomTrends: this.transformSymptomTrends(symptomStats),
        dietPatterns: this.transformDietPatterns(dietReactions),
        triggerAnalysis: this.transformTriggerAnalysis(userAnalytics, patternInsights),
        weeklyProgress: this.transformWeeklyProgress(symptomStats),
        monthlyInsights: this.transformMonthlyInsights(userAnalytics, symptomStats)
      };
    } catch (error) {
      console.error('Failed to fetch comprehensive analytics:', error);
      throw error;
    }
  }

  private async fetchSymptomStats(timeframe: string): Promise<any> {
    try {
      const days = timeframe === 'week' ? 7 : timeframe === 'month' ? 30 : 365;
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/symptom-logs/stats/summary?days=${days}`, {
        headers: this.getAuthHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch symptom stats:', error);
      return null;
    }
  }

  private async fetchDietReactions(): Promise<any> {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/diet/reactions?size=100`, {
        headers: this.getAuthHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch diet reactions:', error);
      return { data: [] };
    }
  }

  private async fetchUserAnalytics(timeframe: string): Promise<any> {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/analytics/user-analytics?timeframe=${timeframe}`, {
        headers: this.getAuthHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch user analytics:', error);
      return null;
    }
  }

  private async fetchPatternInsights(): Promise<any> {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/analytics/pattern-insights`, {
        headers: this.getAuthHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch pattern insights:', error);
      return null;
    }
  }

  private transformSymptomTrends(symptomStats: any): TrendData[] {
    console.log('🔍 transformSymptomTrends called with:', symptomStats);
    
    if (!symptomStats?.weekly_trends) {
      console.log('❌ No weekly_trends found in symptomStats');
      return [];
    }

    console.log('📊 weekly_trends data:', symptomStats.weekly_trends);
    console.log('📊 weekly_trends type:', typeof symptomStats.weekly_trends);

    // Handle both object and array formats
    if (Array.isArray(symptomStats.weekly_trends)) {
      console.log('📈 Processing weekly_trends as array');
      return symptomStats.weekly_trends.map((trend: any, index: number) => ({
        period: `Week ${index + 1}`,
        value: trend?.average_severity || 0,
        change: index > 0 && symptomStats.weekly_trends[index - 1] ? 
          ((trend?.average_severity || 0) - (symptomStats.weekly_trends[index - 1]?.average_severity || 0)) : 0
      }));
    } else if (typeof symptomStats.weekly_trends === 'object' && symptomStats.weekly_trends !== null) {
      console.log('📈 Processing weekly_trends as object');
      const weeks = Object.keys(symptomStats.weekly_trends).sort();
      console.log('📅 Sorted weeks:', weeks);
      
      const trends = weeks.map((week, index) => {
        const weeklyTrends = symptomStats.weekly_trends;
        const weekData = weeklyTrends && weeklyTrends[week] ? weeklyTrends[week] : null;
        const prevWeek = index > 0 ? weeks[index - 1] : null;
        const prevWeekData = prevWeek && weeklyTrends && weeklyTrends[prevWeek] ? weeklyTrends[prevWeek] : null;
        
        const trend = {
          period: `Week ${index + 1}`,
          value: weekData?.average_severity || 0,
          change: prevWeekData ? 
            ((weekData?.average_severity || 0) - (prevWeekData?.average_severity || 0)) : 0
        };
        
        console.log(`📊 Week ${index + 1} trend:`, trend);
        return trend;
      });
      
      console.log('✅ Final trends array:', trends);
      return trends;
    }

    console.log('❌ weekly_trends format not recognized');
    return [];
  }

  private transformDietPatterns(dietReactions: any): DietPattern[] {
    if (!dietReactions?.data) {
      return [];
    }

    // Group reactions by food and calculate frequency and average reaction
    const foodGroups: { [key: string]: { count: number; totalSeverity: number } } = {};
    
    dietReactions.data.forEach((reaction: any) => {
      const food = reaction?.food_item || reaction?.food;
      const severity = reaction?.severity_score || reaction?.severity || 0;
      
      if (food && !foodGroups[food]) {
        foodGroups[food] = { count: 0, totalSeverity: 0 };
      }
      
      if (food && foodGroups[food]) {
        const foodGroup = foodGroups[food];
        if (foodGroup) {
          foodGroup.count++;
          foodGroup.totalSeverity += severity;
        }
      }
    });

    return Object.entries(foodGroups)
      .map(([food, data]) => ({
        food,
        frequency: data.count,
        avgReaction: data.count > 0 ? data.totalSeverity / data.count : 0
      }))
      .sort((a, b) => b.frequency - a.frequency)
      .slice(0, 10); // Top 10 foods
  }

  private transformTriggerAnalysis(userAnalytics: any, patternInsights: any): TriggerAnalysis[] {
    const triggers: TriggerAnalysis[] = [];

    // Add triggers from user analytics
    if (userAnalytics?.trigger_foods) {
      userAnalytics.trigger_foods.forEach((trigger: any) => {
        triggers.push({
          trigger: trigger.food || trigger.trigger,
          frequency: trigger.frequency || 0,
          impact: trigger.severity_impact || 0
        });
      });
    }

    // Add triggers from pattern insights
    if (patternInsights?.common_triggers) {
      patternInsights.common_triggers.forEach((trigger: any) => {
        const existingTrigger = triggers.find(t => t.trigger === trigger.name);
        if (!existingTrigger) {
          triggers.push({
            trigger: trigger.name || trigger.trigger,
            frequency: trigger.frequency || 0,
            impact: trigger.impact_score || 0
          });
        }
      });
    }

    return triggers.slice(0, 8); // Top 8 triggers
  }

  private transformWeeklyProgress(symptomStats: any): WeeklyProgress[] {
    if (!symptomStats?.weekly_progress || !Array.isArray(symptomStats.weekly_progress)) {
      return [];
    }

    return symptomStats.weekly_progress.map((week: any) => {
      const avgSeverity = week.avg_severity;
      const goodDays = week.good_days_count;
      
      return {
        week: week.week_label || `Week ${week.week_number}`,
        avgSeverity: (typeof avgSeverity === 'number' && !isNaN(avgSeverity) && isFinite(avgSeverity)) ? avgSeverity : 0,
        goodDays: (typeof goodDays === 'number' && !isNaN(goodDays) && isFinite(goodDays)) ? goodDays : 0
      };
    });
  }

  private transformMonthlyInsights(userAnalytics: any, symptomStats: any): MonthlyInsights {
    // Validate and sanitize numeric values
    const improvementTrend = userAnalytics?.improvement_trend;
    const consistencyScore = symptomStats?.consistency_score;
    
    return {
      bestMonth: userAnalytics?.best_month || 'N/A',
      worstMonth: userAnalytics?.worst_month || 'N/A',
      improvementTrend: (typeof improvementTrend === 'number' && !isNaN(improvementTrend) && isFinite(improvementTrend)) ? improvementTrend : 0,
      consistencyScore: (typeof consistencyScore === 'number' && !isNaN(consistencyScore) && isFinite(consistencyScore)) ? consistencyScore : 50
    };
  }
}

export const comprehensiveAnalyticsService = new ComprehensiveAnalyticsService();