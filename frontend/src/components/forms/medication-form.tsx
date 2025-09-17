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
import { toast } from 'react-hot-toast';
import { 
  Pill, 
  Clock, 
  Calendar, 
  AlertCircle, 
  Plus, 
  X, 
  Heart, 
  Shield,
  Zap,
  Target,
  CheckCircle2
} from 'lucide-react';

interface MedicationFormData {
  name: string;
  type: string;
  dosage: string;
  frequency: string;
  schedule_times: string[];
  start_date: string;
  end_date?: string;
  purpose: string;
  side_effects: string[];
  effectiveness_rating: number;
  adherence_rating: number;
  taken_with_food: boolean;
  notes: string;
  prescribing_doctor: string;
  pharmacy: string;
  cost?: number;
  insurance_covered: boolean;
  reminder_enabled: boolean;
  is_prn: boolean; // As needed
  max_daily_doses?: number;
}

const MEDICATION_TYPES = [
  'Prescription', 'Over-the-counter', 'Supplement', 'Probiotic', 
  'Herbal', 'Vitamin', 'Mineral', 'Enzyme', 'Other'
];

const FREQUENCY_OPTIONS = [
  'Once daily', 'Twice daily', 'Three times daily', 'Four times daily',
  'Every 8 hours', 'Every 12 hours', 'Every 6 hours', 'Every 4 hours',
  'Weekly', 'As needed', 'Custom'
];

const PURPOSE_OPTIONS = [
  'IBS symptoms', 'Digestive health', 'Pain management', 'Anxiety/Stress',
  'Sleep', 'Inflammation', 'Gut health', 'Immune support', 'General health',
  'Specific condition', 'Preventive care', 'Other'
];

const COMMON_SIDE_EFFECTS = [
  'Nausea', 'Drowsiness', 'Dizziness', 'Headache', 'Stomach upset',
  'Diarrhea', 'Constipation', 'Dry mouth', 'Fatigue', 'Insomnia',
  'Appetite changes', 'Mood changes', 'Skin reactions', 'None observed'
];

export default function MedicationForm() {
  const [formData, setFormData] = useState<MedicationFormData>({
    name: '',
    type: '',
    dosage: '',
    frequency: '',
    schedule_times: [],
    start_date: new Date().toISOString().split('T')[0] || new Date().toISOString().substring(0, 10),
    purpose: '',
    side_effects: [],
    effectiveness_rating: 5,
    adherence_rating: 8,
    taken_with_food: false,
    notes: '',
    prescribing_doctor: '',
    pharmacy: '',
    cost: undefined,
    insurance_covered: false,
    reminder_enabled: true,
    is_prn: false,
    max_daily_doses: undefined
  });

  const [customTime, setCustomTime] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (field: keyof MedicationFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addScheduleTime = () => {
    if (customTime && !formData.schedule_times.includes(customTime)) {
      setFormData(prev => ({
        ...prev,
        schedule_times: [...prev.schedule_times, customTime].sort()
      }));
      setCustomTime('');
    }
  };

  const removeScheduleTime = (timeToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      schedule_times: prev.schedule_times.filter(time => time !== timeToRemove)
    }));
  };

  const toggleSideEffect = (effect: string) => {
    setFormData(prev => ({
      ...prev,
      side_effects: prev.side_effects?.includes(effect)
        ? prev.side_effects.filter(e => e !== effect)
        : [...(prev.side_effects || []), effect]
    }));
  };

  const generateScheduleTimes = (frequency: string) => {
    const times: string[] = [];
    switch (frequency) {
      case 'Once daily':
        times.push('08:00');
        break;
      case 'Twice daily':
        times.push('08:00', '20:00');
        break;
      case 'Three times daily':
        times.push('08:00', '14:00', '20:00');
        break;
      case 'Four times daily':
        times.push('08:00', '12:00', '16:00', '20:00');
        break;
      case 'Every 8 hours':
        times.push('08:00', '16:00', '00:00');
        break;
      case 'Every 12 hours':
        times.push('08:00', '20:00');
        break;
      case 'Every 6 hours':
        times.push('06:00', '12:00', '18:00', '00:00');
        break;
      case 'Every 4 hours':
        times.push('08:00', '12:00', '16:00', '20:00', '00:00', '04:00');
        break;
    }
    
    if (times.length > 0) {
      setFormData(prev => ({
        ...prev,
        schedule_times: times
      }));
    }
  };

  const handleFrequencyChange = (frequency: string) => {
    handleInputChange('frequency', frequency);
    if (frequency !== 'Custom' && frequency !== 'As needed' && frequency !== 'Weekly') {
      generateScheduleTimes(frequency);
    } else if (frequency === 'As needed') {
      handleInputChange('is_prn', true);
      setFormData(prev => ({ ...prev, schedule_times: [] }));
    } else {
      setFormData(prev => ({ ...prev, schedule_times: [] }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      toast.error('Please enter the medication name');
      return;
    }

    if (!formData.type) {
      toast.error('Please select medication type');
      return;
    }

    if (!formData.dosage.trim()) {
      toast.error('Please enter the dosage');
      return;
    }

    if (!formData.frequency) {
      toast.error('Please select frequency');
      return;
    }

    if (!formData.is_prn && formData.schedule_times.length === 0) {
      toast.error('Please add at least one schedule time or mark as "as needed"');
      return;
    }

    setIsLoading(true);

    try {
      // Here you would typically call an API to save the medication
      // await apiService.createMedication(formData);
      
      toast.success('Medication added successfully!');
      
      // Reset form
      setFormData({
        name: '',
        type: '',
        dosage: '',
        frequency: '',
        schedule_times: [],
        start_date: new Date().toISOString().split('T')[0] || new Date().toISOString().substring(0, 10),
        purpose: '',
        side_effects: [],
        effectiveness_rating: 5,
        adherence_rating: 8,
        taken_with_food: false,
        notes: '',
        prescribing_doctor: '',
        pharmacy: '',
        cost: undefined,
        insurance_covered: false,
        reminder_enabled: true,
        is_prn: false,
        max_daily_doses: undefined
      });
    } catch (error) {
      console.error('Error creating medication:', error);
      toast.error('Failed to add medication. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardTitle className="flex items-center gap-2 text-xl">
          <Pill className="h-6 w-6 text-blue-600" />
          Add Medication
        </CardTitle>
        <p className="text-sm text-gray-600">Track your medications, schedules, and effectiveness for better health management</p>
      </CardHeader>
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Medication Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Medication Name */}
            <div className="space-y-2">
              <Label htmlFor="name" className="text-sm font-medium">Medication Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('name', e.target.value)}
                placeholder="Enter medication name (e.g., Imodium, Probiotics)"
                required
                className="w-full"
              />
            </div>

            {/* Medication Type */}
            <div className="space-y-2">
              <Label htmlFor="type" className="text-sm font-medium">Type *</Label>
              <Select
                value={formData.type}
                onValueChange={(value: string) => handleInputChange('type', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select medication type" />
                </SelectTrigger>
                <SelectContent>
                  {MEDICATION_TYPES.map((type) => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Dosage and Purpose */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Dosage */}
            <div className="space-y-2">
              <Label htmlFor="dosage" className="text-sm font-medium">Dosage *</Label>
              <Input
                id="dosage"
                value={formData.dosage}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('dosage', e.target.value)}
                placeholder="e.g., 2mg, 1 tablet, 1 capsule"
                required
                className="w-full"
              />
            </div>

            {/* Purpose */}
            <div className="space-y-2">
              <Label htmlFor="purpose" className="text-sm font-medium flex items-center gap-1">
                <Target className="h-4 w-4" />
                Purpose
              </Label>
              <Select
                value={formData.purpose}
                onValueChange={(value: string) => handleInputChange('purpose', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="What is this medication for?" />
                </SelectTrigger>
                <SelectContent>
                  {PURPOSE_OPTIONS.map((purpose) => (
                    <SelectItem key={purpose} value={purpose}>{purpose}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Frequency and Schedule */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-green-500" />
              <Label className="text-sm font-medium">Schedule Information</Label>
            </div>

            {/* Frequency */}
            <div className="space-y-2">
              <Label htmlFor="frequency" className="text-sm font-medium">Frequency *</Label>
              <Select
                value={formData.frequency}
                onValueChange={handleFrequencyChange}
              >
                <SelectTrigger>
                  <SelectValue placeholder="How often do you take this?" />
                </SelectTrigger>
                <SelectContent>
                  {FREQUENCY_OPTIONS.map((freq) => (
                    <SelectItem key={freq} value={freq}>{freq}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* As Needed Options */}
            {formData.is_prn && (
              <div className="space-y-3 p-4 bg-yellow-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-yellow-600" />
                  <span className="text-sm font-medium text-yellow-800">As Needed (PRN) Medication</span>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="max_daily_doses" className="text-sm font-medium">Maximum doses per day</Label>
                  <Input
                    id="max_daily_doses"
                    type="number"
                    min="1"
                    max="20"
                    value={formData.max_daily_doses || ''}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                      handleInputChange('max_daily_doses', e.target.value ? parseInt(e.target.value) : undefined)
                    }
                    placeholder="Maximum number of doses per day"
                    className="w-full"
                  />
                </div>
              </div>
            )}

            {/* Schedule Times */}
            {!formData.is_prn && (
              <div className="space-y-3">
                <Label className="text-sm font-medium">Schedule Times</Label>
                
                {/* Add Custom Time */}
                <div className="flex gap-2">
                  <Input
                    type="time"
                    value={customTime}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCustomTime(e.target.value)}
                    className="flex-1"
                  />
                  <Button type="button" onClick={addScheduleTime} variant="outline" size="sm">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>

                {/* Display Schedule Times */}
                {formData.schedule_times.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm text-gray-600">Scheduled times:</p>
                    <div className="flex flex-wrap gap-2">
                      {formData.schedule_times.map((time, index) => (
                        <div
                          key={index}
                          className="bg-green-100 text-green-800 px-3 py-2 rounded-full text-sm flex items-center gap-2"
                        >
                          <Clock className="h-3 w-3" />
                          {time}
                          <button
                            type="button"
                            onClick={() => removeScheduleTime(time)}
                            className="text-green-600 hover:text-green-800 ml-1"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Date Range */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Start Date */}
            <div className="space-y-2">
              <Label htmlFor="start_date" className="text-sm font-medium flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                Start Date *
              </Label>
              <Input
                id="start_date"
                type="date"
                value={formData.start_date}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('start_date', e.target.value)}
                required
                className="w-full"
              />
            </div>

            {/* End Date */}
            <div className="space-y-2">
              <Label htmlFor="end_date" className="text-sm font-medium">End Date (if applicable)</Label>
              <Input
                id="end_date"
                type="date"
                value={formData.end_date || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('end_date', e.target.value || undefined)}
                className="w-full"
              />
            </div>
          </div>

          {/* Effectiveness and Adherence */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Effectiveness Rating */}
            <div className="space-y-3">
              <Label htmlFor="effectiveness_rating" className="text-sm font-medium flex items-center gap-1">
                <Zap className="h-4 w-4 text-yellow-500" />
                Effectiveness Rating
              </Label>
              <div className="px-3 py-4 bg-yellow-50 rounded-lg">
                <Slider
                  value={[formData.effectiveness_rating || 5]}
                  onValueChange={(value: number[]) => handleInputChange('effectiveness_rating', value[0])}
                  max={10}
                  min={1}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-2">
                  <span>😞 Not Effective</span>
                  <span>😐 Moderate</span>
                  <span>😊 Very Effective</span>
                </div>
                <div className="text-center mt-2 font-medium text-yellow-700">
                  Rating: {formData.effectiveness_rating}/10
                </div>
              </div>
            </div>

            {/* Adherence Rating */}
            <div className="space-y-3">
              <Label htmlFor="adherence_rating" className="text-sm font-medium flex items-center gap-1">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                Adherence Rating
              </Label>
              <div className="px-3 py-4 bg-green-50 rounded-lg">
                <Slider
                  value={[formData.adherence_rating || 8]}
                  onValueChange={(value: number[]) => handleInputChange('adherence_rating', value[0])}
                  max={10}
                  min={1}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-2">
                  <span>😔 Often Miss</span>
                  <span>😐 Sometimes</span>
                  <span>✅ Always Take</span>
                </div>
                <div className="text-center mt-2 font-medium text-green-700">
                  Adherence: {formData.adherence_rating}/10
                </div>
              </div>
            </div>
          </div>

          {/* Side Effects */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <Label className="text-sm font-medium">Side Effects</Label>
            </div>
            <p className="text-sm text-gray-600">Select any side effects you've experienced:</p>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {COMMON_SIDE_EFFECTS.map((effect) => (
                <div key={effect} className="flex items-center space-x-2">
                  <Checkbox
                    id={effect}
                    checked={formData.side_effects?.includes(effect) || false}
                    onCheckedChange={() => toggleSideEffect(effect)}
                  />
                  <Label htmlFor={effect} className="text-xs cursor-pointer">
                    {effect}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Additional Options */}
          <div className="space-y-4">
            <Label className="text-sm font-medium">Additional Options</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="taken_with_food"
                  checked={formData.taken_with_food}
                  onCheckedChange={(checked) => handleInputChange('taken_with_food', checked)}
                />
                <Label htmlFor="taken_with_food" className="text-sm cursor-pointer">
                  Take with food
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="reminder_enabled"
                  checked={formData.reminder_enabled}
                  onCheckedChange={(checked) => handleInputChange('reminder_enabled', checked)}
                />
                <Label htmlFor="reminder_enabled" className="text-sm cursor-pointer">
                  Enable reminders
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="insurance_covered"
                  checked={formData.insurance_covered}
                  onCheckedChange={(checked) => handleInputChange('insurance_covered', checked)}
                />
                <Label htmlFor="insurance_covered" className="text-sm cursor-pointer">
                  Covered by insurance
                </Label>
              </div>
            </div>
          </div>

          {/* Healthcare Provider Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Prescribing Doctor */}
            <div className="space-y-2">
              <Label htmlFor="prescribing_doctor" className="text-sm font-medium">Prescribing Doctor</Label>
              <Input
                id="prescribing_doctor"
                value={formData.prescribing_doctor || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('prescribing_doctor', e.target.value)}
                placeholder="Dr. Smith, Gastroenterologist"
                className="w-full"
              />
            </div>

            {/* Pharmacy */}
            <div className="space-y-2">
              <Label htmlFor="pharmacy" className="text-sm font-medium">Pharmacy</Label>
              <Input
                id="pharmacy"
                value={formData.pharmacy || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('pharmacy', e.target.value)}
                placeholder="CVS, Walgreens, etc."
                className="w-full"
              />
            </div>
          </div>

          {/* Cost */}
          <div className="space-y-2">
            <Label htmlFor="cost" className="text-sm font-medium">Cost per Month (optional)</Label>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">$</span>
              <Input
                id="cost"
                type="number"
                min="0"
                step="0.01"
                value={formData.cost || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                  handleInputChange('cost', e.target.value ? parseFloat(e.target.value) : undefined)
                }
                placeholder="0.00"
                className="flex-1"
              />
            </div>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes" className="text-sm font-medium">Notes</Label>
            <Textarea
              id="notes"
              value={formData.notes || ''}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleInputChange('notes', e.target.value)}
              placeholder="Any additional notes about this medication, special instructions, or observations..."
              rows={4}
              className="resize-none"
            />
          </div>

          <Button type="submit" disabled={isLoading} className="w-full py-3 text-lg">
            {isLoading ? 'Adding Medication...' : 'Add Medication'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}