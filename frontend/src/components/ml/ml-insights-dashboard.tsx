'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Brain, 
  Target, 
  Shield, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Lightbulb,
  Activity,
  Heart,
  Utensils,
  Moon,
  Zap,
  RefreshCw
} from 'lucide-react';
import { mlService, MLPredictionResponse, PersonalizedRecommendationsResponse } from '@/services/ml-service';
import { toast } from 'react-hot-toast';

interface MLInsightsDashboardProps {
  userId?: string;
  className?: string;
}

interface InsightCard {
  id: string;
  type: 'prediction' | 'recommendation' | 'alert' | 'tip';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  category: string;
  confidence?: number;
  actionable: boolean;
  action?: string;
}

export function MLInsightsDashboard({ userId, className }: MLInsightsDashboardProps) {
  const [predictions, setPredictions] = useState<MLPredictionResponse | null>(null);
  const [recommendations, setRecommendations] = useState<PersonalizedRecommendationsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'day' | 'week' | 'month'>('day');

  const loadMLInsights = async () => {
    try {
      setLoading(true);
      const [predictionsData, recommendationsData] = await Promise.all([
        mlService.getPredictions(),
        mlService.getPersonalizedRecommendations()
      ]);
      
      setPredictions(predictionsData);
      setRecommendations(recommendationsData);
    } catch (error) {
      console.error('Failed to load ML insights:', error);
      toast.error('Failed to load AI insights');
    } finally {
      setLoading(false);
    }
  };

  const refreshInsights = async () => {
    try {
      setRefreshing(true);
      await loadMLInsights();
      toast.success('Insights refreshed successfully');
    } catch (error) {
      console.error('Failed to refresh insights:', error);
      toast.error('Failed to refresh insights');
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadMLInsights();
  }, [selectedTimeframe]);

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'high': return 'border-red-300 bg-red-50';
      case 'medium': return 'border-yellow-300 bg-yellow-50';
      case 'low': return 'border-green-300 bg-green-50';
      default: return 'border-gray-300 bg-gray-50';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return <AlertTriangle className="h-4 w-4 text-red-500 flex-shrink-0" />;
      case 'medium': return <Clock className="h-4 w-4 text-yellow-500 flex-shrink-0" />;
      case 'low': return <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />;
      default: return <Activity className="h-4 w-4 text-gray-500 flex-shrink-0" />;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'sleep': return <Moon className="h-4 w-4 text-blue-500 flex-shrink-0 mt-0.5" />;
      case 'exercise': return <Activity className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />;
      case 'stress': return <Heart className="h-4 w-4 text-red-500 flex-shrink-0 mt-0.5" />;
      case 'diet': return <Utensils className="h-4 w-4 text-orange-500 flex-shrink-0 mt-0.5" />;
      default: return <Activity className="h-4 w-4 text-blue-500 flex-shrink-0 mt-0.5" />;
    }
  };

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-4 lg:space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Brain className="h-6 w-6 text-purple-600" />
          <h2 className="text-xl lg:text-2xl font-bold text-gray-900">AI-Powered Insights</h2>
        </div>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
          <select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value as 'day' | 'week' | 'month')}
            className="w-full sm:w-auto px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="day">Next Day</option>
            <option value="week">Next Week</option>
            <option value="month">Next Month</option>
          </select>
          <Button
            onClick={refreshInsights}
            disabled={refreshing}
            variant="outline"
            size="sm"
            className="flex items-center gap-2 w-full sm:w-auto"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      {predictions && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="p-3 lg:p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900 text-sm lg:text-base truncate">Flare-up Risk</h4>
                <Target className="h-4 w-4 text-red-500 flex-shrink-0" />
              </div>
              <div className="text-lg lg:text-2xl xl:text-3xl font-bold text-red-600 mb-1 truncate">
                {predictions.next_flare_probability}%
              </div>
              <p className="text-xs lg:text-sm text-gray-600 mb-2 break-words">
                in the {predictions.timeline}
              </p>
              <div className="w-full">
                <Progress value={predictions.next_flare_probability} className="h-2" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-3 lg:p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900 text-sm lg:text-base truncate">Severity Score</h4>
                <TrendingUp className="h-4 w-4 text-blue-500 flex-shrink-0" />
              </div>
              <div className="text-lg lg:text-2xl xl:text-3xl font-bold text-blue-600 mb-1 truncate">
                {predictions.predicted_severity}/10
              </div>
              <p className="text-xs lg:text-sm text-gray-600 break-words">
                Predicted severity
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-3 lg:p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900 text-sm lg:text-base truncate">Key Factors</h4>
                <Zap className="h-4 w-4 text-yellow-500 flex-shrink-0" />
              </div>
              <div className="text-lg lg:text-2xl xl:text-3xl font-bold text-yellow-600 mb-1 truncate">
                {predictions.key_factors.length}
              </div>
              <p className="text-xs lg:text-sm text-gray-600 break-words">
                Risk factors identified
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Detailed Insights */}
      <div className="w-full overflow-hidden">
        <Tabs defaultValue="predictions" className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-4">
            <TabsTrigger value="predictions" className="text-xs lg:text-sm truncate">Predictions</TabsTrigger>
            <TabsTrigger value="recommendations" className="text-xs lg:text-sm truncate">Recommendations</TabsTrigger>
            <TabsTrigger value="insights" className="text-xs lg:text-sm truncate">Insights</TabsTrigger>
            <TabsTrigger value="actions" className="text-xs lg:text-sm truncate">Actions</TabsTrigger>
          </TabsList>

          <TabsContent value="predictions" className="space-y-4">
            {predictions && (
              <>
                {/* Risk Factors */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base lg:text-lg">
                      <AlertTriangle className="h-4 lg:h-5 w-4 lg:w-5 text-orange-500 flex-shrink-0" />
                      <span className="truncate">Key Risk Factors</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 gap-3 max-w-full overflow-hidden">
                      {predictions.key_factors.map((factor, index) => (
                        <div key={index} className="flex items-start gap-3 p-3 bg-orange-50 rounded-lg border border-orange-200">
                          <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0" />
                          <span className="text-sm text-orange-800 break-words flex-1 min-w-0">{factor}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Immediate Actions */}
                {predictions.recommendations?.immediate_actions && (
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="flex items-center gap-2 text-base lg:text-lg">
                        <Zap className="h-4 lg:h-5 w-4 lg:w-5 text-red-500" />
                        Immediate Actions Required
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {predictions.recommendations.immediate_actions.map((action, index) => (
                          <div key={index} className="border border-red-200 rounded-lg p-4 bg-red-50">
                            <div className="flex items-start gap-3">
                              {getPriorityIcon(action.priority)}
                              <div className="flex-1 min-w-0">
                                <h4 className="font-semibold text-red-800 mb-1 break-words">{action.action}</h4>
                                <p className="text-sm text-red-700 mb-2 break-words">{action.explanation}</p>
                                <div className="text-xs text-red-600 bg-red-100 px-2 py-1 rounded break-words">
                                  Expected benefit: {action.expected_benefit}
                                </div>
                              </div>
                              <Badge variant="outline" className="text-red-600 border-red-300 flex-shrink-0">
                                {action.priority}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </TabsContent>

          <TabsContent value="recommendations" className="space-y-4">
            {recommendations && (
              <>
                {/* Dietary Recommendations */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base lg:text-lg">
                      <Utensils className="h-5 w-5 text-green-500" />
                      Dietary Recommendations
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {recommendations.dietary_recommendations.map((rec, index) => (
                        <div key={index} className="flex items-start gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                          <Utensils className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                          <div className="flex-1 min-w-0">
                            <h4 className="font-semibold text-green-800 break-words">{rec.title}</h4>
                            <p className="text-sm text-green-700 mt-1 break-words">{rec.description}</p>
                          </div>
                          <Badge variant="outline" className="text-green-600 border-green-300 flex-shrink-0">
                            {rec.priority}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Lifestyle Insights */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base lg:text-lg">
                      <Heart className="h-4 lg:h-5 w-4 lg:w-5 text-blue-500" />
                      Lifestyle Insights
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {recommendations.lifestyle_insights.map((insight, index) => (
                        <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                          {getCategoryIcon(insight.category)}
                          <div className="flex-1 min-w-0">
                            <h4 className="font-semibold text-blue-800 break-words">{insight.category}</h4>
                            <p className="text-sm text-blue-700 mt-1 break-words">{insight.insight}</p>
                            <p className="text-sm text-blue-600 mt-2 font-medium break-words">
                              Recommendation: {insight.recommendation}
                            </p>
                          </div>
                          <Badge variant="outline" className="text-blue-600 border-blue-300 flex-shrink-0">
                            {insight.priority}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          <TabsContent value="insights" className="space-y-4">
            {recommendations && (
              <>
                {/* Trigger Analysis */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base lg:text-lg">
                      <Target className="h-4 lg:h-5 w-4 lg:w-5 text-purple-500" />
                      Trigger Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="mb-4">
                      <h4 className="font-semibold text-purple-800 mb-2 break-words">
                        Primary Category: {recommendations.trigger_analysis.primary_category}
                      </h4>
                      <div className="space-y-2">
                        {recommendations.trigger_analysis.insights.map((insight, index) => (
                          <div key={index} className="flex items-start gap-2 text-sm text-purple-700">
                            <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 flex-shrink-0"></div>
                            <span className="break-words">{insight}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Management Strategy */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-base lg:text-lg">
                      <Shield className="h-4 lg:h-5 w-4 lg:w-5 text-indigo-500" />
                      Management Strategy
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <h4 className="font-semibold text-indigo-800">Strategy</h4>
                        <p className="text-sm text-indigo-700 break-words">{recommendations.management_strategy.strategy}</p>
                      </div>
                      <div>
                        <h4 className="font-semibold text-indigo-800">Approach</h4>
                        <p className="text-sm text-indigo-700 break-words">{recommendations.management_strategy.approach}</p>
                      </div>
                      <div>
                        <h4 className="font-semibold text-indigo-800">Timeline</h4>
                        <p className="text-sm text-indigo-700 break-words">{recommendations.management_strategy.timeline}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          <TabsContent value="actions" className="space-y-4">
            {recommendations && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2 text-base lg:text-lg">
                    <Lightbulb className="h-4 lg:h-5 w-4 lg:w-5 text-yellow-500" />
                    Personalized Tips
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 gap-3">
                    {recommendations.personalized_tips.map((tip, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                        <Lightbulb className="h-4 w-4 text-yellow-500 flex-shrink-0 mt-0.5" />
                        <p className="text-sm text-yellow-800 break-words">{tip}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}