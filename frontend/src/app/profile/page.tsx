'use client';

import { ProtectedRoute } from "@/components/protected-route";
import { DashboardHeader } from "@/components/layout/dashboard-header";
import { ProfilePreview } from "@/components/profile/profile-preview";
import { ProfileCompletionTracker } from "@/components/profile/profile-completion-tracker";
import { ProfileDataDisplay } from '@/components/profile/profile-data-display';

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50/30">
        <DashboardHeader title="Your Health Profile" showBackButton />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
          {/* Single column layout without sidebar */}
          <div className="space-y-6 lg:space-y-8">
            {/* Profile Completion Tracker - Full width */}
            <div>
              <ProfileCompletionTracker />
            </div>
            
            {/* Profile Preview - Full width */}
            <div>
              <ProfilePreview />
            </div>
            
            {/* Profile Data Display - Full width */}
            <div>
              <ProfileDataDisplay />
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}