'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ProtectedRoute } from "@/components/protected-route";
import { DashboardHeader } from "@/components/layout/dashboard-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  User, 
  Heart, 
  Utensils, 
  Activity, 
  Target, 
  CheckCircle, 
  ArrowRight, 
  ArrowLeft,
  Clock
} from "lucide-react";
import { useAuth } from '@/contexts/auth-context';
import { profileCompletionService } from '@/services/profile-completion-service';

interface SetupStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  route: string;
  completed: boolean;
}

export default function ProfileSetupPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);

  const setupSteps: SetupStep[] = [
    {
      id: 'basic-info',
      title: 'Basic Information',
      description: 'Tell us about yourself - name, age, contact details',
      icon: <User className="h-6 w-6" />,
      route: '/profile/basic-info',
      completed: false
    },
    {
      id: 'medical-history',
      title: 'Medical History',
      description: 'Share your IBS diagnosis and medical background',
      icon: <Heart className="h-6 w-6" />,
      route: '/profile/medical-history',
      completed: false
    },
    {
      id: 'dietary-preferences',
      title: 'Dietary Preferences',
      description: 'Set up your food preferences and restrictions',
      icon: <Utensils className="h-6 w-6" />,
      route: '/profile/dietary-preferences',
      completed: false
    },
    {
      id: 'lifestyle-factors',
      title: 'Lifestyle Factors',
      description: 'Tell us about your daily routine and habits',
      icon: <Activity className="h-6 w-6" />,
      route: '/profile/lifestyle-factors',
      completed: false
    },
    {
      id: 'goals-preferences',
      title: 'Goals & Preferences',
      description: 'Set your health goals and app preferences',
      icon: <Target className="h-6 w-6" />,
      route: '/profile/goals-preferences',
      completed: false
    }
  ];

  const [steps, setSteps] = useState(setupSteps);

  useEffect(() => {
    // Check which steps are already completed by making API calls
    checkCompletedSteps();
  }, []);

  const checkCompletedSteps = async () => {
    try {
      const completionData = await profileCompletionService.checkProfileCompletion();
      
      setCompletedSteps(completionData.completedSections);
      setSteps(prev => prev.map(step => ({
        ...step,
        completed: completionData.sectionStatus[step.id] || false
      })));

      // Find the first incomplete step
      const firstIncomplete = setupSteps.findIndex(step => !completionData.completedSections.includes(step.id));
      if (firstIncomplete !== -1) {
        setCurrentStep(firstIncomplete);
      } else {
        // All steps completed, set to last step
        setCurrentStep(setupSteps.length - 1);
      }
    } catch (error) {
      console.error('Error checking completed steps:', error);
    }
  };

  const handleStepClick = (stepIndex: number) => {
    const step = steps[stepIndex];
    if (step) {
      router.push(`${step.route}?setup=true`);
    }
  };

  const handleSkipSetup = () => {
    router.push('/dashboard');
  };

  const handleCompleteSetup = () => {
    router.push('/dashboard');
  };

  const completionPercentage = (completedSteps.length / steps.length) * 100;
  const allStepsCompleted = completedSteps.length === steps.length;

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader />
        
        <div className="max-w-4xl mx-auto p-6">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Welcome to IBS Wellness Companion</h1>
                <p className="text-gray-600 mt-2">
                  Let's set up your profile to provide personalized insights and recommendations
                </p>
              </div>
              <Button 
                variant="outline" 
                onClick={handleSkipSetup}
                className="flex items-center gap-2"
              >
                <Clock className="h-4 w-4" />
                Skip for now
              </Button>
            </div>

            {/* Progress */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">
                  Setup Progress
                </span>
                <span className="text-sm text-gray-500">
                  {completedSteps.length} of {steps.length} completed
                </span>
              </div>
              <Progress value={completionPercentage} className="h-3" />
            </div>
          </div>

          {/* Setup Steps */}
          <div className="space-y-4">
            {steps.map((step, index) => (
              <Card 
                key={step.id}
                className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                  step.completed 
                    ? 'border-green-200 bg-green-50' 
                    : index === currentStep 
                      ? 'border-blue-200 bg-blue-50 ring-2 ring-blue-100' 
                      : 'hover:border-gray-300'
                }`}
                onClick={() => handleStepClick(index)}
              >
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`p-3 rounded-full ${
                        step.completed 
                          ? 'bg-green-100 text-green-600' 
                          : index === currentStep 
                            ? 'bg-blue-100 text-blue-600' 
                            : 'bg-gray-100 text-gray-600'
                      }`}>
                        {step.completed ? <CheckCircle className="h-6 w-6" /> : step.icon}
                      </div>
                      <div>
                        <div className="flex items-center gap-3">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {step.title}
                          </h3>
                          {step.completed && (
                            <Badge variant="secondary" className="bg-green-100 text-green-700">
                              Completed
                            </Badge>
                          )}
                          {index === currentStep && !step.completed && (
                            <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                              Current
                            </Badge>
                          )}
                        </div>
                        <p className="text-gray-600 mt-1">
                          {step.description}
                        </p>
                      </div>
                    </div>
                    <ArrowRight className="h-5 w-5 text-gray-400" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="mt-8 flex items-center justify-between">
            <Button 
              variant="outline" 
              onClick={() => router.push('/dashboard')}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Button>

            {allStepsCompleted ? (
              <Button 
                onClick={handleCompleteSetup}
                className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
              >
                <CheckCircle className="h-4 w-4" />
                Setup Complete - Go to Dashboard
              </Button>
            ) : (
              <Button 
                onClick={() => currentStep < steps.length && handleStepClick(currentStep)}
                className="flex items-center gap-2"
                disabled={currentStep >= steps.length}
              >
                Continue Setup
                <ArrowRight className="h-4 w-4" />
              </Button>
            )}
          </div>

          {/* Help Text */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-800">
              <strong>💡 Tip:</strong> Completing your profile helps us provide more accurate predictions 
              and personalized recommendations for managing your IBS symptoms.
            </p>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}