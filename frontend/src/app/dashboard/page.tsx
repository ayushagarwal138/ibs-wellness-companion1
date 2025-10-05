'use client';

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ProtectedRoute } from "@/components/protected-route";
import { ErrorBoundary } from "@/components/error-boundary";
import { DashboardHeader } from "@/components/layout/dashboard-header";
import MainDashboard from "@/components/dashboard/main-dashboard";
import DynamicDashboard from "@/components/dashboard/dashboard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Activity, 
  Utensils, 
  BarChart3, 
  Brain, 
  Target, 
  Calendar,
  Plus,
  TrendingUp,
  Heart,
  Zap,
  CheckCircle,
  ArrowRight,
  Settings,
  User
} from "lucide-react";
import { useAuth } from "@/contexts/auth-context";
import { profileCompletionService, ProfileCompletionResult } from "@/services/profile-completion-service";

export default function DashboardPage() {
  const { user } = useAuth();
  const [profileCompletion, setProfileCompletion] = useState(0);
  const [isOnboardingComplete, setIsOnboardingComplete] = useState(false);
  const [isLoadingCompletion, setIsLoadingCompletion] = useState(true);

  useEffect(() => {
    // Check onboarding status
    const checkOnboardingStatus = async () => {
      try {
        setIsLoadingCompletion(true);
        const completionData = await profileCompletionService.checkProfileCompletion();
        setProfileCompletion(completionData.completionPercentage);
        setIsOnboardingComplete(completionData.completionPercentage >= 80);
      } catch (error) {
        console.error('Error checking onboarding status:', error);
        // Fallback to basic completion check
        setProfileCompletion(0);
        setIsOnboardingComplete(false);
      } finally {
        setIsLoadingCompletion(false);
      }
    };

    if (user) {
      checkOnboardingStatus();
    }
  }, [user]);

  return (
    <ProtectedRoute>
      <ErrorBoundary>
        <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50/30">
          <DashboardHeader />
        
        <main className="container mx-auto px-4 py-8 space-y-8">
          {/* Welcome Section */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Welcome back, {user?.first_name || 'there'}! 👋
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Track your wellness journey with AI-powered insights and personalized recommendations.
            </p>
          </div>

          {/* Profile Completion Tracker */}
          {!isLoadingCompletion && profileCompletion < 100 && (
            <Card className="border-l-4 border-l-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5 text-blue-600" />
                  Complete Your Profile
                  <Badge variant="outline" className="ml-auto">
                    {profileCompletion}% Complete
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Progress value={profileCompletion} className="h-3" />
                <div className="flex items-center justify-between">
                  <p className="text-sm text-gray-600">
                    Complete your profile to get more personalized insights
                  </p>
                  <Link href={isOnboardingComplete ? "/profile/settings" : "/profile/setup"}>
                    <Button size="sm" className="flex items-center gap-2">
                      {isOnboardingComplete ? <Settings className="h-4 w-4" /> : <User className="h-4 w-4" />}
                      {isOnboardingComplete ? "Settings" : "Complete Setup"}
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Quick Actions Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link href="/dashboard/log-symptoms">
              <Card className="hover:shadow-lg transition-all duration-300 cursor-pointer group border-l-4 border-l-red-400">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Log Symptoms</p>
                      <p className="text-lg font-semibold text-red-600 group-hover:text-red-700">
                        Track Today
                      </p>
                    </div>
                    <div className="p-3 rounded-full bg-red-100 group-hover:bg-red-200 transition-colors">
                      <Activity className="h-6 w-6 text-red-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>

            <Link href="/dashboard/log-diet">
              <Card className="hover:shadow-lg transition-all duration-300 cursor-pointer group border-l-4 border-l-orange-400">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Track Diet</p>
                      <p className="text-lg font-semibold text-orange-600 group-hover:text-orange-700">
                        Log Meals
                      </p>
                    </div>
                    <div className="p-3 rounded-full bg-orange-100 group-hover:bg-orange-200 transition-colors">
                      <Utensils className="h-6 w-6 text-orange-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>

            <Link href="/dashboard/analytics">
              <Card className="hover:shadow-lg transition-all duration-300 cursor-pointer group border-l-4 border-l-blue-400">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">View Analytics</p>
                      <p className="text-lg font-semibold text-blue-600 group-hover:text-blue-700">
                        Insights
                      </p>
                    </div>
                    <div className="p-3 rounded-full bg-blue-100 group-hover:bg-blue-200 transition-colors">
                      <BarChart3 className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>

            <Link href="/reports">
              <Card className="hover:shadow-lg transition-all duration-300 cursor-pointer group border-l-4 border-l-purple-400">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Health Reports</p>
                      <p className="text-lg font-semibold text-purple-600 group-hover:text-purple-700">
                        View Reports
                      </p>
                    </div>
                    <div className="p-3 rounded-full bg-purple-100 group-hover:bg-purple-200 transition-colors">
                      <TrendingUp className="h-6 w-6 text-purple-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          </div>

          {/* AI-Powered Insights Section */}
          <Card className="border-l-4 border-l-green-500 bg-gradient-to-r from-green-50 to-emerald-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-6 w-6 text-green-600" />
                AI-Powered Real-Time Predictions
                <Badge variant="outline" className="ml-auto bg-green-100 text-green-700">
                  <Zap className="h-3 w-3 mr-1" />
                  Live
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-white rounded-lg border">
                  <Heart className="h-8 w-8 text-green-600 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-600">Wellness Score</p>
                  <p className="text-2xl font-bold text-green-600">8.2/10</p>
                  <p className="text-xs text-gray-500">Trending up</p>
                </div>
                <div className="text-center p-4 bg-white rounded-lg border">
                  <Activity className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-600">Risk Level</p>
                  <p className="text-2xl font-bold text-blue-600">Low</p>
                  <p className="text-xs text-gray-500">Stable</p>
                </div>
                <div className="text-center p-4 bg-white rounded-lg border">
                  <Target className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-600">Goal Progress</p>
                  <p className="text-2xl font-bold text-purple-600">85%</p>
                  <p className="text-xs text-gray-500">On track</p>
                </div>
              </div>
              <div className="mt-4 p-4 bg-white rounded-lg border">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="font-medium text-gray-900">Today's Recommendation</span>
                </div>
                <p className="text-gray-700">
                  Based on your recent patterns, consider having a light lunch with probiotics. 
                  Your digestive system shows optimal response to smaller meals around this time.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Main Dashboard Component */}
          <ErrorBoundary>
            <DynamicDashboard />
          </ErrorBoundary>
        </main>
        </div>
      </ErrorBoundary>
    </ProtectedRoute>
  );
}