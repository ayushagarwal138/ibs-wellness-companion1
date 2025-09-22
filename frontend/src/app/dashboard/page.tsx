'use client';

import MainDashboard from "@/components/dashboard/main-dashboard"
import { ProtectedRoute } from "@/components/protected-route"
import { DashboardHeader } from "@/components/layout/dashboard-header"
import { ProfileCompletionTracker } from "@/components/profile/profile-completion-tracker"
import { MLInsightsDashboard } from "@/components/ml/ml-insights-dashboard"
import { RealTimePredictions } from "@/components/ml/real-time-predictions"
import { PersonalizedRecommendations } from "@/components/ml/personalized-recommendations"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import { Plus, Calendar, TrendingUp, User } from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { useEffect, useState } from "react"

export default function DashboardPage() {
  const { checkOnboardingStatus } = useAuth();
  const [onboardingCompleted, setOnboardingCompleted] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const isCompleted = await checkOnboardingStatus();
        setOnboardingCompleted(isCompleted);
      } catch (error) {
        console.error('Failed to check onboarding status:', error);
      } finally {
        setLoading(false);
      }
    };
    
    checkStatus();
  }, [checkOnboardingStatus]);

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50/30">
        <DashboardHeader />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
          {/* Mobile-first responsive grid layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
            {/* Profile Completion Tracker - Full width on mobile, narrow sidebar on desktop */}
            <div className="lg:col-span-3 order-2 lg:order-1">
              <div className="sticky top-24">
                <ProfileCompletionTracker />
              </div>
            </div>
            
            {/* Main Dashboard Content - Full width on mobile, main content on desktop */}
            <div className="lg:col-span-9 order-1 lg:order-2 space-y-6 lg:space-y-8">
              {/* Quick Actions */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-4 lg:gap-6">
                <Link href="/dashboard/log-symptoms" className="bg-white p-4 lg:p-6 rounded-lg border hover:shadow-md transition-shadow">
                  <div className="flex items-center space-x-3">
                    <Plus className="text-blue-500 flex-shrink-0" size={24} />
                    <div className="min-w-0">
                      <h3 className="font-medium text-gray-900 truncate">Log Symptoms</h3>
                      <p className="text-sm text-gray-500 truncate">Record your daily symptoms</p>
                    </div>
                  </div>
                </Link>
                
                <Link href="/dashboard/log-diet" className="bg-white p-4 lg:p-6 rounded-lg border hover:shadow-md transition-shadow">
                  <div className="flex items-center space-x-3">
                    <Calendar className="text-green-500 flex-shrink-0" size={24} />
                    <div className="min-w-0">
                      <h3 className="font-medium text-gray-900 truncate">Diet Tracker</h3>
                      <p className="text-sm text-gray-500 truncate">Log your meals and track dietary patterns</p>
                    </div>
                  </div>
                </Link>
                
                <Link href="/analytics" className="bg-white p-4 lg:p-6 rounded-lg border hover:shadow-md transition-shadow">
                  <div className="flex items-center space-x-3">
                    <TrendingUp className="text-purple-500 flex-shrink-0" size={24} />
                    <div className="min-w-0">
                      <h3 className="font-medium text-gray-900 truncate">Analytics</h3>
                      <p className="text-sm text-gray-500 truncate">View trends and insights</p>
                    </div>
                  </div>
                </Link>
                
                <Link href="/reports" className="bg-white p-4 lg:p-6 rounded-lg border hover:shadow-md transition-shadow">
                  <div className="flex items-center space-x-3">
                    <TrendingUp className="text-blue-500 flex-shrink-0" size={24} />
                    <div className="min-w-0">
                      <h3 className="font-medium text-gray-900 truncate">Health Reports</h3>
                      <p className="text-sm text-gray-500 truncate">AI-powered insights and predictions</p>
                    </div>
                  </div>
                </Link>
                
                {!loading && (
                  <Link 
                    href={onboardingCompleted ? "/profile/settings" : "/profile-setup"} 
                    className="bg-white p-4 lg:p-6 rounded-lg border hover:shadow-md transition-shadow sm:col-span-2 lg:col-span-1"
                  >
                    <div className="flex items-center space-x-3">
                      <User className="text-orange-500 flex-shrink-0" size={24} />
                      <div className="min-w-0">
                        <h3 className="font-medium text-gray-900 truncate">
                          {onboardingCompleted ? "Edit Profile" : "Profile Setup"}
                        </h3>
                        <p className="text-sm text-gray-500 truncate">
                          {onboardingCompleted ? "Update your health profile" : "Complete your health profile"}
                        </p>
                      </div>
                    </div>
                  </Link>
                )}
              </div>
              
              {/* ML Insights Section */}
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl lg:text-2xl font-bold text-gray-900">AI-Powered Insights</h2>
                  <Badge variant="secondary" className="bg-purple-100 text-purple-800 font-medium">
                    Real-time
                  </Badge>
                </div>
                
                <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                  {/* Real-time Predictions */}
                  <div className="xl:col-span-1">
                    <div className="h-full min-h-0 overflow-hidden">
                      <RealTimePredictions className="h-full" />
                    </div>
                  </div>
                  
                  {/* ML Insights Dashboard */}
                  <div className="xl:col-span-2">
                    <div className="h-full min-h-0 overflow-hidden">
                      <MLInsightsDashboard className="h-full" />
                    </div>
                  </div>
                </div>
              </div>
              <div className="w-full overflow-hidden">
                <MainDashboard />
              </div>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}