import { ProtectedRoute } from "@/components/protected-route";
import FoodReactionForm from "@/components/forms/food-reaction-form";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function FoodReactionsPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center py-6">
              <Link 
                href="/dashboard" 
                className="flex items-center text-gray-600 hover:text-gray-900 mr-4"
              >
                <ArrowLeft className="h-5 w-5 mr-1" />
                Back to Dashboard
              </Link>
              <h1 className="text-3xl font-bold text-gray-900">
                Track Food Reactions
              </h1>
            </div>
          </div>
        </header>
        
        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <FoodReactionForm />
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}