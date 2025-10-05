'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  mlService,
  ModelInfoResponse,
  SeverityPredictionResponse,
  FlareupPredictionResponse,
  MedicationEffectivenessResponse,
  DietaryTriggerResponse,
  StressSymptomCorrelationResponse,
  SleepQualityImpactResponse,
  ExerciseToleranceResponse,
  SymptomProgressionResponse,
  TreatmentResponseResponse,
  MultimodalPredictionResponse
} from '@/services/ml-service';
import { toast } from 'react-hot-toast';
import { ProtectedRoute } from '@/components/protected-route';
import { formatSmartNumber, formatConfidence, formatProbability } from '@/lib/number-formatting';

export default function TestMLPage() {
  const [predictions, setPredictions] = useState<any>(null);
  const [realtimePredictions, setRealtimePredictions] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [modelInfo, setModelInfo] = useState<ModelInfoResponse | null>(null);
  const [severityPrediction, setSeverityPrediction] = useState<SeverityPredictionResponse | null>(null);
  const [flareupPrediction, setFlareupPrediction] = useState<FlareupPredictionResponse | null>(null);
  const [medicationEffectiveness, setMedicationEffectiveness] = useState<MedicationEffectivenessResponse | null>(null);
  const [dietaryTriggers, setDietaryTriggers] = useState<DietaryTriggerResponse | null>(null);
  const [stressCorrelation, setStressCorrelation] = useState<StressSymptomCorrelationResponse | null>(null);
  const [sleepImpact, setSleepImpact] = useState<SleepQualityImpactResponse | null>(null);
  const [exerciseTolerance, setExerciseTolerance] = useState<ExerciseToleranceResponse | null>(null);
  const [symptomProgression, setSymptomProgression] = useState<SymptomProgressionResponse | null>(null);
  const [treatmentResponse, setTreatmentResponse] = useState<TreatmentResponseResponse | null>(null);
  const [multimodalPrediction, setMultimodalPrediction] = useState<MultimodalPredictionResponse | null>(null);
  const [loading, setLoading] = useState<{ [key: string]: boolean }>({});

  const testPredictions = async () => {
    setLoading(prev => ({ ...prev, predictions: true }));
    try {
      const result = await mlService.getPredictions({ 
        timeframe: 'week', 
        include_recommendations: true 
      });
      setPredictions(result);
      toast.success('Predictions loaded successfully!');
    } catch (error) {
      console.error('Error testing predictions:', error);
      toast.error('Failed to load predictions');
    } finally {
      setLoading(prev => ({ ...prev, predictions: false }));
    }
  };

  const testRealtimePredictions = async () => {
    setLoading(prev => ({ ...prev, realtime: true }));
    try {
      const result = await mlService.getRealtimePredictions();
      setRealtimePredictions(result);
      toast.success('Real-time predictions loaded successfully!');
    } catch (error) {
      console.error('Error testing real-time predictions:', error);
      toast.error('Failed to load real-time predictions');
    } finally {
      setLoading(prev => ({ ...prev, realtime: false }));
    }
  };

  const testRecommendations = async () => {
    setLoading(prev => ({ ...prev, recommendations: true }));
    try {
      const result = await mlService.getPersonalizedRecommendations();
      setRecommendations(result);
      toast.success('Personalized recommendations loaded successfully');
    } catch (error) {
      console.error('Error testing recommendations:', error);
      toast.error('Failed to load personalized recommendations');
    } finally {
      setLoading(prev => ({ ...prev, recommendations: false }));
    }
  };

  const testModelInfo = async () => {
    setLoading(prev => ({ ...prev, modelInfo: true }));
    try {
      const result = await mlService.getModelInfo();
      setModelInfo(result);
      toast.success('Model info loaded successfully');
    } catch (error) {
      console.error('Error testing model info:', error);
      toast.error('Failed to load model info');
    } finally {
      setLoading(prev => ({ ...prev, modelInfo: false }));
    }
  };

  const testSeverityPrediction = async () => {
    setLoading(prev => ({ ...prev, severity: true }));
    try {
      const result = await mlService.predictSeverity({
        symptoms: {
          pain_level: 7,
          bloating: 6,
          diarrhea: 5,
          constipation: 2,
          nausea: 3,
          fatigue: 6
        },
        context: { stress_level: 7, sleep_quality: 5 }
      });
      setSeverityPrediction(result);
      toast.success('Severity prediction completed');
    } catch (error) {
      console.error('Error testing severity prediction:', error);
      toast.error('Failed to predict severity');
    } finally {
      setLoading(prev => ({ ...prev, severity: false }));
    }
  };

  const testFlareupPrediction = async () => {
    setLoading(prev => ({ ...prev, flareup: true }));
    try {
      const result = await mlService.predictFlareup({
        recent_symptoms: [
          {
            date: new Date().toISOString().split('T')[0] || '2024-01-01',
            symptoms: {
              abdominal_pain: 8,
              bloating: 7,
              diarrhea: 5,
              constipation: 2
            },
            triggers: ['stress', 'spicy food']
          }
        ],
        lifestyle_factors: {
          stress_level: 8,
          sleep_quality: 4,
          exercise_frequency: 2,
          diet_adherence: 6
        },
        prediction_horizon: 7
      });
      setFlareupPrediction(result);
      toast.success('Flareup prediction completed');
    } catch (error) {
      console.error('Error testing flareup prediction:', error);
      toast.error('Failed to predict flareup');
    } finally {
      setLoading(prev => ({ ...prev, flareup: false }));
    }
  };

  const testMedicationEffectiveness = async () => {
    setLoading(prev => ({ ...prev, medication: true }));
    try {
      const result = await mlService.predictMedicationEffectiveness({
        medication_history: [
          {
            medication: 'loperamide',
            dosage: '2mg',
            frequency: 'twice daily',
            adherence_rate: 0.85,
            effectiveness_score: 7,
            side_effects: ['mild drowsiness'],
            duration_days: 7
          }
        ],
        current_symptoms: {
          abdominal_pain: 6,
          diarrhea: 4,
          bloating: 5,
          constipation: 2,
          nausea: 3
        },
        user_profile: {
          age: 35,
          weight: 70,
          ibs_type: 'IBS-D',
          comorbidities: ['anxiety']
        },
        prediction_period: 14
      });
      setMedicationEffectiveness(result);
      toast.success('Medication effectiveness prediction completed');
    } catch (error) {
      console.error('Error testing medication effectiveness:', error);
      toast.error('Failed to predict medication effectiveness');
    } finally {
      setLoading(prev => ({ ...prev, medication: false }));
    }
  };

  const testDietaryTriggers = async () => {
    setLoading(prev => ({ ...prev, dietary: true }));
    try {
      const result = await mlService.predictDietaryTriggers({
        foods_consumed: ['dairy', 'gluten', 'spicy_food'],
        meal_timing: ['evening', 'late_night'],
        portion_sizes: ['large', 'medium'],
        timeframe_hours: 24
      });
      setDietaryTriggers(result);
      toast.success('Dietary triggers prediction completed');
    } catch (error) {
      console.error('Error testing dietary triggers:', error);
      toast.error('Failed to predict dietary triggers');
    } finally {
      setLoading(prev => ({ ...prev, dietary: false }));
    }
  };

  const testStressCorrelation = async () => {
    setLoading(prev => ({ ...prev, stress: true }));
    try {
      const result = await mlService.predictStressSymptomCorrelation({
        stress_levels: { day1: 8, day2: 7, day3: 9, day4: 6, day5: 8 },
        symptoms: { day1: 7, day2: 6, day3: 8, day4: 5, day5: 7 },
        timeframe_days: 7
      });
      setStressCorrelation(result);
      toast.success('Stress correlation prediction completed');
    } catch (error) {
      console.error('Error testing stress correlation:', error);
      toast.error('Failed to predict stress correlation');
    } finally {
      setLoading(prev => ({ ...prev, stress: false }));
    }
  };

  const testSleepImpact = async () => {
    setLoading(prev => ({ ...prev, sleep: true }));
    try {
      const result = await mlService.predictSleepQualityImpact({
        sleep_hours: [5, 6, 7, 5, 6],
        sleep_quality_scores: [3, 4, 6, 3, 4],
        symptom_severity: [7, 6, 5, 8, 7],
        timeframe_days: 7
      });
      setSleepImpact(result);
      toast.success('Sleep impact prediction completed');
    } catch (error) {
      console.error('Error testing sleep impact:', error);
      toast.error('Failed to predict sleep impact');
    } finally {
      setLoading(prev => ({ ...prev, sleep: false }));
    }
  };

  const testExerciseTolerance = async () => {
    setLoading(prev => ({ ...prev, exercise: true }));
    try {
      const result = await mlService.predictExerciseTolerance({
        exercise_types: ['cardio', 'yoga', 'walking'],
        exercise_intensities: [6, 3, 4],
        exercise_durations: [30, 45, 60],
        post_exercise_symptoms: [5, 2, 3]
      });
      setExerciseTolerance(result);
      toast.success('Exercise tolerance prediction completed');
    } catch (error) {
      console.error('Error testing exercise tolerance:', error);
      toast.error('Failed to predict exercise tolerance');
    } finally {
      setLoading(prev => ({ ...prev, exercise: false }));
    }
  };

  const testSymptomProgression = async () => {
    setLoading(prev => ({ ...prev, progression: true }));
    try {
      const result = await mlService.predictSymptomProgression({
        historical_symptoms: [
          { date: '2024-01-01', severity: 6, type: 'abdominal_pain' },
          { date: '2024-01-02', severity: 7, type: 'bloating' },
          { date: '2024-01-03', severity: 5, type: 'diarrhea' }
        ],
        timeframe_days: 7
      });
      setSymptomProgression(result);
      toast.success('Symptom progression prediction completed');
    } catch (error) {
      console.error('Error testing symptom progression:', error);
      toast.error('Failed to predict symptom progression');
    } finally {
      setLoading(prev => ({ ...prev, progression: false }));
    }
  };

  const testTreatmentResponse = async () => {
    setLoading(prev => ({ ...prev, treatment: true }));
    try {
      const result = await mlService.predictTreatmentResponse({
        treatment_type: 'dietary_modification',
        treatment_duration: 30,
        baseline_symptoms: {
          pain_level: 7,
          bloating: 6,
          bowel_movement_frequency: 4
        }
      });
      setTreatmentResponse(result);
      toast.success('Treatment response prediction completed');
    } catch (error) {
      console.error('Error testing treatment response:', error);
      toast.error('Failed to predict treatment response');
    } finally {
      setLoading(prev => ({ ...prev, treatment: false }));
    }
  };

  const testMultimodalPrediction = async () => {
    setLoading(prev => ({ ...prev, multimodal: true }));
    try {
      const result = await mlService.predictMultimodal(30);
      setMultimodalPrediction(result);
      toast.success('Multimodal prediction completed');
    } catch (error) {
      console.error('Error testing multimodal prediction:', error);
      toast.error('Failed to complete multimodal prediction');
    } finally {
      setLoading(prev => ({ ...prev, multimodal: false }));
    }
  };

  const testAllEndpoints = async () => {
    await Promise.all([
      testPredictions(),
      testRealtimePredictions(),
      testRecommendations(),
      testModelInfo(),
      testSeverityPrediction(),
      testFlareupPrediction(),
      testMedicationEffectiveness(),
      testDietaryTriggers(),
      testStressCorrelation(),
      testSleepImpact(),
      testExerciseTolerance(),
      testSymptomProgression(),
      testTreatmentResponse(),
      testMultimodalPrediction()
    ]);
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">ML Integration Test</h1>
            <p className="text-gray-600">Test all ML endpoints and verify integration</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2 justify-center">
            <Button onClick={testPredictions} disabled={loading['predictions']} size="sm">
              {loading['predictions'] ? 'Loading...' : 'Predictions'}
            </Button>
            <Button onClick={testRealtimePredictions} disabled={loading['realtime']} size="sm">
              {loading['realtime'] ? 'Loading...' : 'Real-time'}
            </Button>
            <Button onClick={testRecommendations} disabled={loading['recommendations']} size="sm">
              {loading['recommendations'] ? 'Loading...' : 'Recommendations'}
            </Button>
            <Button onClick={testModelInfo} disabled={loading['modelInfo']} size="sm">
              {loading['modelInfo'] ? 'Loading...' : 'Model Info'}
            </Button>
            <Button onClick={testSeverityPrediction} disabled={loading['severity']} size="sm">
              {loading['severity'] ? 'Loading...' : 'Severity'}
            </Button>
            <Button onClick={testFlareupPrediction} disabled={loading['flareup']} size="sm">
              {loading['flareup'] ? 'Loading...' : 'Flareup'}
            </Button>
            <Button onClick={testMedicationEffectiveness} disabled={loading['medication']} size="sm">
              {loading['medication'] ? 'Loading...' : 'Medication'}
            </Button>
            <Button onClick={testDietaryTriggers} disabled={loading['dietary']} size="sm">
              {loading['dietary'] ? 'Loading...' : 'Dietary'}
            </Button>
            <Button onClick={testStressCorrelation} disabled={loading['stress']} size="sm">
              {loading['stress'] ? 'Loading...' : 'Stress'}
            </Button>
            <Button onClick={testSleepImpact} disabled={loading['sleep']} size="sm">
              {loading['sleep'] ? 'Loading...' : 'Sleep'}
            </Button>
            <Button onClick={testExerciseTolerance} disabled={loading['exercise']} size="sm">
              {loading['exercise'] ? 'Loading...' : 'Exercise'}
            </Button>
            <Button onClick={testSymptomProgression} disabled={loading['progression']} size="sm">
              {loading['progression'] ? 'Loading...' : 'Progression'}
            </Button>
            <Button onClick={testTreatmentResponse} disabled={loading['treatment']} size="sm">
              {loading['treatment'] ? 'Loading...' : 'Treatment'}
            </Button>
            <Button onClick={testMultimodalPrediction} disabled={loading['multimodal']} size="sm">
              {loading['multimodal'] ? 'Loading...' : 'Multimodal'}
            </Button>
            <Button onClick={testAllEndpoints} variant="outline" size="sm" className="col-span-2">
              Test All Endpoints
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Predictions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  ML Predictions
                  {predictions && <Badge variant="secondary">Loaded</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {predictions ? (
                  <div className="space-y-2">
                    <p><strong>Risk Level:</strong> {predictions.risk_level}</p>
                    <p><strong>Confidence:</strong> {formatConfidence(predictions.confidence)}</p>
                    <p><strong>Next Flare Probability:</strong> {formatProbability(predictions.next_flare_probability)}</p>
                    <p><strong>Timeline:</strong> {predictions.timeline}</p>
                    <div>
                      <strong>Key Factors:</strong>
                      <ul className="list-disc list-inside mt-1">
                        {predictions.key_factors?.map((factor: string, index: number) => (
                          <li key={index} className="text-sm">{factor}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">Click "Test Predictions" to load data</p>
                )}
              </CardContent>
            </Card>

            {/* Real-time Predictions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Real-time Predictions
                  {realtimePredictions && <Badge variant="secondary">Loaded</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {realtimePredictions ? (
                  <div className="space-y-2">
                    <p><strong>Current Risk:</strong> {formatSmartNumber(realtimePredictions.current_risk)}%</p>
                    <p><strong>Confidence Score:</strong> {formatConfidence(realtimePredictions.confidence_score)}</p>
                    <div>
                      <strong>Risk Factors:</strong>
                      <ul className="list-disc list-inside mt-1">
                        {realtimePredictions.risk_factors?.map((factor: string, index: number) => (
                          <li key={index} className="text-sm">{factor}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <strong>Immediate Recommendations:</strong>
                      <ul className="list-disc list-inside mt-1">
                        {realtimePredictions.immediate_recommendations?.map((rec: string, index: number) => (
                          <li key={index} className="text-sm">{rec}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">Click "Test Real-time" to load data</p>
                )}
              </CardContent>
            </Card>

            {/* Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Personalized Recommendations
                  {recommendations && <Badge variant="secondary">Loaded</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {recommendations ? (
                  <div className="space-y-2">
                    <div>
                      <strong>Management Strategy:</strong>
                      <p className="text-sm">{recommendations.management_strategy?.strategy}</p>
                      <p className="text-sm text-gray-600">{recommendations.management_strategy?.timeline}</p>
                    </div>
                    <div>
                      <strong>Trigger Analysis:</strong>
                      <p className="text-sm">Primary: {recommendations.trigger_analysis?.primary_category}</p>
                    </div>
                    <div>
                      <strong>Personalized Tips:</strong>
                      <ul className="list-disc list-inside mt-1">
                        {recommendations.personalized_tips?.slice(0, 3).map((tip: string, index: number) => (
                          <li key={index} className="text-sm">{tip}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">Click "Test Recommendations" to load data</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* New ML Prediction Results */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Model Info */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Model Information
                  {modelInfo && <Badge variant="secondary">Loaded</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {modelInfo ? (
                  <div className="space-y-2">
                    <p><strong>Total Models:</strong> {modelInfo.total_models}</p>
                    <p><strong>Active Models:</strong> {modelInfo.active_models}</p>
                    <p><strong>Last Updated:</strong> {new Date(modelInfo.last_updated).toLocaleString()}</p>
                    <p><strong>Average Performance:</strong> {formatConfidence(modelInfo.average_performance)}</p>
                    <p><strong>Models:</strong> {modelInfo.models.map(m => m.name).join(', ')}</p>
                  </div>
                ) : (
                  <p className="text-gray-500">Click "Model Info" to load data</p>
                )}
              </CardContent>
            </Card>

            {/* Severity Prediction */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Severity Prediction
                  {severityPrediction && <Badge variant="secondary">Loaded</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {severityPrediction ? (
                  <div className="space-y-2">
                    <p><strong>Predicted Severity:</strong> {formatSmartNumber(severityPrediction.predicted_severity)}/10</p>
                    <p><strong>Category:</strong> {severityPrediction.severity_category}</p>
                    <p><strong>Confidence:</strong> {formatConfidence(severityPrediction.confidence)}</p>
                    <p><strong>Timeline:</strong> {severityPrediction.timeline}</p>
                  </div>
                ) : (
                  <p className="text-gray-500">Click "Severity" to load data</p>
                )}
              </CardContent>
            </Card>

            {/* Flareup Prediction */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Flareup Prediction
                  {flareupPrediction && <Badge variant="secondary">Loaded</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {flareupPrediction ? (
                  <div className="space-y-2">
                    <p><strong>Flareup Probability:</strong> {formatProbability(flareupPrediction.flareup_probability)}</p>
                    <p><strong>Risk Level:</strong> {flareupPrediction.risk_level}</p>
                    <p><strong>Confidence:</strong> {flareupPrediction.confidence ? formatConfidence(flareupPrediction.confidence) : 'N/A'}</p>
                    <p><strong>Timeline:</strong> {flareupPrediction.timeline}</p>
                  </div>
                ) : (
                  <p className="text-gray-500">Click "Flareup" to load data</p>
                )}
              </CardContent>
            </Card>

            {/* Medication Effectiveness */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Medication Effectiveness
                  {medicationEffectiveness && <Badge variant="secondary">Loaded</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {medicationEffectiveness ? (
                  <div className="space-y-2">
                    <p><strong>Effectiveness Score:</strong> {formatConfidence(medicationEffectiveness.effectiveness_score)}</p>
                    <p><strong>Confidence:</strong> {formatConfidence(medicationEffectiveness.confidence)}</p>
                  </div>
                ) : (
                  <p className="text-gray-500">Click "Medication" to load data</p>
                )}
              </CardContent>
            </Card>

            {/* Dietary Triggers */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Dietary Triggers
                  {dietaryTriggers && <Badge variant="secondary">Loaded</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {dietaryTriggers ? (
                  <div className="space-y-2">
                    <p><strong>Confidence:</strong> {formatConfidence(dietaryTriggers.confidence)}</p>
                    <div>
                      <strong>Trigger Foods:</strong>
                      <ul className="list-disc list-inside mt-1">
                        {dietaryTriggers.trigger_foods?.slice(0, 3).map((trigger, index) => (
                          <li key={index} className="text-sm">{trigger.food} ({formatProbability(trigger.trigger_probability)})</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">Click "Dietary" to load data</p>
                )}
              </CardContent>
            </Card>

            {/* Stress Correlation */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Stress Correlation
                  {stressCorrelation && <Badge variant="secondary">Loaded</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {stressCorrelation ? (
                  <div className="space-y-2">
                    <p><strong>Correlation Score:</strong> {formatConfidence(stressCorrelation.correlation_score)}</p>
                    <p><strong>Stress Triggers:</strong> {stressCorrelation.stress_triggers.join(', ')}</p>
                    <p><strong>Management Strategies:</strong> {stressCorrelation.management_strategies.join(', ')}</p>
                  </div>
                ) : (
                  <p className="text-gray-500">Click "Stress" to load data</p>
                )}
              </CardContent>
            </Card>

            {/* Sleep Impact */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Sleep Quality Impact
                  {sleepImpact && <Badge variant="secondary">Loaded</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {sleepImpact ? (
                  <div className="space-y-2">
                    <p><strong>Sleep Impact Score:</strong> {formatConfidence(sleepImpact.sleep_impact_score)}</p>
                    <p><strong>Optimal Sleep Hours:</strong> {sleepImpact.optimal_sleep_hours}h</p>
                    <p><strong>Confidence:</strong> {formatConfidence(sleepImpact.confidence)}</p>
                  </div>
                ) : (
                  <p className="text-gray-500">Click "Sleep" to load data</p>
                )}
              </CardContent>
            </Card>

            {/* Exercise Tolerance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Exercise Tolerance
                  {exerciseTolerance && <Badge variant="secondary">Loaded</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {exerciseTolerance ? (
                  <div className="space-y-2">
                    <p><strong>Tolerance Score:</strong> {formatConfidence(exerciseTolerance.tolerance_score)}</p>
                    <p><strong>Confidence:</strong> {formatConfidence(exerciseTolerance.confidence)}</p>
                    <div>
                      <strong>Recommended Exercises:</strong>
                      <ul className="list-disc list-inside mt-1">
                        {exerciseTolerance.recommended_exercises?.slice(0, 2).map((exercise, index) => (
                          <li key={index} className="text-sm">{exercise.type} ({exercise.duration}min)</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">Click "Exercise" to load data</p>
                )}
              </CardContent>
            </Card>

            {/* Symptom Progression */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Symptom Progression
                  {symptomProgression && <Badge variant="secondary">Loaded</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {symptomProgression ? (
                  <div className="space-y-2">
                    <p><strong>Progression Trend:</strong> {symptomProgression.progression_trend}</p>
                    <p><strong>Predicted Severity:</strong> {formatSmartNumber(symptomProgression.predicted_severity)}/10</p>
                    <p><strong>Confidence:</strong> {formatConfidence(symptomProgression.confidence)}</p>
                  </div>
                ) : (
                  <p className="text-gray-500">Click "Progression" to load data</p>
                )}
              </CardContent>
            </Card>

            {/* Treatment Response */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Treatment Response
                  {treatmentResponse && <Badge variant="secondary">Loaded</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {treatmentResponse ? (
                  <div className="space-y-2">
                    <p><strong>Predicted Response:</strong> {formatConfidence(treatmentResponse.predicted_response)}</p>
                    <p><strong>Response Category:</strong> {treatmentResponse.response_category}</p>
                    <p><strong>Confidence:</strong> {formatConfidence(treatmentResponse.confidence)}</p>
                  </div>
                ) : (
                  <p className="text-gray-500">Click "Treatment" to load data</p>
                )}
              </CardContent>
            </Card>

            {/* Multimodal Prediction */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Multimodal Prediction
                  {multimodalPrediction && <Badge variant="secondary">Loaded</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {multimodalPrediction ? (
                  <div className="space-y-2">
                    <p><strong>Overall Risk Score:</strong> {formatConfidence(multimodalPrediction.overall_risk_score)}</p>
                    <p><strong>Risk Category:</strong> {multimodalPrediction.risk_category}</p>
                    <p><strong>Confidence:</strong> {formatConfidence(multimodalPrediction.confidence)}</p>
                    <div>
                      <strong>Predictions:</strong>
                      <ul className="list-disc list-inside mt-1">
                        <li className="text-sm">Severity: {formatConfidence(multimodalPrediction.predictions?.severity)}</li>
                        <li className="text-sm">Flareup Risk: {formatConfidence(multimodalPrediction.predictions?.flareup_risk)}</li>
                      </ul>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">Click "Multimodal" to load data</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Raw Data Display */}
          {(predictions || realtimePredictions || recommendations) && (
            <Card>
              <CardHeader>
                <CardTitle>Raw API Responses (for debugging)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {predictions && (
                    <div>
                      <h4 className="font-semibold">Predictions:</h4>
                      <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto">
                        {JSON.stringify(predictions, null, 2)}
                      </pre>
                    </div>
                  )}
                  {realtimePredictions && (
                    <div>
                      <h4 className="font-semibold">Real-time Predictions:</h4>
                      <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto">
                        {JSON.stringify(realtimePredictions, null, 2)}
                      </pre>
                    </div>
                  )}
                  {recommendations && (
                    <div>
                      <h4 className="font-semibold">Recommendations:</h4>
                      <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto">
                        {JSON.stringify(recommendations, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}