'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useRouter } from 'next/navigation';
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
  Zap,
  Sparkles,
  Award,
  ArrowRight
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
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [profilePredictions, setProfilePredictions] = useState<ProfilePredictions | null>(predictions || null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (isClient && onboardingData && !predictions) {
      generatePredictions();
    }
  }, [onboardingData, predictions, isClient]);

  const generatePredictions = async () => {
    if (!onboardingData || !isClient) return;
    
    setIsLoading(true);
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      if (!token) {
        console.error('No access token found');
        return;
      }

      const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000'}/api/v1/onboarding/predictions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
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
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-transparent to-purple-50/30 pointer-events-none" />
          <CardContent className="relative p-8 text-center">
            <div className="p-4 bg-blue-100 rounded-full w-fit mx-auto mb-6">
              <Brain className="h-12 w-12 text-blue-600 animate-pulse" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Generating Your Profile Insights</h3>
            <p className="text-gray-600 mb-6">Our AI is analyzing your responses to create personalized recommendations...</p>
            <div className="w-full max-w-xs mx-auto">
              <Progress value={75} className="h-3 bg-gray-200 rounded-full" />
              <p className="text-sm text-gray-500 mt-2">Analyzing patterns...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!profilePredictions) {
    return (
      <div className="space-y-6">
        <Card className="relative overflow-hidden border-2 border-dashed border-gray-300">
          <div className="absolute inset-0 bg-gradient-to-br from-gray-50/50 via-transparent to-blue-50/30 pointer-events-none" />
          <CardContent className="relative p-8 text-center">
            <div className="p-4 bg-gray-100 rounded-full w-fit mx-auto mb-6">
              <User className="h-12 w-12 text-gray-500" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Complete Your Profile</h3>
            <p className="text-gray-600 mb-6">
              Complete the onboarding questionnaire to get personalized AI-powered insights and recommendations.
            </p>
            <Button 
              onClick={() => window.location.href = '/onboarding'}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
            >
              <Sparkles className="h-4 w-4 mr-2" />
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
        <Card className="relative overflow-hidden border-l-4 border-l-orange-500">
          <div className="absolute inset-0 bg-gradient-to-br from-orange-50/50 via-transparent to-yellow-50/30 pointer-events-none" />
          <CardHeader className="relative bg-orange-50 border-b border-orange-100">
            <CardTitle className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-xl">
                <Target className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-orange-900">Profile Completion</h3>
                <p className="text-base text-orange-700 font-normal">Unlock more personalized insights</p>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="relative p-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-base font-medium text-gray-700">Progress</span>
                <Badge className="bg-orange-100 text-orange-800 font-bold">
                  {completionPercentage}%
                </Badge>
              </div>
              <div className="relative">
                <Progress value={completionPercentage} className="h-3 bg-gray-200 rounded-full" />
                <div className="absolute inset-0 bg-gradient-to-r from-orange-400 to-yellow-400 rounded-full opacity-20 animate-pulse" />
              </div>
              <p className="text-base text-orange-700 font-medium">
                Complete your profile to unlock more personalized insights and recommendations.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Enhanced AI Risk Assessment */}
      <Card className="relative overflow-hidden border-l-4 border-l-blue-500">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-transparent to-indigo-50/30 pointer-events-none" />
        <CardHeader className="relative bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-100">
          <CardTitle className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-xl shadow-sm">
              <Brain className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-blue-900">AI Health Assessment</h3>
              <p className="text-base text-blue-700 font-normal">Personalized risk analysis and insights</p>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="relative p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Enhanced Risk Level */}
            <div className="text-center p-4 bg-gradient-to-br from-white to-blue-50 rounded-xl border border-blue-200 min-w-0">
              <div className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-bold border-2 shadow-sm break-words ${getRiskColor(profilePredictions.risk_assessment.level)}`}>
                <Shield className="h-4 w-4 mr-2 flex-shrink-0" />
                <span className="truncate">{profilePredictions.risk_assessment.level.toUpperCase()} RISK</span>
              </div>
              <p className="text-sm font-medium text-gray-600 mt-2 uppercase tracking-wide break-words">Current Risk Level</p>
            </div>

            {/* Enhanced Confidence Score */}
            <div className="text-center p-4 bg-gradient-to-br from-white to-green-50 rounded-xl border border-green-200 min-w-0">
              <div className="text-3xl font-bold text-green-600 mb-1">
                {Math.round(profilePredictions.risk_assessment.confidence * 100)}%
              </div>
              <p className="text-sm font-medium text-gray-600 mb-2 uppercase tracking-wide break-words">Prediction Confidence</p>
              <Progress value={profilePredictions.risk_assessment.confidence * 100} className="h-2 bg-gray-200" />
            </div>

            {/* Enhanced Predicted Severity */}
            <div className="text-center p-4 bg-gradient-to-br from-white to-purple-50 rounded-xl border border-purple-200 min-w-0">
              <div className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-bold border-2 shadow-sm break-words ${getRiskColor(profilePredictions.predicted_severity)}`}>
                <Activity className="h-4 w-4 mr-2 flex-shrink-0" />
                <span className="truncate">{profilePredictions.predicted_severity.toUpperCase()}</span>
              </div>
              <p className="text-sm font-medium text-gray-600 mt-2 uppercase tracking-wide break-words">Predicted Severity</p>
            </div>
          </div>

          <div className="p-5 bg-gradient-to-r from-white to-blue-50 rounded-xl border-2 border-blue-200">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-blue-100 rounded-lg flex-shrink-0">
                <Lightbulb className="h-4 w-4 text-blue-600" />
              </div>
              <p className="text-base text-gray-700 font-medium leading-relaxed break-words">{profilePredictions.risk_assessment.description}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Enhanced Detailed Insights Tabs */}
      <Card className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-gray-50/30 via-transparent to-purple-50/20 pointer-events-none" />
        <CardContent className="relative p-6">
          <Tabs defaultValue="insights" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4 bg-gray-100 p-1 rounded-xl">
              <TabsTrigger value="insights" className="rounded-lg font-semibold">Insights</TabsTrigger>
              <TabsTrigger value="diet" className="rounded-lg font-semibold">Diet</TabsTrigger>
              <TabsTrigger value="management" className="rounded-lg font-semibold">Management</TabsTrigger>
              <TabsTrigger value="tips" className="rounded-lg font-semibold">Tips</TabsTrigger>
            </TabsList>

            <TabsContent value="insights" className="space-y-6">
              {/* Enhanced Trigger Analysis */}
              <Card className="border-2 border-orange-200">
                <CardHeader className="bg-gradient-to-r from-orange-50 to-yellow-50 border-b border-orange-100">
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-2 bg-orange-100 rounded-xl">
                      <AlertTriangle className="h-5 w-5 text-orange-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-orange-900">Trigger Analysis</h3>
                      <p className="text-sm text-orange-700 font-normal">Identify your primary symptom triggers</p>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6 space-y-4">
                  <div className="flex items-center gap-3 p-3 bg-orange-50 rounded-xl border border-orange-200">
                    <Badge variant="outline" className="capitalize bg-orange-100 text-orange-800 border-orange-300 font-semibold">
                      {profilePredictions.trigger_analysis.primary_category}
                    </Badge>
                    <span className="text-sm font-medium text-orange-700">Primary category</span>
                  </div>
                  <div className="space-y-3">
                    {profilePredictions.trigger_analysis.insights.map((insight, index) => (
                      <div key={index} className="flex items-start gap-3 p-4 bg-gradient-to-r from-orange-50 to-yellow-50 rounded-xl border border-orange-200">
                        <div className="p-1 bg-orange-100 rounded-lg">
                          <Lightbulb className="h-4 w-4 text-orange-600" />
                        </div>
                        <span className="text-sm text-orange-800 font-medium leading-relaxed">{insight}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Enhanced Lifestyle Insights */}
              <Card className="border-2 border-purple-200">
                <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 border-b border-purple-100">
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-2 bg-purple-100 rounded-xl">
                      <Heart className="h-5 w-5 text-purple-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-purple-900">Lifestyle Insights</h3>
                      <p className="text-sm text-purple-700 font-normal">Personalized lifestyle recommendations</p>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="space-y-4">
                    {profilePredictions.lifestyle_insights.map((insight, index) => (
                      <div key={index} className="p-5 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border-2 border-purple-200">
                        <div className="flex items-center justify-between mb-3">
                          <Badge variant="outline" className="text-xs bg-purple-100 text-purple-800 border-purple-300 font-semibold">
                            {insight.category}
                          </Badge>
                          <Badge className={`text-xs font-bold ${getPriorityColor(insight.priority)}`}>
                            {insight.priority}
                          </Badge>
                        </div>
                        <h4 className="font-bold text-purple-900 mb-2 text-base">{insight.insight}</h4>
                        <p className="text-sm text-purple-700 leading-relaxed">{insight.recommendation}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="diet" className="space-y-6">
              <Card className="border-2 border-green-200">
                <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 border-b border-green-100">
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded-xl">
                      <Utensils className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-green-900">Dietary Recommendations</h3>
                      <p className="text-sm text-green-700 font-normal">Personalized nutrition guidance</p>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {profilePredictions.dietary_recommendations.map((rec, index) => (
                      <div key={index} className="p-5 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border-2 border-green-200">
                        <div className="flex items-center justify-between mb-3">
                          <Badge variant="outline" className="text-xs bg-green-100 text-green-800 border-green-300 font-semibold">
                            {rec.type}
                          </Badge>
                          <Badge className={`text-xs font-bold ${getPriorityColor(rec.priority)}`}>
                            {rec.priority}
                          </Badge>
                        </div>
                        <h4 className="font-bold text-green-900 mb-2 text-base">{rec.title}</h4>
                        <p className="text-sm text-green-700 leading-relaxed">{rec.description}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="management" className="space-y-6">
              <Card className="border-2 border-blue-200">
                <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-100">
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 rounded-xl">
                      <Target className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-blue-900">Management Strategy</h3>
                      <p className="text-sm text-blue-700 font-normal">Your personalized wellness plan</p>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="space-y-6">
                    <div className="p-5 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200">
                      <h4 className="font-bold text-blue-900 mb-3 flex items-center gap-2">
                        <div className="p-1 bg-blue-100 rounded-lg">
                          <Target className="h-4 w-4 text-blue-600" />
                        </div>
                        Strategy: {profilePredictions.management_strategy.strategy}
                      </h4>
                      <p className="text-sm text-blue-700 mb-4 leading-relaxed">{profilePredictions.management_strategy.approach}</p>
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-blue-600" />
                        <span className="text-sm font-medium text-blue-800">Timeline: {profilePredictions.management_strategy.timeline}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="tips" className="space-y-6">
              <Card className="border-2 border-yellow-200">
                <CardHeader className="bg-gradient-to-r from-yellow-50 to-orange-50 border-b border-yellow-100">
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-2 bg-yellow-100 rounded-xl">
                      <Star className="h-5 w-5 text-yellow-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-yellow-900">Personalized Tips</h3>
                      <p className="text-sm text-yellow-700 font-normal">Daily wellness recommendations</p>
                    </div>
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {profilePredictions.personalized_tips.map((tip, index) => (
                      <div key={index} className="flex items-start gap-3 p-4 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl border-2 border-yellow-200">
                        <div className="p-1 bg-yellow-100 rounded-lg">
                          <CheckCircle className="h-4 w-4 text-yellow-600" />
                        </div>
                        <span className="text-sm text-yellow-800 font-medium leading-relaxed">{tip}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Enhanced Action Buttons */}
      <div className="flex gap-4 pt-4">
        <Button 
          onClick={() => router.push('/dashboard')} 
          className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
        >
          <BarChart3 className="h-4 w-4 mr-2" />
          View Dashboard
        </Button>
        <Button 
          variant="outline" 
          onClick={() => router.push('/onboarding')} 
          className="flex-1 border-2 hover:bg-gray-50 font-semibold py-3 rounded-xl transition-all duration-200"
        >
          <User className="h-4 w-4 mr-2" />
          Update Profile
        </Button>
      </div>
    </div>
  );
}