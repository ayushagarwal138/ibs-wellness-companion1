'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import OnboardingQuestionnaire from '@/components/onboarding/onboarding-questionnaire';

export default function BasicOnboardingPage() {
  const { user, loading, checkOnboardingStatus } = useAuth();
  const router = useRouter();

  useEffect(() => {
    const checkUserStatus = async () => {
      if (!loading && !user) {
        // User not authenticated, redirect to login
        router.push('/login');
        return;
      }
    };

    checkUserStatus();
  }, [user, loading, router]);

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
              Basic Information
            </h1>
            <p className="text-lg text-gray-600">
              Tell us about yourself to get started
            </p>
          </div>
          
          <OnboardingQuestionnaire />
        </div>
      </div>
    </div>
  );
}