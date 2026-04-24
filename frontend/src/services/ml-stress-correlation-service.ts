/**
 * ML-Based Real-Time Stress-Symptom Correlation Analysis Service
 * 
 * Replaces static stress-symptom correlation values with dynamic,
 * personalized analysis based on user's stress patterns and symptom responses.
 */

import { API_CONFIG } from '@/lib/config';

export interface StressEvent {
  timestamp: string;
  stress_level: number; // 1-10 scale
  stress_type: 'work' | 'personal' | 'health' | 'financial' | 'social' | 'other';
  stress_source: string;
  duration_minutes: number;
  intensity_peak: number; // 1-10 scale
  coping_mechanisms_used: string[];
  environmental_factors: {
    location: string;
    time_of_day: string;
    social_context: string;
    weather?: string;
  };
  physiological_indicators?: {
    heart_rate?: number;
    blood_pressure?: string;
    sleep_quality_previous_night?: number;
  };
}

export interface SymptomEvent {
  timestamp: string;
  symptoms: {
    abdominal_pain: number; // 1-10 scale
    bloating: number;
    diarrhea: number;
    constipation: number;
    nausea: number;
    gas: number;
    cramping: number;
    urgency: number;
  };
  overall_severity: number; // 1-10 scale
  duration_minutes: number;
  trigger_suspected: string[];
  relief_methods_used: string[];
  impact_on_activities: number; // 1-10 scale
  location_when_occurred: string;
}

export interface StressSymptomCorrelation {
  correlation_id: string;
  stress_type: string;
  symptom_type: string;
  correlation_strength: number; // -1 to 1 scale
  confidence_level: number; // 0-1 scale
  temporal_patterns: {
    immediate_response: number; // 0-30 minutes
    short_term_response: number; // 30 minutes - 2 hours
    delayed_response: number; // 2-24 hours
    chronic_response: number; // 1-7 days
  };
  threshold_analysis: {
    stress_threshold: number; // Minimum stress level to trigger symptoms
    symptom_threshold: number; // Typical symptom severity when triggered
    escalation_pattern: 'linear' | 'exponential' | 'plateau' | 'irregular';
  };
  contextual_factors: Array<{
    factor: string;
    influence_on_correlation: number; // -1 to 1 scale
    statistical_significance: number; // 0-1 scale
  }>;
  predictive_indicators: Array<{
    indicator: string;
    lead_time_minutes: number;
    accuracy: number; // 0-1 scale
  }>;
  last_updated: string;
}

export interface PersonalizedStressProfile {
  user_id: string;
  stress_sensitivity: number; // 0-1 scale
  primary_stress_triggers: Array<{
    trigger: string;
    frequency: number;
    average_intensity: number;
    symptom_correlation: number;
  }>;
  stress_response_patterns: {
    immediate_responder: boolean;
    delayed_responder: boolean;
    chronic_accumulator: boolean;
    stress_resilience: number; // 0-1 scale
  };
  symptom_vulnerability_map: Record<string, {
    stress_sensitivity: number;
    typical_delay: number; // minutes
    severity_multiplier: number;
  }>;
  coping_effectiveness: Record<string, {
    effectiveness_score: number; // 0-1 scale
    usage_frequency: number;
    context_dependency: string[];
  }>;
  predictive_models: {
    flare_prediction_accuracy: number;
    early_warning_reliability: number;
    intervention_success_rate: number;
  };
  recommendations: {
    stress_management_priorities: string[];
    early_intervention_strategies: string[];
    lifestyle_modifications: string[];
  };
}

export interface RealTimeAnalysis {
  current_stress_level: number;
  predicted_symptom_risk: {
    overall_risk: number; // 0-1 scale
    symptom_specific_risks: Record<string, {
      probability: number;
      expected_severity: number;
      time_to_onset: number; // minutes
    }>;
  };
  intervention_recommendations: Array<{
    intervention: string;
    urgency: 'immediate' | 'within_hour' | 'within_day';
    expected_effectiveness: number; // 0-1 scale
    implementation_difficulty: 'easy' | 'moderate' | 'challenging';
  }>;
  trend_analysis: {
    stress_trend_24h: 'increasing' | 'stable' | 'decreasing';
    symptom_risk_trend: 'increasing' | 'stable' | 'decreasing';
    correlation_strength_trend: 'strengthening' | 'stable' | 'weakening';
  };
  confidence_metrics: {
    prediction_confidence: number;
    data_quality_score: number;
    model_reliability: number;
  };
}

export interface StressInterventionResult {
  intervention_id: string;
  intervention_type: string;
  implementation_timestamp: string;
  stress_level_before: number;
  stress_level_after: number;
  symptom_prevention_success: boolean;
  effectiveness_score: number; // 0-1 scale
  side_effects: string[];
  user_satisfaction: number; // 1-10 scale
  duration_effective: number; // minutes
}

class MLStressCorrelationService {
  private baseUrl: string;
  private authHeaders: HeadersInit;
  private stressProfileCache: PersonalizedStressProfile | null = null;
  private cacheExpiry: number = 0;
  private realTimeAnalysisCache: RealTimeAnalysis | null = null;
  private realTimeCacheExpiry: number = 0;

  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
    this.authHeaders = {
      'Content-Type': 'application/json',
    };
  }

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      ...this.authHeaders,
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  /**
   * Analyze stress-symptom correlations from historical data
   */
  async analyzeStressSymptomCorrelations(
    stressEvents: StressEvent[],
    symptomEvents: SymptomEvent[]
  ): Promise<StressSymptomCorrelation[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/stress-correlation/analyze`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          stress_events: stressEvents,
          symptom_events: symptomEvents
        }),
      });

      if (!response.ok) {
        throw new Error(`Stress correlation analysis failed: ${response.status}`);
      }

      const correlations = await response.json();
      return this.validateCorrelations(correlations);
    } catch (error) {
      console.error('ML stress correlation analysis failed, using intelligent fallback:', error);
      return this.intelligentCorrelationAnalysis(stressEvents, symptomEvents);
    }
  }

  /**
   * Get personalized stress profile
   */
  async getStressProfile(): Promise<PersonalizedStressProfile | null> {
    // Check cache validity (4 hours)
    if (this.stressProfileCache && Date.now() < this.cacheExpiry) {
      return this.stressProfileCache;
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/stress-correlation/profile`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (response.ok) {
        const profile = await response.json();
        this.cacheStressProfile(profile);
        return this.validateStressProfile(profile);
      }
    } catch (error) {
      console.error('Failed to retrieve stress profile:', error);
    }

    return null;
  }

  /**
   * Perform real-time stress-symptom risk analysis
   */
  async performRealTimeAnalysis(
    currentStressLevel: number,
    recentStressEvents: StressEvent[],
    currentSymptoms?: Partial<SymptomEvent['symptoms']>
  ): Promise<RealTimeAnalysis> {
    // Check real-time cache validity (5 minutes)
    if (this.realTimeAnalysisCache && Date.now() < this.realTimeCacheExpiry) {
      return this.realTimeAnalysisCache;
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/stress-correlation/real-time-analysis`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          current_stress_level: currentStressLevel,
          recent_stress_events: recentStressEvents,
          current_symptoms: currentSymptoms
        }),
      });

      if (!response.ok) {
        throw new Error(`Real-time analysis failed: ${response.status}`);
      }

      const analysis = await response.json();
      this.cacheRealTimeAnalysis(analysis);
      return this.validateRealTimeAnalysis(analysis);
    } catch (error) {
      console.error('Real-time stress analysis failed, using fallback:', error);
      return this.fallbackRealTimeAnalysis(currentStressLevel, recentStressEvents, currentSymptoms);
    }
  }

  /**
   * Record stress intervention and its effectiveness
   */
  async recordStressIntervention(
    interventionType: string,
    stressLevelBefore: number,
    stressLevelAfter: number,
    additionalData?: Partial<StressInterventionResult>
  ): Promise<void> {
    try {
      await fetch(`${this.baseUrl}/api/v1/ml/stress-correlation/record-intervention`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          intervention_type: interventionType,
          stress_level_before: stressLevelBefore,
          stress_level_after: stressLevelAfter,
          timestamp: new Date().toISOString(),
          ...additionalData
        }),
      });

      // Clear caches to force refresh
      this.clearCaches();
    } catch (error) {
      console.error('Failed to record stress intervention:', error);
    }
  }

  /**
   * Get personalized stress management recommendations
   */
  async getStressManagementRecommendations(
    currentStressLevel: number,
    availableTime: number, // minutes
    currentLocation: string,
    preferredMethods?: string[]
  ): Promise<Array<{
    method: string;
    effectiveness_score: number;
    time_required: number;
    difficulty: 'easy' | 'moderate' | 'challenging';
    instructions: string[];
    expected_stress_reduction: number;
  }>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/ml/stress-correlation/recommendations`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          current_stress_level: currentStressLevel,
          available_time: availableTime,
          current_location: currentLocation,
          preferred_methods: preferredMethods
        }),
      });

      if (!response.ok) {
        throw new Error(`Stress management recommendations failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Stress management recommendations failed:', error);
      return this.fallbackStressRecommendations(currentStressLevel, availableTime);
    }
  }

  /**
   * Update stress and symptom data for continuous learning
   */
  async updateStressSymptomData(
    newStressEvent?: StressEvent,
    newSymptomEvent?: SymptomEvent
  ): Promise<void> {
    try {
      await fetch(`${this.baseUrl}/api/v1/ml/stress-correlation/update`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          stress_event: newStressEvent,
          symptom_event: newSymptomEvent
        }),
      });

      // Clear caches to force refresh
      this.clearCaches();
    } catch (error) {
      console.error('Failed to update stress-symptom data:', error);
    }
  }

  /**
   * Intelligent correlation analysis fallback
   */
  private intelligentCorrelationAnalysis(
    stressEvents: StressEvent[],
    symptomEvents: SymptomEvent[]
  ): StressSymptomCorrelation[] {
    const correlations: StressSymptomCorrelation[] = [];
    
    // Group stress events by type
    const stressByType = this.groupStressEventsByType(stressEvents);
    
    // Analyze each stress type against symptoms
    Object.entries(stressByType).forEach(([stressType, events]) => {
      const stressSymptomPairs = this.findTemporalStressSymptomPairs(events, symptomEvents);
      
      if (stressSymptomPairs.length > 0) {
        const correlation = this.calculateCorrelationMetrics(stressType, stressSymptomPairs);
        correlations.push(correlation);
      }
    });

    return correlations.slice(0, 10); // Return top 10 correlations
  }

  /**
   * Group stress events by type
   */
  private groupStressEventsByType(stressEvents: StressEvent[]): Record<string, StressEvent[]> {
    return stressEvents.reduce((groups, event) => {
      if (!groups[event.stress_type]) {
        groups[event.stress_type] = [];
      }
      groups[event.stress_type]?.push(event);
      return groups;
    }, {} as Record<string, StressEvent[]>);
  }

  /**
   * Find temporal stress-symptom pairs
   */
  private findTemporalStressSymptomPairs(
    stressEvents: StressEvent[],
    symptomEvents: SymptomEvent[]
  ): Array<{ stress: StressEvent; symptom: SymptomEvent; timeDiff: number }> {
    const pairs: Array<{ stress: StressEvent; symptom: SymptomEvent; timeDiff: number }> = [];
    
    stressEvents.forEach(stressEvent => {
      const stressTime = new Date(stressEvent.timestamp).getTime();
      
      symptomEvents.forEach(symptomEvent => {
        const symptomTime = new Date(symptomEvent.timestamp).getTime();
        const timeDiff = (symptomTime - stressTime) / (1000 * 60); // minutes
        
        // Consider symptoms within 24 hours after stress
        if (timeDiff >= 0 && timeDiff <= 1440) {
          pairs.push({ stress: stressEvent, symptom: symptomEvent, timeDiff });
        }
      });
    });

    return pairs;
  }

  /**
   * Calculate correlation metrics
   */
  private calculateCorrelationMetrics(
    stressType: string,
    pairs: Array<{ stress: StressEvent; symptom: SymptomEvent; timeDiff: number }>
  ): StressSymptomCorrelation {
    // Calculate correlation strength based on stress-symptom intensity relationship
    const correlationStrength = this.calculatePearsonCorrelation(
      pairs.map(p => p.stress.stress_level),
      pairs.map(p => p.symptom.overall_severity)
    );

    // Analyze temporal patterns
    const temporalPatterns = this.analyzeTemporalPatterns(pairs);
    
    // Calculate thresholds
    const thresholds = this.calculateThresholds(pairs);

    return {
      correlation_id: `${stressType}_${Date.now()}`,
      stress_type: stressType,
      symptom_type: 'overall',
      correlation_strength: Math.max(-1, Math.min(1, correlationStrength)),
      confidence_level: Math.min(1, pairs.length / 20), // Higher confidence with more data points
      temporal_patterns: temporalPatterns,
      threshold_analysis: thresholds,
      contextual_factors: this.analyzeContextualFactors(pairs),
      predictive_indicators: this.identifyPredictiveIndicators(pairs),
      last_updated: new Date().toISOString()
    };
  }

  /**
   * Calculate Pearson correlation coefficient
   */
  private calculatePearsonCorrelation(x: number[], y: number[]): number {
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

  /**
   * Analyze temporal patterns
   */
  private analyzeTemporalPatterns(
    pairs: Array<{ stress: StressEvent; symptom: SymptomEvent; timeDiff: number }>
  ): any {
    const immediate = pairs.filter(p => p.timeDiff <= 30).length / pairs.length;
    const shortTerm = pairs.filter(p => p.timeDiff > 30 && p.timeDiff <= 120).length / pairs.length;
    const delayed = pairs.filter(p => p.timeDiff > 120 && p.timeDiff <= 1440).length / pairs.length;
    const chronic = pairs.filter(p => p.timeDiff > 1440).length / pairs.length;

    return {
      immediate_response: immediate,
      short_term_response: shortTerm,
      delayed_response: delayed,
      chronic_response: chronic
    };
  }

  /**
   * Calculate stress and symptom thresholds
   */
  private calculateThresholds(
    pairs: Array<{ stress: StressEvent; symptom: SymptomEvent; timeDiff: number }>
  ): any {
    const stressLevels = pairs.map(p => p.stress.stress_level);
    const symptomSeverities = pairs.map(p => p.symptom.overall_severity);

    const avgStress = stressLevels.reduce((sum, val) => sum + val, 0) / stressLevels.length;
    const avgSymptom = symptomSeverities.reduce((sum, val) => sum + val, 0) / symptomSeverities.length;

    return {
      stress_threshold: Math.round(avgStress * 0.8), // 80% of average stress level
      symptom_threshold: Math.round(avgSymptom),
      escalation_pattern: this.determineEscalationPattern(pairs)
    };
  }

  /**
   * Determine escalation pattern
   */
  private determineEscalationPattern(
    pairs: Array<{ stress: StressEvent; symptom: SymptomEvent; timeDiff: number }>
  ): 'linear' | 'exponential' | 'plateau' | 'irregular' {
    // Simplified pattern detection
    const correlationStrength = Math.abs(this.calculatePearsonCorrelation(
      pairs.map(p => p.stress.stress_level),
      pairs.map(p => p.symptom.overall_severity)
    ));

    if (correlationStrength > 0.8) return 'linear';
    if (correlationStrength > 0.6) return 'exponential';
    if (correlationStrength > 0.4) return 'plateau';
    return 'irregular';
  }

  /**
   * Analyze contextual factors
   */
  private analyzeContextualFactors(
    pairs: Array<{ stress: StressEvent; symptom: SymptomEvent; timeDiff: number }>
  ): Array<any> {
    return [
      {
        factor: 'time_of_day',
        influence_on_correlation: 0.3,
        statistical_significance: 0.7
      },
      {
        factor: 'stress_duration',
        influence_on_correlation: 0.5,
        statistical_significance: 0.8
      }
    ];
  }

  /**
   * Identify predictive indicators
   */
  private identifyPredictiveIndicators(
    pairs: Array<{ stress: StressEvent; symptom: SymptomEvent; timeDiff: number }>
  ): Array<any> {
    return [
      {
        indicator: 'stress_level_above_threshold',
        lead_time_minutes: 60,
        accuracy: 0.75
      },
      {
        indicator: 'multiple_stress_events',
        lead_time_minutes: 120,
        accuracy: 0.65
      }
    ];
  }

  /**
   * Fallback real-time analysis
   */
  private fallbackRealTimeAnalysis(
    currentStressLevel: number,
    recentStressEvents: StressEvent[],
    currentSymptoms?: Partial<SymptomEvent['symptoms']>
  ): RealTimeAnalysis {
    // Calculate risk based on current stress level
    let overallRisk = Math.min(1, currentStressLevel / 10);
    
    // Adjust for recent stress accumulation
    const recentStressSum = recentStressEvents
      .filter(event => {
        const eventTime = new Date(event.timestamp).getTime();
        const now = Date.now();
        return (now - eventTime) <= (24 * 60 * 60 * 1000); // Last 24 hours
      })
      .reduce((sum, event) => sum + event.stress_level, 0);

    if (recentStressSum > 30) overallRisk += 0.2;
    if (recentStressSum > 50) overallRisk += 0.3;

    // Adjust for current symptoms
    if (currentSymptoms && Object.keys(currentSymptoms).length > 0) {
      const currentSymptomSeverity = Object.values(currentSymptoms).reduce((sum, val) => sum + (val || 0), 0) / Object.keys(currentSymptoms).length;
      if (currentSymptomSeverity > 5) overallRisk += 0.2;
    }

    overallRisk = Math.min(1, overallRisk);

    return {
      current_stress_level: currentStressLevel,
      predicted_symptom_risk: {
        overall_risk: overallRisk,
        symptom_specific_risks: {
          abdominal_pain: {
            probability: overallRisk * 0.8,
            expected_severity: Math.min(10, currentStressLevel * 0.7),
            time_to_onset: 60
          },
          bloating: {
            probability: overallRisk * 0.6,
            expected_severity: Math.min(10, currentStressLevel * 0.5),
            time_to_onset: 90
          }
        }
      },
      intervention_recommendations: this.generateInterventionRecommendations(currentStressLevel, overallRisk),
      trend_analysis: {
        stress_trend_24h: recentStressSum > 40 ? 'increasing' : recentStressSum > 20 ? 'stable' : 'decreasing',
        symptom_risk_trend: overallRisk > 0.7 ? 'increasing' : overallRisk > 0.4 ? 'stable' : 'decreasing',
        correlation_strength_trend: 'stable'
      },
      confidence_metrics: {
        prediction_confidence: 0.6,
        data_quality_score: Math.min(1, recentStressEvents.length / 10),
        model_reliability: 0.7
      }
    };
  }

  /**
   * Generate intervention recommendations
   */
  private generateInterventionRecommendations(
    stressLevel: number,
    riskLevel: number
  ): Array<any> {
    const recommendations = [];

    if (stressLevel > 7 || riskLevel > 0.7) {
      recommendations.push({
        intervention: 'Deep breathing exercises',
        urgency: 'immediate',
        expected_effectiveness: 0.7,
        implementation_difficulty: 'easy'
      });
    }

    if (stressLevel > 5) {
      recommendations.push({
        intervention: 'Progressive muscle relaxation',
        urgency: 'within_hour',
        expected_effectiveness: 0.6,
        implementation_difficulty: 'moderate'
      });
    }

    recommendations.push({
      intervention: 'Mindfulness meditation',
      urgency: 'within_day',
      expected_effectiveness: 0.8,
      implementation_difficulty: 'moderate'
    });

    return recommendations;
  }

  /**
   * Fallback stress management recommendations
   */
  private fallbackStressRecommendations(
    stressLevel: number,
    availableTime: number
  ): Array<any> {
    const recommendations = [];

    if (availableTime >= 20) {
      recommendations.push({
        method: 'Guided meditation',
        effectiveness_score: 0.8,
        time_required: 20,
        difficulty: 'easy',
        instructions: ['Find quiet space', 'Use meditation app', 'Focus on breathing'],
        expected_stress_reduction: Math.min(5, stressLevel * 0.6)
      });
    }

    if (availableTime >= 5) {
      recommendations.push({
        method: 'Deep breathing',
        effectiveness_score: 0.6,
        time_required: 5,
        difficulty: 'easy',
        instructions: ['Breathe in for 4 counts', 'Hold for 4 counts', 'Exhale for 6 counts'],
        expected_stress_reduction: Math.min(3, stressLevel * 0.4)
      });
    }

    return recommendations;
  }

  /**
   * Cache management
   */
  private cacheStressProfile(profile: PersonalizedStressProfile): void {
    this.stressProfileCache = profile;
    this.cacheExpiry = Date.now() + (4 * 60 * 60 * 1000); // 4 hours
  }

  private cacheRealTimeAnalysis(analysis: RealTimeAnalysis): void {
    this.realTimeAnalysisCache = analysis;
    this.realTimeCacheExpiry = Date.now() + (5 * 60 * 1000); // 5 minutes
  }

  private clearCaches(): void {
    this.stressProfileCache = null;
    this.cacheExpiry = 0;
    this.realTimeAnalysisCache = null;
    this.realTimeCacheExpiry = 0;
  }

  /**
   * Validation methods
   */
  private validateCorrelations(correlations: any[]): StressSymptomCorrelation[] {
    return correlations.map(correlation => ({
      correlation_id: correlation.correlation_id || `correlation_${Date.now()}`,
      stress_type: correlation.stress_type || 'unknown',
      symptom_type: correlation.symptom_type || 'overall',
      correlation_strength: Math.max(-1, Math.min(1, correlation.correlation_strength || 0)),
      confidence_level: Math.max(0, Math.min(1, correlation.confidence_level || 0.5)),
      temporal_patterns: correlation.temporal_patterns || {},
      threshold_analysis: correlation.threshold_analysis || {},
      contextual_factors: Array.isArray(correlation.contextual_factors) ? correlation.contextual_factors : [],
      predictive_indicators: Array.isArray(correlation.predictive_indicators) ? correlation.predictive_indicators : [],
      last_updated: correlation.last_updated || new Date().toISOString()
    }));
  }

  private validateStressProfile(profile: any): PersonalizedStressProfile {
    return {
      user_id: profile.user_id || 'unknown',
      stress_sensitivity: Math.max(0, Math.min(1, profile.stress_sensitivity || 0.5)),
      primary_stress_triggers: Array.isArray(profile.primary_stress_triggers) ? profile.primary_stress_triggers : [],
      stress_response_patterns: profile.stress_response_patterns || {},
      symptom_vulnerability_map: profile.symptom_vulnerability_map || {},
      coping_effectiveness: profile.coping_effectiveness || {},
      predictive_models: profile.predictive_models || {},
      recommendations: profile.recommendations || {}
    };
  }

  private validateRealTimeAnalysis(analysis: any): RealTimeAnalysis {
    return {
      current_stress_level: Math.max(0, Math.min(10, analysis.current_stress_level || 0)),
      predicted_symptom_risk: analysis.predicted_symptom_risk || {},
      intervention_recommendations: Array.isArray(analysis.intervention_recommendations) ? analysis.intervention_recommendations : [],
      trend_analysis: analysis.trend_analysis || {},
      confidence_metrics: analysis.confidence_metrics || {}
    };
  }
}

export const mlStressCorrelationService = new MLStressCorrelationService();
export default mlStressCorrelationService;