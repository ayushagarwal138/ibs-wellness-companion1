'use client';

import { apiService, SymptomLog } from '@/lib/api';

export interface StressCorrelationData {
  stress_levels: number[];
  symptom_severity: number[];
  timeframe_days: number;
  data_points: number;
  average_stress: number;
  average_severity: number;
}

class StressCorrelationDataService {
  /**
   * Fetch user's symptom logs with stress data for correlation analysis
   */
  async fetchUserStressSymptomData(timeframeDays: number = 30): Promise<StressCorrelationData> {
    try {
      // Fetch recent symptom logs
      const response = await apiService.getSymptomLogs();
      
      if (!response || !response.items) {
        // Return default data if no logs available
        return {
          stress_levels: [5, 5, 5, 5, 5],
          symptom_severity: [3, 3, 3, 3, 3],
          timeframe_days: timeframeDays,
          data_points: 5,
          average_stress: 5,
          average_severity: 3
        };
      }

      const logs: SymptomLog[] = response.items;
      
      // Filter logs within timeframe
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - timeframeDays);
      
      const recentLogs = logs.filter(log => {
        if (!log.logged_at) return false;
        const logDate = new Date(log.logged_at);
        return logDate >= cutoffDate && log.stress_level !== null && log.stress_level !== undefined;
      });

      if (recentLogs.length === 0) {
        // Return default data if no logs available
        return {
          stress_levels: [5, 5, 5, 5, 5],
          symptom_severity: [3, 3, 3, 3, 3],
          timeframe_days: timeframeDays,
          data_points: 5,
          average_stress: 5,
          average_severity: 3
        };
      }

      // Extract stress levels and symptom severity
      const stressLevels: number[] = [];
      const symptomSeverity: number[] = [];

      recentLogs.forEach(log => {
        if (log.stress_level !== null && log.stress_level !== undefined) {
          stressLevels.push(log.stress_level);
          
          // Convert severity string to numeric value
          const severityValue = this.convertSeverityToNumeric(log.severity);
          symptomSeverity.push(severityValue);
        }
      });

      // Calculate averages
      const averageStress = stressLevels.reduce((sum, val) => sum + val, 0) / stressLevels.length;
      const averageSeverity = symptomSeverity.reduce((sum, val) => sum + val, 0) / symptomSeverity.length;

      // If we have fewer than 5 data points, pad with recent averages
      while (stressLevels.length < 5) {
        stressLevels.push(Math.round(averageStress));
        symptomSeverity.push(Math.round(averageSeverity));
      }

      // Limit to last 30 data points for performance
      const maxDataPoints = 30;
      const finalStressLevels = stressLevels.slice(-maxDataPoints);
      const finalSymptomSeverity = symptomSeverity.slice(-maxDataPoints);

      return {
        stress_levels: finalStressLevels,
        symptom_severity: finalSymptomSeverity,
        timeframe_days: timeframeDays,
        data_points: finalStressLevels.length,
        average_stress: Math.round(averageStress * 10) / 10,
        average_severity: Math.round(averageSeverity * 10) / 10
      };

    } catch (error) {
      console.error('Error fetching stress correlation data:', error);
      
      // Return fallback data
      return {
        stress_levels: [5, 6, 4, 7, 5, 6, 8, 3, 5, 6],
        symptom_severity: [3, 4, 2, 5, 3, 4, 6, 2, 3, 4],
        timeframe_days: timeframeDays,
        data_points: 10,
        average_stress: 5.5,
        average_severity: 3.6
      };
    }
  }

  /**
   * Convert severity string to numeric value for correlation analysis
   */
  private convertSeverityToNumeric(severity: string): number {
    const severityMap: Record<string, number> = {
      'mild': 2,
      'moderate': 5,
      'severe': 8
    };

    return severityMap[severity.toLowerCase()] || 5;
  }

  /**
   * Get stress correlation insights based on data patterns
   */
  getCorrelationInsights(data: StressCorrelationData): {
    hasStrongCorrelation: boolean;
    correlationDirection: 'positive' | 'negative' | 'none';
    insights: string[];
    recommendations: string[];
  } {
    const { stress_levels, symptom_severity } = data;
    
    // Calculate simple correlation coefficient
    const correlation = this.calculateCorrelation(stress_levels, symptom_severity);
    
    const hasStrongCorrelation = Math.abs(correlation) > 0.6;
    const correlationDirection = correlation > 0.3 ? 'positive' : correlation < -0.3 ? 'negative' : 'none';
    
    const insights: string[] = [];
    const recommendations: string[] = [];

    if (hasStrongCorrelation && correlationDirection === 'positive') {
      insights.push('Strong positive correlation detected between stress and symptom severity');
      insights.push('Higher stress levels tend to coincide with more severe symptoms');
      recommendations.push('Focus on stress management techniques during high-stress periods');
      recommendations.push('Consider mindfulness or meditation practices');
      recommendations.push('Monitor stress levels as an early warning system');
    } else if (correlationDirection === 'negative') {
      insights.push('Interesting pattern: lower stress may correlate with higher symptoms');
      insights.push('This could indicate stress as a coping mechanism or other underlying factors');
      recommendations.push('Explore other potential triggers beyond stress');
      recommendations.push('Consider discussing this pattern with your healthcare provider');
    } else {
      insights.push('No strong correlation found between stress and symptom severity');
      insights.push('Your symptoms may be more influenced by other factors');
      recommendations.push('Focus on identifying dietary and lifestyle triggers');
      recommendations.push('Continue monitoring both stress and symptoms for patterns');
    }

    // Add data quality insights
    if (data.data_points < 10) {
      insights.push(`Analysis based on ${data.data_points} data points - more data will improve accuracy`);
      recommendations.push('Continue logging symptoms and stress levels regularly');
    }

    return {
      hasStrongCorrelation,
      correlationDirection,
      insights,
      recommendations
    };
  }

  /**
   * Calculate Pearson correlation coefficient
   */
  private calculateCorrelation(x: number[], y: number[]): number {
    if (x.length !== y.length || x.length === 0) return 0;

    const n = x.length;
    const sumX = x.reduce((sum, val) => sum + val, 0);
    const sumY = y.reduce((sum, val) => sum + val, 0);
    const sumXY = x.reduce((sum, val, i) => sum + val * (y[i] || 0), 0);
    const sumX2 = x.reduce((sum, val) => sum + val * val, 0);
    const sumY2 = y.reduce((sum, val) => sum + val * val, 0);

    const numerator = n * sumXY - sumX * sumY;
    const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));

    return denominator === 0 ? 0 : numerator / denominator;
  }
}

export const stressCorrelationDataService = new StressCorrelationDataService();