'use client';

import { API_CONFIG } from '@/lib/config';
import { apiService } from './api-service';
import { dynamicRiskFactorService, DynamicRiskAssessment } from './dynamic-risk-factor-service';
import { ApiError } from '@/lib/api';

// Enhanced error handling for dashboard operations
interface DashboardError extends Error {
  type: 'network' | 'auth' | 'server' | 'validation' | 'timeout' | 'data' | 'unknown';
  component?: string;
  retryable: boolean;
  userMessage: string;
}

// Retry configuration for dashboard operations
const DASHBOARD_RETRY_CONFIG = {
  maxRetries: 2,
  retryDelay: 2000,
  components: {
    predictions: { maxRetries: 3, critical: true },
    symptoms: { maxRetries: 2, critical: false },
    stats: { maxRetries: 2, critical: false },
    insights: { maxRetries: 1, critical: false },
    reminders: { maxRetries: 1, critical: false },
    recommendations: { maxRetries: 2, critical: false }
  }
};

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
  
  // Helper method to create dashboard-specific errors
  private createDashboardError(error: any, component: string): DashboardError {
    let type: DashboardError['type'] = 'unknown';
    let retryable = false;
    let userMessage = 'An unexpected error occurred';

    if (error && typeof error === 'object' && 'type' in error) {
      // Handle ApiError from our enhanced API client
      const apiError = error as ApiError;
      type = apiError.type;
      retryable = apiError.retryable;
      
      switch (apiError.type) {
        case 'network':
          userMessage = `Unable to connect to ${this.getComponentDisplayName(component)} service. Please check your internet connection and try again.`;
          break;
        case 'auth':
          userMessage = `Please log in to access ${this.getComponentDisplayName(component)}.`;
          break;
        case 'server':
          userMessage = `${this.getComponentDisplayName(component)} service is temporarily unavailable. Please try again in a moment.`;
          break;
        case 'timeout':
          userMessage = `${this.getComponentDisplayName(component)} is taking longer than usual to load. Please try again.`;
          break;
        case 'validation':
          userMessage = 'Invalid data provided. Please check your input and try again.';
          break;
        default:
          userMessage = `Failed to load ${this.getComponentDisplayName(component)}. Please try again.`;
      }
    } else {
      // Handle other types of errors
      type = 'data';
      retryable = true;
      userMessage = this.getContextualErrorMessage(error, component);
    }

    const dashboardError = new Error(error?.message || userMessage) as DashboardError;
    dashboardError.type = type;
    dashboardError.component = component;
    dashboardError.retryable = retryable;
    dashboardError.userMessage = userMessage;
    
    return dashboardError;
  }

  private getComponentDisplayName(component: string): string {
    const displayNames: Record<string, string> = {
      'predictions': 'AI Predictions',
      'symptoms': 'Recent Symptoms',
      'stats': 'Weekly Statistics',
      'insights': 'Personalized Insights',
      'reminders': 'Upcoming Reminders',
      'recommendations': 'Personalized Recommendations',
      'dashboard': 'Dashboard',
    };
    
    return displayNames[component] || component;
  }

  private getContextualErrorMessage(error: any, component: string): string {
    const componentName = this.getComponentDisplayName(component);
    
    // Check if error has a user-friendly message from the API client
    if (error?.userMessage) {
      return error.userMessage;
    }
    
    // Check for specific error patterns
    if (error?.response?.data?.detail) {
      const detail = error.response.data.detail;
      if (typeof detail === 'string') {
        return `${componentName}: ${detail}`;
      }
    }
    
    // Default contextual message
    return `Unable to load ${componentName}. Please try again.`;
  }

  // Helper method to execute operations with component-specific retry logic
  private async executeWithRetry<T>(
    operation: () => Promise<T>,
    component: keyof typeof DASHBOARD_RETRY_CONFIG.components,
    fallbackData?: T
  ): Promise<T> {
    const config = DASHBOARD_RETRY_CONFIG.components[component];
    let lastError: any;

    for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error;
        
        const dashboardError = this.createDashboardError(error, component);
        
        // If it's not retryable or we've exhausted retries, throw the error
        if (!dashboardError.retryable || attempt === config.maxRetries) {
          // For non-critical components, return fallback data if available
          if (!config.critical && fallbackData !== undefined) {
            console.warn(`Failed to load ${component}, using fallback data:`, dashboardError);
            return fallbackData;
          }
          throw dashboardError;
        }

        // Wait before retrying (exponential backoff)
        if (attempt < config.maxRetries) {
          const delay = DASHBOARD_RETRY_CONFIG.retryDelay * Math.pow(2, attempt);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    throw this.createDashboardError(lastError, component);
  }

  async getMLPredictions(): Promise<DynamicDashboardData['aiPredictions']> {
    try {
      // Get enhanced predictions, trigger analysis, and dynamic risk assessment in parallel
      const [predictionsData, triggerAnalysisData, dynamicRiskAssessment] = await Promise.all([
        apiService.get(`${API_CONFIG.BASE_URL}/api/v1/ml/predictions`),
        apiService.get(`${API_CONFIG.BASE_URL}/api/v1/diet/analysis/triggers?days=90`),
        dynamicRiskFactorService.calculateDynamicRiskFactors()
      ]);

      // Validate required fields from ML model response
      if (!predictionsData || typeof predictionsData !== 'object') {
        throw new Error('Invalid ML prediction response format');
      }

      // Extract trigger foods from enhanced analysis
      const enhancedTriggerFoods = (triggerAnalysisData as any)?.trigger_foods?.map((trigger: any) => 
        `${trigger.food_name} (${trigger.risk_score}% risk)`
      ) || [];

      // Fallback to basic trigger foods if enhanced analysis fails
      const triggerFoods = enhancedTriggerFoods.length > 0 
        ? enhancedTriggerFoods 
        : this.validateStringArray((predictionsData as any).triggerFoods);

      // Integrate dynamic risk factors with ML predictions
      const enhancedKeyFactors = this.combineRiskFactors(
        this.validateStringArray((predictionsData as any).keyFactors),
        dynamicRiskAssessment
      );

      // Enhance recommendations with dynamic insights
      const enhancedRecommendations = this.combineRecommendations(
        this.validateStringArray((predictionsData as any).recommendations),
        dynamicRiskAssessment
      );

      // Use dynamic risk level if confidence is higher
      const finalRiskLevel = this.selectBestRiskLevel(
        this.validateRiskLevel((predictionsData as any).riskLevel),
        dynamicRiskAssessment
      );

      // Combine confidence scores
      const combinedConfidence = this.calculateCombinedConfidence(
        this.validateConfidence((predictionsData as any).confidence),
        dynamicRiskAssessment.confidence
      );

      // Ensure all required fields are present and valid
      const predictions = {
        riskLevel: finalRiskLevel,
        nextFlareRisk: this.validatePercentage((predictionsData as any).nextFlareRisk),
        confidence: combinedConfidence,
        triggerFoods: triggerFoods,
        recommendations: enhancedRecommendations,
        keyFactors: enhancedKeyFactors,
        timeline: this.validateTimeline((predictionsData as any).timeline),
        modelVersion: this.validateModelVersion((predictionsData as any).modelVersion),
      };

      console.log('Enhanced ML predictions with dynamic risk analysis retrieved successfully:', predictions);
      return predictions;
    } catch (error) {
      console.error('Failed to fetch ML predictions:', error);
      throw new Error(`ML prediction service unavailable: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Combine ML-generated key factors with dynamic risk factors
   */
  private combineRiskFactors(mlFactors: string[], riskAssessment: DynamicRiskAssessment): string[] {
    const dynamicFactors = riskAssessment.riskFactors
      .filter(factor => factor.impact === 'high' || factor.impact === 'critical')
      .map(factor => factor.factor);

    // Combine and deduplicate factors, prioritizing high-impact dynamic factors
    const combinedFactors = [...dynamicFactors, ...mlFactors];
    const uniqueFactors = Array.from(new Set(combinedFactors));
    
    // Limit to top 6 factors for display
    return uniqueFactors.slice(0, 6);
  }

  /**
   * Combine ML recommendations with dynamic risk-based recommendations
   */
  private combineRecommendations(mlRecommendations: string[], riskAssessment: DynamicRiskAssessment): string[] {
    // Get top priority recommendations from dynamic assessment
    const dynamicRecommendations = riskAssessment.recommendations.slice(0, 3);
    
    // Combine recommendations, prioritizing dynamic ones
    const combinedRecommendations = [...dynamicRecommendations, ...mlRecommendations];
    const uniqueRecommendations = Array.from(new Set(combinedRecommendations));
    
    // Limit to top 8 recommendations for display
    return uniqueRecommendations.slice(0, 8);
  }

  /**
   * Select the best risk level based on confidence scores
   */
  private selectBestRiskLevel(mlRiskLevel: 'low' | 'medium' | 'high', riskAssessment: DynamicRiskAssessment): 'low' | 'medium' | 'high' {
    // Convert dynamic risk level to match ML format
    const dynamicRiskLevel = riskAssessment.riskLevel === 'moderate' ? 'medium' : 
                             riskAssessment.riskLevel === 'critical' ? 'high' : 
                             riskAssessment.riskLevel;

    // Use dynamic risk level if it has higher confidence or if it indicates higher risk
    if (riskAssessment.confidence > 0.7) {
      return dynamicRiskLevel as 'low' | 'medium' | 'high';
    }

    // Otherwise, use the higher of the two risk levels
    const riskLevels = { low: 1, medium: 2, high: 3 };
    const mlLevel = riskLevels[mlRiskLevel];
    const dynamicLevel = riskLevels[dynamicRiskLevel as 'low' | 'medium' | 'high'];
    
    const maxLevel = Math.max(mlLevel, dynamicLevel);
    return Object.keys(riskLevels).find(key => riskLevels[key as keyof typeof riskLevels] === maxLevel) as 'low' | 'medium' | 'high';
  }

  /**
   * Calculate combined confidence score
   */
  private calculateCombinedConfidence(mlConfidence: number, dynamicConfidence: number): number {
    // Weighted average with slight preference for dynamic confidence if it's high
    const weight = dynamicConfidence > 0.8 ? 0.6 : 0.4;
    const combinedConfidence = (dynamicConfidence * weight) + (mlConfidence * (1 - weight));
    return Math.round(combinedConfidence * 100) / 100;
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
      const data = await apiService.get(`${API_CONFIG.BASE_URL}/api/v1/symptom-logs?limit=10`) as any;

      const logs = data.data || data.items || [];
      return logs.map((log: any) => ({
        date: new Date(log.logged_at).toLocaleDateString(),
        severity_score: log.severity === 'mild' ? 2 : log.severity === 'moderate' ? 5 : log.severity === 'severe' ? 8 : log.severity === 'very_severe' ? 10 : 0,
        severity: log.severity || 'none',
        symptom_name: log.symptom_name || 'Unknown',
        symptoms: log.symptom_name ? [log.symptom_name] : [],
        stress_level: log.stress_level || 0,
        sleep_quality: log.sleep_quality || 0,
        logged_at: log.logged_at,
        notes: log.notes,
      }));
    } catch (error) {
      console.error('Failed to fetch recent symptoms:', error);
      return [];
    }
  }

  async getWeeklyStats(): Promise<DynamicDashboardData['weeklyStats']> {
    try {
      const [symptomsData, analyticsData] = await Promise.all([
        apiService.get(`${API_CONFIG.BASE_URL}/api/v1/symptom-logs?days=7`),
        apiService.get(`${API_CONFIG.BASE_URL}/api/v1/analytics/weekly-summary`),
      ]);

      const symptoms = (symptomsData as any).data || (symptomsData as any).items || [];
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
        adherenceRate: this.validateAdherenceRate((analyticsData as any).adherence_rate),
        improvementTrend: this.validateImprovementTrend((analyticsData as any).improvement_trend),
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
      const data = await apiService.get(`${API_CONFIG.BASE_URL}/api/v1/analytics/insights`) as any;

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
      const data = await apiService.get(`${API_CONFIG.BASE_URL}/api/v1/reminders/upcoming`) as any;

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
      const data = await apiService.get(`${API_CONFIG.BASE_URL}/api/v1/recommendations/personalized`) as any;

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
      // Define fallback data for non-critical components
      const fallbackSymptoms: DynamicDashboardData['recentSymptoms'] = [];
      const fallbackStats: DynamicDashboardData['weeklyStats'] = {
        avgSeverity: 0,
        symptomFreeDays: 0,
        totalLogs: 0,
        adherenceRate: 0,
        improvementTrend: 0,
      };
      const fallbackInsights: DynamicDashboardData['insights'] = [];
      const fallbackReminders: DynamicDashboardData['upcomingReminders'] = [];
      const fallbackRecommendations: DynamicDashboardData['personalizedRecommendations'] = {
        dietary: [],
        lifestyle: [],
        medical: [],
      };

      // Use Promise.allSettled to handle partial failures gracefully
      const results = await Promise.allSettled([
        this.executeWithRetry(() => this.getMLPredictions(), 'predictions'),
        this.executeWithRetry(() => this.getRecentSymptoms(), 'symptoms', fallbackSymptoms),
        this.executeWithRetry(() => this.getWeeklyStats(), 'stats', fallbackStats),
        this.executeWithRetry(() => this.getPersonalizedInsights(), 'insights', fallbackInsights),
        this.executeWithRetry(() => this.getUpcomingReminders(), 'reminders', fallbackReminders),
        this.executeWithRetry(() => this.getPersonalizedRecommendations(), 'recommendations', fallbackRecommendations),
      ]);

      // Extract results, using fallbacks for failed non-critical components
      const [
        predictionsResult,
        symptomsResult,
        statsResult,
        insightsResult,
        remindersResult,
        recommendationsResult,
      ] = results;

      // AI Predictions is critical - if it fails, the whole dashboard fails
      if (predictionsResult.status === 'rejected') {
        throw predictionsResult.reason;
      }

      return {
        aiPredictions: predictionsResult.value,
        recentSymptoms: symptomsResult.status === 'fulfilled' ? symptomsResult.value : fallbackSymptoms,
        weeklyStats: statsResult.status === 'fulfilled' ? statsResult.value : fallbackStats,
        insights: insightsResult.status === 'fulfilled' ? insightsResult.value : fallbackInsights,
        upcomingReminders: remindersResult.status === 'fulfilled' ? remindersResult.value : fallbackReminders,
        personalizedRecommendations: recommendationsResult.status === 'fulfilled' ? recommendationsResult.value : fallbackRecommendations,
      };
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      throw this.createDashboardError(error, 'dashboard');
    }
  }

  // Real-time updates
  async refreshPredictions(): Promise<DynamicDashboardData['aiPredictions']> {
    try {
      const data = await apiService.get(`${API_CONFIG.BASE_URL}/api/v1/ml/realtime-predictions`) as any;

      // Validate required fields from ML model response
      if (!data || typeof data !== 'object') {
        throw new Error('Invalid ML predictions data received');
      }

      const predictions = {
        riskLevel: this.validateRiskLevel(data.riskLevel),
        nextFlareRisk: this.validatePercentage(data.nextFlareRisk),
        confidence: this.validateConfidence(data.confidence),
        triggerFoods: this.validateStringArray(data.triggerFoods),
        recommendations: this.validateStringArray(data.recommendations),
        keyFactors: this.validateStringArray(data.keyFactors),
        timeline: data.timeline || 'Next 7 days',
        modelVersion: data.modelVersion || 'v1.0'
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
      const data = await apiService.get(`${API_CONFIG.BASE_URL}/api/v1/config/dashboard-thresholds`) as any;

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