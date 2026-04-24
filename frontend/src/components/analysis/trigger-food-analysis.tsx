'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  AlertTriangle, 
  CheckCircle, 
  RefreshCw, 
  Loader2,
  TrendingUp,
  TrendingDown,
  Calendar,
  BarChart3,
  Utensils,
  Shield,
  Target,
  Clock
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { correlationCalculationService, UserFoodHistory } from '@/services/correlation-calculation-service';

interface TriggerFood {
  food_name: string;
  reaction_count: number;
  risk_score: number;
  average_severity: number;
}

interface TriggerFoodAnalysisData {
  analysis_period_days: number;
  trigger_foods: TriggerFood[];
  safe_foods: string[];
  recommendations: string[];
  confidence?: number;
  correlation_strength?: number;
}

interface EnhancedTriggerAnalysis {
  trigger_foods: string[];
  safe_foods: string[];
  confidence: number;
  correlation_strength: number;
  recommendations: Array<{
    type: string;
    priority: string;
    message: string;
  }>;
  meal_timing_insights: Record<string, any>;
  portion_size_recommendations: Record<string, any>;
}

const API_BASE_URL = process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000';

export default function TriggerFoodAnalysis() {
  const [basicAnalysis, setBasicAnalysis] = useState<TriggerFoodAnalysisData | null>(null);
  const [enhancedAnalysis, setEnhancedAnalysis] = useState<EnhancedTriggerAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);


  const getAuthHeaders = (): HeadersInit => {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  };

  const fetchBasicAnalysis = async (): Promise<TriggerFoodAnalysisData> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/diet/analysis/triggers?days=90`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  };

  const fetchEnhancedAnalysis = async (): Promise<EnhancedTriggerAnalysis> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/ml/personalized`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Fetch user food history for correlation calculations
    let correlationResult;
    try {
      const userHistoryResponse = await fetch(`${API_BASE_URL}/api/v1/user/food-history`, {
        headers: getAuthHeaders(),
      });
      
      if (userHistoryResponse.ok) {
        const userHistory: UserFoodHistory = await userHistoryResponse.json();
        correlationResult = await correlationCalculationService.calculateFoodSymptomCorrelations(userHistory);
      }
    } catch (error) {
      console.warn('Failed to fetch user history for correlation analysis:', error);
    }
    
    // Use real correlation calculations or fallback to defaults
    const confidence = correlationResult?.overall_confidence || 0.3;
    const correlationStrength = correlationResult?.correlation_strength || 0.2;
    
    // Extract safe foods from correlation analysis
    const safeFoods = correlationResult?.food_correlations
      ?.filter(food => food.correlation_coefficient < 0.1) // Low correlation = safer
      ?.map(food => food.food_name)
      ?.slice(0, 4) || ['Rice', 'Bananas', 'Lean chicken', 'Herbal tea'];
    
    // Transform the response to match our interface
    return {
      trigger_foods: data.trigger_analysis?.insights || [],
      safe_foods: safeFoods,
      confidence,
      correlation_strength: correlationStrength,
      recommendations: data.dietary_recommendations?.map((rec: any) => ({
        type: rec.type || 'dietary',
        priority: rec.priority || 'medium',
        message: rec.description || rec.title || 'No description available'
      })) || [],
      meal_timing_insights: correlationResult?.temporal_patterns || {},
      portion_size_recommendations: correlationResult?.personalization_factors || {}
    };
  };

  const fetchAnalysis = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const [basicData, enhancedData] = await Promise.all([
        fetchBasicAnalysis().catch(() => null),
        fetchEnhancedAnalysis().catch(() => null)
      ]);

      setBasicAnalysis(basicData);
      setEnhancedAnalysis(enhancedData);

      if (!basicData && !enhancedData) {
        throw new Error('Failed to fetch trigger food analysis');
      }

      if (isRefresh) {
        toast.success('Trigger food analysis updated successfully');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch analysis';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAnalysis();
  }, []);

  const getRiskColor = (riskScore: number) => {
    if (riskScore >= 70) return 'text-red-600';
    if (riskScore >= 40) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getRiskBadgeVariant = (riskScore: number): "default" | "secondary" | "destructive" | "outline" => {
    if (riskScore >= 70) return 'destructive';
    if (riskScore >= 40) return 'secondary';
    return 'outline';
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-500" />
            <p className="text-gray-600">Analyzing your trigger foods...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error && !basicAnalysis && !enhancedAnalysis) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <div className="text-center">
            <AlertTriangle className="h-8 w-8 mx-auto mb-4 text-red-500" />
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={() => fetchAnalysis()} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-red-500" />
                Trigger Food Analysis
              </CardTitle>
              <p className="text-sm text-gray-600">
                Identify foods that may trigger your IBS symptoms
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchAnalysis(true)}
              disabled={refreshing}
              className="flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
          </div>
        </CardHeader>
      </Card>

      <Tabs defaultValue="enhanced">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="basic">Basic Analysis</TabsTrigger>
          <TabsTrigger value="enhanced">Enhanced Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="space-y-6">
          {basicAnalysis ? (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">
                        {basicAnalysis.trigger_foods.length}
                      </div>
                      <p className="text-sm text-muted-foreground">Trigger Foods</p>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {basicAnalysis.safe_foods.length}
                      </div>
                      <p className="text-sm text-muted-foreground">Safe Foods</p>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold">
                        {basicAnalysis.analysis_period_days}
                      </div>
                      <p className="text-sm text-muted-foreground">Days Analyzed</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Trigger Foods */}
              {basicAnalysis.trigger_foods.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="h-5 w-5 text-red-500" />
                      Identified Trigger Foods
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {basicAnalysis.trigger_foods.map((trigger, index) => (
                        <div key={index} className="border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <span className="font-medium">{trigger.food_name}</span>
                              <Badge variant={getRiskBadgeVariant(trigger.risk_score)}>
                                {trigger.risk_score}% Risk
                              </Badge>
                            </div>
                            <span className={`text-sm font-medium ${getRiskColor(trigger.risk_score)}`}>
                              {trigger.reaction_count} reactions
                            </span>
                          </div>
                          <Progress value={trigger.risk_score} className="h-2 mb-2" />
                          <p className="text-sm text-gray-600">
                            Average severity: {trigger.average_severity.toFixed(1)}/10
                          </p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Safe Foods */}
              {basicAnalysis.safe_foods.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="h-5 w-5 text-green-500" />
                      Safe Foods
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {basicAnalysis.safe_foods.map((food, index) => (
                        <Badge key={index} variant="outline" className="justify-center py-2 text-green-700 border-green-200">
                          {food}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Recommendations */}
              {basicAnalysis.recommendations.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Recommendations</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {basicAnalysis.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-start gap-2 p-3 bg-blue-50 rounded-lg">
                          <CheckCircle className="h-5 w-5 text-blue-500 mt-0.5 flex-shrink-0" />
                          <p className="text-sm">{rec}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <p className="text-gray-500">Basic analysis not available</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="enhanced" className="space-y-6">
          {enhancedAnalysis ? (
            <>
              {/* Enhanced Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold">
                        {(enhancedAnalysis.confidence * 100).toFixed(0)}%
                      </div>
                      <p className="text-sm text-muted-foreground">Analysis Confidence</p>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold">
                        {(enhancedAnalysis.correlation_strength * 100).toFixed(0)}%
                      </div>
                      <p className="text-sm text-muted-foreground">Correlation Strength</p>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {enhancedAnalysis.recommendations.length}
                      </div>
                      <p className="text-sm text-muted-foreground">AI Recommendations</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Enhanced Recommendations */}
              {enhancedAnalysis.recommendations.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5 text-blue-500" />
                      AI-Powered Insights
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {enhancedAnalysis.recommendations.map((rec, index) => (
                        <div key={index} className={`border rounded-lg p-4 ${
                          rec.priority === 'high' ? 'border-red-200 bg-red-50' :
                          rec.priority === 'medium' ? 'border-yellow-200 bg-yellow-50' :
                          'border-blue-200 bg-blue-50'
                        }`}>
                          <div className="flex items-center justify-between mb-2">
                            <Badge variant={
                              rec.priority === 'high' ? 'destructive' :
                              rec.priority === 'medium' ? 'secondary' : 'outline'
                            }>
                              {rec.priority} priority
                            </Badge>
                            <span className="text-xs text-gray-500 uppercase">{rec.type}</span>
                          </div>
                          <p className="text-sm">{rec.message}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Trigger Insights */}
              {enhancedAnalysis.trigger_foods.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-orange-500" />
                      Pattern Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {enhancedAnalysis.trigger_foods.map((insight, index) => (
                        <div key={index} className="flex items-start gap-2 p-3 bg-orange-50 rounded-lg">
                          <Utensils className="h-5 w-5 text-orange-500 mt-0.5 flex-shrink-0" />
                          <p className="text-sm">{insight}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <p className="text-gray-500">Enhanced analysis not available</p>
                <p className="text-xs text-gray-400 mt-2">Continue logging meals and symptoms for better insights</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}