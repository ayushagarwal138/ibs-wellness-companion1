'use client';

import { ProtectedRoute } from "@/components/protected-route";
import { DashboardHeader } from "@/components/layout/dashboard-header";
import TestDataGeneratorComponent from "@/components/testing/test-data-generator";

export default function TestingPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Testing & Data Generation</h1>
            <p className="text-gray-600 mt-2">Generate test data and validate ML predictions for development and testing purposes.</p>
          </div>
          
          <TestDataGeneratorComponent />
        </main>
      </div>
    </ProtectedRoute>
  );
}