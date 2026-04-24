import { analytics } from './firebase';
import { logEvent, setUserId, setUserProperties } from 'firebase/analytics';

export interface AnalyticsService {
  trackEvent: (eventName: string, parameters?: Record<string, any>) => void;
  trackPageView: (pageName: string, pageTitle?: string) => void;
  trackUserAction: (action: string, category: string, label?: string) => void;
  trackHealthMetric: (metric: string, value: number, unit?: string) => void;
  setUser: (userId: string, properties?: Record<string, any>) => void;
  trackSymptomLog: (symptoms: string[], severity: number) => void;
  trackDietLog: (foodItems: string[], mealType: string) => void;
  trackFlareUpPrediction: (riskLevel: string, confidence: number) => void;
}

class AnalyticsServiceImpl implements AnalyticsService {
  private isEnabled(): boolean {
    return (
      analytics !== null && 
      process.env['NEXT_PUBLIC_ENABLE_ANALYTICS'] === 'true' &&
      typeof window !== 'undefined'
    );
  }

  trackEvent(eventName: string, parameters: Record<string, any> = {}): void {
    if (!this.isEnabled()) return;

    try {
      logEvent(analytics, eventName, {
        ...parameters,
        timestamp: new Date().toISOString(),
      });
      console.log(`Analytics event tracked: ${eventName}`, parameters);
    } catch (error) {
      console.error('Error tracking analytics event:', error);
    }
  }

  trackPageView(pageName: string, pageTitle?: string): void {
    this.trackEvent('page_view', {
      page_name: pageName,
      page_title: pageTitle || pageName,
      page_location: window.location.href,
    });
  }

  trackUserAction(action: string, category: string, label?: string): void {
    this.trackEvent('user_action', {
      action,
      category,
      label,
    });
  }

  trackHealthMetric(metric: string, value: number, unit?: string): void {
    this.trackEvent('health_metric', {
      metric_name: metric,
      metric_value: value,
      metric_unit: unit,
    });
  }

  setUser(userId: string, properties: Record<string, any> = {}): void {
    if (!this.isEnabled()) return;

    try {
      setUserId(analytics, userId);
      setUserProperties(analytics, {
        ...properties,
        last_active: new Date().toISOString(),
      });
      console.log(`Analytics user set: ${userId}`, properties);
    } catch (error) {
      console.error('Error setting analytics user:', error);
    }
  }

  trackSymptomLog(symptoms: string[], severity: number): void {
    this.trackEvent('symptom_logged', {
      symptom_count: symptoms.length,
      symptoms: symptoms.join(','),
      severity_level: severity,
      log_type: 'symptom',
    });
  }

  trackDietLog(foodItems: string[], mealType: string): void {
    this.trackEvent('diet_logged', {
      food_count: foodItems.length,
      meal_type: mealType,
      log_type: 'diet',
    });
  }

  trackFlareUpPrediction(riskLevel: string, confidence: number): void {
    this.trackEvent('flareup_prediction', {
      risk_level: riskLevel,
      confidence_score: confidence,
      prediction_type: 'ml_model',
    });
  }

  // IBS-specific tracking methods
  trackMedicationTaken(medicationName: string, dosage?: string): void {
    this.trackEvent('medication_taken', {
      medication_name: medicationName,
      dosage,
      log_type: 'medication',
    });
  }

  trackTriggerIdentified(trigger: string, confidence: number): void {
    this.trackEvent('trigger_identified', {
      trigger_name: trigger,
      confidence_score: confidence,
      identification_type: 'user_reported',
    });
  }

  trackGoalProgress(goalType: string, progress: number): void {
    this.trackEvent('goal_progress', {
      goal_type: goalType,
      progress_percentage: progress,
      tracking_type: 'health_goal',
    });
  }

  trackChatbotInteraction(query: string, responseType: string): void {
    this.trackEvent('chatbot_interaction', {
      query_length: query.length,
      response_type: responseType,
      interaction_type: 'ai_chat',
    });
  }

  trackNotificationInteraction(notificationType: string, action: string): void {
    this.trackEvent('notification_interaction', {
      notification_type: notificationType,
      user_action: action,
      interaction_type: 'push_notification',
    });
  }

  trackDataExport(exportType: string, dateRange: string): void {
    this.trackEvent('data_export', {
      export_type: exportType,
      date_range: dateRange,
      feature_type: 'data_management',
    });
  }

  trackFeatureUsage(featureName: string, usageCount: number): void {
    this.trackEvent('feature_usage', {
      feature_name: featureName,
      usage_count: usageCount,
      tracking_type: 'feature_analytics',
    });
  }
}

export const analyticsService = new AnalyticsServiceImpl();

// Utility functions for common tracking scenarios
export const trackPageVisit = (pageName: string) => {
  analyticsService.trackPageView(pageName);
};

export const trackButtonClick = (buttonName: string, location: string) => {
  analyticsService.trackUserAction('click', 'button', `${buttonName}_${location}`);
};

export const trackFormSubmission = (formName: string, success: boolean) => {
  analyticsService.trackUserAction('submit', 'form', `${formName}_${success ? 'success' : 'error'}`);
};

export const trackSearchQuery = (query: string, resultCount: number) => {
  analyticsService.trackEvent('search', {
    search_term: query,
    result_count: resultCount,
  });
};

export const trackError = (errorType: string, errorMessage: string, location: string) => {
  analyticsService.trackEvent('error', {
    error_type: errorType,
    error_message: errorMessage,
    error_location: location,
  });
};