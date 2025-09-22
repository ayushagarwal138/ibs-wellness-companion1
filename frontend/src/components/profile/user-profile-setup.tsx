'use client';

import React, { useState } from 'react';
import { User, Calendar, Activity, Heart, AlertCircle, CheckCircle, ArrowRight, ArrowLeft } from 'lucide-react';
import { Badge } from '../ui/badge';
import { useUserSync } from '@/hooks/useUserSync';
import { toast } from 'react-hot-toast';
import { SyncStatusIndicator } from '../ui/sync-status-indicator';

interface UserProfileData {
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

const initialProfileData: UserProfileData = {
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
  { id: 'basic', title: 'Basic Information', icon: User },
  { id: 'ibs', title: 'IBS Details', icon: Activity },
  { id: 'lifestyle', title: 'Lifestyle', icon: Heart },
  { id: 'medical', title: 'Medical History', icon: AlertCircle },
  { id: 'goals', title: 'Goals & Preferences', icon: CheckCircle }
];

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

export default function UserProfileSetup() {
  const { syncProfile, syncStatus } = useUserSync();
  const [currentStep, setCurrentStep] = useState(0);
  const [profileData, setProfileData] = useState<UserProfileData>(initialProfileData);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const updateProfileData = (updates: Partial<UserProfileData>) => {
    setProfileData(prev => ({ ...prev, ...updates }));
    setHasUnsavedChanges(true);
  };

  const toggleArrayItem = (array: string[], item: string) => {
    return array.includes(item)
      ? array.filter(i => i !== item)
      : [...array, item];
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      // Transform profile data to match API format
      const transformedData = {
        first_name: '', // Would need to be collected in basic info
        last_name: '',  // Would need to be collected in basic info
        email: '',      // Would need to be collected in basic info
        height_cm: profileData.height,
        weight_kg: profileData.weight,
        gender: profileData.gender,
        ibs_type: profileData.ibsType,
        diagnosis_date: `${profileData.diagnosisYear}-01-01`,
        // Additional profile data would be stored in separate endpoints
      };

      // Use sync profile for real-time updates
      const result = await syncProfile(transformedData, {
        optimistic: true,
        triggerML: true,
        showToast: false // We'll handle toasts manually
      });

      if (result.success) {
        toast.success('Profile setup completed successfully!');
        setHasUnsavedChanges(false);
        
        // Handle ML predictions if available
        if (result.ml_predictions) {
          toast.success('AI insights: Profile analysis complete with personalized recommendations');
        }
      } else {
        throw new Error(result.error || 'Failed to save profile');
      }
    } catch (error) {
      console.error('Error submitting profile:', error);
      toast.error('Error submitting profile. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderBasicInfo = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Age
          </label>
          <input
            type="number"
            min="18"
            max="120"
            value={profileData.age}
            onChange={(e) => updateProfileData({ age: parseInt(e.target.value) || 25 })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Gender
          </label>
          <select
            value={profileData.gender}
            onChange={(e) => updateProfileData({ gender: e.target.value as any })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="prefer_not_to_say">Prefer not to say</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Height (cm)
          </label>
          <input
            type="number"
            min="100"
            max="250"
            value={profileData.height}
            onChange={(e) => updateProfileData({ height: parseInt(e.target.value) || 170 })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Weight (kg)
          </label>
          <input
            type="number"
            min="30"
            max="300"
            value={profileData.weight}
            onChange={(e) => updateProfileData({ weight: parseInt(e.target.value) || 70 })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
      
      <div className="p-4 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>BMI:</strong> {((profileData.weight / (profileData.height / 100)) ** 2).toFixed(1)}
        </p>
      </div>
    </div>
  );

  const renderIBSDetails = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Year of IBS Diagnosis
          </label>
          <input
            type="number"
            min="1950"
            max={new Date().getFullYear()}
            value={profileData.diagnosisYear}
            onChange={(e) => updateProfileData({ diagnosisYear: parseInt(e.target.value) || new Date().getFullYear() })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            IBS Type
          </label>
          <select
            value={profileData.ibsType}
            onChange={(e) => updateProfileData({ ibsType: e.target.value as any })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="not_diagnosed">Not formally diagnosed</option>
            <option value="ibs-d">IBS-D (Diarrhea predominant)</option>
            <option value="ibs-c">IBS-C (Constipation predominant)</option>
            <option value="ibs-m">IBS-M (Mixed)</option>
            <option value="ibs-u">IBS-U (Unsubtyped)</option>
          </select>
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Current Severity Level
        </label>
        <div className="flex space-x-4">
          {['mild', 'moderate', 'severe'].map((level) => (
            <button
              key={level}
              onClick={() => updateProfileData({ severityLevel: level as any })}
              className={`px-4 py-2 rounded-md capitalize ${
                profileData.severityLevel === level
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {level}
            </button>
          ))}
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Known Triggers
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {triggerOptions.map((trigger) => (
            <button
              key={trigger}
              onClick={() => updateProfileData({
                knownTriggers: toggleArrayItem(profileData.knownTriggers, trigger)
              })}
              className={`p-2 text-sm rounded-md text-left ${
                profileData.knownTriggers.includes(trigger)
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
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Common Symptoms
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {symptomOptions.map((symptom) => (
            <button
              key={symptom}
              onClick={() => updateProfileData({
                commonSymptoms: toggleArrayItem(profileData.commonSymptoms, symptom)
              })}
              className={`p-2 text-sm rounded-md text-left ${
                profileData.commonSymptoms.includes(symptom)
                  ? 'bg-orange-100 text-orange-800 border border-orange-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {symptom}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  const renderLifestyle = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Stress Level (1-10)
        </label>
        <input
          type="range"
          min="1"
          max="10"
          value={profileData.stressLevel}
          onChange={(e) => updateProfileData({ stressLevel: parseInt(e.target.value) })}
          className="w-full"
        />
        <div className="flex justify-between text-sm text-gray-500 mt-1">
          <span>Low (1)</span>
          <span className="font-medium">Current: {profileData.stressLevel}</span>
          <span>High (10)</span>
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Sleep Quality (1-10)
        </label>
        <input
          type="range"
          min="1"
          max="10"
          value={profileData.sleepQuality}
          onChange={(e) => updateProfileData({ sleepQuality: parseInt(e.target.value) })}
          className="w-full"
        />
        <div className="flex justify-between text-sm text-gray-500 mt-1">
          <span>Poor (1)</span>
          <span className="font-medium">Current: {profileData.sleepQuality}</span>
          <span>Excellent (10)</span>
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Exercise Frequency
        </label>
        <div className="flex space-x-4">
          {['none', 'light', 'moderate', 'intense'].map((level) => (
            <button
              key={level}
              onClick={() => updateProfileData({ exerciseFrequency: level as any })}
              className={`px-4 py-2 rounded-md capitalize ${
                profileData.exerciseFrequency === level
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {level}
            </button>
          ))}
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Dietary Restrictions/Preferences
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {dietaryOptions.map((diet) => (
            <button
              key={diet}
              onClick={() => updateProfileData({
                dietaryRestrictions: toggleArrayItem(profileData.dietaryRestrictions, diet)
              })}
              className={`p-2 text-sm rounded-md text-left ${
                profileData.dietaryRestrictions.includes(diet)
                  ? 'bg-green-100 text-green-800 border border-green-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {diet}
            </button>
          ))}
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Symptom Patterns
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {patternOptions.map((pattern) => (
            <button
              key={pattern}
              onClick={() => updateProfileData({
                symptomPatterns: toggleArrayItem(profileData.symptomPatterns, pattern)
              })}
              className={`p-2 text-sm rounded-md text-left ${
                profileData.symptomPatterns.includes(pattern)
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

  const renderMedicalHistory = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Current Medications
        </label>
        <textarea
          value={profileData.medications ? profileData.medications.join('\n') : ''}
          onChange={(e) => updateProfileData({ 
            medications: e.target.value.split('\n').filter(m => m.trim()) 
          })}
          placeholder="Enter each medication on a new line"
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Allergies
        </label>
        <textarea
          value={profileData.allergies ? profileData.allergies.join('\n') : ''}
          onChange={(e) => updateProfileData({ 
            allergies: e.target.value.split('\n').filter(a => a.trim()) 
          })}
          placeholder="Enter each allergy on a new line"
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Other Medical Conditions
        </label>
        <textarea
          value={profileData.otherConditions ? profileData.otherConditions.join('\n') : ''}
          onChange={(e) => updateProfileData({ 
            otherConditions: e.target.value.split('\n').filter(c => c.trim()) 
          })}
          placeholder="Enter each condition on a new line"
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  );

  const renderGoalsAndPreferences = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Primary Goals
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {goalOptions.map((goal) => (
            <button
              key={goal}
              onClick={() => updateProfileData({
                primaryGoals: toggleArrayItem(profileData.primaryGoals, goal)
              })}
              className={`p-3 text-sm rounded-md text-left ${
                profileData.primaryGoals.includes(goal)
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
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Preferred Treatment Approaches
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {treatmentOptions.map((treatment) => (
            <button
              key={treatment}
              onClick={() => updateProfileData({
                preferredTreatments: toggleArrayItem(profileData.preferredTreatments, treatment)
              })}
              className={`p-3 text-sm rounded-md text-left ${
                profileData.preferredTreatments.includes(treatment)
                  ? 'bg-green-100 text-green-800 border border-green-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {treatment}
            </button>
          ))}
        </div>
      </div>
      
      <div className="p-4 bg-yellow-50 rounded-lg">
        <h4 className="font-medium text-yellow-800 mb-2">Profile Summary</h4>
        <div className="space-y-2 text-sm text-yellow-700">
          <p><strong>Age:</strong> {profileData.age} years old</p>
          <p><strong>IBS Type:</strong> {profileData.ibsType.toUpperCase()}</p>
          <p><strong>Severity:</strong> {profileData.severityLevel}</p>
          <p><strong>Known Triggers:</strong> {profileData.knownTriggers.length} identified</p>
          <p><strong>Primary Goals:</strong> {profileData.primaryGoals.length} selected</p>
        </div>
      </div>
    </div>
  );

  const renderStepContent = () => {
    switch (steps[currentStep]?.id) {
      case 'basic':
        return renderBasicInfo();
      case 'ibs':
        return renderIBSDetails();
      case 'lifestyle':
        return renderLifestyle();
      case 'medical':
        return renderMedicalHistory();
      case 'goals':
        return renderGoalsAndPreferences();
      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Complete Your IBS Profile
            </h1>
            <p className="text-gray-600">
              Help us personalize your experience by sharing information about your IBS journey.
            </p>
          </div>
          <div>
            <SyncStatusIndicator status={syncStatus} />
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isActive = index === currentStep;
            const isCompleted = index < currentStep;
            
            return (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
                  isCompleted 
                    ? 'bg-green-500 text-white' 
                    : isActive 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-200 text-gray-500'
                }`}>
                  {isCompleted ? (
                    <CheckCircle size={20} />
                  ) : (
                    <Icon size={20} />
                  )}
                </div>
                <div className="ml-3">
                  <p className={`text-sm font-medium ${
                    isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                  }`}>
                    {step.title}
                  </p>
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-16 h-0.5 mx-4 ${
                    isCompleted ? 'bg-green-500' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          {steps[currentStep]?.title}
        </h2>
        {renderStepContent()}
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={handlePrevious}
          disabled={currentStep === 0}
          className={`flex items-center px-4 py-2 rounded-md ${
            currentStep === 0
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-gray-500 text-white hover:bg-gray-600'
          }`}
        >
          <ArrowLeft size={16} className="mr-2" />
          Previous
        </button>
        
        {currentStep === steps.length - 1 ? (
          <button
            onClick={handleSubmit}
            disabled={isSubmitting || syncStatus.syncing}
            className={`flex items-center px-6 py-2 rounded-md ${
              isSubmitting || syncStatus.syncing
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-500 hover:bg-green-600'
            } text-white`}
          >
            {syncStatus.syncing ? 'Syncing...' : isSubmitting ? 'Submitting...' : 'Complete Setup'}
            {!isSubmitting && !syncStatus.syncing && <CheckCircle size={16} className="ml-2" />}
          </button>
        ) : (
          <button
            onClick={handleNext}
            className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            Next
            <ArrowRight size={16} className="ml-2" />
          </button>
        )}
      </div>
    </div>
  );
}