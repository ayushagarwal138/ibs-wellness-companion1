'use client';

import React, { useState, useEffect } from 'react';
import { ProtectedRoute } from "@/components/protected-route";
import { DashboardHeader } from "@/components/layout/dashboard-header";
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Brain, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Heart, 
  Target,
  Calendar,
  Activity,
  Lightbulb,
  Shield,
  Clock,
  Star,
  BarChart3,
  Zap,
  User,
  FileText,
  Download,
  Share2
} from 'lucide-react';

import { mlService } from '@/services/ml-service';

interface MLPrediction {
  risk_level: 'low' | 'medium' | 'moderate' | 'high';
  confidence: number;
  next_flare_probability: number;
  predicted_severity: number;
  timeline: string;
  key_factors: string[];
}

interface PersonalizedRecommendations {
  immediate_actions: Array<{
    action: string;
    priority: 'high' | 'medium' | 'low';
    explanation: string;
    expected_benefit: string;
  }>;
  dietary_suggestions: Array<{
    type: 'avoid' | 'include' | 'moderate';
    foods: string[];
    reason: string;
    timeline: string;
  }>;
  lifestyle_changes: Array<{
    category: string;
    suggestion: string;
    difficulty: 'easy' | 'moderate' | 'challenging';
    impact: string;
  }>;
  medical_advice: {
    should_consult_doctor: boolean;
    urgency: 'low' | 'medium' | 'high';
    reasons: string[];
    suggested_specialists: string[];
  };
}

interface ReportData {
  user_summary: {
    name: string;
    tracking_days: number;
    last_updated: string;
    overall_trend: 'improving' | 'stable' | 'declining';
  };
  severity_assessment: {
    current_level: 'low' | 'medium' | 'moderate' | 'high';
    trend: 'improving' | 'stable' | 'worsening';
    score: number;
    description: string;
  };
  ml_predictions: MLPrediction;
  recommendations: PersonalizedRecommendations;
  insights: Array<{
    type: 'positive' | 'warning' | 'info';
    title: string;
    description: string;
    action_required: boolean;
  }>;
  progress_metrics: {
    symptom_control: number;
    quality_of_life: number;
    goal_achievement: number;
    consistency_score: number;
  };
}

// Mock data - in production, this would come from the ML prediction API
const mockReportData: ReportData = {
  user_summary: {
    name: "User",
    tracking_days: 45,
    last_updated: new Date().toLocaleDateString(),
    overall_trend: 'improving'
  },
  severity_assessment: {
    current_level: 'medium',
    trend: 'improving',
    score: 4.2,
    description: "Your IBS symptoms are currently at a medium level, but showing positive improvement over the past month."
  },
  ml_predictions: {
    risk_level: 'medium',
    confidence: 78,
    next_flare_probability: 35,
    predicted_severity: 4.5,
    timeline: "next 7 days",
    key_factors: ["Stress levels", "Dairy consumption", "Sleep quality"]
  },
  recommendations: {
    immediate_actions: [
      {
        action: "Reduce dairy intake for the next 3-5 days",
        priority: 'high',
        explanation: "Our analysis shows dairy products trigger symptoms in 73% of your logged episodes",
        expected_benefit: "May reduce bloating and discomfort by 40-60%"
      },
      {
        action: "Practice 10 minutes of deep breathing before meals",
        priority: 'medium',
        explanation: "Stress management significantly impacts your digestive health",
        expected_benefit: "Can improve digestion and reduce symptom severity"
      }
    ],
    dietary_suggestions: [
      {
        type: 'avoid',
        foods: ["Dairy products", "Spicy foods", "High-fat meals"],
        reason: "These foods consistently trigger symptoms based on your tracking data",
        timeline: "Next 1-2 weeks"
      },
      {
        type: 'include',
        foods: ["Oats", "Bananas", "Lean proteins", "Herbal teas"],
        reason: "These foods have shown positive effects on your digestive health",
        timeline: "Daily incorporation recommended"
      }
    ],
    lifestyle_changes: [
      {
        category: "Sleep",
        suggestion: "Maintain consistent 8+ hour sleep schedule",
        difficulty: 'easy',
        impact: "Better sleep quality correlates with 30% fewer symptom days"
      },
      {
        category: "Exercise",
        suggestion: "Add 20 minutes of gentle walking after meals",
        difficulty: 'easy',
        impact: "Can improve digestion and reduce bloating"
      }
    ],
    medical_advice: {
      should_consult_doctor: false,
      urgency: 'low',
      reasons: ["Symptoms are well-managed", "Positive improvement trend"],
      suggested_specialists: []
    }
  },
  insights: [
    {
      type: 'positive',
      title: "Great Progress This Month!",
      description: "Your symptom severity has decreased by 23% compared to last month. Keep up the excellent work!",
      action_required: false
    },
    {
      type: 'info',
      title: "Pattern Detected: Weekend Symptoms",
      description: "You tend to experience more symptoms on weekends. This might be related to changes in routine or diet.",
      action_required: true
    }
  ],
  progress_metrics: {
    symptom_control: 78,
    quality_of_life: 72,
    goal_achievement: 85,
    consistency_score: 91
  }
};

export default function ReportsPage() {
  const [reportData, setReportData] = useState<ReportData>(mockReportData);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'day' | 'week' | 'month'>('month');

  useEffect(() => {
    // In production, fetch real ML predictions and report data
    fetchReportData();
  }, [selectedTimeframe]);

  const fetchReportData = async () => {
    setIsLoading(true);
    try {
      // Fetch real ML predictions and recommendations
      const mlReport = await mlService.generateReport(selectedTimeframe);
      
      // Transform the API response to match our ReportData interface
      const transformedData: ReportData = {
        user_summary: {
          name: "User",
          tracking_days: 45,
          last_updated: new Date().toLocaleDateString(),
          overall_trend: 'improving'
        },
        severity_assessment: {
          current_level: mlReport.predictions.risk_level,
          trend: 'improving',
          score: mlReport.predictions.predicted_severity,
          description: getSeverityDescription(mlReport.predictions.risk_level)
        },
        ml_predictions: mlReport.predictions,
        recommendations: {
          immediate_actions: mlReport.predictions.recommendations?.immediate_actions || [],
          dietary_suggestions: mlReport.predictions.recommendations?.dietary_suggestions || [],
          lifestyle_changes: mlReport.predictions.recommendations?.lifestyle_changes || [],
          medical_advice: {
            should_consult_doctor: mlReport.predictions.risk_level === 'high',
            urgency: mlReport.predictions.risk_level === 'high' ? 'high' : 'low',
            reasons: mlReport.predictions.risk_level === 'high' 
              ? ["High symptom severity detected", "Professional evaluation recommended"]
              : ["Symptoms are well-managed", "Positive improvement trend"],
            suggested_specialists: mlReport.predictions.risk_level === 'high' 
              ? ["Gastroenterologist", "Registered Dietitian"] 
              : []
          }
        },
        insights: [
          {
            type: 'positive',
            title: "AI Analysis Complete",
            description: `Based on your data, we've identified ${mlReport.predictions.key_factors.length} key factors affecting your symptoms.`,
            action_required: false
          }
        ],
        progress_metrics: {
          symptom_control: Math.round((10 - mlReport.predictions.predicted_severity) * 10),
          quality_of_life: Math.round(mlReport.predictions.confidence * 0.9),
          goal_achievement: 85,
          consistency_score: 91
        }
      };
      
      setReportData(transformedData);
    } catch (error) {
      console.error('Error fetching report data:', error);
      // Keep using mock data on error
    } finally {
      setIsLoading(false);
    }
  };

  const getSeverityColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'moderate': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSeverityDescription = (level: string) => {
    switch (level) {
      case 'low': 
        return "Your symptoms are minimal and well-controlled. Continue your current management approach.";
      case 'medium': 
        return "Your symptoms are noticeable but manageable. Some adjustments to your routine may help.";
      case 'moderate': 
        return "Your symptoms are affecting your daily life. Consider implementing the recommended changes and monitoring closely.";
      case 'high': 
        return "Your symptoms are significantly impacting your quality of life. We recommend consulting with a healthcare provider.";
      default: 
        return "Unable to assess severity. Please ensure you're logging symptoms regularly.";
    }
  };

  const renderSeverityAssessment = () => (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-blue-500" />
          IBS Severity Assessment
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <Badge className={`px-4 py-2 text-lg font-semibold ${getSeverityColor(reportData.severity_assessment.current_level)}`}>
                {reportData.severity_assessment.current_level.toUpperCase()} SEVERITY
              </Badge>
              <div className="flex items-center gap-1">
                {reportData.severity_assessment.trend === 'improving' ? (
                  <TrendingUp className="h-4 w-4 text-green-500" />
                ) : reportData.severity_assessment.trend === 'worsening' ? (
                  <TrendingUp className="h-4 w-4 text-red-500 rotate-180" />
                ) : (
                  <Activity className="h-4 w-4 text-gray-500" />
                )}
                <span className="text-sm text-gray-600 capitalize">{reportData.severity_assessment.trend}</span>
              </div>
            </div>
            <p className="text-gray-700 mb-4">
              {getSeverityDescription(reportData.severity_assessment.current_level)}
            </p>
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <p className="text-sm text-blue-800">
                <strong>Current Score:</strong> {reportData.severity_assessment.score}/10
              </p>
              <Progress 
                value={reportData.severity_assessment.score * 10} 
                className="mt-2"
              />
            </div>
          </div>
          
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">What This Means</h4>
            <div className="space-y-3">
              {reportData.severity_assessment.current_level === 'high' && (
                <div className="bg-red-50 p-3 rounded-lg border border-red-200">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-red-800">Doctor Consultation Recommended</p>
                      <p className="text-xs text-red-700">Consider scheduling an appointment with a gastroenterologist</p>
                    </div>
                  </div>
                </div>
              )}
              
              {reportData.severity_assessment.current_level === 'moderate' && (
                <div className="bg-orange-50 p-3 rounded-lg border border-orange-200">
                  <div className="flex items-start gap-2">
                    <Clock className="h-4 w-4 text-orange-500 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-orange-800">Monitor Closely</p>
                      <p className="text-xs text-orange-700">If symptoms worsen, consider medical consultation</p>
                    </div>
                  </div>
                </div>
              )}
              
              {['low', 'medium'].includes(reportData.severity_assessment.current_level) && (
                <div className="bg-green-50 p-3 rounded-lg border border-green-200">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-green-800">Well Managed</p>
                      <p className="text-xs text-green-700">Continue current approach and lifestyle habits</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderMLPredictions = () => (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-purple-500" />
          AI-Powered Predictions
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">Flare-up Risk</h4>
              <Target className="h-4 w-4 text-blue-500" />
            </div>
            <div className="text-2xl font-bold text-blue-600 mb-1">
              {reportData.ml_predictions.next_flare_probability}%
            </div>
            <p className="text-sm text-gray-600">in the {reportData.ml_predictions.timeline}</p>
            <Progress value={reportData.ml_predictions.next_flare_probability} className="mt-2" />
          </div>
          
          <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg border">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">Confidence Level</h4>
              <Shield className="h-4 w-4 text-green-500" />
            </div>
            <div className="text-2xl font-bold text-green-600 mb-1">
              {reportData.ml_predictions.confidence}%
            </div>
            <p className="text-sm text-gray-600">prediction accuracy</p>
            <Progress value={reportData.ml_predictions.confidence} className="mt-2" />
          </div>
          
          <div className="bg-gradient-to-r from-orange-50 to-yellow-50 p-4 rounded-lg border">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">Expected Severity</h4>
              <BarChart3 className="h-4 w-4 text-orange-500" />
            </div>
            <div className="text-2xl font-bold text-orange-600 mb-1">
              {reportData.ml_predictions.predicted_severity}/10
            </div>
            <p className="text-sm text-gray-600">if symptoms occur</p>
            <Progress value={reportData.ml_predictions.predicted_severity * 10} className="mt-2" />
          </div>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
          <h4 className="font-medium text-purple-900 mb-3">Key Factors Influencing Your Predictions</h4>
          <div className="flex flex-wrap gap-2">
            {reportData.ml_predictions.key_factors.map((factor, index) => (
              <Badge key={index} variant="secondary" className="bg-purple-100 text-purple-800">
                {factor}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderRecommendations = () => (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-yellow-500" />
          Personalized Recommendations
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="immediate" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="immediate">Immediate Actions</TabsTrigger>
            <TabsTrigger value="dietary">Dietary Changes</TabsTrigger>
            <TabsTrigger value="lifestyle">Lifestyle</TabsTrigger>
            <TabsTrigger value="medical">Medical Advice</TabsTrigger>
          </TabsList>
          
          <TabsContent value="immediate" className="space-y-4">
            {reportData.recommendations.immediate_actions.map((action, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{action.action}</h4>
                  <Badge variant={action.priority === 'high' ? 'destructive' : action.priority === 'medium' ? 'default' : 'secondary'}>
                    {action.priority} priority
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 mb-2">{action.explanation}</p>
                <div className="bg-green-50 p-2 rounded border border-green-200">
                  <p className="text-sm text-green-800">
                    <strong>Expected benefit:</strong> {action.expected_benefit}
                  </p>
                </div>
              </div>
            ))}
          </TabsContent>
          
          <TabsContent value="dietary" className="space-y-4">
            {reportData.recommendations.dietary_suggestions.map((suggestion, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant={suggestion.type === 'avoid' ? 'destructive' : suggestion.type === 'include' ? 'default' : 'secondary'}>
                    {suggestion.type}
                  </Badge>
                  <span className="text-sm text-gray-500">{suggestion.timeline}</span>
                </div>
                <div className="mb-2">
                  <div className="flex flex-wrap gap-1">
                    {suggestion.foods.map((food, foodIndex) => (
                      <span key={foodIndex} className="bg-gray-100 px-2 py-1 rounded text-sm">
                        {food}
                      </span>
                    ))}
                  </div>
                </div>
                <p className="text-sm text-gray-600">{suggestion.reason}</p>
              </div>
            ))}
          </TabsContent>
          
          <TabsContent value="lifestyle" className="space-y-4">
            {reportData.recommendations.lifestyle_changes.map((change, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h4 className="font-medium text-gray-900">{change.category}</h4>
                    <p className="text-sm text-gray-600">{change.suggestion}</p>
                  </div>
                  <Badge variant={change.difficulty === 'easy' ? 'default' : change.difficulty === 'moderate' ? 'secondary' : 'destructive'}>
                    {change.difficulty}
                  </Badge>
                </div>
                <div className="bg-blue-50 p-2 rounded border border-blue-200">
                  <p className="text-sm text-blue-800">
                    <strong>Impact:</strong> {change.impact}
                  </p>
                </div>
              </div>
            ))}
          </TabsContent>
          
          <TabsContent value="medical" className="space-y-4">
            <div className={`border rounded-lg p-4 ${reportData.recommendations.medical_advice.should_consult_doctor ? 'border-orange-200 bg-orange-50' : 'border-green-200 bg-green-50'}`}>
              <div className="flex items-center gap-2 mb-3">
                {reportData.recommendations.medical_advice.should_consult_doctor ? (
                  <AlertTriangle className="h-5 w-5 text-orange-500" />
                ) : (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                )}
                <h4 className="font-medium">
                  {reportData.recommendations.medical_advice.should_consult_doctor 
                    ? 'Medical Consultation Recommended' 
                    : 'No Immediate Medical Consultation Needed'}
                </h4>
              </div>
              
              <div className="space-y-2">
                {reportData.recommendations.medical_advice.reasons.map((reason, index) => (
                  <p key={index} className="text-sm text-gray-700">• {reason}</p>
                ))}
              </div>
              
              {reportData.recommendations.medical_advice.suggested_specialists.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm font-medium text-gray-900 mb-1">Suggested Specialists:</p>
                  <div className="flex flex-wrap gap-1">
                    {reportData.recommendations.medical_advice.suggested_specialists.map((specialist, index) => (
                      <Badge key={index} variant="outline">{specialist}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );

  const renderProgressMetrics = () => (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Star className="h-5 w-5 text-yellow-500" />
          Your Progress
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-1">
              {reportData.progress_metrics.symptom_control}%
            </div>
            <p className="text-sm text-gray-600">Symptom Control</p>
            <Progress value={reportData.progress_metrics.symptom_control} className="mt-2" />
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 mb-1">
              {reportData.progress_metrics.quality_of_life}%
            </div>
            <p className="text-sm text-gray-600">Quality of Life</p>
            <Progress value={reportData.progress_metrics.quality_of_life} className="mt-2" />
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600 mb-1">
              {reportData.progress_metrics.goal_achievement}%
            </div>
            <p className="text-sm text-gray-600">Goal Achievement</p>
            <Progress value={reportData.progress_metrics.goal_achievement} className="mt-2" />
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600 mb-1">
              {reportData.progress_metrics.consistency_score}%
            </div>
            <p className="text-sm text-gray-600">Tracking Consistency</p>
            <Progress value={reportData.progress_metrics.consistency_score} className="mt-2" />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderInsights = () => (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5 text-blue-500" />
          Key Insights
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {reportData.insights.map((insight, index) => (
            <div 
              key={index} 
              className={`p-4 rounded-lg border ${
                insight.type === 'positive' ? 'bg-green-50 border-green-200' :
                insight.type === 'warning' ? 'bg-orange-50 border-orange-200' :
                'bg-blue-50 border-blue-200'
              }`}
            >
              <div className="flex items-start gap-3">
                {insight.type === 'positive' ? (
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                ) : insight.type === 'warning' ? (
                  <AlertTriangle className="h-5 w-5 text-orange-500 mt-0.5" />
                ) : (
                  <Lightbulb className="h-5 w-5 text-blue-500 mt-0.5" />
                )}
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-1">{insight.title}</h4>
                  <p className="text-sm text-gray-700">{insight.description}</p>
                  {insight.action_required && (
                    <Button variant="outline" size="sm" className="mt-2">
                      Take Action
                    </Button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50">
          <DashboardHeader title="Health Reports" showBackButton />
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-4 text-gray-600">Generating your personalized report...</p>
              </div>
            </div>
          </main>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader title="Health Reports" showBackButton />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header Section */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Your Health Report</h1>
                <p className="text-gray-600">
                  Comprehensive analysis based on {reportData.user_summary.tracking_days} days of tracking
                </p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Export PDF
                </Button>
                <Button variant="outline" size="sm">
                  <Share2 className="h-4 w-4 mr-2" />
                  Share
                </Button>
              </div>
            </div>
            
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span>Last updated: {reportData.user_summary.last_updated}</span>
              <Badge variant={reportData.user_summary.overall_trend === 'improving' ? 'default' : 'secondary'}>
                {reportData.user_summary.overall_trend}
              </Badge>
            </div>
          </div>

          {/* Report Content */}
          {renderSeverityAssessment()}
          {renderMLPredictions()}
          {renderRecommendations()}
          {renderProgressMetrics()}
          {renderInsights()}
          
          {/* Footer */}
          <div className="bg-white p-6 rounded-lg border">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">
                This report is generated using AI and machine learning based on your personal health data.
              </p>
              <p className="text-xs text-gray-500">
                Always consult with healthcare professionals for medical decisions. This report is for informational purposes only.
              </p>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}