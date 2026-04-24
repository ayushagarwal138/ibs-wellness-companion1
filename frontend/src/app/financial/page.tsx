'use client';

import { ProtectedRoute } from "@/components/protected-route";
import { DashboardHeader } from "@/components/layout/dashboard-header";
import { FinancialDashboard } from "@/components/financial";

export default function FinancialPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader title="Financial Management" showBackButton />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <FinancialDashboard />
        </main>
      </div>
    </ProtectedRoute>
  );
}