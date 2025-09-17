'use client';

import { ProtectedRoute } from "@/components/protected-route";
import { DashboardHeader } from "@/components/layout/dashboard-header";
import { ProfileCompletionTracker } from "@/components/profile/profile-completion-tracker";
import { ProfilePreview } from "@/components/profile/profile-preview";
import UserProfileSetup from "@/components/profile/user-profile-setup";

export default function ProfileSetupPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column - Profile Setup */}
            <div className="lg:col-span-2">
              <UserProfileSetup />
            </div>
            
            {/* Right Column - Profile Completion & Preview */}
            <div className="space-y-6">
              <ProfileCompletionTracker />
              <ProfilePreview />
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}