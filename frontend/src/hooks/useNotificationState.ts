import { useState, useEffect, useCallback } from 'react';
import { Notification } from '@/components/ui/notification-icon';
import { useAuth } from '@/contexts/auth-context';
import { toast } from 'react-hot-toast';
import { notificationService } from '@/lib/notifications';
import { onMessageListener } from '@/lib/firebase';

interface NotificationState {
  notifications: Notification[];
  isLoading: boolean;
  error: string | null;
  unreadCount: number;
}

interface UseNotificationStateReturn extends NotificationState {
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  dismissNotification: (id: string) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  refreshNotifications: () => void;
}

// Mock notifications for development - replace with API calls
const generateMockNotifications = (): Notification[] => [
  {
    id: '1',
    title: 'Symptom Reminder',
    message: 'Don\'t forget to log your symptoms for today. Consistent tracking helps identify patterns.',
    type: 'info',
    timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
    read: false,
    actionUrl: '/dashboard/symptoms',
    actionLabel: 'Log Symptoms'
  },
  {
    id: '2',
    title: 'Meal Logged Successfully',
    message: 'Your breakfast has been logged. We\'ll monitor for any reactions.',
    type: 'success',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
    read: false,
  },
  {
    id: '3',
    title: 'Potential Trigger Detected',
    message: 'Our AI detected that dairy products might be triggering your symptoms. Consider reviewing your recent meals.',
    type: 'warning',
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
    read: true,
    actionUrl: '/dashboard/insights',
    actionLabel: 'View Insights'
  },
  {
    id: '4',
    title: 'Weekly Report Ready',
    message: 'Your weekly health summary is ready. Check out your progress and trends.',
    type: 'info',
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
    read: true,
    actionUrl: '/dashboard/reports',
    actionLabel: 'View Report'
  },
  {
    id: '5',
    title: 'Medication Reminder',
    message: 'Time to take your evening medication. Don\'t forget to log any side effects.',
    type: 'info',
    timestamp: new Date(Date.now() - 10 * 60 * 1000), // 10 minutes ago
    read: false,
    actionUrl: '/dashboard/medications',
    actionLabel: 'Mark Taken'
  }
];

export const useNotificationState = (): UseNotificationStateReturn => {
  const { user } = useAuth();
  const [state, setState] = useState<NotificationState>({
    notifications: [],
    isLoading: true,
    error: null,
    unreadCount: 0
  });

  // Calculate unread count whenever notifications change
  const updateUnreadCount = useCallback((notifications: Notification[]) => {
    const unreadCount = notifications.filter(n => !n.read).length;
    setState(prev => ({ ...prev, unreadCount }));
  }, []);

  // Fetch notifications from API
  const fetchNotifications = useCallback(async () => {
    if (!user) return;

    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      // TODO: Replace with actual API call
      // const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/notifications`, {
      //   headers: {
      //     Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      //   },
      // });
      // 
      // if (!response.ok) {
      //   throw new Error('Failed to fetch notifications');
      // }
      // 
      // const data = await response.json();
      // const notifications = data.notifications || [];

      // For now, use mock data
      const notifications = generateMockNotifications();

      setState(prev => ({
        ...prev,
        notifications,
        isLoading: false,
        unreadCount: notifications.filter(n => !n.read).length
      }));

    } catch (error) {
      console.error('Failed to fetch notifications:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to fetch notifications',
        isLoading: false
      }));
    }
  }, [user]);

  // Mark notification as read
  const markAsRead = useCallback(async (id: string) => {
    try {
      // TODO: Replace with actual API call
      // await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/notifications/${id}/read`, {
      //   method: 'PATCH',
      //   headers: {
      //     Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      //   },
      // });

      setState(prev => {
        const updatedNotifications = prev.notifications.map(notification =>
          notification.id === id ? { ...notification, read: true } : notification
        );
        return {
          ...prev,
          notifications: updatedNotifications,
          unreadCount: updatedNotifications.filter(n => !n.read).length
        };
      });

    } catch (error) {
      console.error('Failed to mark notification as read:', error);
      toast.error('Failed to mark notification as read');
    }
  }, []);

  // Mark all notifications as read
  const markAllAsRead = useCallback(async () => {
    try {
      // TODO: Replace with actual API call
      // await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/notifications/read-all`, {
      //   method: 'PATCH',
      //   headers: {
      //     Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      //   },
      // });

      setState(prev => ({
        ...prev,
        notifications: prev.notifications.map(notification => ({ ...notification, read: true })),
        unreadCount: 0
      }));

      toast.success('All notifications marked as read');

    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
      toast.error('Failed to mark all notifications as read');
    }
  }, []);

  // Dismiss notification
  const dismissNotification = useCallback(async (id: string) => {
    try {
      // TODO: Replace with actual API call
      // await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/notifications/${id}`, {
      //   method: 'DELETE',
      //   headers: {
      //     Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      //   },
      // });

      setState(prev => {
        const updatedNotifications = prev.notifications.filter(notification => notification.id !== id);
        return {
          ...prev,
          notifications: updatedNotifications,
          unreadCount: updatedNotifications.filter(n => !n.read).length
        };
      });

    } catch (error) {
      console.error('Failed to dismiss notification:', error);
      toast.error('Failed to dismiss notification');
    }
  }, []);

  // Add new notification (for real-time notifications)
  const addNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
    };

    setState(prev => {
      const updatedNotifications = [newNotification, ...prev.notifications];
      return {
        ...prev,
        notifications: updatedNotifications,
        unreadCount: updatedNotifications.filter(n => !n.read).length
      };
    });

    // Show toast for new notifications
    if (!notification.read) {
      toast(notification.title, {
        icon: notification.type === 'success' ? '✅' : 
              notification.type === 'warning' ? '⚠️' : 
              notification.type === 'error' ? '❌' : 'ℹ️',
      });
    }
  }, []);

  // Refresh notifications
  const refreshNotifications = useCallback(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  // Initial fetch
  useEffect(() => {
    if (user) {
      fetchNotifications();
    }
  }, [user, fetchNotifications]);

  // Set up real-time notification listener
  useEffect(() => {
    if (!user) return;

    // Set up Firebase Cloud Messaging listener for real-time notifications
    const setupFCMListener = async () => {
      try {
        // Set up the foreground message listener
        notificationService.setupForegroundListener();

        // Set up custom listener for our notification state
        onMessageListener()
          .then((payload: any) => {
            if (payload) {
              console.log('Received FCM message:', payload);
              
              // Convert FCM payload to our notification format
              const notification: Omit<Notification, 'id' | 'timestamp'> = {
                title: payload.notification?.title || 'IBS Wellness Companion',
                message: payload.notification?.body || 'You have a new notification',
                type: payload.data?.type || 'info',
                read: false,
                actionUrl: payload.data?.url,
                actionLabel: payload.data?.actionLabel,
              };

              // Add to our notification state
              addNotification(notification);
            }
          })
          .catch((error) => {
            console.error('Error in FCM listener:', error);
          });
      } catch (error) {
        console.error('Error setting up FCM listener:', error);
      }
    };

    setupFCMListener();

    // For development: simulate periodic updates
    const interval = setInterval(() => {
      // Simulate receiving a new notification occasionally
      if (Math.random() < 0.1) { // 10% chance every 30 seconds
        const mockNotifications = [
          {
            title: 'Hydration Reminder',
            message: 'Remember to drink water! Staying hydrated is important for digestive health.',
            type: 'info' as const,
            read: false,
          },
          {
            title: 'Exercise Logged',
            message: 'Great job on your 30-minute walk! Regular exercise can help with IBS symptoms.',
            type: 'success' as const,
            read: false,
          }
        ];
        
        const randomIndex = Math.floor(Math.random() * mockNotifications.length);
        const randomNotification = mockNotifications[randomIndex];
        if (randomNotification) {
          addNotification(randomNotification);
        }
      }
    }, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, [user, addNotification]);

  return {
    ...state,
    markAsRead,
    markAllAsRead,
    dismissNotification,
    addNotification,
    refreshNotifications,
  };
};