'use client';

import { ProtectedRoute } from "@/components/protected-route";
import { DashboardHeader } from "@/components/layout/dashboard-header";
import { ProfilePreview } from "@/components/profile/profile-preview";
import { ProfileCompletionTracker } from "@/components/profile/profile-completion-tracker";

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader title="Your Health Profile" showBackButton />
        
        <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Left Column - Profile Completion Tracker */}
            <div className="lg:col-span-1">
              <ProfileCompletionTracker />
            </div>
            
            {/* Right Column - Profile Preview with AI Insights */}
            <div className="lg:col-span-3">
              <ProfilePreview />
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}