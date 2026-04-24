'use client';

import { useState } from 'react';
import { toast } from 'react-hot-toast';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Slider } from '@/components/ui/slider';
import { Calendar, Clock, Loader2, Save, AlertCircle, Activity } from 'lucide-react';
import { apiService, SymptomLogCreate } from '@/lib/api';
import { SeverityLevel, BristolStoolType } from '@ibs-wellness/shared-types';

interface SymptomLogFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export default function SymptomLogForm({ onSuccess, onCancel }: SymptomLogFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<SymptomLogCreate>({
    severity: SeverityLevel.MILD,
    symptoms: [],
    pain_location: '',
    bristol_stool_type: undefined,
    bowel_movement_frequency: undefined,
    pain_type: '',
    stress_level: 5,
    sleep_quality: 5,
    exercise_minutes: 0,
    potential_triggers: '',
    notes: '',
    logged_at: new Date().toISOString(),
    symptom_id: 1, // Default to general IBS symptoms
  });

  // Common IBS symptoms for checklist
  const commonSymptoms = [
    'Abdominal pain',
    'Bloating',
    'Gas',
    'Diarrhea',
    'Constipation',
    'Cramping',
    'Nausea',
    'Urgency',
    'Incomplete evacuation',
    'Mucus in stool',
    'Fatigue',
    'Headache'
  ];

  const handleInputChange = (field: keyof SymptomLogCreate, value: string | number | undefined) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSymptomToggle = (symptom: string) => {
    setFormData(prev => ({
      ...prev,
      symptoms: prev.symptoms?.includes(symptom)
        ? prev.symptoms.filter(s => s !== symptom)
        : [...(prev.symptoms || []), symptom]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.symptoms || formData.symptoms.length === 0) {
      toast.error('Please select at least one symptom');
      return;
    }

    setIsLoading(true);

    try {
      // Convert bristol stool type number to enum string
      const bristolStoolTypeMap: Record<number, string> = {
        1: 'type_1',
        2: 'type_2', 
        3: 'type_3',
        4: 'type_4',
        5: 'type_5',
        6: 'type_6',
        7: 'type_7'
      };

      // Prepare data to match backend schema exactly
      const submitData = {
        symptom_id: formData.symptom_id || 1,
        severity: formData.severity,
        bristol_stool_type: formData.bristol_stool_type ? bristolStoolTypeMap[formData.bristol_stool_type] : undefined,
        bowel_movement_frequency: formData.bowel_movement_frequency,
        pain_location: formData.pain_location || '',
        pain_type: formData.pain_type || '',
        stress_level: formData.stress_level,
        sleep_quality: formData.sleep_quality,
        exercise_minutes: formData.exercise_minutes,
        potential_triggers: formData.symptoms.join(', '), // Convert symptoms array to string for triggers
        notes: formData.notes || '',
        logged_at: formData.logged_at || new Date().toISOString(),
      };

      // Cast to any to bypass type checking since backend schema differs from frontend types
      const result = await apiService.createSymptomLog(submitData as any);
      console.log('Symptom log save result:', result);
      toast.success('Symptom log saved successfully!');
      
      // Reset form
      setFormData({
        severity: SeverityLevel.MILD,
        symptoms: [],
        pain_location: '',
        bristol_stool_type: undefined,
        bowel_movement_frequency: undefined,
        pain_type: '',
        stress_level: 5,
        sleep_quality: 5,
        exercise_minutes: 0,
        potential_triggers: '',
        notes: '',
        logged_at: new Date().toISOString(),
        symptom_id: 1,
      });

      onSuccess?.();
    } catch (error) {
      console.error('Error creating symptom log:', error);
      
      // Try to get more detailed error information
      let errorMessage = 'Failed to save symptom log. Please try again.';
      if (error instanceof Error) {
        errorMessage = `Failed to save symptom log: ${error.message}`;
      }
      
      toast.error(errorMessage);
      alert(`Error saving symptom log: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader className="space-y-1">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-blue-600" />
          <CardTitle className="text-xl">Log Your Symptoms</CardTitle>
        </div>
        <CardDescription>
          Track your IBS symptoms to help identify patterns and triggers
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Date and Time */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="date" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Date & Time
              </Label>
              <Input
                id="date"
                type="datetime-local"
                value={formData.logged_at ? new Date(formData.logged_at).toISOString().slice(0, 16) : ''}
                onChange={(e) => handleInputChange('logged_at', e.target.value ? new Date(e.target.value).toISOString() : '')}
                className="w-full"
              />
            </div>
          </div>

          {/* Severity */}
          <div className="space-y-3">
            <Label className="text-base font-medium">Overall Severity</Label>
            <Select
              value={formData.severity}
              onValueChange={(value) => handleInputChange('severity', value as SeverityLevel)}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select severity level" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={SeverityLevel.NONE}>None</SelectItem>
                <SelectItem value={SeverityLevel.MILD}>Mild</SelectItem>
                <SelectItem value={SeverityLevel.MODERATE}>Moderate</SelectItem>
                <SelectItem value={SeverityLevel.SEVERE}>Severe</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Symptoms Checklist */}
          <div className="space-y-3">
            <Label className="text-base font-medium">Symptoms Experienced</Label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {commonSymptoms.map((symptom) => (
                <div key={symptom} className="flex items-center space-x-2">
                  <Checkbox
                    id={symptom}
                    checked={formData.symptoms?.includes(symptom) || false}
                    onCheckedChange={() => handleSymptomToggle(symptom)}
                  />
                  <Label htmlFor={symptom} className="text-sm font-normal cursor-pointer">
                    {symptom}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Bristol Stool Type */}
          <div className="space-y-3">
            <Label className="text-base font-medium">Bristol Stool Type (if applicable)</Label>
            <Select
              value={formData.bristol_stool_type?.toString() || 'not_applicable'}
              onValueChange={(value) => handleInputChange('bristol_stool_type', value === 'not_applicable' ? undefined : parseInt(value) as BristolStoolType)}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select stool type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="not_applicable">Not applicable</SelectItem>
                <SelectItem value="1">Type 1 - Separate hard lumps</SelectItem>
                <SelectItem value="2">Type 2 - Lumpy sausage</SelectItem>
                <SelectItem value="3">Type 3 - Cracked sausage</SelectItem>
                <SelectItem value="4">Type 4 - Smooth sausage</SelectItem>
                <SelectItem value="5">Type 5 - Soft blobs</SelectItem>
                <SelectItem value="6">Type 6 - Mushy consistency</SelectItem>
                <SelectItem value="7">Type 7 - Liquid consistency</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Bowel Movement Frequency */}
          <div className="space-y-2">
            <Label htmlFor="frequency">Bowel Movement Frequency (times today)</Label>
            <Input
              id="frequency"
              type="number"
              min="0"
              max="20"
              value={formData.bowel_movement_frequency || ''}
              onChange={(e) => handleInputChange('bowel_movement_frequency', e.target.value ? parseInt(e.target.value) : undefined)}
              placeholder="Enter number of bowel movements"
            />
          </div>

          {/* Pain Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="pain-location">Pain Location</Label>
              <Input
                id="pain-location"
                value={formData.pain_location || ''}
                onChange={(e) => handleInputChange('pain_location', e.target.value)}
                placeholder="e.g., Lower left abdomen"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="pain-type">Pain Type</Label>
              <Select
                value={formData.pain_type || 'no_pain'}
                onValueChange={(value) => handleInputChange('pain_type', value === 'no_pain' ? '' : value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select pain type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="no_pain">No pain</SelectItem>
                  <SelectItem value="cramping">Cramping</SelectItem>
                  <SelectItem value="sharp">Sharp</SelectItem>
                  <SelectItem value="dull">Dull ache</SelectItem>
                  <SelectItem value="burning">Burning</SelectItem>
                  <SelectItem value="stabbing">Stabbing</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Stress and Sleep Quality */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <Label className="text-base font-medium">
                Stress Level: {formData.stress_level}/10
              </Label>
              <Slider
                value={[formData.stress_level || 5]}
                onValueChange={(value) => handleInputChange('stress_level', value[0])}
                max={10}
                min={1}
                step={1}
                className="w-full"
              />
            </div>
            <div className="space-y-3">
              <Label className="text-base font-medium">
                Sleep Quality: {formData.sleep_quality}/10
              </Label>
              <Slider
                value={[formData.sleep_quality || 5]}
                onValueChange={(value) => handleInputChange('sleep_quality', value[0])}
                max={10}
                min={1}
                step={1}
                className="w-full"
              />
            </div>
          </div>

          {/* Exercise */}
          <div className="space-y-2">
            <Label htmlFor="exercise">Exercise (minutes today)</Label>
            <Input
              id="exercise"
              type="number"
              min="0"
              value={formData.exercise_minutes || ''}
              onChange={(e) => handleInputChange('exercise_minutes', e.target.value ? parseInt(e.target.value) : 0)}
              placeholder="Minutes of exercise today"
            />
          </div>

          {/* Potential Triggers */}
          <div className="space-y-2">
            <Label htmlFor="triggers">Potential Triggers</Label>
            <Input
              id="triggers"
              value={formData.potential_triggers || ''}
              onChange={(e) => handleInputChange('potential_triggers', e.target.value)}
              placeholder="e.g., spicy food, stress, lack of sleep"
            />
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">Additional Notes</Label>
            <Textarea
              id="notes"
              value={formData.notes || ''}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              placeholder="Any additional details about your symptoms..."
              rows={3}
            />
          </div>

          {/* Form Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="submit"
              disabled={isLoading}
              className="flex-1 bg-blue-600 hover:bg-blue-700"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save Symptom Log
                </>
              )}
            </Button>
            {onCancel && (
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isLoading}
              >
                Cancel
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
}