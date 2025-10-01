'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { mlService } from '@/services/ml-service';
import { toast } from 'react-hot-toast';
import { ProtectedRoute } from '@/components/protected-route';

export default function TestMLPage() {
  const [predictions, setPredictions] = useState<any>(null);
  const [realtimePredictions, setRealtimePredictions] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any>(null);
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
      toast.success('Recommendations loaded successfully!');
    } catch (error) {
      console.error('Error testing recommendations:', error);
      toast.error('Failed to load recommendations');
    } finally {
      setLoading(prev => ({ ...prev, recommendations: false }));
    }
  };

  const testAllEndpoints = async () => {
    await Promise.all([
      testPredictions(),
      testRealtimePredictions(),
      testRecommendations()
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

          <div className="flex gap-4 justify-center">
            <Button onClick={testPredictions} disabled={loading['predictions']}>
              {loading['predictions'] ? 'Loading...' : 'Test Predictions'}
            </Button>
            <Button onClick={testRealtimePredictions} disabled={loading['realtime']}>
              {loading['realtime'] ? 'Loading...' : 'Test Real-time'}
            </Button>
            <Button onClick={testRecommendations} disabled={loading['recommendations']}>
              {loading['recommendations'] ? 'Loading...' : 'Test Recommendations'}
            </Button>
            <Button onClick={testAllEndpoints} variant="outline">
              Test All
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
                    <p><strong>Confidence:</strong> {predictions.confidence}%</p>
                    <p><strong>Next Flare Probability:</strong> {predictions.next_flare_probability}%</p>
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
                    <p><strong>Current Risk:</strong> {realtimePredictions.current_risk}%</p>
                    <p><strong>Confidence Score:</strong> {realtimePredictions.confidence_score}%</p>
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