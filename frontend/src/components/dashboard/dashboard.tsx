'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Brain, 
  Calendar,
  Activity,
  Utensils,
  Pill,
  Heart,
  Target,
  Zap,
  BarChart3,
  PieChart,
  LineChart,
  Bell,
  Star,
  Clock,
  Shield,
  Lightbulb,
  Plus,
  RefreshCw,
  Loader2
} from 'lucide-react';
import { dynamicDashboardService, DynamicDashboardData } from '@/services/dynamic-dashboard-service';

// Use the dynamic interface from the service
type DashboardData = DynamicDashboardData;

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async (showRefreshIndicator = false) => {
    try {
      if (showRefreshIndicator) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }
      setError(null);

      const dashboardData = await dynamicDashboardService.getDashboardData();
      setData(dashboardData);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleRefresh = () => {
    loadDashboardData(true);
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSeverityColor = (severity: number) => {
    if (severity <= 3) return 'bg-green-500';
    if (severity <= 6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'medium': return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'low': return <CheckCircle className="h-4 w-4 text-green-500" />;
      default: return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading Your Dashboard</h2>
          <p className="text-gray-600">Fetching your personalized health insights...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Unable to Load Dashboard</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => loadDashboardData()} className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">IBS Wellness Dashboard</h1>
            <p className="text-gray-600 mt-1">Your personalized health insights and AI-powered recommendations</p>
          </div>
          <div className="flex items-center gap-3">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              {isRefreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
            <Button variant="outline" size="sm">
              <Calendar className="h-4 w-4 mr-2" />
              View Calendar
            </Button>
            <Button size="sm">
              <Plus size={16} />
              Quick Log
            </Button>
          </div>
        </div>

        {/* AI Predictions Card */}
        <Card className="border-l-4 border-l-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-6 w-6 text-blue-600" />
              AI Health Predictions
              <Badge variant="outline" className="ml-auto text-xs">
                {data.aiPredictions.modelVersion}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Risk Level */}
              <div className="text-center">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(data.aiPredictions.riskLevel)}`}>
                  <Shield className="h-4 w-4 mr-1" />
                  {data.aiPredictions.riskLevel.toUpperCase()} RISK
                </div>
                <p className="text-xs text-gray-600 mt-1">Current risk level</p>
                <div className="mt-2">
                  <Badge variant="outline" className="text-xs">
                    {Math.round(data.aiPredictions.confidence * 100)}% confidence
                  </Badge>
                </div>
              </div>

              {/* Flare Risk */}
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{data.aiPredictions.nextFlareRisk}%</div>
                <p className="text-xs text-gray-600">Flare risk ({data.aiPredictions.timeline})</p>
                <Progress value={data.aiPredictions.nextFlareRisk} className="mt-2 h-2" />
              </div>

              {/* Trigger Foods */}
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{data.aiPredictions.triggerFoods.length}</div>
                <p className="text-xs text-gray-600">Identified trigger foods</p>
              </div>
            </div>

            {/* Key Factors */}
            {data.aiPredictions.keyFactors.length > 0 && (
              <div className="mt-6">
                <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <Target className="h-4 w-4 text-blue-500" />
                  Key Risk Factors
                </h4>
                <div className="flex flex-wrap gap-2">
                  {data.aiPredictions.keyFactors.map((factor, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {factor}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* AI Recommendations */}
            <div className="mt-6">
              <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-yellow-500" />
                Personalized Recommendations
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {data.aiPredictions.recommendations.map((rec, index) => (
                  <div key={index} className="bg-white p-3 rounded-lg border border-blue-200 text-sm">
                    <div className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{rec}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Personalized Recommendations Tabs */}
            {data.personalizedRecommendations && (
              <div className="mt-6">
                <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <Heart className="h-4 w-4 text-red-500" />
                  Detailed Recommendations
                </h4>
                <Tabs defaultValue="dietary" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="dietary">Dietary</TabsTrigger>
                    <TabsTrigger value="lifestyle">Lifestyle</TabsTrigger>
                    <TabsTrigger value="medical">Medical</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="dietary" className="mt-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {data.personalizedRecommendations.dietary.map((rec, index) => (
                        <div key={index} className="bg-white p-3 rounded-lg border border-green-200">
                          <div className="flex items-start justify-between mb-2">
                            <h5 className="font-medium text-green-700">{rec.category}</h5>
                            <Badge variant="outline" className="text-xs">
                              Priority: {rec.priority}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-700 mb-2">{rec.recommendation}</p>
                          <p className="text-xs text-gray-500">{rec.reasoning}</p>
                        </div>
                      ))}
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="lifestyle" className="mt-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {data.personalizedRecommendations.lifestyle.map((rec, index) => (
                        <div key={index} className="bg-white p-3 rounded-lg border border-blue-200">
                          <div className="flex items-start justify-between mb-2">
                            <h5 className="font-medium text-blue-700">{rec.category}</h5>
                            <Badge variant="outline" className="text-xs">
                              Priority: {rec.priority}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-700 mb-2">{rec.recommendation}</p>
                          <p className="text-xs text-gray-500">{rec.reasoning}</p>
                        </div>
                      ))}
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="medical" className="mt-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {data.personalizedRecommendations.medical.map((rec, index) => (
                        <div key={index} className="bg-white p-3 rounded-lg border border-purple-200">
                          <div className="flex items-start justify-between mb-2">
                            <h5 className="font-medium text-purple-700">{rec.category}</h5>
                            <Badge variant="outline" className="text-xs">
                              Priority: {rec.priority}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-700 mb-2">{rec.recommendation}</p>
                          <p className="text-xs text-gray-500">{rec.reasoning}</p>
                        </div>
                      ))}
                    </div>
                  </TabsContent>
                </Tabs>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Avg Severity</p>
                  <p className="text-2xl font-bold text-gray-900">{data.weeklyStats.avgSeverity}/10</p>
                </div>
                <div className={`p-3 rounded-full ${getSeverityColor(data.weeklyStats.avgSeverity)}`}>
                  <Activity className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="mt-4">
                <Progress value={data.weeklyStats.avgSeverity * 10} className="h-2" />
              </div>
              {data.weeklyStats.improvementTrend !== 0 && (
                <div className="mt-2 flex items-center gap-1">
                  {data.weeklyStats.improvementTrend > 0 ? (
                    <TrendingUp className="h-3 w-3 text-green-500" />
                  ) : (
                    <TrendingDown className="h-3 w-3 text-red-500" />
                  )}
                  <span className={`text-xs ${data.weeklyStats.improvementTrend > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {Math.abs(data.weeklyStats.improvementTrend)}% vs last week
                  </span>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Symptom-Free Days</p>
                  <p className="text-2xl font-bold text-green-600">{data.weeklyStats.symptomFreeDays}</p>
                </div>
                <div className="p-3 rounded-full bg-green-100">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-2">This week</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Logs</p>
                  <p className="text-2xl font-bold text-blue-600">{data.weeklyStats.totalLogs}</p>
                </div>
                <div className="p-3 rounded-full bg-blue-100">
                  <BarChart3 className="h-6 w-6 text-blue-600" />
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-2">This week</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Adherence Rate</p>
                  <p className="text-2xl font-bold text-purple-600">{data.weeklyStats.adherenceRate}%</p>
                </div>
                <div className="p-3 rounded-full bg-purple-100">
                  <Target className="h-6 w-6 text-purple-600" />
                </div>
              </div>
              <div className="mt-4">
                <Progress value={data.weeklyStats.adherenceRate} className="h-2" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="insights">Insights</TabsTrigger>
            <TabsTrigger value="trends">Trends</TabsTrigger>
            <TabsTrigger value="reminders">Reminders</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recent Symptoms */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-red-500" />
                    Recent Symptoms
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {data.recentSymptoms.length === 0 ? (
                      <div className="text-center py-8">
                        <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-2" />
                        <p className="text-gray-500">No recent symptoms logged</p>
                        <p className="text-xs text-gray-400">Keep up the great work!</p>
                      </div>
                    ) : (
                      data.recentSymptoms.map((symptom, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-sm font-medium">{symptom.date}</span>
                              <Badge variant="outline" className={`text-xs ${getSeverityColor(symptom.severity)} text-white`}>
                                {symptom.severity}/10
                              </Badge>
                            </div>
                            <div className="flex flex-wrap gap-1">
                              {symptom.symptoms.map((s, i) => (
                                <span key={i} className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">
                                  {s}
                                </span>
                              ))}
                            </div>
                            {symptom.notes && (
                              <p className="text-xs text-gray-500 mt-1">{symptom.notes}</p>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Trigger Foods */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Utensils className="h-5 w-5 text-orange-500" />
                    Identified Trigger Foods
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {data.aiPredictions.triggerFoods.length === 0 ? (
                      <div className="text-center py-8">
                        <Utensils className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                        <p className="text-gray-500">No trigger foods identified yet</p>
                        <p className="text-xs text-gray-400">Continue logging to identify patterns</p>
                      </div>
                    ) : (
                      data.aiPredictions.triggerFoods.map((food, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                          <span className="text-sm font-medium text-red-800">{food}</span>
                          <AlertTriangle className="h-4 w-4 text-red-500" />
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="insights" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {data.insights.map((insight, index) => (
                <Card key={index} className={`border-l-4 ${
                  insight.type === 'positive' ? 'border-l-green-500 bg-green-50' :
                  insight.type === 'warning' ? 'border-l-yellow-500 bg-yellow-50' :
                  'border-l-blue-500 bg-blue-50'
                }`}>
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      {insight.type === 'positive' && <CheckCircle className="h-5 w-5 text-green-600" />}
                      {insight.type === 'warning' && <AlertTriangle className="h-5 w-5 text-yellow-600" />}
                      {insight.type === 'info' && <Lightbulb className="h-5 w-5 text-blue-600" />}
                      {insight.title}
                      <Badge variant="outline" className="ml-auto text-xs">
                        {insight.priority}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700 mb-3">{insight.description}</p>
                    {insight.action && (
                      <Button variant="outline" size="sm" className="text-xs">
                        {insight.action}
                      </Button>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="trends" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <LineChart className="h-5 w-5 text-blue-500" />
                    Symptom Trends
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                    <div className="text-center">
                      <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-500">Chart visualization would go here</p>
                      <p className="text-xs text-gray-400">Showing symptom severity over time</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <PieChart className="h-5 w-5 text-green-500" />
                    Food Impact Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                    <div className="text-center">
                      <PieChart className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-500">Chart visualization would go here</p>
                      <p className="text-xs text-gray-400">Showing food impact on symptoms</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="reminders" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="h-5 w-5 text-purple-500" />
                  Upcoming Reminders
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {data.upcomingReminders.length === 0 ? (
                    <div className="text-center py-8">
                      <Bell className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-500">No upcoming reminders</p>
                      <p className="text-xs text-gray-400">You're all caught up!</p>
                    </div>
                  ) : (
                    data.upcomingReminders.map((reminder, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border">
                        <div className="flex items-center gap-3">
                          {getPriorityIcon(reminder.priority)}
                          <div>
                            <h4 className="font-medium text-gray-900">{reminder.title}</h4>
                            <p className="text-sm text-gray-600">{reminder.time}</p>
                            {reminder.description && (
                              <p className="text-xs text-gray-500 mt-1">{reminder.description}</p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {reminder.type}
                          </Badge>
                          <Button variant="outline" size="sm">
                            Mark Done
                          </Button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}