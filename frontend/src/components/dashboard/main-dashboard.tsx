'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import SymptomStats from './symptom-stats';
import DietStats from './diet-stats';
import { dashboardAnalyticsService, DashboardAnalytics } from '@/services/dashboard-analytics-service';
import { useAuth } from '@/contexts/auth-context';

type DashboardView = 'overview' | 'symptoms' | 'diet';

export default function MainDashboard() {
  const { user, loading: authLoading } = useAuth();
  const [activeView, setActiveView] = useState<DashboardView>('overview');
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Only load analytics when auth is complete and user is authenticated
    if (!authLoading && user) {
      loadDashboardAnalytics();
    }
  }, [authLoading, user]);

  const loadDashboardAnalytics = async () => {
    try {
      setIsLoading(true);
      console.log('Loading dashboard analytics for user:', user?.email);
      const dashboardData = await dashboardAnalyticsService.getDashboardAnalytics();
      setAnalytics(dashboardData);
    } catch (error) {
      console.error('Failed to load dashboard analytics:', error);
      // Fallback to basic analytics if service fails
      setAnalytics({
        totalSymptomLogs: 0,
        mealsLogged: 0,
        foodReactions: 0,
        avgWellnessScore: 0,
        symptomLogsChange: '+0%',
        mealsLoggedChange: '+0%',
        foodReactionsChange: '+0%',
        wellnessScoreChange: '+0%',
        recentActivity: []
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Show loading state while auth is loading or data is loading
  if (authLoading || (isLoading && !analytics)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const renderContent = () => {
    switch (activeView) {
      case 'symptoms':
        return <SymptomStats />;
      case 'diet':
        return <DietStats />;
      case 'overview':
      default:
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Quick Stats Cards */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Symptom Logs</CardTitle>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    className="h-4 w-4 text-muted-foreground"
                  >
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                  </svg>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics?.totalSymptomLogs || 0}</div>
                  <p className="text-xs text-muted-foreground">{analytics?.symptomLogsChange || '+0%'} from last month</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Meals Logged</CardTitle>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    className="h-4 w-4 text-muted-foreground"
                  >
                    <rect width="20" height="14" x="2" y="5" rx="2" />
                    <path d="M2 10h20" />
                  </svg>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics?.mealsLogged || 0}</div>
                  <p className="text-xs text-muted-foreground">{analytics?.mealsLoggedChange || '+0%'} from last month</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Food Reactions</CardTitle>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    className="h-4 w-4 text-muted-foreground"
                  >
                    <path d="M12 2v20m8-10H4" />
                  </svg>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics?.foodReactions || 0}</div>
                  <p className="text-xs text-muted-foreground">{analytics?.foodReactionsChange || '+0%'} from last month</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Avg. Wellness Score</CardTitle>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    className="h-4 w-4 text-muted-foreground"
                  >
                    <path d="M3 3v18h18" />
                    <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3" />
                  </svg>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics?.avgWellnessScore?.toFixed(1) || '0.0'}</div>
                  <p className="text-xs text-muted-foreground">{analytics?.wellnessScoreChange || '+0%'} from last month</p>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analytics?.recentActivity?.length ? (
                     analytics.recentActivity.map((activity, index) => {
                       const colorClass = activity.color === 'blue' ? 'bg-blue-500' :
                                         activity.color === 'yellow' ? 'bg-yellow-500' :
                                         activity.color === 'red' ? 'bg-red-500' :
                                         activity.color === 'green' ? 'bg-green-500' :
                                         'bg-gray-500';
                       
                       return (
                         <div key={index} className="flex items-center space-x-4">
                           <div className={`w-2 h-2 ${colorClass} rounded-full`}></div>
                           <div className="flex-1">
                             <p className="text-sm font-medium">{activity.description}</p>
                             <p className="text-xs text-gray-500">{activity.timeAgo}</p>
                           </div>
                         </div>
                       );
                     })
                   ) : (
                     <p className="text-sm text-gray-500">No recent activity</p>
                   )}
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button className="h-20 flex flex-col items-center justify-center space-y-2" asChild>
                    <Link href="/dashboard/log-symptoms">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        className="h-6 w-6"
                      >
                        <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                      </svg>
                      <span className="text-sm">Log Symptoms</span>
                    </Link>
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2" asChild>
                    <Link href="/diet-history">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        className="h-6 w-6"
                      >
                        <rect width="20" height="14" x="2" y="5" rx="2" />
                        <path d="M2 10h20" />
                      </svg>
                      <span className="text-sm">Log Meal</span>
                    </Link>
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2" asChild>
                    <Link href="/dashboard/food-reactions">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        className="h-6 w-6"
                      >
                        <path d="M12 2v20m8-10H4" />
                      </svg>
                      <span className="text-sm">Food Reaction</span>
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Navigation Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        <button
          onClick={() => setActiveView('overview')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeView === 'overview'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveView('symptoms')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeView === 'symptoms'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Symptoms
        </button>
        <button
          onClick={() => setActiveView('diet')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeView === 'diet'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Diet
        </button>
      </div>

      {/* Content */}
      {renderContent()}
    </div>
  );
}