import { ProtectedRoute } from "@/components/protected-route";
import DataVisualization from "@/components/dashboard/data-visualization";
import { DashboardHeader } from "@/components/layout/dashboard-header";

export default function AnalyticsPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader title="Analytics & Insights" showBackButton />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <DataVisualization />
        </main>
      </div>
    </ProtectedRoute>
  );
}