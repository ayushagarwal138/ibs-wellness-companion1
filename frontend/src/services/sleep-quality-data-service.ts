import { apiService, SymptomLog } from '@/lib/api';

export interface SleepQualityData {
  sleep_hours: number[];
  sleep_quality_scores: number[];
  symptom_severity: number[];
  timeframe_days: number;
}

export class SleepQualityDataService {
  /**
   * Fetch user sleep and symptom data for the specified timeframe
   */
  async fetchUserSleepSymptomData(timeframeDays: number = 30): Promise<SleepQualityData> {
    try {
      // Calculate date range
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(endDate.getDate() - timeframeDays);

      // Fetch symptom logs with sleep quality data
      const response = await apiService.getSymptomLogs({
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        limit: 1000 // Get all logs in the timeframe
      });

      if (!response.items) {
        throw new Error('No symptom logs found');
      }

      const logs = response.items;

      // Filter logs that have sleep quality data
      const logsWithSleepData = logs.filter(log => 
        log.sleep_quality !== null && 
        log.sleep_quality !== undefined &&
        log.logged_at
      );

      if (logsWithSleepData.length === 0) {
        throw new Error('No sleep quality data found in the specified timeframe');
      }

      // Sort by date
      logsWithSleepData.sort((a, b) => 
        new Date(a.logged_at!).getTime() - new Date(b.logged_at!).getTime()
      );

      // Extract sleep and symptom data
      const sleepHours: number[] = [];
      const sleepQualityScores: number[] = [];
      const symptomSeverity: number[] = [];

      logsWithSleepData.forEach(log => {
        // Convert sleep quality (1-10) to estimated sleep hours
        // Assume: quality 1-3 = 4-5 hours, 4-6 = 6-7 hours, 7-8 = 7-8 hours, 9-10 = 8-9 hours
        const sleepQuality = log.sleep_quality!;
        let estimatedHours: number;
        
        if (sleepQuality <= 3) {
          estimatedHours = 4 + (sleepQuality - 1) * 0.5; // 4-5 hours
        } else if (sleepQuality <= 6) {
          estimatedHours = 6 + (sleepQuality - 4) * 0.33; // 6-7 hours
        } else if (sleepQuality <= 8) {
          estimatedHours = 7 + (sleepQuality - 7) * 0.5; // 7-8 hours
        } else {
          estimatedHours = 8 + (sleepQuality - 9) * 0.5; // 8-9 hours
        }

        sleepHours.push(Math.round(estimatedHours * 10) / 10);
        sleepQualityScores.push(sleepQuality);
        
        // Convert severity enum to numeric value
        const severityValue = this.convertSeverityToNumeric(log.severity);
        symptomSeverity.push(severityValue);
      });

      return {
        sleep_hours: sleepHours,
        sleep_quality_scores: sleepQualityScores,
        symptom_severity: symptomSeverity,
        timeframe_days: timeframeDays
      };

    } catch (error) {
      console.error('Error fetching sleep quality data:', error);
      throw error;
    }
  }

  /**
   * Convert severity enum to numeric value
   */
  private convertSeverityToNumeric(severity: string): number {
    const severityMap: { [key: string]: number } = {
      'mild': 2,
      'moderate': 5,
      'severe': 8,
      'very_severe': 10
    };
    
    return severityMap[severity.toLowerCase()] || 5;
  }

  /**
   * Calculate sleep quality insights
   */
  calculateSleepInsights(data: SleepQualityData): {
    averageSleepHours: number;
    averageSleepQuality: number;
    averageSymptomSeverity: number;
    sleepQualityTrend: 'improving' | 'stable' | 'declining';
    recommendations: string[];
  } {
    const { sleep_hours, sleep_quality_scores, symptom_severity } = data;
    
    if (sleep_hours.length === 0) {
      throw new Error('No data available for analysis');
    }

    // Calculate averages
    const avgSleepHours = sleep_hours.reduce((sum, hours) => sum + hours, 0) / sleep_hours.length;
    const avgSleepQuality = sleep_quality_scores.reduce((sum, quality) => sum + quality, 0) / sleep_quality_scores.length;
    const avgSymptomSeverity = symptom_severity.reduce((sum, severity) => sum + severity, 0) / symptom_severity.length;

    // Determine trend (compare first half vs second half)
    const midpoint = Math.floor(sleep_quality_scores.length / 2);
    const firstHalfAvg = sleep_quality_scores.slice(0, midpoint).reduce((sum, val) => sum + val, 0) / midpoint;
    const secondHalfAvg = sleep_quality_scores.slice(midpoint).reduce((sum, val) => sum + val, 0) / (sleep_quality_scores.length - midpoint);
    
    let sleepQualityTrend: 'improving' | 'stable' | 'declining';
    const trendDiff = secondHalfAvg - firstHalfAvg;
    
    if (trendDiff > 0.5) {
      sleepQualityTrend = 'improving';
    } else if (trendDiff < -0.5) {
      sleepQualityTrend = 'declining';
    } else {
      sleepQualityTrend = 'stable';
    }

    // Generate recommendations
    const recommendations: string[] = [];
    
    if (avgSleepHours < 7) {
      recommendations.push('Aim for 7-9 hours of sleep per night for optimal IBS symptom management');
    }
    
    if (avgSleepQuality < 6) {
      recommendations.push('Focus on improving sleep quality through better sleep hygiene');
      recommendations.push('Consider creating a consistent bedtime routine');
    }
    
    if (avgSymptomSeverity > 6 && avgSleepQuality < 7) {
      recommendations.push('Poor sleep may be contributing to symptom severity - prioritize sleep improvement');
    }
    
    if (sleepQualityTrend === 'declining') {
      recommendations.push('Your sleep quality trend is declining - consider identifying and addressing sleep disruptors');
    }

    return {
      averageSleepHours: Math.round(avgSleepHours * 10) / 10,
      averageSleepQuality: Math.round(avgSleepQuality * 10) / 10,
      averageSymptomSeverity: Math.round(avgSymptomSeverity * 10) / 10,
      sleepQualityTrend,
      recommendations
    };
  }
}

export const sleepQualityDataService = new SleepQualityDataService();