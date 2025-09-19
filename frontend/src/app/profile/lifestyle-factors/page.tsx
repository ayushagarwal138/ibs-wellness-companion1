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
import { Activity, Save, ArrowLeft, Plus, X } from "lucide-react";
import { useRouter } from 'next/navigation';

interface LifestyleFactorsData {
  exerciseFrequency: string;
  exerciseTypes: string[];
  exerciseDuration: number;
  exerciseIntensity: string;
  sleepHours: number;
  sleepQuality: string;
  bedtime: string;
  wakeupTime: string;
  stressLevel: number;
  stressManagement: string[];
  workSchedule: string;
  workStressLevel: number;
  smokingStatus: string;
  smokingFrequency: string;
  socialSupport: string;
  hobbies: string[];
  screenTime: number;
  outdoorTime: number;
  travelFrequency: string;
  livingEnvironment: string;
  petOwnership: string;
  relaxationActivities: string[];
  mentalHealthSupport: string;
  specialNotes: string;
}

const exerciseTypeOptions = [
  'Walking', 'Running', 'Cycling', 'Swimming', 'Yoga', 'Pilates', 
  'Weight training', 'Cardio machines', 'Dancing', 'Sports', 
  'Hiking', 'Rock climbing', 'Martial arts', 'Stretching'
];

const exerciseFrequencyOptions = [
  { value: 'none', label: 'No exercise' },
  { value: 'rarely', label: 'Rarely (less than once/week)' },
  { value: '1-2_week', label: '1-2 times per week' },
  { value: '3-4_week', label: '3-4 times per week' },
  { value: '5-6_week', label: '5-6 times per week' },
  { value: 'daily', label: 'Daily' }
];

const exerciseIntensityOptions = [
  { value: 'light', label: 'Light (easy pace, can talk easily)' },
  { value: 'moderate', label: 'Moderate (somewhat hard, can talk with effort)' },
  { value: 'vigorous', label: 'Vigorous (hard, difficult to talk)' },
  { value: 'mixed', label: 'Mixed intensity' }
];

const sleepQualityOptions = [
  { value: 'excellent', label: 'Excellent' },
  { value: 'good', label: 'Good' },
  { value: 'fair', label: 'Fair' },
  { value: 'poor', label: 'Poor' },
  { value: 'very_poor', label: 'Very Poor' }
];

const stressManagementOptions = [
  'Meditation', 'Deep breathing', 'Exercise', 'Yoga', 'Reading', 
  'Music', 'Journaling', 'Therapy/Counseling', 'Social support', 
  'Hobbies', 'Nature walks', 'Massage', 'Prayer/Spirituality'
];

const workScheduleOptions = [
  { value: 'regular_day', label: 'Regular day shift (9-5)' },
  { value: 'irregular_hours', label: 'Irregular hours' },
  { value: 'night_shift', label: 'Night shift' },
  { value: 'rotating_shifts', label: 'Rotating shifts' },
  { value: 'part_time', label: 'Part-time' },
  { value: 'freelance', label: 'Freelance/Self-employed' },
  { value: 'retired', label: 'Retired' },
  { value: 'unemployed', label: 'Unemployed' },
  { value: 'student', label: 'Student' }
];

const smokingStatusOptions = [
  { value: 'never', label: 'Never smoked' },
  { value: 'former', label: 'Former smoker' },
  { value: 'current', label: 'Current smoker' },
  { value: 'occasional', label: 'Occasional smoker' }
];

const smokingFrequencyOptions = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'socially', label: 'Socially only' }
];

const socialSupportOptions = [
  { value: 'excellent', label: 'Excellent support system' },
  { value: 'good', label: 'Good support system' },
  { value: 'moderate', label: 'Moderate support' },
  { value: 'limited', label: 'Limited support' },
  { value: 'none', label: 'No support system' }
];

const travelFrequencyOptions = [
  { value: 'never', label: 'Never' },
  { value: 'rarely', label: 'Rarely (once a year or less)' },
  { value: 'occasionally', label: 'Occasionally (2-3 times/year)' },
  { value: 'frequently', label: 'Frequently (monthly)' },
  { value: 'very_frequently', label: 'Very frequently (weekly)' }
];

const livingEnvironmentOptions = [
  { value: 'urban', label: 'Urban/City' },
  { value: 'suburban', label: 'Suburban' },
  { value: 'rural', label: 'Rural/Country' },
  { value: 'apartment', label: 'Apartment' },
  { value: 'house', label: 'House' }
];

const petOwnershipOptions = [
  { value: 'none', label: 'No pets' },
  { value: 'dog', label: 'Dog(s)' },
  { value: 'cat', label: 'Cat(s)' },
  { value: 'both', label: 'Both dogs and cats' },
  { value: 'other', label: 'Other pets' }
];

const relaxationOptions = [
  'Reading', 'Watching TV/Movies', 'Listening to music', 'Gardening',
  'Cooking', 'Art/Crafts', 'Gaming', 'Socializing', 'Meditation',
  'Bath/Spa activities', 'Photography', 'Writing'
];

const mentalHealthOptions = [
  { value: 'none', label: 'No support currently' },
  { value: 'therapy', label: 'Regular therapy/counseling' },
  { value: 'medication', label: 'Medication only' },
  { value: 'both', label: 'Both therapy and medication' },
  { value: 'support_groups', label: 'Support groups' },
  { value: 'informal', label: 'Informal support (friends/family)' }
];

export default function LifestyleFactorsPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<LifestyleFactorsData>({
    exerciseFrequency: '',
    exerciseTypes: [],
    exerciseDuration: 30,
    exerciseIntensity: '',
    sleepHours: 8,
    sleepQuality: '',
    bedtime: '',
    wakeupTime: '',
    stressLevel: 5,
    stressManagement: [],
    workSchedule: '',
    workStressLevel: 5,
    smokingStatus: '',
    smokingFrequency: '',
    socialSupport: '',
    hobbies: [],
    screenTime: 4,
    outdoorTime: 1,
    travelFrequency: '',
    livingEnvironment: '',
    petOwnership: '',
    relaxationActivities: [],
    mentalHealthSupport: '',
    specialNotes: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [newHobby, setNewHobby] = useState('');

  useEffect(() => {
    loadLifestyleFactors();
  }, []);

  const loadLifestyleFactors = async () => {
    setIsLoading(true);
    try {
      // TODO: Replace with actual API call
      const response = await fetch('/api/profile/lifestyle-factors');
      if (response.ok) {
        const data = await response.json();
        setFormData(data);
      }
    } catch (error) {
      console.error('Failed to load lifestyle factors:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: keyof LifestyleFactorsData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleArrayToggle = (field: keyof LifestyleFactorsData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: (prev[field] as string[]).includes(value)
        ? (prev[field] as string[]).filter(item => item !== value)
        : [...(prev[field] as string[]), value]
    }));
  };

  const addToArray = (field: keyof LifestyleFactorsData, value: string) => {
    if (value.trim() && !(formData[field] as string[]).includes(value.trim())) {
      setFormData(prev => ({
        ...prev,
        [field]: [...(prev[field] as string[]), value.trim()]
      }));
    }
  };

  const removeFromArray = (field: keyof LifestyleFactorsData, value: string) => {
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
      const response = await fetch('/api/profile/lifestyle-factors', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        router.push('/profile');
      } else {
        throw new Error('Failed to save lifestyle factors');
      }
    } catch (error) {
      console.error('Failed to save lifestyle factors:', error);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50">
          <DashboardHeader title="Lifestyle Factors" showBackButton />
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
        <DashboardHeader title="Lifestyle Factors" showBackButton />
        
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
                <div className="p-2 bg-blue-100 rounded-full">
                  <Activity className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Lifestyle Factors</h1>
                  <p className="text-gray-600">Exercise, sleep, stress levels, and daily routine</p>
                </div>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Exercise & Physical Activity */}
              <Card>
                <CardHeader>
                  <CardTitle>Exercise & Physical Activity</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="exerciseFrequency">Exercise Frequency</Label>
                      <Select value={formData.exerciseFrequency} onValueChange={(value) => handleInputChange('exerciseFrequency', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="How often do you exercise?" />
                        </SelectTrigger>
                        <SelectContent>
                          {exerciseFrequencyOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="exerciseIntensity">Exercise Intensity</Label>
                      <Select value={formData.exerciseIntensity} onValueChange={(value) => handleInputChange('exerciseIntensity', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select exercise intensity" />
                        </SelectTrigger>
                        <SelectContent>
                          {exerciseIntensityOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label>Exercise Duration (minutes per session): {formData.exerciseDuration}</Label>
                    <Slider
                      value={[formData.exerciseDuration]}
                      onValueChange={(value) => handleInputChange('exerciseDuration', value[0])}
                      max={180}
                      min={10}
                      step={5}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label>Types of Exercise</Label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                      {exerciseTypeOptions.map(type => (
                        <div key={type} className="flex items-center space-x-2">
                          <Checkbox
                            id={`exercise-${type}`}
                            checked={formData.exerciseTypes.includes(type)}
                            onCheckedChange={() => handleArrayToggle('exerciseTypes', type)}
                          />
                          <Label htmlFor={`exercise-${type}`} className="text-sm">
                            {type}
                          </Label>
                        </div>
                      ))}
                    </div>
                    {formData.exerciseTypes.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-4">
                        {formData.exerciseTypes.map(type => (
                          <Badge key={type} variant="secondary" className="flex items-center gap-1">
                            {type}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('exerciseTypes', type)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Sleep Patterns */}
              <Card>
                <CardHeader>
                  <CardTitle>Sleep Patterns</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>Sleep Hours per night: {formData.sleepHours}</Label>
                      <Slider
                        value={[formData.sleepHours]}
                        onValueChange={(value) => handleInputChange('sleepHours', value[0])}
                        max={12}
                        min={3}
                        step={0.5}
                        className="mt-2"
                      />
                    </div>
                    <div>
                      <Label htmlFor="sleepQuality">Sleep Quality</Label>
                      <Select value={formData.sleepQuality} onValueChange={(value) => handleInputChange('sleepQuality', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Rate your sleep quality" />
                        </SelectTrigger>
                        <SelectContent>
                          {sleepQualityOptions.map(option => (
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
                      <Label htmlFor="bedtime">Typical Bedtime</Label>
                      <Input
                        id="bedtime"
                        type="time"
                        value={formData.bedtime}
                        onChange={(e) => handleInputChange('bedtime', e.target.value)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="wakeupTime">Typical Wake-up Time</Label>
                      <Input
                        id="wakeupTime"
                        type="time"
                        value={formData.wakeupTime}
                        onChange={(e) => handleInputChange('wakeupTime', e.target.value)}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Stress & Mental Health */}
              <Card>
                <CardHeader>
                  <CardTitle>Stress & Mental Health</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label>Overall Stress Level (1-10): {formData.stressLevel}</Label>
                      <Slider
                        value={[formData.stressLevel]}
                        onValueChange={(value) => handleInputChange('stressLevel', value[0])}
                        max={10}
                        min={1}
                        step={1}
                        className="mt-2"
                      />
                    </div>
                    <div>
                      <Label>Work Stress Level (1-10): {formData.workStressLevel}</Label>
                      <Slider
                        value={[formData.workStressLevel]}
                        onValueChange={(value) => handleInputChange('workStressLevel', value[0])}
                        max={10}
                        min={1}
                        step={1}
                        className="mt-2"
                      />
                    </div>
                  </div>

                  <div>
                    <Label>Stress Management Techniques</Label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                      {stressManagementOptions.map(technique => (
                        <div key={technique} className="flex items-center space-x-2">
                          <Checkbox
                            id={`stress-${technique}`}
                            checked={formData.stressManagement.includes(technique)}
                            onCheckedChange={() => handleArrayToggle('stressManagement', technique)}
                          />
                          <Label htmlFor={`stress-${technique}`} className="text-sm">
                            {technique}
                          </Label>
                        </div>
                      ))}
                    </div>
                    {formData.stressManagement.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-4">
                        {formData.stressManagement.map(technique => (
                          <Badge key={technique} variant="outline" className="flex items-center gap-1">
                            {technique}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('stressManagement', technique)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="mentalHealthSupport">Mental Health Support</Label>
                    <Select value={formData.mentalHealthSupport} onValueChange={(value) => handleInputChange('mentalHealthSupport', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select mental health support" />
                      </SelectTrigger>
                      <SelectContent>
                        {mentalHealthOptions.map(option => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>

              {/* Work & Social Life */}
              <Card>
                <CardHeader>
                  <CardTitle>Work & Social Life</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="workSchedule">Work Schedule</Label>
                      <Select value={formData.workSchedule} onValueChange={(value) => handleInputChange('workSchedule', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select work schedule" />
                        </SelectTrigger>
                        <SelectContent>
                          {workScheduleOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="socialSupport">Social Support System</Label>
                      <Select value={formData.socialSupport} onValueChange={(value) => handleInputChange('socialSupport', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Rate your social support" />
                        </SelectTrigger>
                        <SelectContent>
                          {socialSupportOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label>Hobbies & Interests</Label>
                    <div className="flex gap-2 mt-2">
                      <Input
                        placeholder="Add hobby or interest..."
                        value={newHobby}
                        onChange={(e) => setNewHobby(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            addToArray('hobbies', newHobby);
                            setNewHobby('');
                          }
                        }}
                      />
                      <Button
                        type="button"
                        onClick={() => {
                          addToArray('hobbies', newHobby);
                          setNewHobby('');
                        }}
                      >
                        <Plus className="h-4 w-4" />
                      </Button>
                    </div>
                    {formData.hobbies.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {formData.hobbies.map(hobby => (
                          <Badge key={hobby} variant="outline" className="flex items-center gap-1">
                            {hobby}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('hobbies', hobby)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Daily Habits */}
              <Card>
                <CardHeader>
                  <CardTitle>Daily Habits & Environment</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label>Screen Time (hours/day): {formData.screenTime}</Label>
                      <Slider
                        value={[formData.screenTime]}
                        onValueChange={(value) => handleInputChange('screenTime', value[0])}
                        max={16}
                        min={0}
                        step={0.5}
                        className="mt-2"
                      />
                    </div>
                    <div>
                      <Label>Outdoor Time (hours/day): {formData.outdoorTime}</Label>
                      <Slider
                        value={[formData.outdoorTime]}
                        onValueChange={(value) => handleInputChange('outdoorTime', value[0])}
                        max={12}
                        min={0}
                        step={0.5}
                        className="mt-2"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="smokingStatus">Smoking Status</Label>
                      <Select value={formData.smokingStatus} onValueChange={(value) => handleInputChange('smokingStatus', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select smoking status" />
                        </SelectTrigger>
                        <SelectContent>
                          {smokingStatusOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    {(formData.smokingStatus === 'current' || formData.smokingStatus === 'occasional') && (
                      <div>
                        <Label htmlFor="smokingFrequency">Smoking Frequency</Label>
                        <Select value={formData.smokingFrequency} onValueChange={(value) => handleInputChange('smokingFrequency', value)}>
                          <SelectTrigger>
                            <SelectValue placeholder="How often do you smoke?" />
                          </SelectTrigger>
                          <SelectContent>
                            {smokingFrequencyOptions.map(option => (
                              <SelectItem key={option.value} value={option.value}>
                                {option.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="travelFrequency">Travel Frequency</Label>
                      <Select value={formData.travelFrequency} onValueChange={(value) => handleInputChange('travelFrequency', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="How often do you travel?" />
                        </SelectTrigger>
                        <SelectContent>
                          {travelFrequencyOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="livingEnvironment">Living Environment</Label>
                      <Select value={formData.livingEnvironment} onValueChange={(value) => handleInputChange('livingEnvironment', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select living environment" />
                        </SelectTrigger>
                        <SelectContent>
                          {livingEnvironmentOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="petOwnership">Pet Ownership</Label>
                    <Select value={formData.petOwnership} onValueChange={(value) => handleInputChange('petOwnership', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Do you have pets?" />
                      </SelectTrigger>
                      <SelectContent>
                        {petOwnershipOptions.map(option => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Relaxation Activities</Label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                      {relaxationOptions.map(activity => (
                        <div key={activity} className="flex items-center space-x-2">
                          <Checkbox
                            id={`relaxation-${activity}`}
                            checked={formData.relaxationActivities.includes(activity)}
                            onCheckedChange={() => handleArrayToggle('relaxationActivities', activity)}
                          />
                          <Label htmlFor={`relaxation-${activity}`} className="text-sm">
                            {activity}
                          </Label>
                        </div>
                      ))}
                    </div>
                    {formData.relaxationActivities.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-4">
                        {formData.relaxationActivities.map(activity => (
                          <Badge key={activity} variant="outline" className="flex items-center gap-1">
                            {activity}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('relaxationActivities', activity)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
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
                      placeholder="Any additional lifestyle information, routines, or factors that might affect your IBS..."
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