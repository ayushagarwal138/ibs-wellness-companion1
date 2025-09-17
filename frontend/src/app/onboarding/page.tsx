'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import OnboardingQuestionnaire from '@/components/onboarding/onboarding-questionnaire';

export default function OnboardingPage() {
  const { user, loading, checkOnboardingStatus } = useAuth();
  const router = useRouter();

  useEffect(() => {
    const checkUserStatus = async () => {
      if (!loading && !user) {
        // User not authenticated, redirect to login
        router.push('/login');
        return;
      }

      if (user) {
        // Check if user has already completed onboarding
        const onboardingCompleted = await checkOnboardingStatus();
        if (onboardingCompleted) {
          router.push('/dashboard');
        }
      }
    };

    checkUserStatus();
  }, [user, loading, router, checkOnboardingStatus]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome to IBS Wellness Companion
            </h1>
            <p className="text-lg text-gray-600">
              Let's personalize your experience with a quick questionnaire
            </p>
          </div>
          
          <OnboardingQuestionnaire />
        </div>
      </div>
    </div>
  );
}