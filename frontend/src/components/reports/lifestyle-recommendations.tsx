'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  Activity, 
  Brain, 
  Heart, 
  Moon, 
  Droplets,
  Clock,
  Target,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Calendar,
  Timer,
  Zap,
  Shield,
  Smile,
  Wind,
  Thermometer,
  Users,
  BookOpen,
  Coffee
} from 'lucide-react';

interface LifestyleRecommendation {
  id: string;
  category: 'exercise' | 'stress' | 'sleep' | 'hydration' | 'mindfulness' | 'social';
  title: string;
  description: string;
  benefits: string[];
  actionItems: string[];
  difficulty: 'easy' | 'medium' | 'hard';
  timeCommitment: string;
  frequency: string;
  priority: 'high' | 'medium' | 'low';
  ibsSpecific: boolean;
  tips: string[];
}

interface UserHealthProfile {
  ibsType: string;
  severityLevel: string;
  stressLevel: number; // 1-10
  sleepQuality: number; // 1-10
  exerciseLevel: string;
  currentSymptoms: string[];
  triggers: string[];
}

interface LifestyleRecommendationsProps {
  userProfile?: UserHealthProfile;
}

const mockUserProfile: UserHealthProfile = {
  ibsType: "IBS-D",
  severityLevel: "Moderate",
  stressLevel: 7,
  sleepQuality: 5,
  exerciseLevel: "Low",
  currentSymptoms: ["Bloating", "Abdominal pain", "Irregular bowel movements"],
  triggers: ["Stress", "Certain foods", "Lack of sleep"]
};

const mockRecommendations: LifestyleRecommendation[] = [
  {
    id: "stress-management",
    category: "stress",
    title: "Stress Management Techniques",
    description: "Implement daily stress reduction practices to minimize IBS symptom triggers",
    benefits: ["Reduces IBS flare-ups", "Improves gut-brain connection", "Better sleep quality", "Enhanced mood"],
    actionItems: [
      "Practice 10 minutes of deep breathing daily",
      "Try progressive muscle relaxation before bed",
      "Use stress tracking apps to identify patterns",
      "Schedule regular 'worry time' to process concerns"
    ],
    difficulty: "easy",
    timeCommitment: "15-30 minutes daily",
    frequency: "Daily",
    priority: "high",
    ibsSpecific: true,
    tips: [
      "Start with just 5 minutes if 10 feels overwhelming",
      "Use guided meditation apps like Headspace or Calm",
      "Practice breathing exercises during stressful moments"
    ]
  },
  {
    id: "gentle-exercise",
    category: "exercise",
    title: "Gentle Physical Activity",
    description: "Low-impact exercises that support digestive health without triggering symptoms",
    benefits: ["Improves gut motility", "Reduces stress hormones", "Better sleep", "Increased energy"],
    actionItems: [
      "Take a 20-minute walk after meals",
      "Practice yoga poses for digestion (child's pose, cat-cow)",
      "Try swimming or water aerobics",
      "Do gentle stretching exercises daily"
    ],
    difficulty: "easy",
    timeCommitment: "20-45 minutes",
    frequency: "4-5 times per week",
    priority: "high",
    ibsSpecific: true,
    tips: [
      "Avoid high-intensity workouts during flare-ups",
      "Listen to your body and adjust intensity",
      "Exercise at least 2 hours after eating"
    ]
  },
  {
    id: "sleep-hygiene",
    category: "sleep",
    title: "Sleep Quality Improvement",
    description: "Establish healthy sleep patterns to support gut healing and reduce IBS symptoms",
    benefits: ["Better gut healing", "Reduced inflammation", "Improved mood", "Stronger immune system"],
    actionItems: [
      "Maintain consistent sleep schedule (same bedtime/wake time)",
      "Create a relaxing bedtime routine",
      "Avoid screens 1 hour before bed",
      "Keep bedroom cool, dark, and quiet"
    ],
    difficulty: "medium",
    timeCommitment: "8-9 hours sleep + 30 min routine",
    frequency: "Daily",
    priority: "high",
    ibsSpecific: true,
    tips: [
      "Use blackout curtains or eye mask",
      "Try chamomile tea 30 minutes before bed",
      "Keep a sleep diary to track patterns"
    ]
  },
  {
    id: "hydration-routine",
    category: "hydration",
    title: "Optimal Hydration Strategy",
    description: "Maintain proper hydration to support digestive function and overall health",
    benefits: ["Better digestion", "Reduced constipation", "Improved energy", "Clearer skin"],
    actionItems: [
      "Drink 8-10 glasses of water daily",
      "Start day with warm water and lemon",
      "Sip herbal teas throughout the day",
      "Monitor urine color as hydration indicator"
    ],
    difficulty: "easy",
    timeCommitment: "Throughout the day",
    frequency: "Daily",
    priority: "medium",
    ibsSpecific: false,
    tips: [
      "Set hourly water reminders on your phone",
      "Keep a water bottle visible at your workspace",
      "Flavor water with cucumber or mint if plain water is boring"
    ]
  },
  {
    id: "mindfulness-practice",
    category: "mindfulness",
    title: "Mindfulness and Meditation",
    description: "Develop mindfulness practices to improve gut-brain connection and reduce anxiety",
    benefits: ["Reduced anxiety", "Better body awareness", "Improved stress response", "Enhanced focus"],
    actionItems: [
      "Practice 10-minute guided meditation daily",
      "Try mindful eating exercises",
      "Use body scan techniques to identify tension",
      "Practice gratitude journaling"
    ],
    difficulty: "medium",
    timeCommitment: "10-20 minutes daily",
    frequency: "Daily",
    priority: "medium",
    ibsSpecific: true,
    tips: [
      "Start with 3-5 minutes if you're new to meditation",
      "Use apps like Insight Timer for free guided sessions",
      "Practice mindful breathing during meals"
    ]
  },
  {
    id: "social-support",
    category: "social",
    title: "Social Connection and Support",
    description: "Build and maintain supportive relationships to improve mental health and IBS management",
    benefits: ["Reduced isolation", "Better stress management", "Emotional support", "Shared coping strategies"],
    actionItems: [
      "Join IBS support groups (online or local)",
      "Share your condition with trusted friends/family",
      "Schedule regular social activities",
      "Consider counseling or therapy if needed"
    ],
    difficulty: "medium",
    timeCommitment: "1-2 hours weekly",
    frequency: "Weekly",
    priority: "medium",
    ibsSpecific: true,
    tips: [
      "Look for IBS communities on Reddit or Facebook",
      "Be open about your needs with friends",
      "Don't let IBS prevent you from social activities"
    ]
  }
];

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'exercise': return <Activity className="h-5 w-5" />;
    case 'stress': return <Brain className="h-5 w-5" />;
    case 'sleep': return <Moon className="h-5 w-5" />;
    case 'hydration': return <Droplets className="h-5 w-5" />;
    case 'mindfulness': return <Smile className="h-5 w-5" />;
    case 'social': return <Users className="h-5 w-5" />;
    default: return <Heart className="h-5 w-5" />;
  }
};

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'exercise': return 'text-green-500 bg-green-100';
    case 'stress': return 'text-purple-500 bg-purple-100';
    case 'sleep': return 'text-blue-500 bg-blue-100';
    case 'hydration': return 'text-cyan-500 bg-cyan-100';
    case 'mindfulness': return 'text-orange-500 bg-orange-100';
    case 'social': return 'text-pink-500 bg-pink-100';
    default: return 'text-gray-500 bg-gray-100';
  }
};

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'high': return 'bg-red-100 text-red-800';
    case 'medium': return 'bg-yellow-100 text-yellow-800';
    case 'low': return 'bg-green-100 text-green-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

const RecommendationCard: React.FC<{ recommendation: LifestyleRecommendation }> = ({ 
  recommendation 
}) => (
  <Card className="h-full hover:shadow-lg transition-shadow duration-200">
    <CardHeader className="pb-3">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${getCategoryColor(recommendation.category)}`}>
            {getCategoryIcon(recommendation.category)}
          </div>
          <div>
            <CardTitle className="text-lg font-semibold text-gray-900">
              {recommendation.title}
            </CardTitle>
            <p className="text-sm text-gray-600 mt-1">
              {recommendation.description}
            </p>
          </div>
        </div>
        {recommendation.ibsSpecific && (
          <Badge variant="default" className="text-xs bg-blue-100 text-blue-800">
            IBS Specific
          </Badge>
        )}
      </div>
      
      <div className="flex items-center gap-2 mt-3">
        <Badge className={`text-xs ${getPriorityColor(recommendation.priority)}`}>
          {recommendation.priority} priority
        </Badge>
        <Badge variant="outline" className="text-xs">
          {recommendation.difficulty}
        </Badge>
      </div>
    </CardHeader>
    
    <CardContent className="pt-0">
      {/* Time and Frequency */}
      <div className="bg-gray-50 p-3 rounded-lg mb-4">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-gray-500" />
            <div>
              <p className="text-gray-600">Time</p>
              <p className="font-medium text-gray-900">{recommendation.timeCommitment}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-gray-500" />
            <div>
              <p className="text-gray-600">Frequency</p>
              <p className="font-medium text-gray-900">{recommendation.frequency}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Benefits */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center gap-1">
          <TrendingUp className="h-4 w-4 text-green-500" />
          Key Benefits
        </h4>
        <div className="space-y-1">
          {recommendation.benefits.map((benefit, index) => (
            <div key={index} className="flex items-center gap-2 text-sm">
              <CheckCircle className="h-3 w-3 text-green-500 flex-shrink-0" />
              <span className="text-gray-700">{benefit}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Action Items */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center gap-1">
          <Target className="h-4 w-4 text-blue-500" />
          Action Steps
        </h4>
        <div className="space-y-2">
          {recommendation.actionItems.map((item, index) => (
            <div key={index} className="flex items-start gap-2 text-sm">
              <div className="bg-blue-100 text-blue-800 rounded-full w-5 h-5 flex items-center justify-center text-xs font-medium flex-shrink-0 mt-0.5">
                {index + 1}
              </div>
              <span className="text-gray-700">{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Tips */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center gap-1">
          <Zap className="h-4 w-4 text-yellow-500" />
          Pro Tips
        </h4>
        <div className="space-y-1">
          {recommendation.tips.map((tip, index) => (
            <div key={index} className="flex items-start gap-2 text-sm">
              <div className="w-1 h-1 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
              <span className="text-gray-600">{tip}</span>
            </div>
          ))}
        </div>
      </div>

      <Button variant="outline" size="sm" className="w-full">
        Start This Practice
      </Button>
    </CardContent>
  </Card>
);

const HealthMetrics: React.FC<{ profile: UserHealthProfile }> = ({ profile }) => (
  <Card className="mb-6">
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Shield className="h-5 w-5 text-blue-500" />
        Your Health Profile Overview
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Stress Level */}
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-purple-900">Stress Level</span>
            <Brain className="h-4 w-4 text-purple-500" />
          </div>
          <div className="space-y-2">
            <div className="text-2xl font-bold text-purple-900">{profile.stressLevel}/10</div>
            <Progress value={profile.stressLevel * 10} className="h-2" />
            <p className="text-xs text-purple-700">
              {profile.stressLevel >= 7 ? 'High - Focus on stress reduction' : 
               profile.stressLevel >= 4 ? 'Moderate - Maintain current practices' : 
               'Low - Great job managing stress!'}
            </p>
          </div>
        </div>

        {/* Sleep Quality */}
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-900">Sleep Quality</span>
            <Moon className="h-4 w-4 text-blue-500" />
          </div>
          <div className="space-y-2">
            <div className="text-2xl font-bold text-blue-900">{profile.sleepQuality}/10</div>
            <Progress value={profile.sleepQuality * 10} className="h-2" />
            <p className="text-xs text-blue-700">
              {profile.sleepQuality >= 7 ? 'Good - Keep it up!' : 
               profile.sleepQuality >= 4 ? 'Fair - Room for improvement' : 
               'Poor - Priority focus area'}
            </p>
          </div>
        </div>

        {/* Exercise Level */}
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-green-900">Exercise Level</span>
            <Activity className="h-4 w-4 text-green-500" />
          </div>
          <div className="space-y-2">
            <div className="text-lg font-bold text-green-900">{profile.exerciseLevel}</div>
            <p className="text-xs text-green-700">
              {profile.exerciseLevel === 'High' ? 'Excellent activity level' : 
               profile.exerciseLevel === 'Medium' ? 'Good, consider gentle increases' : 
               'Start with gentle activities'}
            </p>
          </div>
        </div>

        {/* IBS Severity */}
        <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-orange-900">IBS Severity</span>
            <AlertCircle className="h-4 w-4 text-orange-500" />
          </div>
          <div className="space-y-2">
            <div className="text-lg font-bold text-orange-900">{profile.severityLevel}</div>
            <p className="text-xs text-orange-700">
              Type: {profile.ibsType}
            </p>
          </div>
        </div>
      </div>

      {/* Current Symptoms */}
      <div className="mt-4 p-4 bg-red-50 rounded-lg border border-red-200">
        <h4 className="text-sm font-medium text-red-900 mb-2">Current Symptoms</h4>
        <div className="flex flex-wrap gap-2">
          {profile.currentSymptoms.map((symptom, index) => (
            <Badge key={index} variant="secondary" className="bg-red-100 text-red-800 text-xs">
              {symptom}
            </Badge>
          ))}
        </div>
      </div>
    </CardContent>
  </Card>
);

export const LifestyleRecommendations: React.FC<LifestyleRecommendationsProps> = ({ 
  userProfile = mockUserProfile 
}) => {
  // Filter recommendations based on user profile
  const prioritizedRecommendations = mockRecommendations.sort((a, b) => {
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    return priorityOrder[b.priority] - priorityOrder[a.priority];
  });

  return (
    <div className="space-y-6">
      {/* Health Profile Overview */}
      <HealthMetrics profile={userProfile} />

      {/* Lifestyle Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5 text-red-500" />
            Personalized Lifestyle Recommendations
          </CardTitle>
          <p className="text-sm text-gray-600">
            Evidence-based lifestyle changes tailored to your IBS profile and current health metrics
          </p>
        </CardHeader>
        
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {prioritizedRecommendations.map((recommendation) => (
              <RecommendationCard 
                key={recommendation.id} 
                recommendation={recommendation} 
              />
            ))}
          </div>

          {/* Quick Action Summary */}
          <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
            <h4 className="font-medium text-blue-900 mb-3 flex items-center gap-2">
              <Timer className="h-4 w-4" />
              Quick Start Guide - This Week
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <h5 className="font-medium text-blue-800 mb-2">High Priority Actions:</h5>
                <ul className="space-y-1 text-blue-700">
                  <li>• Start 10-minute daily stress management routine</li>
                  <li>• Establish consistent sleep schedule</li>
                  <li>• Begin gentle 20-minute walks after meals</li>
                </ul>
              </div>
              <div>
                <h5 className="font-medium text-blue-800 mb-2">This Week's Goals:</h5>
                <ul className="space-y-1 text-blue-700">
                  <li>• Track stress levels and sleep quality</li>
                  <li>• Try one new mindfulness technique</li>
                  <li>• Connect with one supportive person about IBS</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};