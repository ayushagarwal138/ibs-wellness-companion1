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
  Plus
} from 'lucide-react';

interface DashboardData {
  aiPredictions: {
    riskLevel: 'low' | 'medium' | 'high';
    nextFlareRisk: number;
    triggerFoods: string[];
    recommendations: string[];
  };
  recentSymptoms: {
    date: string;
    severity: number;
    symptoms: string[];
  }[];
  weeklyStats: {
    avgSeverity: number;
    symptomFreeDays: number;
    totalLogs: number;
    adherenceRate: number;
  };
  insights: {
    type: 'positive' | 'warning' | 'info';
    title: string;
    description: string;
    action?: string;
  }[];
  upcomingReminders: {
    type: 'medication' | 'appointment' | 'log';
    title: string;
    time: string;
    priority: 'high' | 'medium' | 'low';
  }[];
}

// Mock data - in real app, this would come from API
const mockDashboardData: DashboardData = {
  aiPredictions: {
    riskLevel: 'medium',
    nextFlareRisk: 35,
    triggerFoods: ['Dairy products', 'Spicy foods', 'High-fat meals'],
    recommendations: [
      'Consider reducing dairy intake this week',
      'Increase fiber gradually with oats and bananas',
      'Practice stress management techniques before meals',
      'Take probiotics consistently for gut health'
    ]
  },
  recentSymptoms: [
    { date: '2024-01-15', severity: 6, symptoms: ['Bloating', 'Abdominal pain'] },
    { date: '2024-01-14', severity: 3, symptoms: ['Mild discomfort'] },
    { date: '2024-01-13', severity: 8, symptoms: ['Severe cramping', 'Diarrhea'] },
    { date: '2024-01-12', severity: 2, symptoms: ['Slight bloating'] },
    { date: '2024-01-11', severity: 5, symptoms: ['Gas', 'Discomfort'] }
  ],
  weeklyStats: {
    avgSeverity: 4.8,
    symptomFreeDays: 2,
    totalLogs: 12,
    adherenceRate: 85
  },
  insights: [
    {
      type: 'warning',
      title: 'Stress Pattern Detected',
      description: 'Your symptoms tend to worsen during high-stress periods. Consider stress management techniques.',
      action: 'View stress management tips'
    },
    {
      type: 'positive',
      title: 'Medication Adherence Improving',
      description: 'Great job! Your medication adherence has improved by 15% this month.',
    },
    {
      type: 'info',
      title: 'Dietary Pattern Analysis',
      description: 'You have fewer symptoms on days when you eat smaller, more frequent meals.',
      action: 'View meal planning suggestions'
    }
  ],
  upcomingReminders: [
    { type: 'medication', title: 'Take Probiotics', time: '2:00 PM', priority: 'high' },
    { type: 'log', title: 'Log Evening Symptoms', time: '8:00 PM', priority: 'medium' },
    { type: 'appointment', title: 'Dr. Smith Checkup', time: 'Tomorrow 10:00 AM', priority: 'high' }
  ]
};

export default function Dashboard() {
  const [data, setData] = useState<DashboardData>(mockDashboardData);

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
              </div>

              {/* Flare Risk */}
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{data.aiPredictions.nextFlareRisk}%</div>
                <p className="text-xs text-gray-600">Flare risk (next 7 days)</p>
                <Progress value={data.aiPredictions.nextFlareRisk} className="mt-2 h-2" />
              </div>

              {/* Trigger Foods */}
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{data.aiPredictions.triggerFoods.length}</div>
                <p className="text-xs text-gray-600">Identified trigger foods</p>
              </div>
            </div>

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
                      <Star className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                      <span>{rec}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
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
                    {data.recentSymptoms.map((symptom, index) => (
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
                        </div>
                      </div>
                    ))}
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
                    {data.aiPredictions.triggerFoods.map((food, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg border border-orange-200">
                        <div className="flex items-center gap-3">
                          <AlertTriangle className="h-4 w-4 text-orange-500" />
                          <span className="font-medium text-orange-800">{food}</span>
                        </div>
                        <Button variant="outline" size="sm" className="text-xs">
                          View Details
                        </Button>
                      </div>
                    ))}
                    <Button variant="outline" className="w-full mt-4">
                      <PieChart className="h-4 w-4 mr-2" />
                      View Food Analysis
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="insights" className="space-y-4">
            <div className="grid grid-cols-1 gap-4">
              {data.insights.map((insight, index) => (
                <Card key={index} className={`border-l-4 ${
                  insight.type === 'positive' ? 'border-l-green-500 bg-green-50' :
                  insight.type === 'warning' ? 'border-l-yellow-500 bg-yellow-50' :
                  'border-l-blue-500 bg-blue-50'
                }`}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          {insight.type === 'positive' && <CheckCircle className="h-5 w-5 text-green-600" />}
                          {insight.type === 'warning' && <AlertTriangle className="h-5 w-5 text-yellow-600" />}
                          {insight.type === 'info' && <Lightbulb className="h-5 w-5 text-blue-600" />}
                          <h3 className="font-semibold text-gray-900">{insight.title}</h3>
                        </div>
                        <p className="text-gray-700 mb-3">{insight.description}</p>
                        {insight.action && (
                          <Button variant="outline" size="sm">
                            {insight.action}
                          </Button>
                        )}
                      </div>
                    </div>
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
                      <p className="text-xs text-gray-400">Showing food categories and their impact</p>
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
                  {data.upcomingReminders.map((reminder, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        {getPriorityIcon(reminder.priority)}
                        <div>
                          <p className="font-medium text-gray-900">{reminder.title}</p>
                          <p className="text-sm text-gray-600">{reminder.time}</p>
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
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}