'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { 
  User, 
  Calendar, 
  Activity, 
  Heart, 
  AlertCircle, 
  CheckCircle, 
  ArrowRight, 
  ArrowLeft,
  Stethoscope,
  Target,
  Brain,
  Sparkles
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { toast } from 'react-hot-toast';

interface OnboardingData {
  // Basic Information
  age: number;
  gender: 'male' | 'female' | 'other' | 'prefer_not_to_say';
  height: number; // cm
  weight: number; // kg
  
  // IBS-Specific Information
  diagnosisYear: number;
  ibsType: 'ibs-d' | 'ibs-c' | 'ibs-m' | 'ibs-u' | 'not_diagnosed';
  severityLevel: 'mild' | 'moderate' | 'severe';
  
  // Triggers and Patterns
  knownTriggers: string[];
  commonSymptoms: string[];
  symptomPatterns: string[];
  
  // Lifestyle Factors
  stressLevel: number; // 1-10
  sleepQuality: number; // 1-10
  exerciseFrequency: 'none' | 'light' | 'moderate' | 'intense';
  dietaryRestrictions: string[];
  
  // Medical History
  medications: string[];
  allergies: string[];
  otherConditions: string[];
  
  // Goals and Preferences
  primaryGoals: string[];
  preferredTreatments: string[];
  communicationPreferences: string[];
}

const initialData: OnboardingData = {
  age: 25,
  gender: 'prefer_not_to_say',
  height: 170,
  weight: 70,
  diagnosisYear: new Date().getFullYear(),
  ibsType: 'not_diagnosed',
  severityLevel: 'mild',
  knownTriggers: [],
  commonSymptoms: [],
  symptomPatterns: [],
  stressLevel: 5,
  sleepQuality: 5,
  exerciseFrequency: 'moderate',
  dietaryRestrictions: [],
  medications: [],
  allergies: [],
  otherConditions: [],
  primaryGoals: [],
  preferredTreatments: [],
  communicationPreferences: []
};

const steps = [
  { id: 'basic', title: 'Basic Information', icon: User, description: 'Tell us about yourself' },
  { id: 'ibs', title: 'IBS Details', icon: Activity, description: 'Your IBS journey' },
  { id: 'symptoms', title: 'Symptoms & Triggers', icon: AlertCircle, description: 'What affects you most' },
  { id: 'lifestyle', title: 'Lifestyle', icon: Heart, description: 'Your daily habits' },
  { id: 'medical', title: 'Medical History', icon: Stethoscope, description: 'Health background' },
  { id: 'goals', title: 'Goals & Preferences', icon: Target, description: 'What you want to achieve' },
  { id: 'insights', title: 'Your Insights', icon: Brain, description: 'Personalized recommendations' }
];

// Options for various fields
const triggerOptions = [
  'Dairy products', 'Gluten', 'High-fat foods', 'Spicy foods', 'Caffeine',
  'Alcohol', 'Artificial sweeteners', 'Beans/legumes', 'Cruciferous vegetables',
  'Stress', 'Lack of sleep', 'Hormonal changes', 'Travel', 'Certain medications'
];

const symptomOptions = [
  'Abdominal pain', 'Bloating', 'Gas', 'Diarrhea', 'Constipation',
  'Urgency', 'Incomplete evacuation', 'Nausea', 'Fatigue', 'Headaches',
  'Back pain', 'Anxiety', 'Depression'
];

const patternOptions = [
  'Morning symptoms', 'Evening symptoms', 'Symptoms after meals',
  'Symptoms during stress', 'Weekend patterns', 'Seasonal patterns',
  'Menstrual cycle related', 'Travel-related'
];

const dietaryOptions = [
  'Low FODMAP', 'Gluten-free', 'Dairy-free', 'Vegetarian', 'Vegan',
  'Low-fat', 'High-fiber', 'Mediterranean', 'Paleo', 'Keto'
];

const goalOptions = [
  'Reduce symptom frequency', 'Improve quality of life', 'Better sleep',
  'Stress management', 'Weight management', 'Increase energy',
  'Improve digestion', 'Reduce medication dependence'
];

const treatmentOptions = [
  'Dietary modifications', 'Probiotics', 'Stress management', 'Exercise',
  'Meditation/mindfulness', 'Cognitive behavioral therapy', 'Medications',
  'Alternative therapies'
];

export default function OnboardingQuestionnaire() {
  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState<OnboardingData>(initialData);
  const [isLoading, setIsLoading] = useState(false);
  const [predictions, setPredictions] = useState<any>(null);
  const { user, updateProfile } = useAuth();
  const router = useRouter();

  const updateData = (updates: Partial<OnboardingData>) => {
    setData(prev => ({ ...prev, ...updates }));
  };

  const toggleArrayItem = (array: string[], item: string) => {
    return array.includes(item) 
      ? array.filter(i => i !== item)
      : [...array, item];
  };

  const handleNext = async () => {
    if (currentStep === steps.length - 2) {
      // Generate predictions before showing insights
      await generatePredictions();
    }
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const generatePredictions = async () => {
    setIsLoading(true);
    try {
      // Call backend ML prediction endpoint
      const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8001'}/api/v1/onboarding/predictions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        const predictions = await response.json();
        setPredictions(predictions);
      } else {
        // Fallback to mock predictions
        setPredictions(generateMockPredictions());
      }
    } catch (error) {
      console.error('Prediction error:', error);
      setPredictions(generateMockPredictions());
    } finally {
      setIsLoading(false);
    }
  };

  const generateMockPredictions = () => {
    return {
      riskLevel: data.severityLevel === 'severe' ? 'high' : data.severityLevel === 'moderate' ? 'medium' : 'low',
      recommendedDiet: data.knownTriggers.includes('Gluten') ? 'Gluten-free Low FODMAP' : 'Low FODMAP',
      triggerProbability: {
        stress: data.stressLevel > 7 ? 0.85 : 0.45,
        diet: data.knownTriggers.length > 3 ? 0.90 : 0.60,
        sleep: data.sleepQuality < 5 ? 0.75 : 0.30
      },
      personalizedTips: [
        'Consider keeping a detailed food diary',
        'Practice stress-reduction techniques daily',
        'Maintain regular meal times',
        'Stay hydrated throughout the day'
      ],
      nextSteps: [
        'Start with a 2-week elimination diet',
        'Schedule regular symptom tracking',
        'Consider consulting with a gastroenterologist'
      ]
    };
  };

  const handleComplete = async () => {
    setIsLoading(true);
    try {
      // Save onboarding data to backend
      const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8001'}/api/v1/users/onboarding`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          ...data,
          predictions,
          completedAt: new Date().toISOString()
        })
      });

      if (response.ok) {
        // Update user profile with basic info
        await updateProfile({
          height_cm: data.height,
          weight_kg: data.weight,
          gender: data.gender,
          ibs_type: data.ibsType
        });

        toast.success('Welcome! Your profile has been set up successfully.');
        router.push('/dashboard');
      } else {
        throw new Error('Failed to save onboarding data');
      }
    } catch (error) {
      console.error('Onboarding completion error:', error);
      toast.error('There was an issue saving your information. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderProgressBar = () => (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center">
            <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
              index <= currentStep 
                ? 'bg-blue-600 border-blue-600 text-white' 
                : 'border-gray-300 text-gray-400'
            }`}>
              {index < currentStep ? (
                <CheckCircle className="w-5 h-5" />
              ) : (
                <step.icon className="w-5 h-5" />
              )}
            </div>
            {index < steps.length - 1 && (
              <div className={`w-12 h-0.5 mx-2 ${
                index < currentStep ? 'bg-blue-600' : 'bg-gray-300'
              }`} />
            )}
          </div>
        ))}
      </div>
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">{steps[currentStep]?.title}</h2>
        <p className="text-gray-600 mt-1">{steps[currentStep]?.description}</p>
      </div>
    </div>
  );

  const renderBasicInfo = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <Label htmlFor="age">Age</Label>
          <Input
            id="age"
            type="number"
            value={data.age}
            onChange={(e) => updateData({ age: parseInt(e.target.value) || 0 })}
            min="18"
            max="100"
          />
        </div>
        <div>
          <Label htmlFor="gender">Gender</Label>
          <select
            id="gender"
            value={data.gender}
            onChange={(e) => updateData({ gender: e.target.value as any })}
            className="w-full p-2 border border-gray-300 rounded-md"
          >
            <option value="prefer_not_to_say">Prefer not to say</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div>
          <Label htmlFor="height">Height (cm)</Label>
          <Input
            id="height"
            type="number"
            value={data.height}
            onChange={(e) => updateData({ height: parseInt(e.target.value) || 0 })}
            min="100"
            max="250"
          />
        </div>
        <div>
          <Label htmlFor="weight">Weight (kg)</Label>
          <Input
            id="weight"
            type="number"
            value={data.weight}
            onChange={(e) => updateData({ weight: parseInt(e.target.value) || 0 })}
            min="30"
            max="300"
          />
        </div>
      </div>
    </div>
  );

  const renderIBSDetails = () => (
    <div className="space-y-6">
      <div>
        <Label>When were you first diagnosed with IBS?</Label>
        <Input
          type="number"
          value={data.diagnosisYear}
          onChange={(e) => updateData({ diagnosisYear: parseInt(e.target.value) || new Date().getFullYear() })}
          min="1950"
          max={new Date().getFullYear()}
          placeholder="Year of diagnosis"
        />
      </div>
      
      <div>
        <Label>What type of IBS do you have?</Label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
          {[
            { value: 'ibs-d', label: 'IBS-D (Diarrhea predominant)' },
            { value: 'ibs-c', label: 'IBS-C (Constipation predominant)' },
            { value: 'ibs-m', label: 'IBS-M (Mixed)' },
            { value: 'ibs-u', label: 'IBS-U (Unsubtyped)' },
            { value: 'not_diagnosed', label: 'Not formally diagnosed' }
          ].map((option) => (
            <button
              key={option.value}
              onClick={() => updateData({ ibsType: option.value as any })}
              className={`p-3 text-left rounded-lg border ${
                data.ibsType === option.value
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label>How would you rate your symptom severity?</Label>
        <div className="flex gap-3 mt-2">
          {[
            { value: 'mild', label: 'Mild', color: 'green' },
            { value: 'moderate', label: 'Moderate', color: 'yellow' },
            { value: 'severe', label: 'Severe', color: 'red' }
          ].map((option) => (
            <button
              key={option.value}
              onClick={() => updateData({ severityLevel: option.value as any })}
              className={`flex-1 p-3 rounded-lg border ${
                data.severityLevel === option.value
                  ? `border-${option.color}-500 bg-${option.color}-50 text-${option.color}-700`
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  const renderSymptomsAndTriggers = () => (
    <div className="space-y-6">
      <div>
        <Label className="text-lg font-medium">Known Triggers</Label>
        <p className="text-sm text-gray-600 mb-3">Select all that apply to you</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {triggerOptions.map((trigger) => (
            <button
              key={trigger}
              onClick={() => updateData({
                knownTriggers: toggleArrayItem(data.knownTriggers, trigger)
              })}
              className={`p-2 text-sm rounded-md text-left transition-colors ${
                data.knownTriggers.includes(trigger)
                  ? 'bg-red-100 text-red-800 border border-red-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {trigger}
            </button>
          ))}
        </div>
      </div>
      
      <div>
        <Label className="text-lg font-medium">Common Symptoms</Label>
        <p className="text-sm text-gray-600 mb-3">What symptoms do you experience most often?</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {symptomOptions.map((symptom) => (
            <button
              key={symptom}
              onClick={() => updateData({
                commonSymptoms: toggleArrayItem(data.commonSymptoms, symptom)
              })}
              className={`p-2 text-sm rounded-md text-left transition-colors ${
                data.commonSymptoms.includes(symptom)
                  ? 'bg-orange-100 text-orange-800 border border-orange-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {symptom}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-lg font-medium">Symptom Patterns</Label>
        <p className="text-sm text-gray-600 mb-3">When do your symptoms typically occur?</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {patternOptions.map((pattern) => (
            <button
              key={pattern}
              onClick={() => updateData({
                symptomPatterns: toggleArrayItem(data.symptomPatterns, pattern)
              })}
              className={`p-2 text-sm rounded-md text-left transition-colors ${
                data.symptomPatterns.includes(pattern)
                  ? 'bg-purple-100 text-purple-800 border border-purple-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {pattern}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  const renderLifestyle = () => (
    <div className="space-y-6">
      <div>
        <Label>Stress Level (1-10)</Label>
        <div className="flex items-center space-x-4 mt-2">
          <span className="text-sm text-gray-500">Low</span>
          <input
            type="range"
            min="1"
            max="10"
            value={data.stressLevel}
            onChange={(e) => updateData({ stressLevel: parseInt(e.target.value) })}
            className="flex-1"
          />
          <span className="text-sm text-gray-500">High</span>
          <Badge variant="outline" className="ml-2">{data.stressLevel}</Badge>
        </div>
      </div>

      <div>
        <Label>Sleep Quality (1-10)</Label>
        <div className="flex items-center space-x-4 mt-2">
          <span className="text-sm text-gray-500">Poor</span>
          <input
            type="range"
            min="1"
            max="10"
            value={data.sleepQuality}
            onChange={(e) => updateData({ sleepQuality: parseInt(e.target.value) })}
            className="flex-1"
          />
          <span className="text-sm text-gray-500">Excellent</span>
          <Badge variant="outline" className="ml-2">{data.sleepQuality}</Badge>
        </div>
      </div>

      <div>
        <Label>Exercise Frequency</Label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-2">
          {[
            { value: 'none', label: 'None' },
            { value: 'light', label: 'Light' },
            { value: 'moderate', label: 'Moderate' },
            { value: 'intense', label: 'Intense' }
          ].map((option) => (
            <button
              key={option.value}
              onClick={() => updateData({ exerciseFrequency: option.value as any })}
              className={`p-3 rounded-lg border ${
                data.exerciseFrequency === option.value
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label>Dietary Restrictions/Preferences</Label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
          {dietaryOptions.map((diet) => (
            <button
              key={diet}
              onClick={() => updateData({
                dietaryRestrictions: toggleArrayItem(data.dietaryRestrictions, diet)
              })}
              className={`p-2 text-sm rounded-md text-left transition-colors ${
                data.dietaryRestrictions.includes(diet)
                  ? 'bg-green-100 text-green-800 border border-green-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {diet}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  const renderMedicalHistory = () => (
    <div className="space-y-6">
      <div>
        <Label htmlFor="medications">Current Medications</Label>
        <textarea
          id="medications"
          value={data.medications.join(', ')}
          onChange={(e) => updateData({ medications: e.target.value.split(', ').filter(m => m.trim()) })}
          placeholder="List your current medications (comma-separated)"
          className="w-full p-3 border border-gray-300 rounded-md h-24 resize-none"
        />
      </div>

      <div>
        <Label htmlFor="allergies">Allergies</Label>
        <textarea
          id="allergies"
          value={data.allergies.join(', ')}
          onChange={(e) => updateData({ allergies: e.target.value.split(', ').filter(a => a.trim()) })}
          placeholder="List any allergies (comma-separated)"
          className="w-full p-3 border border-gray-300 rounded-md h-24 resize-none"
        />
      </div>

      <div>
        <Label htmlFor="conditions">Other Medical Conditions</Label>
        <textarea
          id="conditions"
          value={data.otherConditions.join(', ')}
          onChange={(e) => updateData({ otherConditions: e.target.value.split(', ').filter(c => c.trim()) })}
          placeholder="List any other medical conditions (comma-separated)"
          className="w-full p-3 border border-gray-300 rounded-md h-24 resize-none"
        />
      </div>
    </div>
  );

  const renderGoalsAndPreferences = () => (
    <div className="space-y-6">
      <div>
        <Label>Primary Goals</Label>
        <p className="text-sm text-gray-600 mb-3">What do you hope to achieve?</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {goalOptions.map((goal) => (
            <button
              key={goal}
              onClick={() => updateData({
                primaryGoals: toggleArrayItem(data.primaryGoals, goal)
              })}
              className={`p-3 text-sm rounded-md text-left transition-colors ${
                data.primaryGoals.includes(goal)
                  ? 'bg-blue-100 text-blue-800 border border-blue-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {goal}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label>Preferred Treatments</Label>
        <p className="text-sm text-gray-600 mb-3">What approaches interest you most?</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {treatmentOptions.map((treatment) => (
            <button
              key={treatment}
              onClick={() => updateData({
                preferredTreatments: toggleArrayItem(data.preferredTreatments, treatment)
              })}
              className={`p-3 text-sm rounded-md text-left transition-colors ${
                data.preferredTreatments.includes(treatment)
                  ? 'bg-teal-100 text-teal-800 border border-teal-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {treatment}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  const renderInsights = () => {
    if (isLoading) {
      return (
        <div className="text-center py-12">
          <Sparkles className="w-12 h-12 text-blue-600 mx-auto mb-4 animate-spin" />
          <h3 className="text-xl font-semibold mb-2">Analyzing Your Profile...</h3>
          <p className="text-gray-600">We're generating personalized insights based on your responses.</p>
        </div>
      );
    }

    if (!predictions) {
      return (
        <div className="text-center py-12">
          <Brain className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2 text-gray-600">No insights available</h3>
          <p className="text-gray-500">Unable to generate personalized insights at this time.</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        <div className="text-center mb-8">
          <Sparkles className="w-12 h-12 text-blue-600 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Your Personalized Insights</h3>
          <p className="text-gray-600">Based on your responses, here's what we've learned about your IBS journey.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <AlertCircle className="w-5 h-5 mr-2" />
                Risk Assessment
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                predictions?.riskLevel === 'high' ? 'bg-red-100 text-red-800' :
                predictions?.riskLevel === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-green-100 text-green-800'
              }`}>
                {predictions?.riskLevel ? predictions.riskLevel.charAt(0).toUpperCase() + predictions.riskLevel.slice(1) : 'Unknown'} Risk
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Based on your symptom severity and triggers
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Heart className="w-5 h-5 mr-2" />
                Recommended Diet
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Badge variant="outline" className="mb-2">{predictions?.recommendedDiet || 'Not available'}</Badge>
              <p className="text-sm text-gray-600">
                This diet plan aligns with your identified triggers and preferences
              </p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Trigger Probability Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {predictions?.triggerProbability && Object.entries(predictions.triggerProbability).map(([trigger, probability]) => (
                <div key={trigger} className="flex items-center justify-between">
                  <span className="capitalize">{trigger}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${(probability as number) * 100}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-600">{Math.round((probability as number) * 100)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Personalized Tips</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {predictions?.personalizedTips?.map((tip: string, index: number) => (
                <li key={index} className="flex items-start">
                  <CheckCircle className="w-4 h-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{tip}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Next Steps</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {predictions?.nextSteps?.map((step: string, index: number) => (
                <li key={index} className="flex items-start">
                  <ArrowRight className="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{step}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderCurrentStep = () => {
    switch (steps[currentStep]?.id) {
      case 'basic': return renderBasicInfo();
      case 'ibs': return renderIBSDetails();
      case 'symptoms': return renderSymptomsAndTriggers();
      case 'lifestyle': return renderLifestyle();
      case 'medical': return renderMedicalHistory();
      case 'goals': return renderGoalsAndPreferences();
      case 'insights': return renderInsights();
      default: return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <Card className="shadow-lg">
          <CardHeader className="pb-6">
            {renderProgressBar()}
          </CardHeader>
          <CardContent className="px-8 pb-8">
            {renderCurrentStep()}
            
            <div className="flex justify-between mt-8 pt-6 border-t">
              <Button
                variant="outline"
                onClick={handlePrevious}
                disabled={currentStep === 0}
                className="flex items-center"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Previous
              </Button>
              
              {currentStep === steps.length - 1 ? (
                <Button
                  onClick={handleComplete}
                  disabled={isLoading}
                  className="flex items-center"
                >
                  {isLoading ? 'Saving...' : 'Complete Setup'}
                  <CheckCircle className="w-4 h-4 ml-2" />
                </Button>
              ) : (
                <Button
                  onClick={handleNext}
                  disabled={isLoading}
                  className="flex items-center"
                >
                  {currentStep === steps.length - 2 ? 'Generate Insights' : 'Next'}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}