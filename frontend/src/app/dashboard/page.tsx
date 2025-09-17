import MainDashboard from "@/components/dashboard/main-dashboard"
import { ProtectedRoute } from "@/components/protected-route"
import { DashboardHeader } from "@/components/layout/dashboard-header"
import { ProfileCompletionTracker } from "@/components/profile/profile-completion-tracker"
import Link from "next/link"
import { Plus, Calendar, TrendingUp, User } from "lucide-react"

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Profile Completion Tracker */}
          <div className="mb-8">
            <ProfileCompletionTracker />
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <Link href="/symptom-log" className="bg-white p-6 rounded-lg border hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3">
                <Plus className="text-blue-500" size={24} />
                <div>
                  <h3 className="font-medium text-gray-900">Log Symptoms</h3>
                  <p className="text-sm text-gray-500">Record your daily symptoms</p>
                </div>
              </div>
            </Link>
            
            <Link href="/diet-log" className="bg-white p-6 rounded-lg border hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3">
                <Calendar className="text-green-500" size={24} />
                <div>
                  <h3 className="font-medium text-gray-900">Diet Tracker</h3>
                  <p className="text-sm text-gray-500">Track your meals and reactions</p>
                </div>
              </div>
            </Link>
            
            <Link href="/analytics" className="bg-white p-6 rounded-lg border hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3">
                <TrendingUp className="text-purple-500" size={24} />
                <div>
                  <h3 className="font-medium text-gray-900">Analytics</h3>
                  <p className="text-sm text-gray-500">View trends and insights</p>
                </div>
              </div>
            </Link>
            
            <Link href="/profile-setup" className="bg-white p-6 rounded-lg border hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3">
                <User className="text-orange-500" size={24} />
                <div>
                  <h3 className="font-medium text-gray-900">Profile Setup</h3>
                  <p className="text-sm text-gray-500">Complete your health profile</p>
                </div>
              </div>
            </Link>
          </div>
          
          <MainDashboard />
        </main>
      </div>
    </ProtectedRoute>
  )
}