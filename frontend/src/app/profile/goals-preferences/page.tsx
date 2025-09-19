'use client';

import { useState, useEffect } from 'react';
import { ProtectedRoute } from "@/components/protected-route";
import { DashboardHeader } from "@/components/layout/dashboard-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";


import { Target, Save, ArrowLeft, Plus, X, Bell, Calendar, TrendingUp } from "lucide-react";
import { useRouter } from 'next/navigation';

interface GoalsPreferencesData {
  healthGoals: string[];
  symptomManagementGoals: string[];
  lifestyleGoals: string[];
  shortTermGoals: string[];
  longTermGoals: string[];
  motivationLevel: number;
  preferredTrackingMethods: string[];
  reminderPreferences: {
    medicationReminders: boolean;
    mealLogging: boolean;
    symptomTracking: boolean;
    exerciseReminders: boolean;
    waterIntakeReminders: boolean;
    sleepReminders: boolean;
  };
  notificationSettings: {
    pushNotifications: boolean;
    emailNotifications: boolean;
    smsNotifications: boolean;
    weeklyReports: boolean;
    monthlyReports: boolean;
  };
  dataPrivacyPreferences: {
    shareAnonymousData: boolean;
    allowResearchParticipation: boolean;
    dataRetentionPeriod: string;
  };
  appPreferences: {
    theme: string;
    language: string;
    measurementUnits: string;
    defaultDashboardView: string;
  };
  supportPreferences: string[];
  prioritySymptoms: string[];
  successMetrics: string[];
  challengeAreas: string[];
  specialNotes: string;
}

const healthGoalOptions = [
  'Reduce IBS symptoms', 'Improve digestive health', 'Better sleep quality',
  'Increase energy levels', 'Reduce stress', 'Maintain healthy weight',
  'Improve mental health', 'Better work-life balance', 'Increase physical activity',
  'Improve diet quality', 'Better hydration', 'Reduce inflammation'
];

const symptomGoalOptions = [
  'Reduce abdominal pain', 'Improve bowel regularity', 'Reduce bloating',
  'Minimize gas and flatulence', 'Reduce nausea', 'Improve stool consistency',
  'Reduce urgency episodes', 'Minimize cramping', 'Better symptom prediction',
  'Reduce symptom severity', 'Increase symptom-free days'
];

const lifestyleGoalOptions = [
  'Establish regular meal times', 'Improve cooking skills', 'Reduce processed foods',
  'Increase fiber intake gradually', 'Better stress management', 'Regular exercise routine',
  'Improve sleep hygiene', 'Reduce screen time', 'More social activities',
  'Better time management', 'Mindfulness practice', 'Hobby development'
];

const trackingMethodOptions = [
  'Daily symptom diary', 'Food logging', 'Mood tracking', 'Exercise logging',
  'Sleep tracking', 'Medication tracking', 'Photo documentation',
  'Voice notes', 'Wearable device sync', 'Manual entry', 'Automated reminders'
];

const supportPreferenceOptions = [
  'Educational articles', 'Video tutorials', 'Community forums',
  'Expert consultations', 'Peer support groups', 'Personalized tips',
  'Progress celebrations', 'Challenge participation', 'Recipe suggestions',
  'Exercise recommendations', 'Meditation guides', 'Live chat support'
];

const prioritySymptomOptions = [
  'Abdominal pain', 'Bloating', 'Diarrhea', 'Constipation', 'Gas',
  'Nausea', 'Cramping', 'Urgency', 'Incomplete evacuation', 'Mucus in stool',
  'Fatigue', 'Anxiety related to symptoms'
];

const successMetricOptions = [
  'Symptom frequency reduction', 'Symptom severity reduction', 'Quality of life improvement',
  'Sleep quality improvement', 'Energy level increase', 'Stress reduction',
  'Weight management', 'Medication reduction', 'Social activity increase',
  'Work productivity improvement', 'Mood improvement', 'Confidence increase'
];

const challengeAreaOptions = [
  'Meal planning', 'Eating out', 'Travel management', 'Work stress',
  'Social situations', 'Exercise consistency', 'Sleep routine',
  'Medication adherence', 'Symptom tracking consistency', 'Dietary restrictions',
  'Time management', 'Motivation maintenance'
];

const themeOptions = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'auto', label: 'Auto (system)' }
];

const languageOptions = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' }
];

const unitOptions = [
  { value: 'metric', label: 'Metric (kg, cm)' },
  { value: 'imperial', label: 'Imperial (lbs, ft/in)' }
];

const dashboardViewOptions = [
  { value: 'overview', label: 'Overview Dashboard' },
  { value: 'symptoms', label: 'Symptom Tracker' },
  { value: 'food', label: 'Food Diary' },
  { value: 'insights', label: 'Insights & Trends' }
];

const dataRetentionOptions = [
  { value: '1year', label: '1 Year' },
  { value: '2years', label: '2 Years' },
  { value: '5years', label: '5 Years' },
  { value: 'indefinite', label: 'Indefinite' }
];

export default function GoalsPreferencesPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<GoalsPreferencesData>({
    healthGoals: [],
    symptomManagementGoals: [],
    lifestyleGoals: [],
    shortTermGoals: [],
    longTermGoals: [],
    motivationLevel: 7,
    preferredTrackingMethods: [],
    reminderPreferences: {
      medicationReminders: true,
      mealLogging: true,
      symptomTracking: true,
      exerciseReminders: false,
      waterIntakeReminders: false,
      sleepReminders: false,
    },
    notificationSettings: {
      pushNotifications: true,
      emailNotifications: false,
      smsNotifications: false,
      weeklyReports: true,
      monthlyReports: true,
    },
    dataPrivacyPreferences: {
      shareAnonymousData: false,
      allowResearchParticipation: false,
      dataRetentionPeriod: '2years',
    },
    appPreferences: {
      theme: 'auto',
      language: 'en',
      measurementUnits: 'metric',
      defaultDashboardView: 'overview',
    },
    supportPreferences: [],
    prioritySymptoms: [],
    successMetrics: [],
    challengeAreas: [],
    specialNotes: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [newShortTermGoal, setNewShortTermGoal] = useState('');
  const [newLongTermGoal, setNewLongTermGoal] = useState('');

  useEffect(() => {
    loadGoalsPreferences();
  }, []);

  const loadGoalsPreferences = async () => {
    setIsLoading(true);
    try {
      // TODO: Replace with actual API call
      const response = await fetch('/api/profile/goals-preferences');
      if (response.ok) {
        const data = await response.json();
        setFormData(data);
      }
    } catch (error) {
      console.error('Failed to load goals and preferences:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: keyof GoalsPreferencesData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNestedChange = (section: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...(prev[section as keyof GoalsPreferencesData] as any),
        [field]: value
      }
    }));
  };

  const handleArrayToggle = (field: keyof GoalsPreferencesData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: (prev[field] as string[]).includes(value)
        ? (prev[field] as string[]).filter(item => item !== value)
        : [...(prev[field] as string[]), value]
    }));
  };

  const addToArray = (field: keyof GoalsPreferencesData, value: string) => {
    if (value.trim() && !(formData[field] as string[]).includes(value.trim())) {
      setFormData(prev => ({
        ...prev,
        [field]: [...(prev[field] as string[]), value.trim()]
      }));
    }
  };

  const removeFromArray = (field: keyof GoalsPreferencesData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: (prev[field] as string[]).filter(item => item !== value)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      // TODO: Replace with actual API call
      const response = await fetch('/api/profile/goals-preferences', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        router.push('/profile');
      } else {
        throw new Error('Failed to save goals and preferences');
      }
    } catch (error) {
      console.error('Failed to save goals and preferences:', error);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50">
          <DashboardHeader title="Goals & Preferences" showBackButton />
          <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="animate-pulse space-y-6">
              <div className="h-8 bg-gray-200 rounded w-1/3"></div>
              <div className="space-y-4">
                {[1, 2, 3, 4, 5].map(i => (
                  <div key={i} className="h-32 bg-gray-200 rounded"></div>
                ))}
              </div>
            </div>
          </main>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader title="Goals & Preferences" showBackButton />
        
        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.back()}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Back
              </Button>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-full">
                  <Target className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Goals & Preferences</h1>
                  <p className="text-gray-600">Health goals and app notification preferences</p>
                </div>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Health Goals */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Health Goals
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <Label>Overall Health Goals</Label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                      {healthGoalOptions.map(goal => (
                        <div key={goal} className="flex items-center space-x-2">
                          <Checkbox
                            id={`health-goal-${goal}`}
                            checked={formData.healthGoals.includes(goal)}
                            onCheckedChange={() => handleArrayToggle('healthGoals', goal)}
                          />
                          <Label htmlFor={`health-goal-${goal}`} className="text-sm">
                            {goal}
                          </Label>
                        </div>
                      ))}
                    </div>
                    {formData.healthGoals.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-4">
                        {formData.healthGoals.map(goal => (
                          <Badge key={goal} variant="secondary" className="flex items-center gap-1">
                            {goal}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('healthGoals', goal)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>

                  <div>
                    <Label>Symptom Management Goals</Label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                      {symptomGoalOptions.map(goal => (
                        <div key={goal} className="flex items-center space-x-2">
                          <Checkbox
                            id={`symptom-goal-${goal}`}
                            checked={formData.symptomManagementGoals.includes(goal)}
                            onCheckedChange={() => handleArrayToggle('symptomManagementGoals', goal)}
                          />
                          <Label htmlFor={`symptom-goal-${goal}`} className="text-sm">
                            {goal}
                          </Label>
                        </div>
                      ))}
                    </div>
                    {formData.symptomManagementGoals.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-4">
                        {formData.symptomManagementGoals.map(goal => (
                          <Badge key={goal} variant="outline" className="flex items-center gap-1">
                            {goal}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('symptomManagementGoals', goal)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>

                  <div>
                    <Label>Lifestyle Goals</Label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                      {lifestyleGoalOptions.map(goal => (
                        <div key={goal} className="flex items-center space-x-2">
                          <Checkbox
                            id={`lifestyle-goal-${goal}`}
                            checked={formData.lifestyleGoals.includes(goal)}
                            onCheckedChange={() => handleArrayToggle('lifestyleGoals', goal)}
                          />
                          <Label htmlFor={`lifestyle-goal-${goal}`} className="text-sm">
                            {goal}
                          </Label>
                        </div>
                      ))}
                    </div>
                    {formData.lifestyleGoals.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-4">
                        {formData.lifestyleGoals.map(goal => (
                          <Badge key={goal} variant="default" className="flex items-center gap-1">
                            {goal}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('lifestyleGoals', goal)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>

                  <div>
                    <Label>Motivation Level (1-10): {formData.motivationLevel}</Label>
                    <Slider
                      value={[formData.motivationLevel]}
                      onValueChange={(value) => handleInputChange('motivationLevel', value[0])}
                      max={10}
                      min={1}
                      step={1}
                      className="mt-2"
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Personal Goals */}
              <Card>
                <CardHeader>
                  <CardTitle>Personal Goals</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Short-term Goals (next 3 months)</Label>
                    <div className="flex gap-2 mt-2">
                      <Input
                        placeholder="Add short-term goal..."
                        value={newShortTermGoal}
                        onChange={(e) => setNewShortTermGoal(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            addToArray('shortTermGoals', newShortTermGoal);
                            setNewShortTermGoal('');
                          }
                        }}
                      />
                      <Button
                        type="button"
                        onClick={() => {
                          addToArray('shortTermGoals', newShortTermGoal);
                          setNewShortTermGoal('');
                        }}
                      >
                        <Plus className="h-4 w-4" />
                      </Button>
                    </div>
                    {formData.shortTermGoals.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {formData.shortTermGoals.map(goal => (
                          <Badge key={goal} variant="secondary" className="flex items-center gap-1">
                            {goal}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('shortTermGoals', goal)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>

                  <div>
                    <Label>Long-term Goals (6+ months)</Label>
                    <div className="flex gap-2 mt-2">
                      <Input
                        placeholder="Add long-term goal..."
                        value={newLongTermGoal}
                        onChange={(e) => setNewLongTermGoal(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            addToArray('longTermGoals', newLongTermGoal);
                            setNewLongTermGoal('');
                          }
                        }}
                      />
                      <Button
                        type="button"
                        onClick={() => {
                          addToArray('longTermGoals', newLongTermGoal);
                          setNewLongTermGoal('');
                        }}
                      >
                        <Plus className="h-4 w-4" />
                      </Button>
                    </div>
                    {formData.longTermGoals.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {formData.longTermGoals.map(goal => (
                          <Badge key={goal} variant="outline" className="flex items-center gap-1">
                            {goal}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('longTermGoals', goal)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Tracking Preferences */}
              <Card>
                <CardHeader>
                  <CardTitle>Tracking Preferences</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Preferred Tracking Methods</Label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                      {trackingMethodOptions.map(method => (
                        <div key={method} className="flex items-center space-x-2">
                          <Checkbox
                            id={`tracking-${method}`}
                            checked={formData.preferredTrackingMethods.includes(method)}
                            onCheckedChange={() => handleArrayToggle('preferredTrackingMethods', method)}
                          />
                          <Label htmlFor={`tracking-${method}`} className="text-sm">
                            {method}
                          </Label>
                        </div>
                      ))}
                    </div>
                    {formData.preferredTrackingMethods.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-4">
                        {formData.preferredTrackingMethods.map(method => (
                          <Badge key={method} variant="outline" className="flex items-center gap-1">
                            {method}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('preferredTrackingMethods', method)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>

                  <div>
                    <Label>Priority Symptoms to Track</Label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                      {prioritySymptomOptions.map(symptom => (
                        <div key={symptom} className="flex items-center space-x-2">
                          <Checkbox
                            id={`priority-${symptom}`}
                            checked={formData.prioritySymptoms.includes(symptom)}
                            onCheckedChange={() => handleArrayToggle('prioritySymptoms', symptom)}
                          />
                          <Label htmlFor={`priority-${symptom}`} className="text-sm">
                            {symptom}
                          </Label>
                        </div>
                      ))}
                    </div>
                    {formData.prioritySymptoms.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-4">
                        {formData.prioritySymptoms.map(symptom => (
                          <Badge key={symptom} variant="destructive" className="flex items-center gap-1">
                            {symptom}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('prioritySymptoms', symptom)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Reminder Preferences */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bell className="h-5 w-5" />
                    Reminder Preferences
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(formData.reminderPreferences).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between">
                        <Label htmlFor={`reminder-${key}`} className="text-sm font-medium">
                          {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                        </Label>
                        <Checkbox
                          id={`reminder-${key}`}
                          checked={value}
                          onCheckedChange={(checked: boolean) => handleNestedChange('reminderPreferences', key, checked)}
                        />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Notification Settings */}
              <Card>
                <CardHeader>
                  <CardTitle>Notification Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(formData.notificationSettings).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between">
                        <Label htmlFor={`notification-${key}`} className="text-sm font-medium">
                          {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                        </Label>
                        <Checkbox
                          id={`notification-${key}`}
                          checked={value}
                          onCheckedChange={(checked: boolean) => handleNestedChange('notificationSettings', key, checked)}
                        />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* App Preferences */}
              <Card>
                <CardHeader>
                  <CardTitle>App Preferences</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="theme">Theme</Label>
                      <Select value={formData.appPreferences.theme} onValueChange={(value) => handleNestedChange('appPreferences', 'theme', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select theme" />
                        </SelectTrigger>
                        <SelectContent>
                          {themeOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="language">Language</Label>
                      <Select value={formData.appPreferences.language} onValueChange={(value) => handleNestedChange('appPreferences', 'language', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select language" />
                        </SelectTrigger>
                        <SelectContent>
                          {languageOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="measurementUnits">Measurement Units</Label>
                      <Select value={formData.appPreferences.measurementUnits} onValueChange={(value) => handleNestedChange('appPreferences', 'measurementUnits', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select units" />
                        </SelectTrigger>
                        <SelectContent>
                          {unitOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="defaultDashboardView">Default Dashboard View</Label>
                      <Select value={formData.appPreferences.defaultDashboardView} onValueChange={(value) => handleNestedChange('appPreferences', 'defaultDashboardView', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select default view" />
                        </SelectTrigger>
                        <SelectContent>
                          {dashboardViewOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Success Metrics & Challenges */}
              <Card>
                <CardHeader>
                  <CardTitle>Success Metrics & Challenges</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>How do you measure success?</Label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                      {successMetricOptions.map(metric => (
                        <div key={metric} className="flex items-center space-x-2">
                          <Checkbox
                            id={`success-${metric}`}
                            checked={formData.successMetrics.includes(metric)}
                            onCheckedChange={() => handleArrayToggle('successMetrics', metric)}
                          />
                          <Label htmlFor={`success-${metric}`} className="text-sm">
                            {metric}
                          </Label>
                        </div>
                      ))}
                    </div>
                    {formData.successMetrics.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-4">
                        {formData.successMetrics.map(metric => (
                          <Badge key={metric} variant="default" className="flex items-center gap-1">
                            {metric}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('successMetrics', metric)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>

                  <div>
                    <Label>Challenge Areas</Label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                      {challengeAreaOptions.map(challenge => (
                        <div key={challenge} className="flex items-center space-x-2">
                          <Checkbox
                            id={`challenge-${challenge}`}
                            checked={formData.challengeAreas.includes(challenge)}
                            onCheckedChange={() => handleArrayToggle('challengeAreas', challenge)}
                          />
                          <Label htmlFor={`challenge-${challenge}`} className="text-sm">
                            {challenge}
                          </Label>
                        </div>
                      ))}
                    </div>
                    {formData.challengeAreas.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-4">
                        {formData.challengeAreas.map(challenge => (
                          <Badge key={challenge} variant="secondary" className="flex items-center gap-1">
                            {challenge}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('challengeAreas', challenge)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Support Preferences */}
              <Card>
                <CardHeader>
                  <CardTitle>Support Preferences</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Preferred Support Types</Label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                      {supportPreferenceOptions.map(support => (
                        <div key={support} className="flex items-center space-x-2">
                          <Checkbox
                            id={`support-${support}`}
                            checked={formData.supportPreferences.includes(support)}
                            onCheckedChange={() => handleArrayToggle('supportPreferences', support)}
                          />
                          <Label htmlFor={`support-${support}`} className="text-sm">
                            {support}
                          </Label>
                        </div>
                      ))}
                    </div>
                    {formData.supportPreferences.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-4">
                        {formData.supportPreferences.map(support => (
                          <Badge key={support} variant="outline" className="flex items-center gap-1">
                            {support}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('supportPreferences', support)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Privacy Preferences */}
              <Card>
                <CardHeader>
                  <CardTitle>Privacy Preferences</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="shareAnonymousData" className="text-sm font-medium">
                          Share Anonymous Data
                        </Label>
                        <p className="text-xs text-gray-500">Help improve the app by sharing anonymized usage data</p>
                      </div>
                      <Checkbox
                        id="shareAnonymousData"
                        checked={formData.dataPrivacyPreferences.shareAnonymousData}
                        onCheckedChange={(checked: boolean) => handleNestedChange('dataPrivacyPreferences', 'shareAnonymousData', checked)}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="allowResearchParticipation" className="text-sm font-medium">
                          Allow Research Participation
                        </Label>
                        <p className="text-xs text-gray-500">Participate in IBS research studies (optional)</p>
                      </div>
                      <Checkbox
                        id="allowResearchParticipation"
                        checked={formData.dataPrivacyPreferences.allowResearchParticipation}
                        onCheckedChange={(checked: boolean) => handleNestedChange('dataPrivacyPreferences', 'allowResearchParticipation', checked)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="dataRetentionPeriod">Data Retention Period</Label>
                      <Select value={formData.dataPrivacyPreferences.dataRetentionPeriod} onValueChange={(value) => handleNestedChange('dataPrivacyPreferences', 'dataRetentionPeriod', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select retention period" />
                        </SelectTrigger>
                        <SelectContent>
                          {dataRetentionOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Additional Notes */}
              <Card>
                <CardHeader>
                  <CardTitle>Additional Notes</CardTitle>
                </CardHeader>
                <CardContent>
                  <div>
                    <Label htmlFor="specialNotes">Special Notes</Label>
                    <Textarea
                      id="specialNotes"
                      placeholder="Any additional goals, preferences, or considerations..."
                      value={formData.specialNotes}
                      onChange={(e) => handleInputChange('specialNotes', e.target.value)}
                      rows={3}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Action Buttons */}
              <div className="flex justify-end gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push('/profile')}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isSaving}
                  className="flex items-center gap-2"
                >
                  {isSaving ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4" />
                      Save Changes
                    </>
                  )}
                </Button>
              </div>
            </form>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}