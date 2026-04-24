'use client'

import { useState, useEffect } from 'react';
import { useNotifications } from '@/hooks/useNotifications';
import { useAuth } from '@/contexts/auth-context';
import { analyticsService } from '@/lib/analytics';
import { toast } from 'react-hot-toast';

interface NotificationPreferences {
  symptomReminders: boolean;
  mealReminders: boolean;
  flareUpAlerts: boolean;
  medicationReminders: boolean;
  weeklyReports: boolean;
  reminderTime: string;
}

export default function NotificationSettings() {
  const { user } = useAuth();
  const {
    permission,
    isSupported,
    token,
    isLoading,
    error,
    requestPermission,
    sendTokenToServer,
  } = useNotifications();

  const [preferences, setPreferences] = useState<NotificationPreferences>({
    symptomReminders: true,
    mealReminders: true,
    flareUpAlerts: true,
    medicationReminders: false,
    weeklyReports: true,
    reminderTime: '09:00',
  });

  const [saving, setSaving] = useState(false);

  useEffect(() => {
    // Load user preferences from backend
    loadPreferences();
  }, [user]);

  useEffect(() => {
    // Send token to server when available
    if (token && user && permission === 'granted') {
      sendTokenToServer(user.id);
    }
  }, [token, user, permission, sendTokenToServer]);

  const loadPreferences = async () => {
    if (!user) return;

    try {
      const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL']}/api/v1/users/notification-preferences`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPreferences(data);
      }
    } catch (error) {
      console.error('Failed to load notification preferences:', error);
    }
  };

  const savePreferences = async () => {
    if (!user) return;

    try {
      setSaving(true);
      
      const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL']}/api/v1/users/notification-preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(preferences),
      });

      if (response.ok) {
        toast.success('Notification preferences saved!');
        analyticsService.trackUserAction('save_preferences', 'notifications', 'success');
      } else {
        throw new Error('Failed to save preferences');
      }
    } catch (error) {
      console.error('Failed to save notification preferences:', error);
      toast.error('Failed to save preferences');
      analyticsService.trackUserAction('save_preferences', 'notifications', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handlePermissionRequest = async () => {
    const granted = await requestPermission();
    if (granted) {
      analyticsService.trackUserAction('enable_notifications', 'settings', 'success');
    }
  };

  const handlePreferenceChange = (key: keyof NotificationPreferences, value: boolean | string) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  if (!isSupported) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              Notifications Not Supported
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>Your browser doesn't support push notifications. Please use a modern browser to enable this feature.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">Notification Settings</h3>
        <p className="mt-1 text-sm text-gray-500">
          Manage your notification preferences and stay on top of your IBS management.
        </p>
      </div>

      {/* Permission Status */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-base font-medium text-gray-900">Push Notifications</h4>
            <p className="text-sm text-gray-500">
              {permission === 'granted' 
                ? 'Notifications are enabled' 
                : permission === 'denied'
                ? 'Notifications are blocked'
                : 'Notifications are not enabled'
              }
            </p>
          </div>
          <div className="flex items-center space-x-3">
            {permission === 'granted' ? (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Enabled
              </span>
            ) : (
              <button
                onClick={handlePermissionRequest}
                disabled={isLoading || permission === 'denied'}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Loading...' : 'Enable Notifications'}
              </button>
            )}
          </div>
        </div>
        
        {error && (
          <div className="mt-3 text-sm text-red-600">
            {error}
          </div>
        )}
        
        {token && (
          <div className="mt-3 text-xs text-gray-500">
            Device registered for notifications
          </div>
        )}
      </div>

      {/* Notification Preferences */}
      {permission === 'granted' && (
        <div className="bg-white shadow rounded-lg p-6">
          <h4 className="text-base font-medium text-gray-900 mb-4">Notification Types</h4>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Symptom Reminders</label>
                <p className="text-sm text-gray-500">Daily reminders to log your symptoms</p>
              </div>
              <input
                type="checkbox"
                checked={preferences.symptomReminders}
                onChange={(e) => handlePreferenceChange('symptomReminders', e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Meal Reminders</label>
                <p className="text-sm text-gray-500">Reminders to log your meals and reactions</p>
              </div>
              <input
                type="checkbox"
                checked={preferences.mealReminders}
                onChange={(e) => handlePreferenceChange('mealReminders', e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Flare-up Alerts</label>
                <p className="text-sm text-gray-500">Alerts when our AI predicts a potential flare-up</p>
              </div>
              <input
                type="checkbox"
                checked={preferences.flareUpAlerts}
                onChange={(e) => handlePreferenceChange('flareUpAlerts', e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Medication Reminders</label>
                <p className="text-sm text-gray-500">Reminders to take your medications</p>
              </div>
              <input
                type="checkbox"
                checked={preferences.medicationReminders}
                onChange={(e) => handlePreferenceChange('medicationReminders', e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Weekly Reports</label>
                <p className="text-sm text-gray-500">Weekly summary of your health data</p>
              </div>
              <input
                type="checkbox"
                checked={preferences.weeklyReports}
                onChange={(e) => handlePreferenceChange('weeklyReports', e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Reminder Time</label>
                <p className="text-sm text-gray-500">Default time for daily reminders</p>
              </div>
              <input
                type="time"
                value={preferences.reminderTime}
                onChange={(e) => handlePreferenceChange('reminderTime', e.target.value)}
                className="block w-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <button
              onClick={savePreferences}
              disabled={saving}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? 'Saving...' : 'Save Preferences'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}