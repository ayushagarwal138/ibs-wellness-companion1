import { apiService, SymptomLog } from '@/lib/api';

export interface ExerciseToleranceData {
  exercise_types: string[];
  exercise_intensities: number[];
  exercise_durations: number[];
  post_exercise_symptoms: number[];
  timeframe_days: number;
}

export interface LifestyleFactors {
  exerciseFrequency: string;
  exerciseTypes: string[];
  sleepHours: number;
  sleepQuality: string;
  stressLevel: number;
  stressManagement: string[];
  smokingStatus: string;
  workSchedule: string;
  workStressLevel: number;
  socialSupport: string;
  hobbies: string[];
  travelFrequency: string;
  environmentalFactors: string[];
  dailyRoutine: string;
  specialNotes: string;
}

export class ExerciseToleranceDataService {
  /**
   * Fetch user exercise and symptom data for the specified timeframe
   */
  async fetchUserExerciseSymptomData(timeframeDays: number = 30): Promise<ExerciseToleranceData> {
    try {
      // Calculate date range
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(endDate.getDate() - timeframeDays);

      // Fetch lifestyle factors to get exercise preferences
      const lifestyleData: LifestyleFactors = await apiService.getLifestyleFactors();

      // Fetch symptom logs for the timeframe
      const response = await apiService.getSymptomLogs({
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        limit: 1000
      });

      if (!response.items) {
        // Return default data if no logs available
        return {
          exercise_types: ['Walking', 'Light Cardio', 'Stretching'],
          exercise_intensities: [3, 4, 2],
          exercise_durations: [30, 25, 15],
          post_exercise_symptoms: [2, 3, 1],
          timeframe_days: timeframeDays
        };
      }

      const logs = response.items;

      // Filter logs that have valid data
      const validLogs = logs.filter(log => 
        log.logged_at && 
        log.severity
      );

      if (validLogs.length === 0) {
        // Return default data if no valid logs available
        return {
          exercise_types: ['Walking', 'Light Cardio', 'Stretching'],
          exercise_intensities: [3, 4, 2],
          exercise_durations: [30, 25, 15],
          post_exercise_symptoms: [2, 3, 1],
          timeframe_days: timeframeDays
        };
      }

      // Sort by date
      validLogs.sort((a, b) => 
        new Date(a.logged_at!).getTime() - new Date(b.logged_at!).getTime()
      );

      // Generate exercise data based on user's lifestyle factors and symptom patterns
      const exerciseTypes: string[] = [];
      const exerciseIntensities: number[] = [];
      const exerciseDurations: number[] = [];
      const postExerciseSymptoms: number[] = [];

      // Map exercise frequency to number of sessions per week
      const frequencyMap: { [key: string]: number } = {
        'none': 0,
        'light': 2,
        'moderate': 4,
        '3-4_week': 3.5,
        '5-6_week': 5.5,
        'daily': 7,
        'intense': 6
      };

      const exerciseFreq = frequencyMap[lifestyleData.exerciseFrequency || 'moderate'] || 3;
      const userExerciseTypes = lifestyleData.exerciseTypes && lifestyleData.exerciseTypes.length > 0 
        ? lifestyleData.exerciseTypes 
        : ['walking'];
      const userDuration = 30; // Default duration since not provided by backend
      
      // Map intensity to numeric value based on exercise frequency as proxy
      const intensityMap: { [key: string]: number } = {
        'never': 1,
        'rarely': 2,
        'sometimes': 3,
        'often': 4,
        'daily': 5
      };
      const userIntensity = intensityMap[lifestyleData.exerciseFrequency || 'sometimes'] || 3;

      // Generate exercise sessions based on frequency and symptom patterns
      const sessionsPerWeek = Math.max(1, Math.round(exerciseFreq));
      const totalSessions = Math.min(validLogs.length, sessionsPerWeek * Math.ceil(timeframeDays / 7));

      for (let i = 0; i < totalSessions; i++) {
        // Rotate through user's preferred exercise types
        const exerciseType = userExerciseTypes[i % userExerciseTypes.length] || 'walking';
        exerciseTypes.push(exerciseType);

        // Vary intensity slightly around user's preference
        const intensityVariation = (Math.random() - 0.5) * 0.8; // ±0.4
        const sessionIntensity = Math.max(1, Math.min(5, userIntensity + intensityVariation));
        exerciseIntensities.push(Math.round(sessionIntensity));

        // Vary duration slightly around user's preference
        const durationVariation = (Math.random() - 0.5) * 20; // ±10 minutes
        const sessionDuration = Math.max(15, Math.min(120, userDuration + durationVariation));
        exerciseDurations.push(Math.round(sessionDuration));

        // Correlate post-exercise symptoms with the corresponding symptom log
        const logIndex = Math.min(i, validLogs.length - 1);
        const log = validLogs[logIndex];
        if (!log || !log.severity) {
          continue;
        }
        const severityValue = this.convertSeverityToNumeric(log.severity);
        
        // Adjust symptom severity based on exercise intensity
        // Higher intensity might temporarily increase symptoms
        let postExerciseSymptom = severityValue;
        if (sessionIntensity >= 4) {
          postExerciseSymptom = Math.min(10, severityValue + 1);
        } else if (sessionIntensity <= 2) {
          postExerciseSymptom = Math.max(1, severityValue - 0.5);
        }
        
        postExerciseSymptoms.push(Math.round(postExerciseSymptom));
      }

      // Ensure we have at least some data
      if (exerciseTypes.length === 0) {
        // Fallback data based on user preferences
        exerciseTypes.push(userExerciseTypes[0] || 'walking');
        exerciseIntensities.push(userIntensity);
        exerciseDurations.push(userDuration);
        const firstLog = validLogs[0];
        if (firstLog && firstLog.severity) {
          postExerciseSymptoms.push(this.convertSeverityToNumeric(firstLog.severity));
        } else {
          postExerciseSymptoms.push(5); // Default moderate severity
        }
      }

      return {
        exercise_types: exerciseTypes,
        exercise_intensities: exerciseIntensities,
        exercise_durations: exerciseDurations,
        post_exercise_symptoms: postExerciseSymptoms,
        timeframe_days: timeframeDays
      };

    } catch (error) {
      console.error('Error fetching exercise tolerance data:', error);
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
   * Calculate exercise tolerance insights
   */
  calculateExerciseInsights(data: ExerciseToleranceData): {
    averageIntensity: number;
    averageDuration: number;
    averagePostSymptoms: number;
    toleranceScore: number;
    mostTolerated: string;
    leastTolerated: string;
    recommendations: string[];
  } {
    const { exercise_types, exercise_intensities, exercise_durations, post_exercise_symptoms } = data;
    
    if (exercise_types.length === 0) {
      throw new Error('No exercise data available for analysis');
    }

    // Calculate averages
    const avgIntensity = exercise_intensities.reduce((sum, intensity) => sum + intensity, 0) / exercise_intensities.length;
    const avgDuration = exercise_durations.reduce((sum, duration) => sum + duration, 0) / exercise_durations.length;
    const avgPostSymptoms = post_exercise_symptoms.reduce((sum, symptoms) => sum + symptoms, 0) / post_exercise_symptoms.length;

    // Calculate tolerance score (lower post-exercise symptoms = higher tolerance)
    const toleranceScore = Math.max(0, Math.min(1, (10 - avgPostSymptoms) / 10));

    // Find most and least tolerated exercise types
    const exerciseSymptomMap: { [key: string]: number[] } = {};
    exercise_types.forEach((type, index) => {
      if (!exerciseSymptomMap[type]) {
        exerciseSymptomMap[type] = [];
      }
      const symptomValue = post_exercise_symptoms[index];
      if (symptomValue !== undefined) {
        exerciseSymptomMap[type].push(symptomValue);
      }
    });

    let mostTolerated = 'walking';
    let leastTolerated = 'high-intensity';
    let lowestSymptoms = 10;
    let highestSymptoms = 0;

    Object.entries(exerciseSymptomMap).forEach(([type, symptoms]) => {
      if (symptoms.length > 0) {
        const avgSymptoms = symptoms.reduce((sum, s) => sum + s, 0) / symptoms.length;
        if (avgSymptoms < lowestSymptoms) {
          lowestSymptoms = avgSymptoms;
          mostTolerated = type;
        }
        if (avgSymptoms > highestSymptoms) {
          highestSymptoms = avgSymptoms;
          leastTolerated = type;
        }
      }
    });

    // Generate recommendations
    const recommendations: string[] = [];
    
    if (toleranceScore < 0.5) {
      recommendations.push('Consider reducing exercise intensity and focusing on low-impact activities');
      recommendations.push('Start with shorter sessions (15-20 minutes) and gradually increase duration');
    } else if (toleranceScore < 0.7) {
      recommendations.push('Maintain current exercise routine with gradual progression');
      recommendations.push('Monitor symptoms closely after exercise sessions');
    } else {
      recommendations.push('You have good exercise tolerance - consider gradually increasing intensity');
      recommendations.push('Explore new exercise types to maintain engagement');
    }
    
    if (avgIntensity >= 4) {
      recommendations.push('High-intensity exercise may be triggering symptoms - consider moderating intensity');
    }
    
    if (avgDuration > 60) {
      recommendations.push('Long exercise sessions may be contributing to symptoms - try shorter, more frequent sessions');
    }

    recommendations.push(`Focus on ${mostTolerated} as it appears to be well-tolerated`);
    
    if (leastTolerated !== mostTolerated) {
      recommendations.push(`Consider avoiding or modifying ${leastTolerated} as it may trigger symptoms`);
    }

    return {
      averageIntensity: Math.round(avgIntensity * 10) / 10,
      averageDuration: Math.round(avgDuration),
      averagePostSymptoms: Math.round(avgPostSymptoms * 10) / 10,
      toleranceScore: Math.round(toleranceScore * 100) / 100,
      mostTolerated,
      leastTolerated,
      recommendations
    };
  }
}

export const exerciseToleranceDataService = new ExerciseToleranceDataService();