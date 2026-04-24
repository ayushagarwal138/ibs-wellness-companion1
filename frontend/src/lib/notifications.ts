import { requestNotificationPermission, onMessageListener } from './firebase';
import { toast } from 'react-hot-toast';

export interface NotificationService {
  requestPermission: () => Promise<string | null>;
  setupForegroundListener: () => void;
  sendTokenToServer: (token: string, userId: string) => Promise<void>;
  showNotification: (title: string, body: string, options?: NotificationOptions) => void;
}

class NotificationServiceImpl implements NotificationService {
  private isListenerSetup = false;

  async requestPermission(): Promise<string | null> {
    try {
      // Check if notifications are supported
      if (!('Notification' in window)) {
        console.log('This browser does not support notifications');
        return null;
      }

      // Check current permission status
      if (Notification.permission === 'denied') {
        console.log('Notification permission denied');
        return null;
      }

      // Request permission and get FCM token
      const token = await requestNotificationPermission();
      
      if (token) {
        console.log('FCM token obtained:', token);
        toast.success('Notifications enabled successfully!');
        return token;
      } else {
        console.log('Failed to get FCM token');
        toast.error('Failed to enable notifications');
        return null;
      }
    } catch (error) {
      console.error('Error requesting notification permission:', error);
      toast.error('Error enabling notifications');
      return null;
    }
  }

  setupForegroundListener(): void {
    if (this.isListenerSetup) {
      return;
    }

    onMessageListener()
      .then((payload: any) => {
        if (payload) {
          console.log('Foreground message received:', payload);
          
          const title = payload.notification?.title || 'IBS Wellness Companion';
          const body = payload.notification?.body || 'You have a new notification';
          
          // Show toast notification
          toast.success(`${title}: ${body}`, {
            duration: 5000,
            position: 'top-right',
          });

          // Show browser notification if permission granted
          if (Notification.permission === 'granted') {
            this.showNotification(title, body, {
              icon: '/icon-192x192.png',
              badge: '/icon-192x192.png',
              tag: 'ibs-wellness-foreground',
              data: payload.data,
            });
          }
        }
      })
      .catch((error) => {
        console.error('Error setting up foreground listener:', error);
      });

    this.isListenerSetup = true;
  }

  async sendTokenToServer(token: string, userId: string): Promise<void> {
    try {
      const API_BASE_URL = process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000';
      
      const response = await fetch(`${API_BASE_URL}/api/v1/notifications/register-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          token,
          user_id: userId,
          platform: 'web',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to register FCM token with server');
      }

      console.log('FCM token registered with server successfully');
    } catch (error) {
      console.error('Error sending token to server:', error);
      // Don't throw error to avoid breaking the flow
    }
  }

  showNotification(title: string, body: string, options?: NotificationOptions): void {
    if (Notification.permission === 'granted') {
      const defaultOptions: NotificationOptions = {
        icon: '/icon-192x192.png',
        badge: '/icon-192x192.png',
        tag: 'ibs-wellness-notification',
        requireInteraction: false,
        ...options,
      };

      const notification = new Notification(title, {
        body,
        ...defaultOptions,
      });

      // Auto close after 5 seconds
      setTimeout(() => {
        notification.close();
      }, 5000);

      // Handle click events
      notification.onclick = () => {
        window.focus();
        notification.close();
        
        // Navigate to dashboard or specific page based on data
        if (options?.data?.url) {
          window.location.href = options.data.url;
        } else {
          window.location.href = '/dashboard';
        }
      };
    }
  }
}

export const notificationService = new NotificationServiceImpl();

// Utility functions for common notification types
export const showSymptomReminder = () => {
  notificationService.showNotification(
    'Symptom Log Reminder',
    "Don't forget to log your symptoms today!",
    {
      data: { url: '/dashboard/log-symptoms' }
    }
  );
};

export const showMealReminder = () => {
  notificationService.showNotification(
    'Meal Log Reminder',
    'Remember to log your meal and how you feel!',
    {
      data: { url: '/diet-history' }
    }
  );
};

export const showFlareUpAlert = (riskLevel: string) => {
  const messages = {
    high: 'High risk of flare-up detected. Consider avoiding trigger foods.',
    medium: 'Moderate flare-up risk. Monitor your symptoms closely.',
    low: 'Low flare-up risk. Keep up the good work!'
  };

  notificationService.showNotification(
    'Flare-up Risk Alert',
    messages[riskLevel as keyof typeof messages] || messages.medium,
    {
      data: { url: '/dashboard/analytics' },
      requireInteraction: riskLevel === 'high',
    }
  );
};