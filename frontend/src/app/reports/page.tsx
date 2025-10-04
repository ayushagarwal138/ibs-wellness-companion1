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
import { downloadPDFReport } from '@/lib/pdf-generator';
import { ShareReportModal } from '@/components/reports/share-report-modal';
import { IndianDietRecommendations } from '@/components/reports/indian-diet-recommendations';
import { LifestyleRecommendations } from '@/components/reports/lifestyle-recommendations';
import { formatSmartNumber, formatConfidence, formatProbability } from '@/lib/number-formatting';

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
    confidence: 0.78,
    next_flare_probability: 0.35,
    predicted_severity: 4.25,
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
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'day' | 'week' | 'month'>('month');
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);

  // Helper functions for personalization
  const calculateTrackingDays = (createdAt?: string): number => {
    if (!createdAt) return 30;
    const created = new Date(createdAt);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - created.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return Math.min(diffDays, 365); // Cap at 1 year
  };

  const determineTrend = (predictions: any): 'improving' | 'stable' | 'worsening' => {
    if (!predictions) return 'stable';
    const riskLevel = predictions.risk_level;
    const confidence = predictions.confidence || 0.5;
    
    if (riskLevel === 'low' && confidence > 0.7) return 'improving';
    if (riskLevel === 'high' && confidence > 0.7) return 'worsening';
    return 'stable';
  };

  const getPersonalizedSeverityDescription = (riskLevel: string, userProfile: any): string => {
    const name = userProfile?.first_name || userProfile?.name || 'User';
    
    switch (riskLevel) {
      case 'low':
        return `Great news, ${name}! Your symptoms are well-controlled. Continue with your current management approach.`;
      case 'medium':
        return `${name}, your symptoms are at a moderate level. Consider implementing the recommended lifestyle changes.`;
      case 'high':
        return `${name}, your symptoms require attention. Please consider consulting with your healthcare provider.`;
      default:
        return `${name}, continue monitoring your symptoms and following your management plan.`;
    }
  };

  const generatePersonalizedInsights = (mlReport: any, userProfile: any): Array<{
    type: 'positive' | 'warning' | 'info';
    title: string;
    description: string;
    action_required: boolean;
  }> => {
    const insights = [];
    const name = userProfile?.first_name || userProfile?.name || 'User';
    
    // Generate insights based on predictions
    if (mlReport.predictions?.risk_level === 'low') {
      insights.push({
        type: 'positive' as const,
        title: `Excellent Progress, ${name}!`,
        description: 'Your symptom management is working well. Keep up the great work!',
        action_required: false
      });
    }
    
    if (mlReport.predictions?.next_flare_probability > 0.5) {
      insights.push({
        type: 'warning' as const,
        title: 'Potential Flare Risk',
        description: 'Our analysis suggests increased flare risk. Consider implementing preventive measures.',
        action_required: true
      });
    }
    
    insights.push({
      type: 'info' as const,
      title: 'Tracking Consistency',
      description: 'Regular symptom tracking helps improve prediction accuracy and personalized recommendations.',
      action_required: false
    });
    
    return insights;
  };

  // Metric calculation functions
  const calculateSymptomControl = (mlReport: any): number => {
    if (!mlReport.predictions) return 70;
    const riskLevel = mlReport.predictions.risk_level;
    switch (riskLevel) {
      case 'low': return 85;
      case 'medium': return 70;
      case 'high': return 45;
      default: return 70;
    }
  };

  const calculateQualityOfLife = (mlReport: any, userProfile: any): number => {
    const baseScore = calculateSymptomControl(mlReport);
    // Adjust based on tracking consistency
    const trackingDays = calculateTrackingDays(userProfile?.created_at);
    const consistencyBonus = Math.min(trackingDays / 30 * 10, 15);
    return Math.round(Math.min(baseScore + consistencyBonus, 100));
  };

  const calculateGoalAchievement = (mlReport: any): number => {
    if (!mlReport.predictions) return 75;
    const confidence = mlReport.predictions.confidence || 0.5;
    return Math.round(confidence * 100);
  };

  const calculateConsistencyScore = (mlReport: any, userProfile: any): number => {
    const trackingDays = calculateTrackingDays(userProfile?.created_at);
    return Math.min(Math.round((trackingDays / 30) * 100), 100);
  };

  const fetchReportData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Fetch real ML predictions and recommendations
      const mlReport = await mlService.generateReport(selectedTimeframe);
      
      // Get user profile data for personalization (optional)
      let userProfile = null;
      try {
        const token = localStorage.getItem('access_token');
        if (token) {
          const response = await fetch('http://localhost:8000/api/v1/profile', {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          if (response.ok) {
            userProfile = await response.json();
          } else {
            console.warn('Could not fetch user profile - using default data:', response.status);
          }
        } else {
          console.warn('No authentication token found - using default profile data');
        }
      } catch (error) {
        console.warn('Could not fetch user profile - using default data:', error);
      }

      // Generate personalized insights based on user data
      const personalizedInsights = generatePersonalizedInsights(mlReport, userProfile);
      
      // Transform the API response to match our ReportData interface
      const transformedData: ReportData = {
        user_summary: {
          name: userProfile?.first_name || userProfile?.name || "User",
          tracking_days: calculateTrackingDays(userProfile?.created_at),
          last_updated: new Date().toLocaleDateString(),
          overall_trend: determineTrend(mlReport.predictions) as 'improving' | 'stable' | 'declining'
        },
        severity_assessment: {
          current_level: mlReport.predictions?.risk_level || 'medium',
          trend: determineTrend(mlReport.predictions),
          score: mlReport.predictions?.predicted_severity || 5,
          description: getPersonalizedSeverityDescription(mlReport.predictions?.risk_level || 'medium', userProfile)
        },
        ml_predictions: {
          risk_level: mlReport.predictions?.risk_level || 'medium',
          confidence: mlReport.predictions?.confidence || 0.78,
          next_flare_probability: mlReport.predictions?.next_flare_probability || 0.35,
          predicted_severity: mlReport.predictions?.predicted_severity || 4.25,
          timeline: mlReport.predictions?.timeline || 'Next week',
          key_factors: mlReport.predictions?.key_factors || ['Stress levels', 'Dietary patterns']
        },
        recommendations: {
          immediate_actions: mlReport.predictions?.recommendations?.immediate_actions || [
            {
              action: 'Continue tracking symptoms daily',
              priority: 'high' as const,
              explanation: 'Consistent tracking helps identify patterns',
              expected_benefit: 'Better symptom management'
            }
          ],
          dietary_suggestions: mlReport.predictions?.recommendations?.dietary_suggestions || [
            {
              type: 'avoid' as const,
              foods: ['High FODMAP foods'],
              reason: 'May trigger symptoms',
              timeline: '2-4 weeks'
            }
          ],
          lifestyle_changes: mlReport.predictions?.recommendations?.lifestyle_changes || [
            {
              category: 'Stress Management',
              suggestion: 'Practice daily meditation',
              difficulty: 'easy' as const,
              impact: 'Reduces stress-related symptoms'
            }
          ],
          medical_advice: {
            should_consult_doctor: false,
            urgency: 'low' as const,
            reasons: [],
            suggested_specialists: []
          }
        },
        insights: personalizedInsights,
        progress_metrics: {
          symptom_control: calculateSymptomControl(mlReport),
          quality_of_life: calculateQualityOfLife(mlReport, userProfile),
          goal_achievement: calculateGoalAchievement(mlReport),
          consistency_score: calculateConsistencyScore(mlReport, userProfile)
        }
      };


      setReportData(transformedData);
    } catch (error) {
      console.error('Error fetching report data:', error);
      setError('Failed to load report data. Please try again.');
      
      // Provide comprehensive fallback data
      setReportData({
        user_summary: {
          name: "User",
          tracking_days: 30,
          last_updated: new Date().toLocaleDateString(),
          overall_trend: "stable"
        },
        severity_assessment: {
          current_level: "medium",
          trend: "stable",
          score: 5,
          description: "Your symptoms appear to be at a moderate level. Continue monitoring and following your management plan."
        },
        ml_predictions: {
          risk_level: 'medium',
          confidence: 0.78,
          next_flare_probability: 0.35,
          predicted_severity: 4.25,
          timeline: 'Next week',
          key_factors: ['Stress levels', 'Dietary patterns', 'Sleep quality']
        },
        recommendations: {
          immediate_actions: [
            {
              action: 'Continue tracking symptoms and food intake daily',
              priority: 'high',
              explanation: 'Consistent tracking is essential for identifying patterns',
              expected_benefit: 'Better symptom management and more accurate predictions'
            },
            {
              action: 'Practice stress reduction techniques',
              priority: 'medium',
              explanation: 'Stress is a common IBS trigger',
              expected_benefit: 'Reduced symptom frequency and severity'
            }
          ],
          dietary_suggestions: [
            {
              type: 'avoid',
              foods: ['High FODMAP foods', 'Dairy products', 'Gluten'],
              reason: 'Common IBS triggers that affect most patients',
              timeline: '2-4 weeks trial elimination'
            },
            {
              type: 'include',
              foods: ['Probiotics', 'Soluble fiber', 'Peppermint tea'],
              reason: 'May help improve digestive health',
              timeline: 'Gradual introduction over 1-2 weeks'
            }
          ],
          lifestyle_changes: [
            {
              category: 'Stress Management',
              suggestion: 'Practice deep breathing exercises for 10 minutes daily',
              difficulty: 'easy',
              impact: 'Reduces stress-related IBS symptoms'
            },
            {
              category: 'Exercise',
              suggestion: 'Take a 20-30 minute walk after meals',
              difficulty: 'easy',
              impact: 'Improves digestion and reduces bloating'
            },
            {
              category: 'Sleep',
              suggestion: 'Maintain consistent sleep schedule (7-9 hours)',
              difficulty: 'moderate',
              impact: 'Better overall health and symptom management'
            }
          ],
          medical_advice: {
            should_consult_doctor: false,
            urgency: 'low',
            reasons: [],
            suggested_specialists: []
          }
        },
        insights: [
          {
            type: 'info',
            title: 'Symptom Patterns',
            description: 'Your symptom patterns suggest stress may be a significant trigger',
            action_required: true
          },
          {
            type: 'info',
            title: 'Food Diary',
            description: 'Consider keeping a detailed food diary to identify dietary triggers',
            action_required: true
          },
          {
            type: 'positive',
            title: 'Meal Timing',
            description: 'Regular meal timing appears to help with symptom management',
            action_required: false
          }
        ],
        progress_metrics: {
          symptom_control: 65,
          quality_of_life: 70,
          goal_achievement: 75,
          consistency_score: 80
        }
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // In production, fetch real ML predictions and report data
    fetchReportData();
  }, [selectedTimeframe]);

  const handleExportPDF = () => {
    // Transform the report data to match the PDF generator interface
    const pdfReportData = {
      user_summary: {
        name: reportData.user_summary.name,
        ibs_type: "Mixed IBS", // Default value
        diagnosis_date: "2023-01-01", // Default value
        last_updated: reportData.user_summary.last_updated,
        overall_trend: reportData.user_summary.overall_trend
      },
      severity_assessment: {
        current_score: reportData.severity_assessment.score,
        trend: reportData.severity_assessment.trend,
        risk_level: reportData.severity_assessment.current_level
      },
      ml_predictions: {
        flareup_risk: reportData.ml_predictions.next_flare_probability,
        severity_forecast: [reportData.ml_predictions.predicted_severity],
        confidence_score: reportData.ml_predictions.confidence
      },
      progress_metrics: {
        symptom_control: reportData.progress_metrics.symptom_control,
        quality_of_life: reportData.progress_metrics.quality_of_life,
        goal_achievement: reportData.progress_metrics.goal_achievement,
        consistency_score: reportData.progress_metrics.consistency_score
      }
    };
    
    downloadPDFReport(pdfReportData);
  };

  const getSuggestedSpecialists = (riskLevel: string, userProfile: any): string[] => {
    const specialists = [];
    
    if (riskLevel === 'high' || riskLevel === 'moderate') {
      specialists.push("Gastroenterologist");
      specialists.push("Registered Dietitian");
    }
    
    if (riskLevel === 'high') {
      specialists.push("Mental Health Counselor (for stress management)");
    }

    return specialists;
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
                <strong>Current Score:</strong> {formatSmartNumber(reportData.severity_assessment.score)}/10
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
              {formatProbability(reportData.ml_predictions.next_flare_probability)}
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
              {formatConfidence(reportData.ml_predictions.confidence)}
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
              {formatSmartNumber(reportData.ml_predictions.predicted_severity)}/10
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
                    {(suggestion.foods || []).map((food, foodIndex) => (
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
              {formatSmartNumber(reportData.progress_metrics.symptom_control)}%
            </div>
            <p className="text-sm text-gray-600">Symptom Control</p>
            <Progress value={reportData.progress_metrics.symptom_control} className="mt-2" />
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 mb-1">
              {formatSmartNumber(reportData.progress_metrics.quality_of_life)}%
            </div>
            <p className="text-sm text-gray-600">Quality of Life</p>
            <Progress value={reportData.progress_metrics.quality_of_life} className="mt-2" />
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600 mb-1">
              {formatSmartNumber(reportData.progress_metrics.goal_achievement)}%
            </div>
            <p className="text-sm text-gray-600">Goal Achievement</p>
            <Progress value={reportData.progress_metrics.goal_achievement} className="mt-2" />
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600 mb-1">
              {formatSmartNumber(reportData.progress_metrics.consistency_score)}%
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
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={handleExportPDF}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export PDF
                </Button>
                <Button variant="outline" size="sm" onClick={() => setIsShareModalOpen(true)}>
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
          <Tabs defaultValue="overview" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="diet">Diet Recommendations</TabsTrigger>
              <TabsTrigger value="lifestyle">Lifestyle Guide</TabsTrigger>
              <TabsTrigger value="insights">Insights</TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview" className="space-y-6">
              {renderSeverityAssessment()}
              {renderMLPredictions()}
              {renderRecommendations()}
              {renderProgressMetrics()}
            </TabsContent>
            
            <TabsContent value="diet" className="space-y-6">
              <IndianDietRecommendations 
                userProfile={{
                  ibsType: reportData.severity_assessment.current_level === 'high' ? 'IBS-D' : 'IBS-M',
                  severityLevel: reportData.severity_assessment.current_level,
                  triggers: reportData.ml_predictions.key_factors,
                  preferences: ['Low FODMAP', 'Anti-inflammatory']
                }}
              />
            </TabsContent>
            
            <TabsContent value="lifestyle" className="space-y-6">
              <LifestyleRecommendations 
                userProfile={{
                  ibsType: reportData.severity_assessment.current_level === 'high' ? 'IBS-D' : 'IBS-M',
                  severityLevel: reportData.severity_assessment.current_level,
                  stressLevel: 7,
                  sleepQuality: 5,
                  exerciseLevel: 'Low',
                  currentSymptoms: ['Bloating', 'Abdominal pain', 'Irregular bowel movements'],
                  triggers: reportData.ml_predictions.key_factors
                }}
              />
            </TabsContent>
            
            <TabsContent value="insights" className="space-y-6">
              {renderInsights()}
            </TabsContent>
          </Tabs>
          
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
      
      {/* Share Modal */}
      <ShareReportModal 
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
        reportData={reportData}
      />
    </ProtectedRoute>
  );
}