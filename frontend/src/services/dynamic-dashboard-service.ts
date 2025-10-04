'use client';

import { API_CONFIG } from '@/lib/config';

export interface DynamicDashboardData {
  aiPredictions: {
    riskLevel: 'low' | 'medium' | 'high';
    nextFlareRisk: number;
    confidence: number;
    triggerFoods: string[];
    recommendations: string[];
    keyFactors: string[];
    timeline: string;
    modelVersion: string;
  };
  recentSymptoms: {
    date: string;
    severity: number;
    symptoms: string[];
    notes?: string;
  }[];
  weeklyStats: {
    avgSeverity: number;
    symptomFreeDays: number;
    totalLogs: number;
    adherenceRate: number;
    improvementTrend: number;
  };
  insights: {
    type: 'positive' | 'warning' | 'info';
    title: string;
    description: string;
    action?: string;
    priority: 'high' | 'medium' | 'low';
  }[];
  upcomingReminders: {
    type: 'medication' | 'appointment' | 'log';
    title: string;
    time: string;
    priority: 'high' | 'medium' | 'low';
    description?: string;
  }[];
  personalizedRecommendations: {
    dietary: Array<{
      category: string;
      recommendation: string;
      reasoning: string;
      priority: number;
    }>;
    lifestyle: Array<{
      category: string;
      recommendation: string;
      reasoning: string;
      priority: number;
    }>;
    medical: Array<{
      category: string;
      recommendation: string;
      reasoning: string;
      priority: number;
    }>;
  };
}

class DynamicDashboardService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  private async fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getAuthHeaders(),
        ...options.headers,
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response;
  }

  async getMLPredictions(): Promise<DynamicDashboardData['aiPredictions']> {
    try {
      // Get enhanced predictions and trigger analysis in parallel
      const [predictionsResponse, triggerAnalysisResponse] = await Promise.all([
        this.fetchWithAuth(`${API_CONFIG.BASE_URL}/api/v1/ml/predictions`),
        this.fetchWithAuth(`${API_CONFIG.BASE_URL}/api/v1/diet/analysis/triggers?days=90`)
      ]);

      const predictionsData = await predictionsResponse.json();
      const triggerData = await triggerAnalysisResponse.json();

      // Validate required fields from ML model response
      if (!predictionsData || typeof predictionsData !== 'object') {
        throw new Error('Invalid ML prediction response format');
      }

      // Extract trigger foods from enhanced analysis
      const enhancedTriggerFoods = triggerData.trigger_foods?.map((trigger: any) => 
        `${trigger.food_name} (${trigger.risk_score}% risk)`
      ) || [];

      // Fallback to basic trigger foods if enhanced analysis fails
      const triggerFoods = enhancedTriggerFoods.length > 0 
        ? enhancedTriggerFoods 
        : this.validateStringArray(predictionsData.trigger_foods);

      // Ensure all required fields are present and valid
      const predictions = {
        riskLevel: this.validateRiskLevel(predictionsData.risk_level),
        nextFlareRisk: this.validatePercentage(predictionsData.next_flare_probability),
        confidence: this.validateConfidence(predictionsData.confidence),
        triggerFoods: triggerFoods,
        recommendations: this.validateStringArray(predictionsData.recommendations),
        keyFactors: this.validateStringArray(predictionsData.key_factors),
        timeline: this.validateTimeline(predictionsData.timeline),
        modelVersion: this.validateModelVersion(predictionsData.model_version),
      };

      console.log('Enhanced ML predictions with trigger analysis retrieved successfully:', predictions);
      return predictions;
    } catch (error) {
      console.error('Failed to fetch ML predictions:', error);
      throw new Error(`ML prediction service unavailable: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private validateRiskLevel(value: any): 'low' | 'medium' | 'high' {
    const validLevels = ['low', 'medium', 'high'];
    const level = typeof value === 'string' ? value.toLowerCase() : '';
    if (!validLevels.includes(level)) {
      throw new Error(`Invalid risk level: ${value}. Must be one of: ${validLevels.join(', ')}`);
    }
    return level as 'low' | 'medium' | 'high';
  }

  private validatePercentage(value: any): number {
    const num = typeof value === 'number' ? value : parseFloat(value);
    if (isNaN(num) || num < 0 || num > 1) {
      throw new Error(`Invalid percentage value: ${value}. Must be between 0 and 1`);
    }
    return Math.round(num * 100);
  }

  private validateConfidence(value: any): number {
    const num = typeof value === 'number' ? value : parseFloat(value);
    if (isNaN(num) || num < 0 || num > 1) {
      throw new Error(`Invalid confidence value: ${value}. Must be between 0 and 1`);
    }
    return num;
  }

  private validateStringArray(value: any): string[] {
    if (!Array.isArray(value)) {
      throw new Error(`Expected array, got ${typeof value}`);
    }
    return value.filter(item => typeof item === 'string' && item.trim().length > 0);
  }

  private validateTimeline(value: any): string {
    if (typeof value !== 'string' || value.trim().length === 0) {
      throw new Error(`Invalid timeline value: ${value}. Must be a non-empty string`);
    }
    return value.trim();
  }

  private validateModelVersion(value: any): string {
    if (typeof value !== 'string' || value.trim().length === 0) {
      throw new Error(`Invalid model version: ${value}. Must be a non-empty string`);
    }
    return value.trim();
  }

  private validateAdherenceRate(value: any): number {
    const num = typeof value === 'number' ? value : parseFloat(value);
    if (isNaN(num) || num < 0 || num > 100) {
      throw new Error(`Invalid adherence rate: ${value}. Must be between 0 and 100`);
    }
    return Math.round(num);
  }

  private validateImprovementTrend(value: any): number {
    const num = typeof value === 'number' ? value : parseFloat(value);
    if (isNaN(num)) {
      throw new Error(`Invalid improvement trend: ${value}. Must be a valid number`);
    }
    return Math.round(num * 10) / 10; // Round to 1 decimal place
  }

  private validateInsightType(value: any): 'positive' | 'warning' | 'info' {
    const validTypes = ['positive', 'warning', 'info'];
    if (!validTypes.includes(value)) {
      throw new Error(`Invalid insight type: ${value}. Must be one of: ${validTypes.join(', ')}`);
    }
    return value as 'positive' | 'warning' | 'info';
  }

  private validateInsightTitle(value: any): string {
    if (typeof value !== 'string' || value.trim().length === 0) {
      throw new Error(`Invalid insight title: ${value}. Must be a non-empty string`);
    }
    return value.trim();
  }

  private validateInsightDescription(value: any): string {
    if (typeof value !== 'string' || value.trim().length === 0) {
      throw new Error(`Invalid insight description: ${value}. Must be a non-empty string`);
    }
    return value.trim();
  }

  private validatePriority(value: any): 'high' | 'medium' | 'low' {
    const validPriorities = ['high', 'medium', 'low'];
    if (!validPriorities.includes(value)) {
      throw new Error(`Invalid priority: ${value}. Must be one of: ${validPriorities.join(', ')}`);
    }
    return value as 'high' | 'medium' | 'low';
  }

  private validateReminderType(value: any): 'medication' | 'appointment' | 'log' {
    const validTypes = ['medication', 'appointment', 'log'];
    if (!validTypes.includes(value)) {
      throw new Error(`Invalid reminder type: ${value}. Must be one of: ${validTypes.join(', ')}`);
    }
    return value as 'medication' | 'appointment' | 'log';
  }

  private validateReminderTitle(value: any): string {
    if (typeof value !== 'string' || value.trim().length === 0) {
      throw new Error(`Invalid reminder title: ${value}. Must be a non-empty string`);
    }
    return value.trim();
  }

  private validateReminderTime(value: any): string {
    if (typeof value !== 'string' || value.trim().length === 0) {
      throw new Error(`Invalid reminder time: ${value}. Must be a non-empty string`);
    }
    return value.trim();
  }

  private validateRecommendationArray(value: any, type: string): Array<{
    category: string;
    recommendation: string;
    reasoning: string;
    priority: number;
  }> {
    if (!Array.isArray(value)) {
      throw new Error(`Invalid ${type} recommendations: Expected array, got ${typeof value}`);
    }

    return value.map((rec: any, index: number) => {
      if (!rec || typeof rec !== 'object') {
        throw new Error(`Invalid ${type} recommendation at index ${index}: Expected object`);
      }

      if (typeof rec.category !== 'string' || rec.category.trim().length === 0) {
        throw new Error(`Invalid ${type} recommendation category at index ${index}: Must be a non-empty string`);
      }

      if (typeof rec.recommendation !== 'string' || rec.recommendation.trim().length === 0) {
        throw new Error(`Invalid ${type} recommendation text at index ${index}: Must be a non-empty string`);
      }

      if (typeof rec.reasoning !== 'string' || rec.reasoning.trim().length === 0) {
        throw new Error(`Invalid ${type} recommendation reasoning at index ${index}: Must be a non-empty string`);
      }

      const priority = typeof rec.priority === 'number' ? rec.priority : parseFloat(rec.priority);
      if (isNaN(priority) || priority < 1 || priority > 10) {
        throw new Error(`Invalid ${type} recommendation priority at index ${index}: Must be between 1 and 10`);
      }

      return {
        category: rec.category.trim(),
        recommendation: rec.recommendation.trim(),
        reasoning: rec.reasoning.trim(),
        priority: Math.round(priority),
      };
    });
  }

  async getRecentSymptoms(): Promise<DynamicDashboardData['recentSymptoms']> {
    try {
      const response = await this.fetchWithAuth(`${API_CONFIG.BASE_URL}/api/v1/symptom-logs?limit=10`);
      const data = await response.json();

      return (data.items || []).map((log: any) => ({
        date: new Date(log.logged_at).toLocaleDateString(),
        severity: log.severity || 0,
        symptoms: log.symptoms || [],
        notes: log.notes,
      }));
    } catch (error) {
      console.error('Failed to fetch recent symptoms:', error);
      return [];
    }
  }

  async getWeeklyStats(): Promise<DynamicDashboardData['weeklyStats']> {
    try {
      const [symptomsResponse, analyticsResponse] = await Promise.all([
        this.fetchWithAuth(`${API_CONFIG.BASE_URL}/api/v1/symptom-logs?days=7`),
        this.fetchWithAuth(`${API_CONFIG.BASE_URL}/api/v1/analytics/weekly-summary`),
      ]);

      const symptomsData = await symptomsResponse.json();
      const analyticsData = await analyticsResponse.json();

      const symptoms = symptomsData.items || [];
      const totalDays = 7;
      const symptomFreeDays = totalDays - new Set(symptoms.map((s: any) => 
        new Date(s.logged_at).toDateString()
      )).size;

      const avgSeverity = symptoms.length > 0 
        ? symptoms.reduce((sum: number, s: any) => sum + (s.severity || 0), 0) / symptoms.length
        : 0;

      // Validate analytics data
      if (!analyticsData || typeof analyticsData !== 'object') {
        throw new Error('Invalid analytics response format');
      }

      const stats = {
        avgSeverity: Math.round(avgSeverity * 10) / 10,
        symptomFreeDays,
        totalLogs: symptoms.length,
        adherenceRate: this.validateAdherenceRate(analyticsData.adherence_rate),
        improvementTrend: this.validateImprovementTrend(analyticsData.improvement_trend),
      };

      console.log('Weekly stats retrieved successfully:', stats);
      return stats;
    } catch (error) {
      console.error('Failed to fetch weekly stats:', error);
      throw new Error(`Weekly statistics service unavailable: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async getPersonalizedInsights(): Promise<DynamicDashboardData['insights']> {
    try {
      const response = await this.fetchWithAuth(`${API_CONFIG.BASE_URL}/api/v1/analytics/insights`);
      const data = await response.json();

      if (!data || !Array.isArray(data.insights)) {
        throw new Error('Invalid insights response format');
      }

      const insights = data.insights.map((insight: any) => {
        if (!insight || typeof insight !== 'object') {
          throw new Error('Invalid insight object format');
        }

        return {
          type: this.validateInsightType(insight.type),
          title: this.validateInsightTitle(insight.title),
          description: this.validateInsightDescription(insight.description),
          action: insight.action || undefined,
          priority: this.validatePriority(insight.priority),
        };
      });

      console.log('Personalized insights retrieved successfully:', insights);
      return insights;
    } catch (error) {
      console.error('Failed to fetch insights:', error);
      throw new Error(`Insights service unavailable: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async getUpcomingReminders(): Promise<DynamicDashboardData['upcomingReminders']> {
    try {
      const response = await this.fetchWithAuth(`${API_CONFIG.BASE_URL}/api/v1/reminders/upcoming`);
      const data = await response.json();

      if (!data || !Array.isArray(data.reminders)) {
        throw new Error('Invalid reminders response format');
      }

      const reminders = data.reminders.map((reminder: any) => {
        if (!reminder || typeof reminder !== 'object') {
          throw new Error('Invalid reminder object format');
        }

        return {
          type: this.validateReminderType(reminder.type),
          title: this.validateReminderTitle(reminder.title),
          time: this.validateReminderTime(reminder.scheduled_time),
          priority: this.validatePriority(reminder.priority),
          description: reminder.description || undefined,
        };
      });

      console.log('Upcoming reminders retrieved successfully:', reminders);
      return reminders;
    } catch (error) {
      console.error('Failed to fetch reminders:', error);
      throw new Error(`Reminders service unavailable: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async getPersonalizedRecommendations(): Promise<DynamicDashboardData['personalizedRecommendations']> {
    try {
      const response = await this.fetchWithAuth(`${API_CONFIG.BASE_URL}/api/v1/recommendations/personalized`);
      const data = await response.json();

      if (!data || typeof data !== 'object') {
        throw new Error('Invalid recommendations response format');
      }

      const recommendations = {
        dietary: this.validateRecommendationArray(data.dietary_recommendations, 'dietary'),
        lifestyle: this.validateRecommendationArray(data.lifestyle_recommendations, 'lifestyle'),
        medical: this.validateRecommendationArray(data.medical_recommendations, 'medical'),
      };

      console.log('Personalized recommendations retrieved successfully:', recommendations);
      return recommendations;
    } catch (error) {
      console.error('Failed to fetch personalized recommendations:', error);
      throw new Error(`Recommendations service unavailable: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async getDashboardData(): Promise<DynamicDashboardData> {
    try {
      const [
        aiPredictions,
        recentSymptoms,
        weeklyStats,
        insights,
        upcomingReminders,
        personalizedRecommendations,
      ] = await Promise.all([
        this.getMLPredictions(),
        this.getRecentSymptoms(),
        this.getWeeklyStats(),
        this.getPersonalizedInsights(),
        this.getUpcomingReminders(),
        this.getPersonalizedRecommendations(),
      ]);

      return {
        aiPredictions,
        recentSymptoms,
        weeklyStats,
        insights,
        upcomingReminders,
        personalizedRecommendations,
      };
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      throw error;
    }
  }

  // Real-time updates
  async refreshPredictions(): Promise<DynamicDashboardData['aiPredictions']> {
    try {
      const response = await this.fetchWithAuth(`${API_CONFIG.BASE_URL}/api/v1/ml/realtime-predictions`);
      const data = await response.json();

      // Validate required fields from ML model response
      if (!data || typeof data !== 'object') {
        throw new Error('Invalid realtime prediction response format');
      }

      // Ensure all required fields are present and valid
      const predictions = {
        riskLevel: this.validateRiskLevel(data.risk_level),
        nextFlareRisk: this.validatePercentage(data.next_flare_probability),
        confidence: this.validateConfidence(data.confidence),
        triggerFoods: this.validateStringArray(data.trigger_foods),
        recommendations: this.validateStringArray(data.recommendations),
        keyFactors: this.validateStringArray(data.key_factors),
        timeline: this.validateTimeline(data.timeline),
        modelVersion: this.validateModelVersion(data.model_version),
      };

      console.log('Realtime predictions refreshed successfully:', predictions);
      return predictions;
    } catch (error) {
      console.error('Failed to refresh predictions:', error);
      throw new Error(`Realtime prediction service unavailable: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  // Configuration-driven thresholds
  async getConfigurableThresholds(): Promise<{
    riskThresholds: { low: number; medium: number; high: number };
    severityLevels: { mild: number; moderate: number; severe: number };
    adherenceTargets: { minimum: number; good: number; excellent: number };
  }> {
    try {
      const response = await this.fetchWithAuth(`${API_CONFIG.BASE_URL}/api/v1/config/dashboard-thresholds`);
      const data = await response.json();

      if (!data || typeof data !== 'object') {
        throw new Error('Invalid thresholds configuration response format');
      }

      const thresholds = {
        riskThresholds: this.validateRiskThresholds(data.risk_thresholds),
        severityLevels: this.validateSeverityLevels(data.severity_levels),
        adherenceTargets: this.validateAdherenceTargets(data.adherence_targets),
      };

      console.log('Configurable thresholds retrieved successfully:', thresholds);
      return thresholds;
    } catch (error) {
      console.error('Failed to fetch configurable thresholds:', error);
      throw new Error(`Configuration service unavailable: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private validateRiskThresholds(value: any): { low: number; medium: number; high: number } {
    if (!value || typeof value !== 'object') {
      throw new Error('Invalid risk thresholds: Expected object');
    }

    const { low, medium, high } = value;
    const lowNum = typeof low === 'number' ? low : parseFloat(low);
    const mediumNum = typeof medium === 'number' ? medium : parseFloat(medium);
    const highNum = typeof high === 'number' ? high : parseFloat(high);

    if (isNaN(lowNum) || isNaN(mediumNum) || isNaN(highNum)) {
      throw new Error('Invalid risk thresholds: All values must be valid numbers');
    }

    if (lowNum < 0 || lowNum > 1 || mediumNum < 0 || mediumNum > 1 || highNum < 0 || highNum > 1) {
      throw new Error('Invalid risk thresholds: All values must be between 0 and 1');
    }

    if (lowNum >= mediumNum || mediumNum >= highNum) {
      throw new Error('Invalid risk thresholds: Values must be in ascending order (low < medium < high)');
    }

    return { low: lowNum, medium: mediumNum, high: highNum };
  }

  private validateSeverityLevels(value: any): { mild: number; moderate: number; severe: number } {
    if (!value || typeof value !== 'object') {
      throw new Error('Invalid severity levels: Expected object');
    }

    const { mild, moderate, severe } = value;
    const mildNum = typeof mild === 'number' ? mild : parseFloat(mild);
    const moderateNum = typeof moderate === 'number' ? moderate : parseFloat(moderate);
    const severeNum = typeof severe === 'number' ? severe : parseFloat(severe);

    if (isNaN(mildNum) || isNaN(moderateNum) || isNaN(severeNum)) {
      throw new Error('Invalid severity levels: All values must be valid numbers');
    }

    if (mildNum < 1 || mildNum > 10 || moderateNum < 1 || moderateNum > 10 || severeNum < 1 || severeNum > 10) {
      throw new Error('Invalid severity levels: All values must be between 1 and 10');
    }

    if (mildNum >= moderateNum || moderateNum >= severeNum) {
      throw new Error('Invalid severity levels: Values must be in ascending order (mild < moderate < severe)');
    }

    return { mild: mildNum, moderate: moderateNum, severe: severeNum };
  }

  private validateAdherenceTargets(value: any): { minimum: number; good: number; excellent: number } {
    if (!value || typeof value !== 'object') {
      throw new Error('Invalid adherence targets: Expected object');
    }

    const { minimum, good, excellent } = value;
    const minimumNum = typeof minimum === 'number' ? minimum : parseFloat(minimum);
    const goodNum = typeof good === 'number' ? good : parseFloat(good);
    const excellentNum = typeof excellent === 'number' ? excellent : parseFloat(excellent);

    if (isNaN(minimumNum) || isNaN(goodNum) || isNaN(excellentNum)) {
      throw new Error('Invalid adherence targets: All values must be valid numbers');
    }

    if (minimumNum < 0 || minimumNum > 100 || goodNum < 0 || goodNum > 100 || excellentNum < 0 || excellentNum > 100) {
      throw new Error('Invalid adherence targets: All values must be between 0 and 100');
    }

    if (minimumNum >= goodNum || goodNum >= excellentNum) {
      throw new Error('Invalid adherence targets: Values must be in ascending order (minimum < good < excellent)');
    }

    return { minimum: minimumNum, good: goodNum, excellent: excellentNum };
  }
}

export const dynamicDashboardService = new DynamicDashboardService();
export default dynamicDashboardService;