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
  Settings,
  Sparkles,
  Award,
  Zap
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
  weight: number;
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
      const isCompleted = await checkOnboardingStatus();
      setOnboardingCompleted(isCompleted);
      
      if (isCompleted) {
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

  const calculateCompletionPercentage = () => {
    const totalWeight = profileSections.reduce((sum, section) => sum + section.weight, 0);
    const completedWeight = profileSections
      .filter(section => section.completed)
      .reduce((sum, section) => sum + section.weight, 0);
    
    setCompletionPercentage(Math.round((completedWeight / totalWeight) * 100));
  };

  const handleSectionClick = (section: ProfileSection) => {
    router.push(section.route);
    
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
    <div className="space-y-4">
      <Card className={`relative overflow-hidden transition-all duration-300 hover:shadow-lg ${completionStatus.borderColor} border-l-4`}>
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-transparent to-purple-50/30 pointer-events-none" />
        
        <CardHeader className={`relative ${completionStatus.bgColor} border-b border-gray-100 pb-3`}>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-xl ${completionStatus.color === 'text-green-600' ? 'bg-green-100' : completionStatus.color === 'text-blue-600' ? 'bg-blue-100' : 'bg-orange-100'}`}>
                <Shield className={`h-5 w-5 ${completionStatus.color}`} />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900">Profile Completion</h3>
                <p className="text-base text-gray-600 font-normal">Build your personalized health journey</p>
              </div>
            </div>
            <div className="text-right">
              <Badge 
                variant="outline" 
                className={`${completionStatus.color} text-base font-bold px-2 py-1 border-2`}
              >
                {completionPercentage}%
              </Badge>
            </div>
          </CardTitle>
          
          <div className="space-y-2 mt-3">
            <div className="relative">
              <Progress 
                value={completionPercentage} 
                className="h-3 bg-gray-200 rounded-full overflow-hidden"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-green-500 rounded-full opacity-20 animate-pulse" />
            </div>
            
            <div className="flex items-center justify-between">
              <p className="text-base font-medium ${completionStatus.color} break-words">
                {completionStatus.message}
              </p>
              {completionPercentage === 100 && (
                <div className="flex items-center gap-1 text-green-600">
                  <Sparkles className="h-4 w-4" />
                  <span className="text-sm font-medium">Complete!</span>
                </div>
              )}
            </div>
          </div>
        </CardHeader>

        <CardContent className="relative space-y-3 p-3">
            <div className="grid grid-cols-3 gap-2">
            <div className="text-center p-2 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border border-blue-200 min-w-0">
              <div className="text-2xl font-bold text-blue-700 mb-1">{completedCount}</div>
              <div className="text-sm font-medium text-blue-600 uppercase tracking-wide break-words">Completed</div>
            </div>
            <div className="text-center p-2 bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl border border-orange-200 min-w-0">
              <div className="text-2xl font-bold text-orange-700 mb-1">{profileSections.length - completedCount}</div>
              <div className="text-sm font-medium text-orange-600 uppercase tracking-wide break-words">Remaining</div>
            </div>
            <div className="text-center p-2 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl border border-purple-200 min-w-0">
              <div className="text-2xl font-bold text-purple-700 mb-1">5</div>
              <div className="text-sm font-medium text-purple-600 uppercase tracking-wide break-words">Min Left</div>
            </div>
          </div>

            <div className="space-y-2">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-bold text-gray-900 text-base">Profile Sections</h4>
              <Badge variant="outline" className="text-sm">
                {completedCount}/{profileSections.length} Complete
              </Badge>
            </div>
            
            <div className="space-y-1">
              {profileSections.map((section, index) => (
                <div
                  key={section.id}
                  className={`group relative flex items-center justify-between p-2 rounded-xl border-2 transition-all duration-200 cursor-pointer ${
                    section.completed
                      ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200'
                      : 'bg-white border-gray-200 hover:border-blue-300'
                  }`}
                  onClick={() => handleSectionClick(section)}
                >
                  <div className="absolute -left-1 -top-1 w-4 h-4 bg-gray-600 text-white text-xs font-bold rounded-full flex items-center justify-center">
                    {index + 1}
                  </div>
                  
                  <div className="flex items-center gap-2 flex-1">
                    <div className={`p-1 rounded-xl transition-all duration-200 ${
                      section.completed 
                        ? 'bg-green-100 text-green-600' 
                        : 'bg-gray-100 text-gray-600 group-hover:bg-blue-100 group-hover:text-blue-600'
                    }`}>
                      {section.completed ? (
                        <CheckCircle className="h-3 w-3" />
                      ) : (
                        section.icon
                      )}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1 mb-0">
                        <h5 className={`font-bold text-sm truncate ${
                          section.completed ? 'text-green-900' : 'text-gray-900'
                        }`}>
                          {section.title}
                        </h5>
                        {section.required && (
                          <Badge variant="outline" className="text-sm bg-red-50 text-red-600 border-red-200 px-1 py-0 flex-shrink-0">
                            Required
                          </Badge>
                        )}
                      </div>
                      <p className={`text-sm break-words ${
                        section.completed ? 'text-green-700' : 'text-gray-600'
                      }`}>
                        {section.description}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-1">
                    {section.completed ? (
                      <div className="p-1 bg-green-100 rounded-full">
                        <CheckCircle className="h-3 w-3 text-green-500" />
                      </div>
                    ) : (
                      <Circle className="h-3 w-3 text-gray-400 group-hover:text-blue-500 transition-colors" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}