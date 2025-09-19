'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useAuth } from '@/contexts/auth-context';
import { useRouter } from 'next/navigation';
import { 
  CheckCircle, 
  Circle, 
  Clock, 
  User, 
  Heart, 
  Utensils, 
  Activity, 
  Target,
  ArrowRight,
  Star,
  TrendingUp,
  Shield,
  AlertCircle,
  Calendar,
  FileText,
  Settings
} from 'lucide-react';

interface ProfileSection {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  completed: boolean;
  required: boolean;
  estimatedTime: string;
  route: string;
  weight: number; // For calculating completion percentage
}

interface ProfileCompletionTrackerProps {
  userId?: string;
  onSectionComplete?: (sectionId: string) => void;
  className?: string;
}

export function ProfileCompletionTracker({ 
  userId, 
  onSectionComplete,
  className = ""
}: ProfileCompletionTrackerProps) {
  const { user, loading, checkOnboardingStatus } = useAuth();
  const router = useRouter();
  const [profileSections, setProfileSections] = useState<ProfileSection[]>([
    {
      id: 'basic-info',
      title: 'Basic Information',
      description: 'Personal details, age, and contact information',
      icon: <User className="h-5 w-5" />,
      completed: false,
      required: true,
      estimatedTime: '2 min',
      route: '/profile/basic-info',
      weight: 15
    },
    {
      id: 'medical-history',
      title: 'Medical History',
      description: 'IBS diagnosis, symptoms, and medical background',
      icon: <Heart className="h-5 w-5" />,
      completed: false,
      required: true,
      estimatedTime: '5 min',
      route: '/profile/medical-history',
      weight: 25
    },
    {
      id: 'dietary-preferences',
      title: 'Dietary Preferences',
      description: 'Food preferences, restrictions, and eating habits',
      icon: <Utensils className="h-5 w-5" />,
      completed: false,
      required: true,
      estimatedTime: '4 min',
      route: '/profile/dietary-preferences',
      weight: 20
    },
    {
      id: 'lifestyle-factors',
      title: 'Lifestyle Factors',
      description: 'Exercise, sleep, stress levels, and daily routine',
      icon: <Activity className="h-5 w-5" />,
      completed: false,
      required: true,
      estimatedTime: '3 min',
      route: '/profile/lifestyle-factors',
      weight: 20
    },
    {
      id: 'goals-preferences',
      title: 'Goals & Preferences',
      description: 'Health goals and app notification preferences',
      icon: <Target className="h-5 w-5" />,
      completed: false,
      required: false,
      estimatedTime: '2 min',
      route: '/profile/goals-preferences',
      weight: 10
    },
    {
      id: 'symptom-tracking',
      title: 'Initial Symptom Log',
      description: 'Log your recent symptoms to establish baseline',
      icon: <Calendar className="h-5 w-5" />,
      completed: false,
      required: false,
      estimatedTime: '3 min',
      route: '/symptoms/log',
      weight: 10
    }
  ]);

  const [completionPercentage, setCompletionPercentage] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [onboardingCompleted, setOnboardingCompleted] = useState(false);

  useEffect(() => {
    loadProfileCompletion();
  }, [userId]);

  useEffect(() => {
    calculateCompletionPercentage();
  }, [profileSections, onboardingCompleted]);

  const loadProfileCompletion = async () => {
    try {
      // Check if onboarding is completed using the auth context
      const isCompleted = await checkOnboardingStatus();
      setOnboardingCompleted(isCompleted);
      
      if (isCompleted) {
        // If onboarding is completed, mark all required sections as completed
        setProfileSections(prev => 
          prev.map(section => ({
            ...section,
            completed: section.required ? true : section.completed
          }))
        );
      }
    } catch (error) {
      console.error('Failed to load profile completion:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateSectionCompletion = (completedSections: string[]) => {
    setProfileSections(prev => 
      prev.map(section => ({
        ...section,
        completed: completedSections.includes(section.id)
      }))
    );
  };

  const calculateCompletionPercentage = () => {
    const totalWeight = profileSections.reduce((sum, section) => sum + section.weight, 0);
    const completedWeight = profileSections
      .filter(section => section.completed)
      .reduce((sum, section) => sum + section.weight, 0);
    
    setCompletionPercentage(Math.round((completedWeight / totalWeight) * 100));
  };

  const handleSectionClick = (section: ProfileSection) => {
    // Navigate to the section using Next.js router for proper client-side navigation
    router.push(section.route);
    
    // Notify parent component
    if (onSectionComplete) {
      onSectionComplete(section.id);
    }
  };

  const getCompletionStatus = () => {
    if (onboardingCompleted) {
      return {
        status: 'complete',
        message: 'Profile Complete! You\'re ready to get personalized insights.',
        color: 'text-green-600',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200'
      };
    }
    
    const requiredSections = profileSections.filter(s => s.required);
    const completedRequired = requiredSections.filter(s => s.completed).length;
    const totalRequired = requiredSections.length;
    
    if (completedRequired > 0) {
      return {
        status: 'in-progress',
        message: `${completedRequired}/${totalRequired} required sections completed`,
        color: 'text-blue-600',
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200'
      };
    } else {
      return {
        status: 'not-started',
        message: 'Complete your profile to unlock personalized features',
        color: 'text-orange-600',
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-200'
      };
    }
  };

  const completionStatus = getCompletionStatus();
  const nextSection = profileSections.find(s => !s.completed);
  const completedCount = profileSections.filter(s => s.completed).length;
  const totalEstimatedTime = profileSections
    .filter(s => !s.completed)
    .reduce((total, section) => {
      const time = parseInt(section.estimatedTime);
      return total + time;
    }, 0);

  if (isLoading) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-2 bg-gray-200 rounded"></div>
            <div className="space-y-2">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-12 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`${className} ${completionStatus.borderColor} border-l-4`}>
      <CardHeader className={completionStatus.bgColor}>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className={`h-6 w-6 ${completionStatus.color}`} />
            Profile Completion
          </div>
          <Badge variant="outline" className={completionStatus.color}>
            {completionPercentage}%
          </Badge>
        </CardTitle>
        <div className="space-y-3">
          <Progress value={completionPercentage} className="h-3" />
          <p className={`text-sm ${completionStatus.color}`}>
            {completionStatus.message}
          </p>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{completedCount}</div>
            <div className="text-xs text-gray-600">Completed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{profileSections.length - completedCount}</div>
            <div className="text-xs text-gray-600">Remaining</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{totalEstimatedTime}</div>
            <div className="text-xs text-gray-600">Min left</div>
          </div>
        </div>

        {/* Next Action */}
        {!onboardingCompleted && nextSection && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-full">
                  {nextSection.icon}
                </div>
                <div>
                  <h4 className="font-medium text-blue-900">Next: {nextSection.title}</h4>
                  <p className="text-sm text-blue-700">{nextSection.estimatedTime} remaining</p>
                </div>
              </div>
              <Button 
                size="sm" 
                onClick={() => handleSectionClick(nextSection)}
                className="bg-blue-600 hover:bg-blue-700"
              >
                Continue
                <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </div>
        )}

        {/* Section List */}
        <div className="space-y-2">
          <h4 className="font-medium text-gray-900 mb-3">Profile Sections</h4>
          {profileSections.map((section) => (
            <div
              key={section.id}
              className={`flex items-center justify-between p-3 rounded-lg border transition-colors cursor-pointer ${
                section.completed
                  ? 'bg-green-50 border-green-200 hover:bg-green-100'
                  : 'bg-white border-gray-200 hover:bg-gray-50'
              }`}
              onClick={() => handleSectionClick(section)}
            >
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-full ${
                  section.completed 
                    ? 'bg-green-100 text-green-600' 
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {section.completed ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    section.icon
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h5 className={`font-medium ${
                      section.completed ? 'text-green-900' : 'text-gray-900'
                    }`}>
                      {section.title}
                    </h5>
                    {section.required && (
                      <Badge variant="outline" className="text-xs">
                        Required
                      </Badge>
                    )}
                  </div>
                  <p className={`text-sm ${
                    section.completed ? 'text-green-700' : 'text-gray-600'
                  }`}>
                    {section.description}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {!section.completed && (
                  <span className="text-xs text-gray-500">{section.estimatedTime}</span>
                )}
                {section.completed ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : (
                  <Circle className="h-5 w-5 text-gray-400" />
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Completion Benefits */}
        {!onboardingCompleted && completionPercentage < 100 && (
          <div className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg">
            <h4 className="font-medium text-purple-900 mb-2 flex items-center gap-2">
              <Star className="h-4 w-4" />
              Unlock with Complete Profile
            </h4>
            <ul className="space-y-1 text-sm text-purple-700">
              <li className="flex items-center gap-2">
                <TrendingUp className="h-3 w-3" />
                AI-powered personalized insights
              </li>
              <li className="flex items-center gap-2">
                <Target className="h-3 w-3" />
                Custom dietary recommendations
              </li>
              <li className="flex items-center gap-2">
                <AlertCircle className="h-3 w-3" />
                Symptom pattern analysis
              </li>
              <li className="flex items-center gap-2">
                <FileText className="h-3 w-3" />
                Detailed health reports
              </li>
            </ul>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 pt-2">
          {onboardingCompleted ? (
            <Button 
              onClick={() => router.push('/profile/settings')} 
              className="flex-1"
            >
              Edit Profile
              <Settings className="h-4 w-4 ml-2" />
            </Button>
          ) : nextSection ? (
            <Button 
              onClick={() => handleSectionClick(nextSection)} 
              className="flex-1"
            >
              Continue Setup
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          ) : (
            <Button 
              onClick={() => router.push('/dashboard')} 
              className="flex-1"
            >
              View Dashboard
              <TrendingUp className="h-4 w-4 ml-2" />
            </Button>
          )}
          {!onboardingCompleted && (
            <Button 
              variant="outline" 
              onClick={() => router.push('/profile/settings')}
            >
              <Settings className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}