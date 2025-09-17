import { ProtectedRoute } from "@/components/protected-route";
import DietLogForm from "@/components/forms/diet-log-form";
import { DashboardHeader } from "@/components/layout/dashboard-header";

export default function LogDietPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader title="Log Meal" showBackButton />
        
        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <DietLogForm />
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}