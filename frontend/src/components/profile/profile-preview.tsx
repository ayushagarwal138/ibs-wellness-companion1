'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Brain, 
  Shield, 
  AlertTriangle, 
  Lightbulb, 
  Target, 
  TrendingUp,
  Heart,
  Activity,
  Utensils,
  Clock,
  CheckCircle,
  Star,
  BarChart3,
  User,
  Calendar,
  Zap
} from 'lucide-react';

interface ProfilePredictions {
  risk_assessment: {
    level: string;
    score: number;
    description: string;
    confidence: number;
  };
  trigger_analysis: {
    primary_category: string;
    insights: string[];
  };
  lifestyle_insights: Array<{
    category: string;
    insight: string;
    recommendation: string;
    priority: string;
  }>;
  dietary_recommendations: Array<{
    type: string;
    title: string;
    description: string;
    priority: string;
  }>;
  management_strategy: {
    strategy: string;
    approach: string;
    timeline: string;
  };
  predicted_severity: string;
  personalized_tips: string[];
}

interface ProfilePreviewProps {
  onboardingData?: any;
  predictions?: ProfilePredictions;
  completionPercentage?: number;
}

export function ProfilePreview({ 
  onboardingData, 
  predictions, 
  completionPercentage = 0 
}: ProfilePreviewProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [profilePredictions, setProfilePredictions] = useState<ProfilePredictions | null>(predictions || null);

  useEffect(() => {
    if (onboardingData && !predictions) {
      generatePredictions();
    }
  }, [onboardingData, predictions]);

  const generatePredictions = async () => {
    if (!onboardingData) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8001'}/api/v1/onboarding/predictions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(onboardingData)
      });

      if (response.ok) {
        const data = await response.json();
        setProfilePredictions(data.predictions);
      }
    } catch (error) {
      console.error('Failed to generate predictions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'moderate':
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-8 text-center">
            <Brain className="h-12 w-12 text-blue-500 mx-auto mb-4 animate-pulse" />
            <h3 className="text-lg font-semibold mb-2">Generating Your Profile Insights</h3>
            <p className="text-gray-600">Our AI is analyzing your responses to create personalized recommendations...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!profilePredictions) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-8 text-center">
            <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Complete Your Profile</h3>
            <p className="text-gray-600 mb-4">
              Complete the onboarding questionnaire to get personalized AI-powered insights and recommendations.
            </p>
            <Button onClick={() => window.location.href = '/onboarding'}>
              Start Questionnaire
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Profile Completion */}
      {completionPercentage < 100 && (
        <Card className="border-l-4 border-l-orange-500 bg-orange-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-800">
              <Target className="h-5 w-5" />
              Profile Completion
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Progress</span>
                <span className="font-medium">{completionPercentage}%</span>
              </div>
              <Progress value={completionPercentage} className="h-2" />
              <p className="text-sm text-orange-700">
                Complete your profile to unlock more personalized insights and recommendations.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* AI Risk Assessment */}
      <Card className="border-l-4 border-l-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-blue-600" />
            AI Health Assessment
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Risk Level */}
            <div className="text-center">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getRiskColor(profilePredictions.risk_assessment.level)}`}>
                <Shield className="h-4 w-4 mr-1" />
                {profilePredictions.risk_assessment.level.toUpperCase()} RISK
              </div>
              <p className="text-xs text-gray-600 mt-1">Current risk level</p>
            </div>

            {/* Confidence Score */}
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {Math.round(profilePredictions.risk_assessment.confidence * 100)}%
              </div>
              <p className="text-xs text-gray-600">Prediction confidence</p>
              <Progress value={profilePredictions.risk_assessment.confidence * 100} className="mt-2 h-2" />
            </div>

            {/* Predicted Severity */}
            <div className="text-center">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getRiskColor(profilePredictions.predicted_severity)}`}>
                <Activity className="h-4 w-4 mr-1" />
                {profilePredictions.predicted_severity.toUpperCase()}
              </div>
              <p className="text-xs text-gray-600 mt-1">Predicted severity</p>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg border border-blue-200">
            <p className="text-sm text-gray-700">{profilePredictions.risk_assessment.description}</p>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Insights Tabs */}
      <Tabs defaultValue="insights" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="diet">Diet</TabsTrigger>
          <TabsTrigger value="management">Management</TabsTrigger>
          <TabsTrigger value="tips">Tips</TabsTrigger>
        </TabsList>

        <TabsContent value="insights" className="space-y-4">
          {/* Trigger Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-500" />
                Trigger Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="capitalize">
                    {profilePredictions.trigger_analysis.primary_category}
                  </Badge>
                  <span className="text-sm text-gray-600">Primary category</span>
                </div>
                <div className="space-y-2">
                  {profilePredictions.trigger_analysis.insights.map((insight, index) => (
                    <div key={index} className="flex items-start gap-2 p-3 bg-orange-50 rounded-lg">
                      <Lightbulb className="h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-orange-800">{insight}</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Lifestyle Insights */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Heart className="h-5 w-5 text-purple-500" />
                Lifestyle Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {profilePredictions.lifestyle_insights.map((insight, index) => (
                  <div key={index} className="border border-purple-200 rounded-lg p-4 bg-purple-50">
                    <div className="flex items-center justify-between mb-2">
                      <Badge variant="outline" className="text-xs">
                        {insight.category}
                      </Badge>
                      <Badge className={`text-xs ${getPriorityColor(insight.priority)}`}>
                        {insight.priority}
                      </Badge>
                    </div>
                    <h4 className="font-medium text-purple-900 mb-1">{insight.insight}</h4>
                    <p className="text-sm text-purple-700">{insight.recommendation}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="diet" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Utensils className="h-5 w-5 text-green-500" />
                Dietary Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {profilePredictions.dietary_recommendations.map((rec, index) => (
                  <div key={index} className="border border-green-200 rounded-lg p-4 bg-green-50">
                    <div className="flex items-center justify-between mb-2">
                      <Badge variant="outline" className="text-xs">
                        {rec.type}
                      </Badge>
                      <Badge className={`text-xs ${getPriorityColor(rec.priority)}`}>
                        {rec.priority}
                      </Badge>
                    </div>
                    <h4 className="font-medium text-green-900 mb-1">{rec.title}</h4>
                    <p className="text-sm text-green-700">{rec.description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="management" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-blue-500" />
                Management Strategy
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <h4 className="font-medium text-blue-900 mb-2 flex items-center gap-2">
                      <Zap className="h-4 w-4" />
                      Strategy
                    </h4>
                    <p className="text-sm text-blue-700">{profilePredictions.management_strategy.strategy}</p>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <h4 className="font-medium text-blue-900 mb-2 flex items-center gap-2">
                      <Clock className="h-4 w-4" />
                      Timeline
                    </h4>
                    <p className="text-sm text-blue-700">{profilePredictions.management_strategy.timeline}</p>
                  </div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <h4 className="font-medium text-blue-900 mb-2 flex items-center gap-2">
                    <BarChart3 className="h-4 w-4" />
                    Approach
                  </h4>
                  <p className="text-sm text-blue-700">{profilePredictions.management_strategy.approach}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tips" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5 text-yellow-500" />
                Personalized Tips
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {profilePredictions.personalized_tips.map((tip, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                    <CheckCircle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-yellow-800">{tip}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Action Buttons */}
      <div className="flex gap-3 pt-4">
        <Button onClick={() => window.location.href = '/dashboard'} className="flex-1">
          <BarChart3 className="h-4 w-4 mr-2" />
          View Dashboard
        </Button>
        <Button variant="outline" onClick={() => window.location.href = '/onboarding'} className="flex-1">
          <User className="h-4 w-4 mr-2" />
          Update Profile
        </Button>
      </div>
    </div>
  );
}