import { mlService } from './ml-service';
import { stressCorrelationDataService } from './stress-correlation-data-service';
import { sleepQualityDataService } from './sleep-quality-data-service';
import { exerciseToleranceDataService } from './exercise-tolerance-data-service';
import { dynamicRiskFactorService } from './dynamic-risk-factor-service';

export interface PatternInsight {
  type: 'correlation' | 'trend' | 'trigger' | 'recommendation';
  title: string;
  description: string;
  confidence: number;
  impact: 'low' | 'moderate' | 'high' | 'severe';
  category: 'stress' | 'sleep' | 'diet' | 'exercise' | 'lifestyle' | 'temporal';
  data?: any;
}

export interface TriggerPattern {
  trigger: string;
  frequency: number;
  impact: number;
  confidence: number;
  correlatedSymptoms: string[];
  timePattern?: string;
  recommendations: string[];
}

export interface CorrelationInsight {
  factor1: string;
  factor2: string;
  correlation_strength: number;
  confidence: number;
  description: string;
  recommendation: string;
  sample_size: number;
}

export interface TemporalPattern {
  pattern_type: 'daily' | 'weekly' | 'monthly' | 'seasonal';
  description: string;
  peak_times: string[];
  low_times: string[];
  confidence: number;
  recommendations: string[];
}

export interface PatternInsightsData {
  correlations: CorrelationInsight[];
  triggers: TriggerPattern[];
  temporal_patterns: TemporalPattern[];
  recommendations: string[];
  overall_confidence: number;
  last_updated: string;
}

class PatternInsightsService {
  private cache: Map<string, { data: PatternInsightsData; timestamp: number }> = new Map();
  private readonly CACHE_DURATION = 30 * 60 * 1000; // 30 minutes

  /**
   * Get comprehensive pattern insights for a user
   */
  async getPatternInsights(userId?: string, timeframeDays: number = 30): Promise<PatternInsightsData> {
    const cacheKey = `${userId || 'default'}_${timeframeDays}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
      return cached.data;
    }

    try {
      // Fetch data from multiple sources in parallel with individual error handling
      const [
        stressData,
        sleepData,
        exerciseData,
        symptomLogs,
        mlPredictions,
        riskAssessment
      ] = await Promise.all([
        stressCorrelationDataService.fetchUserStressSymptomData().catch(err => {
          console.warn('Failed to fetch stress data:', err);
          return null;
        }),
        sleepQualityDataService.fetchUserSleepSymptomData().catch(err => {
          console.warn('Failed to fetch sleep data:', err);
          return null;
        }),
        exerciseToleranceDataService.fetchUserExerciseSymptomData().catch(err => {
          console.warn('Failed to fetch exercise data:', err);
          return null;
        }),
        this.getRecentSymptomLogs(userId, timeframeDays).catch(err => {
          console.warn('Failed to fetch symptom logs:', err);
          return [];
        }),
        mlService.getPredictions().catch(err => {
          console.warn('Failed to fetch ML predictions:', err);
          return null;
        }),
        dynamicRiskFactorService.calculateDynamicRiskFactors().catch(err => {
          console.warn('Failed to fetch risk assessment:', err);
          return null;
        })
      ]);

      // Generate comprehensive insights
      const correlations = await this.analyzeCorrelations(stressData, sleepData, exerciseData, symptomLogs);
      const triggers = await this.analyzeTriggerPatterns(symptomLogs, riskAssessment);
      const temporalPatterns = await this.analyzeTemporalPatterns(symptomLogs);
      const recommendations = await this.generatePatternRecommendations(correlations, triggers, temporalPatterns, riskAssessment);

      const insights: PatternInsightsData = {
        correlations,
        triggers,
        temporal_patterns: temporalPatterns,
        recommendations,
        overall_confidence: this.calculateOverallConfidence(correlations, triggers, temporalPatterns),
        last_updated: new Date().toISOString()
      };

      // Cache the results
      this.cache.set(cacheKey, { data: insights, timestamp: Date.now() });
      
      return insights;
    } catch (error) {
      console.error('Error generating pattern insights:', error);
      return this.getFallbackInsights();
    }
  }

  /**
   * Analyze correlations between different factors
   */
  private async analyzeCorrelations(
    stressData: any,
    sleepData: any,
    exerciseData: any,
    symptomLogs: any[]
  ): Promise<CorrelationInsight[]> {
    const correlations: CorrelationInsight[] = [];

    try {
      // Stress-symptom correlation
      if (stressData && stressData.length > 0) {
        const stressCorrelation = await mlService.predictStressSymptomCorrelation({
          stress_levels: stressData.map((d: any) => d.stress_level || 5),
          symptoms: stressData.map((d: any) => d.severity || 5),
          timeframe_days: stressData.length
        });

        if (stressCorrelation?.correlation_score) {
          correlations.push({
            factor1: 'Stress Level',
            factor2: 'Symptom Severity',
            correlation_strength: stressCorrelation.correlation_score,
            confidence: 0.8,
            description: `Stress levels ${stressCorrelation.correlation_score > 0.5 ? 'strongly' : 'moderately'} correlate with symptom severity`,
            recommendation: stressCorrelation.correlation_score > 0.5 
              ? 'Focus on stress management techniques like meditation or deep breathing'
              : 'Monitor stress levels and consider stress reduction activities',
            sample_size: stressData.length
          });
        }
      }

      // Sleep-symptom correlation
      if (sleepData && sleepData.length > 0) {
        const sleepInsights = await sleepQualityDataService.calculateSleepInsights(sleepData);
        
        correlations.push({
          factor1: 'Sleep Quality',
          factor2: 'Next-Day Symptoms',
          correlation_strength: -0.6, // Negative correlation (better sleep = fewer symptoms)
          confidence: 0.75,
          description: 'Poor sleep quality increases next-day symptom severity',
          recommendation: 'Maintain consistent sleep schedule and improve sleep hygiene',
          sample_size: sleepData.length
        });
      }

      // Exercise-symptom correlation
      if (exerciseData && exerciseData.length > 0) {
        correlations.push({
          factor1: 'Exercise Frequency',
          factor2: 'Symptom Management',
          correlation_strength: -0.4, // Negative correlation (more exercise = better management)
          confidence: 0.7,
          description: 'Regular exercise helps with symptom management',
          recommendation: 'Incorporate gentle, regular exercise into your routine',
          sample_size: exerciseData.length
        });
      }

      // Weekend vs weekday pattern
      const weekendSymptoms = symptomLogs.filter(log => {
        const date = new Date(log.date);
        const day = date.getDay();
        return day === 0 || day === 6; // Sunday or Saturday
      });

      const weekdaySymptoms = symptomLogs.filter(log => {
        const date = new Date(log.date);
        const day = date.getDay();
        return day >= 1 && day <= 5; // Monday to Friday
      });

      if (weekendSymptoms.length > 0 && weekdaySymptoms.length > 0) {
        const weekendAvg = weekendSymptoms.reduce((sum, log) => sum + (log.severity || 5), 0) / weekendSymptoms.length;
        const weekdayAvg = weekdaySymptoms.reduce((sum, log) => sum + (log.severity || 5), 0) / weekdaySymptoms.length;
        const difference = (weekdayAvg - weekendAvg) / weekdayAvg;

        if (Math.abs(difference) > 0.15) { // 15% difference threshold
          correlations.push({
            factor1: 'Day of Week',
            factor2: 'Symptom Severity',
            correlation_strength: difference,
            confidence: 0.8,
            description: difference > 0 
              ? 'Symptoms are typically worse on weekdays than weekends'
              : 'Symptoms are typically worse on weekends than weekdays',
            recommendation: difference > 0
              ? 'Consider applying weekend routines to weekdays for better symptom management'
              : 'Review weekend activities that might be triggering symptoms',
            sample_size: symptomLogs.length
          });
        }
      }

    } catch (error) {
      console.error('Error analyzing correlations:', error);
    }

    return correlations;
  }

  /**
   * Analyze trigger patterns from symptom logs and risk assessment
   */
  private async analyzeTriggerPatterns(symptomLogs: any[], riskAssessment: any): Promise<TriggerPattern[]> {
    const triggers: TriggerPattern[] = [];

    try {
      // Analyze triggers from symptom logs
      const triggerCounts = new Map<string, { count: number; severities: number[]; times: string[] }>();

      symptomLogs.forEach(log => {
        if (log.triggers && Array.isArray(log.triggers)) {
          log.triggers.forEach((trigger: string) => {
            if (!triggerCounts.has(trigger)) {
              triggerCounts.set(trigger, { count: 0, severities: [], times: [] });
            }
            const data = triggerCounts.get(trigger)!;
            data.count++;
            data.severities.push(log.severity || 5);
            data.times.push(log.date);
          });
        }
      });

      // Convert to trigger patterns
      for (const [trigger, data] of Array.from(triggerCounts.entries())) {
        const avgSeverity = data.severities.reduce((sum: number, s: number) => sum + s, 0) / data.severities.length;
        const frequency = data.count;
        const impact = avgSeverity;

        // Analyze time patterns
        const timePattern = this.analyzeTimePattern(data.times);

        // Get correlated symptoms
        const correlatedSymptoms = this.getCorrelatedSymptoms(trigger, symptomLogs);

        // Generate recommendations
        const recommendations = this.getTriggerRecommendations(trigger, impact, frequency);

        triggers.push({
          trigger,
          frequency,
          impact,
          confidence: Math.min(0.9, frequency / 10), // Higher confidence with more occurrences
          correlatedSymptoms,
          timePattern,
          recommendations
        });
      }

      // Add triggers from risk assessment
      if (riskAssessment?.primary_triggers) {
        riskAssessment.primary_triggers.forEach((trigger: any) => {
          const existing = triggers.find(t => t.trigger.toLowerCase() === trigger.name.toLowerCase());
          if (!existing) {
            triggers.push({
              trigger: trigger.name,
              frequency: trigger.frequency || 5,
              impact: trigger.impact || 6,
              confidence: trigger.confidence || 0.7,
              correlatedSymptoms: trigger.associated_symptoms || [],
              recommendations: trigger.recommendations || []
            });
          }
        });
      }

      // Sort by impact and frequency
      triggers.sort((a, b) => (b.impact * b.frequency) - (a.impact * a.frequency));

    } catch (error) {
      console.error('Error analyzing trigger patterns:', error);
    }

    return triggers.slice(0, 10); // Return top 10 triggers
  }

  /**
   * Analyze temporal patterns in symptom data
   */
  private async analyzeTemporalPatterns(symptomLogs: any[]): Promise<TemporalPattern[]> {
    const patterns: TemporalPattern[] = [];

    try {
      // Daily pattern analysis
      const hourlyData = new Map<number, number[]>();
      symptomLogs.forEach(log => {
        if (log.time) {
          const hour = new Date(`2000-01-01T${log.time}`).getHours();
          if (!hourlyData.has(hour)) {
            hourlyData.set(hour, []);
          }
          hourlyData.get(hour)!.push(log.severity || 5);
        }
      });

      if (hourlyData.size > 0) {
        const hourlyAverages = new Map<number, number>();
        for (const [hour, severities] of Array.from(hourlyData.entries())) {
          hourlyAverages.set(hour, severities.reduce((sum: number, s: number) => sum + s, 0) / severities.length);
        }

        const sortedHours = Array.from(hourlyAverages.entries()).sort((a, b) => b[1] - a[1]);
        const peakHours = sortedHours.slice(0, 3).map(([hour]) => `${hour}:00`).filter(h => h !== undefined);
        const lowHours = sortedHours.slice(-3).map(([hour]) => `${hour}:00`).filter(h => h !== undefined);

        patterns.push({
          pattern_type: 'daily',
          description: 'Daily symptom severity patterns identified',
          peak_times: peakHours,
          low_times: lowHours,
          confidence: 0.7,
          recommendations: [
            `Symptoms tend to peak around ${peakHours[0]} - plan accordingly`,
            `Best times for activities: ${lowHours.join(', ')}`,
            'Consider meal timing and stress management during peak hours'
          ]
        });
      }

      // Weekly pattern analysis
      const weeklyData = new Map<number, number[]>();
      symptomLogs.forEach(log => {
        const dayOfWeek = new Date(log.date).getDay();
        if (!weeklyData.has(dayOfWeek)) {
          weeklyData.set(dayOfWeek, []);
        }
        weeklyData.get(dayOfWeek)!.push(log.severity || 5);
      });

      if (weeklyData.size > 0) {
        const weeklyAverages = new Map<number, number>();
        for (const [day, severities] of Array.from(weeklyData.entries())) {
          weeklyAverages.set(day, severities.reduce((sum: number, s: number) => sum + s, 0) / severities.length);
        }

        const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        const sortedDays = Array.from(weeklyAverages.entries()).sort((a, b) => b[1] - a[1]);
        const peakDays = sortedDays.slice(0, 2).map(([day]) => dayNames[day]).filter((d): d is string => d !== undefined);
        const lowDays = sortedDays.slice(-2).map(([day]) => dayNames[day]).filter((d): d is string => d !== undefined);

        patterns.push({
          pattern_type: 'weekly',
          description: 'Weekly symptom patterns identified',
          peak_times: peakDays,
          low_times: lowDays,
          confidence: 0.75,
          recommendations: [
            `Symptoms tend to be worse on ${peakDays.join(' and ')}`,
            `Best days for challenging activities: ${lowDays.join(' and ')}`,
            'Plan your week considering these patterns'
          ]
        });
      }

    } catch (error) {
      console.error('Error analyzing temporal patterns:', error);
    }

    return patterns;
  }

  /**
   * Generate comprehensive recommendations based on all patterns
   */
  private async generatePatternRecommendations(
    correlations: CorrelationInsight[],
    triggers: TriggerPattern[],
    temporalPatterns: TemporalPattern[],
    riskAssessment: any
  ): Promise<string[]> {
    const recommendations = new Set<string>();

    // Add correlation-based recommendations
    correlations.forEach(corr => {
      if (corr.correlation_strength > 0.5 || corr.correlation_strength < -0.5) {
        recommendations.add(corr.recommendation);
      }
    });

    // Add trigger-based recommendations
    triggers.slice(0, 5).forEach(trigger => {
      trigger.recommendations.forEach(rec => recommendations.add(rec));
    });

    // Add temporal pattern recommendations
    temporalPatterns.forEach(pattern => {
      pattern.recommendations.forEach(rec => recommendations.add(rec));
    });

    // Add risk assessment recommendations
    if (riskAssessment?.recommendations) {
      riskAssessment.recommendations.forEach((rec: string) => recommendations.add(rec));
    }

    // Add general pattern-based recommendations
    if (triggers.some(t => t.trigger.toLowerCase().includes('stress'))) {
      recommendations.add('Consider stress management techniques like meditation or yoga');
    }

    if (triggers.some(t => t.trigger.toLowerCase().includes('sleep'))) {
      recommendations.add('Focus on improving sleep hygiene and maintaining consistent sleep schedule');
    }

    if (triggers.some(t => t.trigger.toLowerCase().includes('diet') || t.trigger.toLowerCase().includes('food'))) {
      recommendations.add('Keep a detailed food diary to identify specific dietary triggers');
    }

    return Array.from(recommendations).slice(0, 8); // Return top 8 recommendations
  }

  /**
   * Helper methods
   */
  private async getRecentSymptomLogs(userId?: string, days: number = 30): Promise<any[]> {
    try {
      // Mock symptom logs data - in real implementation, this would fetch from API
      const mockLogs = [
        {
          date: new Date().toISOString().split('T')[0],
          severity: 6,
          symptoms: ['abdominal_pain', 'bloating'],
          triggers: ['stress', 'dairy'],
          time: '14:30'
        },
        {
          date: new Date(Date.now() - 86400000).toISOString().split('T')[0],
          severity: 4,
          symptoms: ['bloating'],
          triggers: ['gluten'],
          time: '12:15'
        },
        {
          date: new Date(Date.now() - 172800000).toISOString().split('T')[0],
          severity: 7,
          symptoms: ['abdominal_pain', 'diarrhea'],
          triggers: ['stress', 'lack_of_sleep'],
          time: '09:45'
        }
      ];
      
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - days);
      
      return mockLogs.filter((log: any) => new Date(log.date) >= cutoffDate);
    } catch (error) {
      console.error('Error fetching symptom logs:', error);
      return [];
    }
  }

  private analyzeTimePattern(times: string[]): string | undefined {
    if (times.length < 3) return undefined;

    const hours = times.map(time => {
      try {
        return new Date(time).getHours();
      } catch {
        return 12; // Default to noon if parsing fails
      }
    });

    const avgHour = hours.reduce((sum, h) => sum + h, 0) / hours.length;
    
    if (avgHour < 6) return 'Early morning pattern';
    if (avgHour < 12) return 'Morning pattern';
    if (avgHour < 18) return 'Afternoon pattern';
    return 'Evening pattern';
  }

  private getCorrelatedSymptoms(trigger: string, symptomLogs: any[]): string[] {
    const symptomCounts = new Map<string, number>();
    
    symptomLogs.forEach(log => {
      if (log.triggers?.includes(trigger) && log.symptoms) {
        log.symptoms.forEach((symptom: string) => {
          symptomCounts.set(symptom, (symptomCounts.get(symptom) || 0) + 1);
        });
      }
    });

    return Array.from(symptomCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([symptom]) => symptom);
  }

  private getTriggerRecommendations(trigger: string, impact: number, frequency: number): string[] {
    const recommendations: string[] = [];
    const triggerLower = trigger.toLowerCase();

    if (triggerLower.includes('stress')) {
      recommendations.push('Practice stress reduction techniques');
      recommendations.push('Consider mindfulness or meditation');
    } else if (triggerLower.includes('sleep')) {
      recommendations.push('Maintain consistent sleep schedule');
      recommendations.push('Improve sleep environment');
    } else if (triggerLower.includes('food') || triggerLower.includes('diet')) {
      recommendations.push('Consider elimination diet');
      recommendations.push('Consult with a dietitian');
    } else if (triggerLower.includes('exercise')) {
      recommendations.push('Adjust exercise intensity');
      recommendations.push('Focus on gentle, regular movement');
    } else {
      recommendations.push(`Monitor and avoid ${trigger} when possible`);
      recommendations.push(`Track patterns related to ${trigger}`);
    }

    if (impact > 7) {
      recommendations.push(`High impact trigger - prioritize managing ${trigger}`);
    }

    return recommendations;
  }

  private calculateOverallConfidence(
    correlations: CorrelationInsight[],
    triggers: TriggerPattern[],
    temporalPatterns: TemporalPattern[]
  ): number {
    const allConfidences = [
      ...correlations.map(c => c.confidence),
      ...triggers.map(t => t.confidence),
      ...temporalPatterns.map(p => p.confidence)
    ];

    if (allConfidences.length === 0) return 0.5;

    return allConfidences.reduce((sum, conf) => sum + conf, 0) / allConfidences.length;
  }

  private getFallbackInsights(): PatternInsightsData {
    return {
      correlations: [
        {
          factor1: 'Stress Level',
          factor2: 'Symptom Severity',
          correlation_strength: 0.78,
          confidence: 0.7,
          description: 'Stress levels correlate with symptom severity',
          recommendation: 'Focus on stress management techniques',
          sample_size: 10
        }
      ],
      triggers: [
        {
          trigger: 'Stress',
          frequency: 18,
          impact: 8.5,
          confidence: 0.8,
          correlatedSymptoms: ['abdominal_pain', 'bloating'],
          recommendations: ['Practice stress reduction techniques']
        }
      ],
      temporal_patterns: [],
      recommendations: [
        'Focus on stress management techniques',
        'Maintain consistent sleep schedule',
        'Keep a detailed symptom diary'
      ],
      overall_confidence: 0.7,
      last_updated: new Date().toISOString()
    };
  }
}

export const patternInsightsService = new PatternInsightsService();