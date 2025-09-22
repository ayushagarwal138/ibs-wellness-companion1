'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { useUserSync } from '@/hooks/useUserSync';
import { useProfileValidation } from '@/hooks/useProfileValidation';
import { ProtectedRoute } from '@/components/protected-route';
import { DashboardHeader } from '@/components/layout/dashboard-header';
import { Card, CardContent } from '@/components/ui/card';
import ProfileForm from '@/components/profile/ProfileForm';
import { ProfileData } from '@/hooks/useProfileValidation';
import { toast } from 'react-hot-toast';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { SyncStatusIndicator } from '@/components/ui/sync-status-indicator';

export default function ProfileSettingsPage() {
  const { user, updateProfile } = useAuth();
  const { syncProfile, syncStatus } = useUserSync();
  const { transformFromBackend } = useProfileValidation();
  const [profileData, setProfileData] = useState<Partial<ProfileData>>({});
  const [isLoading, setIsLoading] = useState(true);

  // Load profile data on component mount
  useEffect(() => {
    const loadProfileData = async () => {
      try {
        if (user) {
          // Use the transformFromBackend function from the hook
          const transformedData = transformFromBackend(user);
          setProfileData(transformedData);
        }
      } catch (error) {
        console.error('Failed to load profile data:', error);
        toast.error('Failed to load profile data');
      } finally {
        setIsLoading(false);
      }
    };

    loadProfileData();
  }, [user, transformFromBackend]);

  // Handle profile save
  const handleSaveProfile = async (data: ProfileData) => {
    try {
      await updateProfile(data);
      setProfileData(data);
      toast.success('Profile saved successfully!');
    } catch (error) {
      console.error('Failed to save profile:', error);
      toast.error('Failed to save profile');
      throw error;
    }
  };

  // Handle profile sync
  const handleSyncProfile = async (data: ProfileData) => {
    try {
      await syncProfile(data);
      toast.success('Profile synced successfully!');
    } catch (error) {
      console.error('Failed to sync profile:', error);
      toast.error('Failed to sync profile');
      throw error;
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50">
          <DashboardHeader />
          <div className="container mx-auto py-8">
            <Card>
              <CardContent className="flex items-center justify-center py-8">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
                  <p>Loading profile...</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader />
        
        <div className="container mx-auto py-8">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-4 mb-2">
                <Link 
                  href="/dashboard" 
                  className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back to Dashboard
                </Link>
              </div>
              <h1 className="text-3xl font-bold">Profile Settings</h1>
              <p className="text-muted-foreground mt-2">
                Manage your personal information and health profile to get personalized recommendations.
              </p>
            </div>
            
            {/* Sync Status */}
            <div className="flex items-center gap-4">
              <SyncStatusIndicator status={syncStatus} />
            </div>
          </div>

          {/* Profile Form */}
          <ProfileForm
            initialData={profileData}
            onSave={handleSaveProfile}
            onSync={handleSyncProfile}
            isLoading={isLoading}
          />
        </div>
      </div>
    </ProtectedRoute>
  );
}