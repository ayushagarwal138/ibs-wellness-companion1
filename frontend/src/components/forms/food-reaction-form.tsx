'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Slider } from '@/components/ui/slider';
import { apiService } from '@/lib/api';
import { toast } from 'react-hot-toast';
import { SeverityLevel } from '@ibs-wellness/shared-types';
import { AlertTriangle, Clock, Plus, X, Activity, Thermometer } from 'lucide-react';

interface FoodReactionFormData {
  food_name: string;
  severity: 'mild' | 'moderate' | 'severe' | '';
  symptoms: string[];
  onset_time?: number;
  duration_minutes?: number;
  notes?: string;
  consumed_at?: string;
  reaction_type?: string;
  environmental_factors?: string[];
  stress_level?: number;
  sleep_quality?: number;
  medication_taken?: string[];
  previous_reactions?: boolean;
  confidence_level?: number;
}

const COMMON_SYMPTOMS = [
  'Abdominal pain', 'Bloating', 'Gas', 'Diarrhea', 'Constipation', 'Nausea', 
  'Vomiting', 'Heartburn', 'Cramping', 'Urgency', 'Incomplete evacuation',
  'Headache', 'Fatigue', 'Joint pain', 'Skin rash', 'Hives', 'Itching',
  'Difficulty breathing', 'Swelling', 'Dizziness', 'Brain fog'
];

const REACTION_TYPES = [
  'Food Intolerance', 'Food Allergy', 'IBS Trigger', 'FODMAP Reaction', 
  'Lactose Intolerance', 'Gluten Sensitivity', 'Unknown'
];

const ENVIRONMENTAL_FACTORS = [
  'High Stress', 'Poor Sleep', 'Menstrual Cycle', 'Travel', 'Weather Change',
  'Medication Change', 'Exercise', 'Dehydration', 'Alcohol Consumption'
];

const COMMON_MEDICATIONS = [
  'Antacids', 'Probiotics', 'Anti-diarrheal', 'Laxatives', 'Pain relievers',
  'Antihistamines', 'Digestive enzymes', 'Fiber supplements'
];

export default function FoodReactionForm() {
  const [formData, setFormData] = useState<FoodReactionFormData>({
    food_name: '',
    severity: '',
    symptoms: [],
    onset_time: undefined,
    duration_minutes: undefined,
    notes: '',
    consumed_at: new Date().toISOString().slice(0, 16),
    reaction_type: '',
    environmental_factors: [],
    stress_level: 5,
    sleep_quality: 5,
    medication_taken: [],
    previous_reactions: false,
    confidence_level: 8
  });

  const [symptomInput, setSymptomInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (field: keyof FoodReactionFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addSymptom = (symptom: string) => {
    if (symptom.trim() && !formData.symptoms.includes(symptom.trim())) {
      setFormData(prev => ({
        ...prev,
        symptoms: [...prev.symptoms, symptom.trim()]
      }));
    }
  };

  const addCustomSymptom = () => {
    if (symptomInput.trim()) {
      addSymptom(symptomInput);
      setSymptomInput('');
    }
  };

  const removeSymptom = (index: number) => {
    setFormData(prev => ({
      ...prev,
      symptoms: prev.symptoms.filter((_, i) => i !== index)
    }));
  };

  const toggleEnvironmentalFactor = (factor: string) => {
    setFormData(prev => ({
      ...prev,
      environmental_factors: prev.environmental_factors?.includes(factor)
        ? prev.environmental_factors.filter(f => f !== factor)
        : [...(prev.environmental_factors || []), factor]
    }));
  };

  const toggleMedication = (medication: string) => {
    setFormData(prev => ({
      ...prev,
      medication_taken: prev.medication_taken?.includes(medication)
        ? prev.medication_taken.filter(m => m !== medication)
        : [...(prev.medication_taken || []), medication]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.food_name.trim()) {
      toast.error('Please enter the food name');
      return;
    }

    if (!formData.severity) {
      toast.error('Please select reaction severity');
      return;
    }

    if (formData.symptoms.length === 0) {
      toast.error('Please add at least one symptom');
      return;
    }

    setIsLoading(true);

    try {
      const submitData = {
        food_name: formData.food_name.trim(),
        severity: formData.severity as SeverityLevel,
        symptoms: formData.symptoms,
        onset_time: formData.onset_time,
        duration_minutes: formData.duration_minutes,
        notes: formData.notes,
        consumed_at: formData.consumed_at ? new Date(formData.consumed_at).toISOString() : undefined,
      };

      await apiService.createFoodReaction(submitData);
      toast.success('Food reaction logged successfully!');
      
      // Reset form
      setFormData({
        food_name: '',
        severity: '',
        symptoms: [],
        onset_time: undefined,
        duration_minutes: undefined,
        notes: '',
        consumed_at: new Date().toISOString().slice(0, 16),
        reaction_type: '',
        environmental_factors: [],
        stress_level: 5,
        sleep_quality: 5,
        medication_taken: [],
        previous_reactions: false,
        confidence_level: 8
      });
      setSymptomInput('');
    } catch (error) {
      console.error('Error creating food reaction:', error);
      toast.error('Failed to log food reaction. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader className="bg-gradient-to-r from-red-50 to-orange-50">
        <CardTitle className="flex items-center gap-2 text-xl">
          <AlertTriangle className="h-6 w-6 text-red-600" />
          Log Food Reaction
        </CardTitle>
        <p className="text-sm text-gray-600">Track adverse reactions to help identify trigger foods and patterns</p>
      </CardHeader>
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Reaction Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Food Name */}
            <div className="space-y-2">
              <Label htmlFor="food_name" className="text-sm font-medium">Food Name *</Label>
              <Input
                id="food_name"
                value={formData.food_name}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('food_name', e.target.value)}
                placeholder="Enter the specific food that caused the reaction"
                required
                className="w-full"
              />
            </div>

            {/* Consumed At */}
            <div className="space-y-2">
              <Label htmlFor="consumed_at" className="text-sm font-medium flex items-center gap-1">
                <Clock className="h-4 w-4" />
                When did you eat this food?
              </Label>
              <Input
                id="consumed_at"
                type="datetime-local"
                value={formData.consumed_at}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('consumed_at', e.target.value)}
                className="w-full"
              />
            </div>
          </div>

          {/* Severity and Reaction Type */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Severity */}
            <div className="space-y-2">
              <Label htmlFor="severity" className="text-sm font-medium">Reaction Severity *</Label>
              <Select
                value={formData.severity}
                onValueChange={(value: string) => handleInputChange('severity', value as 'mild' | 'moderate' | 'severe')}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select severity level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="mild">🟢 Mild - Minor discomfort</SelectItem>
                  <SelectItem value="moderate">🟡 Moderate - Noticeable symptoms</SelectItem>
                  <SelectItem value="severe">🔴 Severe - Significant distress</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Reaction Type */}
            <div className="space-y-2">
              <Label htmlFor="reaction_type" className="text-sm font-medium">Suspected Reaction Type</Label>
              <Select
                value={formData.reaction_type}
                onValueChange={(value: string) => handleInputChange('reaction_type', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="What type of reaction?" />
                </SelectTrigger>
                <SelectContent>
                  {REACTION_TYPES.map((type) => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Timing Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Onset Time */}
            <div className="space-y-2">
              <Label htmlFor="onset_time" className="text-sm font-medium">Reaction Onset Time</Label>
              <div className="flex items-center gap-2">
                <Input
                  id="onset_time"
                  type="number"
                  min="0"
                  max="1440"
                  value={formData.onset_time || ''}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('onset_time', e.target.value ? parseInt(e.target.value) : undefined)}
                  placeholder="Minutes after eating"
                  className="flex-1"
                />
                <span className="text-sm text-gray-500">minutes</span>
              </div>
            </div>

            {/* Duration */}
            <div className="space-y-2">
              <Label htmlFor="duration_minutes" className="text-sm font-medium">Duration</Label>
              <div className="flex items-center gap-2">
                <Input
                  id="duration_minutes"
                  type="number"
                  min="0"
                  max="10080"
                  value={formData.duration_minutes || ''}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('duration_minutes', e.target.value ? parseInt(e.target.value) : undefined)}
                  placeholder="How long did it last?"
                  className="flex-1"
                />
                <span className="text-sm text-gray-500">minutes</span>
              </div>
            </div>
          </div>

          {/* Symptoms */}
          <div className="space-y-4">
            <Label htmlFor="symptoms" className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Symptoms Experienced *
            </Label>
            
            {/* Common Symptoms Grid */}
            <div className="space-y-3">
              <p className="text-sm text-gray-600">Select symptoms you experienced:</p>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                {COMMON_SYMPTOMS.map((symptom) => (
                  <button
                    key={symptom}
                    type="button"
                    onClick={() => addSymptom(symptom)}
                    disabled={formData.symptoms.includes(symptom)}
                    className={`px-3 py-2 rounded-lg text-sm border transition-all text-left ${
                      formData.symptoms.includes(symptom)
                        ? 'bg-red-100 text-red-800 border-red-300 cursor-not-allowed'
                        : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 hover:border-gray-300'
                    }`}
                  >
                    {symptom}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Symptom Input */}
            <div className="flex gap-2">
              <Input
                value={symptomInput}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSymptomInput(e.target.value)}
                placeholder="Add custom symptom"
                onKeyPress={(e: React.KeyboardEvent) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addCustomSymptom();
                  }
                }}
                className="flex-1"
              />
              <Button type="button" onClick={addCustomSymptom} variant="outline" size="sm">
                <Plus className="h-4 w-4" />
              </Button>
            </div>

            {/* Selected Symptoms */}
            {formData.symptoms.length > 0 && (
              <div className="space-y-3">
                <p className="text-sm font-medium text-gray-700">Selected symptoms:</p>
                <div className="flex flex-wrap gap-2 p-4 bg-red-50 rounded-lg">
                  {formData.symptoms.map((symptom, index) => (
                    <div
                      key={index}
                      className="bg-white border border-red-200 px-3 py-2 rounded-full text-sm flex items-center gap-2 shadow-sm"
                    >
                      {symptom}
                      <button
                        type="button"
                        onClick={() => removeSymptom(index)}
                        className="text-red-500 hover:text-red-700 ml-1"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Environmental Factors */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Thermometer className="h-4 w-4 text-blue-500" />
              <Label className="text-sm font-medium">Environmental Factors</Label>
            </div>
            <p className="text-sm text-gray-600">What else was happening when you had this reaction?</p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {ENVIRONMENTAL_FACTORS.map((factor) => (
                <div key={factor} className="flex items-center space-x-2">
                  <Checkbox
                    id={factor}
                    checked={formData.environmental_factors?.includes(factor) || false}
                    onCheckedChange={() => toggleEnvironmentalFactor(factor)}
                  />
                  <Label htmlFor={factor} className="text-xs cursor-pointer">
                    {factor}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Context Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Stress Level */}
            <div className="space-y-3">
              <Label htmlFor="stress_level" className="text-sm font-medium">Stress Level at Time of Reaction</Label>
              <div className="px-3 py-4 bg-orange-50 rounded-lg">
                <Slider
                  value={[formData.stress_level || 5]}
                  onValueChange={(value: number[]) => handleInputChange('stress_level', value[0])}
                  max={10}
                  min={1}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-2">
                  <span>😌 Very Calm</span>
                  <span>😐 Moderate</span>
                  <span>😰 Very Stressed</span>
                </div>
                <div className="text-center mt-2 font-medium text-orange-700">
                  Level: {formData.stress_level}/10
                </div>
              </div>
            </div>

            {/* Sleep Quality */}
            <div className="space-y-3">
              <Label htmlFor="sleep_quality" className="text-sm font-medium">Sleep Quality (Previous Night)</Label>
              <div className="px-3 py-4 bg-purple-50 rounded-lg">
                <Slider
                  value={[formData.sleep_quality || 5]}
                  onValueChange={(value: number[]) => handleInputChange('sleep_quality', value[0])}
                  max={10}
                  min={1}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-2">
                  <span>😴 Very Poor</span>
                  <span>😐 Average</span>
                  <span>😊 Excellent</span>
                </div>
                <div className="text-center mt-2 font-medium text-purple-700">
                  Quality: {formData.sleep_quality}/10
                </div>
              </div>
            </div>
          </div>

          {/* Medications Taken */}
          <div className="space-y-4">
            <Label className="text-sm font-medium">Medications/Supplements Taken for Reaction</Label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {COMMON_MEDICATIONS.map((medication) => (
                <div key={medication} className="flex items-center space-x-2">
                  <Checkbox
                    id={medication}
                    checked={formData.medication_taken?.includes(medication) || false}
                    onCheckedChange={() => toggleMedication(medication)}
                  />
                  <Label htmlFor={medication} className="text-xs cursor-pointer">
                    {medication}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Previous Reactions */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="previous_reactions"
                checked={formData.previous_reactions || false}
                onCheckedChange={(checked) => handleInputChange('previous_reactions', checked)}
              />
              <Label htmlFor="previous_reactions" className="text-sm font-medium cursor-pointer">
                I've had reactions to this food before
              </Label>
            </div>
          </div>

          {/* Confidence Level */}
          <div className="space-y-3">
            <Label htmlFor="confidence_level" className="text-sm font-medium">Confidence Level</Label>
            <p className="text-xs text-gray-600">How confident are you that this food caused the reaction?</p>
            <div className="px-3 py-4 bg-gray-50 rounded-lg">
              <Slider
                value={[formData.confidence_level || 8]}
                onValueChange={(value: number[]) => handleInputChange('confidence_level', value[0])}
                max={10}
                min={1}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-2">
                <span>🤔 Not Sure</span>
                <span>🤷 Maybe</span>
                <span>✅ Very Confident</span>
              </div>
              <div className="text-center mt-2 font-medium text-gray-700">
                Confidence: {formData.confidence_level}/10
              </div>
            </div>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes" className="text-sm font-medium">Additional Notes</Label>
            <Textarea
              id="notes"
              value={formData.notes || ''}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleInputChange('notes', e.target.value)}
              placeholder="Any additional details about the reaction, circumstances, treatments tried, or other observations..."
              rows={4}
              className="resize-none"
            />
          </div>

          <Button type="submit" disabled={isLoading} className="w-full py-3 text-lg">
            {isLoading ? 'Logging Reaction...' : 'Log Food Reaction'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}