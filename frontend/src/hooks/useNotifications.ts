import { useEffect, useState } from 'react';
import { notificationService } from '@/lib/notifications';
import { analyticsService } from '@/lib/analytics';

export interface NotificationState {
  permission: NotificationPermission;
  isSupported: boolean;
  token: string | null;
  isLoading: boolean;
  error: string | null;
}

export const useNotifications = () => {
  const [state, setState] = useState<NotificationState>({
    permission: 'default',
    isSupported: false,
    token: null,
    isLoading: true,
    error: null,
  });

  useEffect(() => {
    const initializeNotifications = async () => {
      try {
        setState(prev => ({ ...prev, isLoading: true, error: null }));

        // Check if notifications are supported
        const isSupported = 'Notification' in window;
        
        if (!isSupported) {
          setState(prev => ({
            ...prev,
            isSupported: false,
            isLoading: false,
            error: 'Notifications are not supported in this browser',
          }));
          return;
        }

        // Get current permission status
        const permission = Notification.permission;
        
        setState(prev => ({
          ...prev,
          permission,
          isSupported: true,
        }));

        // If permission is granted, get the token
        if (permission === 'granted') {
          const token = await notificationService.requestPermission();
          setState(prev => ({
            ...prev,
            token,
            isLoading: false,
          }));
        } else {
          setState(prev => ({ ...prev, isLoading: false }));
        }

        // Set up foreground message listener
        notificationService.setupForegroundListener();

      } catch (error) {
        console.error('Failed to initialize notifications:', error);
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: error instanceof Error ? error.message : 'Failed to initialize notifications',
        }));
      }
    };

    initializeNotifications();
  }, []);

  const requestPermission = async (): Promise<boolean> => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));
      
      const token = await notificationService.requestPermission();
      const permission = Notification.permission;
      
      if (permission === 'granted' && token) {
        setState(prev => ({
          ...prev,
          permission,
          token,
          isLoading: false,
        }));
        
        // Track permission granted
        analyticsService.trackUserAction('grant_permission', 'notifications', 'success');
        
        return true;
      } else {
        setState(prev => ({
          ...prev,
          permission,
          isLoading: false,
          error: 'Notification permission denied',
        }));
        
        // Track permission denied
        analyticsService.trackUserAction('deny_permission', 'notifications', 'denied');
        
        return false;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to request permission';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      
      // Track permission error
      analyticsService.trackUserAction('request_permission', 'notifications', 'error');
      
      return false;
    }
  };

  const showNotification = (title: string, body: string, options?: NotificationOptions) => {
    if (state.permission !== 'granted') {
      console.warn('Cannot show notification: permission not granted');
      return;
    }

    notificationService.showNotification(title, body, options);
    
    // Track notification shown
    analyticsService.trackNotificationInteraction(title, 'shown');
  };

  const scheduleSymptomReminder = (time: string) => {
    // This would typically integrate with a scheduling service
    // For now, we'll just track the intent
    analyticsService.trackUserAction('schedule_reminder', 'notifications', 'symptom_log');
    console.log(`Symptom reminder scheduled for ${time}`);
  };

  const scheduleMealReminder = (time: string) => {
    // This would typically integrate with a scheduling service
    // For now, we'll just track the intent
    analyticsService.trackUserAction('schedule_reminder', 'notifications', 'meal_log');
    console.log(`Meal reminder scheduled for ${time}`);
  };

  const sendTokenToServer = async (userId: string) => {
    if (!state.token) {
      console.warn('No FCM token available to send to server');
      return;
    }

    try {
      await notificationService.sendTokenToServer(state.token, userId);
      analyticsService.trackUserAction('register_token', 'notifications', 'success');
    } catch (error) {
      console.error('Failed to send token to server:', error);
      analyticsService.trackUserAction('register_token', 'notifications', 'error');
    }
  };

  return {
    ...state,
    requestPermission,
    showNotification,
    scheduleSymptomReminder,
    scheduleMealReminder,
    sendTokenToServer,
  };
};