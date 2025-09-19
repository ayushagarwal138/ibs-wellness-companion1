import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { analyticsService } from '@/lib/analytics';
import { useAuth } from '@/contexts/auth-context';

export const useAnalytics = () => {
  const router = useRouter();
  const { user } = useAuth();

  useEffect(() => {
    // Set up user analytics when user is available
    if (user) {
      analyticsService.setUser(user.id, {
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        ibs_type: user.ibs_type || undefined,
        diagnosis_date: user.diagnosis_date || undefined,
        registration_date: user.created_at,
      });
    }
  }, [user]);

  // Track page views automatically
  useEffect(() => {
    const handleRouteChange = (url: string) => {
      const pageName = url.split('?')[0] || url; // Remove query parameters, fallback to original url
      analyticsService.trackPageView(pageName);
    };

    // Track initial page load
    if (typeof window !== 'undefined' && window.location.pathname) {
      handleRouteChange(window.location.pathname);
    }

    // Note: Next.js 13+ app router doesn't have router events
    // We'll track page views manually in components
  }, []);

  return {
    // Health tracking methods
    trackSymptomLog: (symptoms: string[], severity: number) => {
      analyticsService.trackSymptomLog(symptoms, severity);
    },

    trackDietLog: (foodItems: string[], mealType: string) => {
      analyticsService.trackDietLog(foodItems, mealType);
    },

    trackMedicationTaken: (medicationName: string, dosage?: string) => {
      analyticsService.trackMedicationTaken(medicationName, dosage);
    },

    trackFlareUpPrediction: (riskLevel: string, confidence: number) => {
      analyticsService.trackFlareUpPrediction(riskLevel, confidence);
    },

    trackTriggerIdentified: (trigger: string, confidence: number) => {
      analyticsService.trackTriggerIdentified(trigger, confidence);
    },

    // User interaction tracking
    trackButtonClick: (buttonName: string, location: string) => {
      analyticsService.trackUserAction('click', 'button', `${buttonName}_${location}`);
    },

    trackFormSubmission: (formName: string, success: boolean) => {
      analyticsService.trackUserAction('submit', 'form', `${formName}_${success ? 'success' : 'error'}`);
    },

    trackFeatureUsage: (featureName: string, usageCount: number = 1) => {
      analyticsService.trackFeatureUsage(featureName, usageCount);
    },

    trackGoalProgress: (goalType: string, progress: number) => {
      analyticsService.trackGoalProgress(goalType, progress);
    },

    trackChatbotInteraction: (query: string, responseType: string) => {
      analyticsService.trackChatbotInteraction(query, responseType);
    },

    trackNotificationInteraction: (notificationType: string, action: string) => {
      analyticsService.trackNotificationInteraction(notificationType, action);
    },

    trackDataExport: (exportType: string, dateRange: string) => {
      analyticsService.trackDataExport(exportType, dateRange);
    },

    trackSearchQuery: (query: string, resultCount: number) => {
      analyticsService.trackEvent('search', {
        search_term: query,
        result_count: resultCount,
      });
    },

    trackError: (errorType: string, errorMessage: string, location: string) => {
      analyticsService.trackEvent('error', {
        error_type: errorType,
        error_message: errorMessage,
        error_location: location,
      });
    },

    // Page tracking (manual for app router)
    trackPageView: (pageName: string, pageTitle?: string) => {
      analyticsService.trackPageView(pageName, pageTitle);
    },

    // Health metrics tracking
    trackHealthMetric: (metric: string, value: number, unit?: string) => {
      analyticsService.trackHealthMetric(metric, value, unit);
    },

    // Custom event tracking
    trackCustomEvent: (eventName: string, parameters?: Record<string, any>) => {
      analyticsService.trackEvent(eventName, parameters);
    },
  };
};