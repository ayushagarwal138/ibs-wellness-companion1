"use client";

import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/protected-route";
import SymptomLogForm from "@/components/forms/symptom-log-form";
import { DashboardHeader } from "@/components/layout/dashboard-header";

export default function InitialSymptomLogPage() {
  const router = useRouter();

  const handleSuccess = () => {
    // Redirect to profile after successful submission
    router.push('/profile');
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader title="Initial Symptom Log" showBackButton />
        
        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Log Your Initial Symptoms
              </h2>
              <p className="text-gray-600">
                Help us understand your current symptoms to create a personalized wellness plan. 
                This information will be used to track your progress over time.
              </p>
            </div>
            
            <SymptomLogForm onSuccess={handleSuccess} />
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}