/**
 * Comprehensive Profile Form Component with validation and data handling
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Save, RefreshCw, CheckCircle, AlertCircle, Info, Loader2 } from 'lucide-react';
import { useProfileValidation, ProfileData, ValidationResult, ValidationError } from '@/hooks/useProfileValidation';

interface ProfileFormProps {
  initialData?: Partial<ProfileData>;
  onSave?: (data: ProfileData) => Promise<void>;
  onSync?: (data: ProfileData) => Promise<void>;
  isLoading?: boolean;
  className?: string;
}

export const ProfileForm: React.FC<ProfileFormProps> = ({
  initialData = {},
  onSave,
  onSync,
  isLoading = false,
  className = ''
}) => {
  const [profileData, setProfileData] = useState<Partial<ProfileData>>(initialData);
  const [activeTab, setActiveTab] = useState('basic');
  const [isSaving, setIsSaving] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const {
    validationState,
    validateField,
    validateProfile,
    calculateCompletion,
    transformForBackend,
    transformFromBackend,
    setValidationState
  } = useProfileValidation();

  // Initialize form data
  useEffect(() => {
    if (initialData && Object.keys(initialData).length > 0) {
      const transformedData = transformFromBackend(initialData);
      setProfileData(transformedData);
    }
  }, [initialData, transformFromBackend]);

  // Calculate completion status
  const completionStatus = calculateCompletion(profileData);

  // Handle field changes with validation
  const handleFieldChange = useCallback((fieldName: string, value: any) => {
    setProfileData(prev => ({
      ...prev,
      [fieldName]: value
    }));

    // Real-time validation
    validateField(fieldName, value);
  }, [validateField]);

  // Handle form submission
  const handleSave = useCallback(async () => {
    if (!onSave) return;

    setIsSaving(true);
    setSaveMessage(null);

    try {
      // Validate entire profile
      const validation = validateProfile(profileData);
      setValidationState(validation);

      if (!validation.isValid) {
        setSaveMessage({
          type: 'error',
          message: 'Please fix validation errors before saving'
        });
        return;
      }

      // Transform data for backend
      const backendData = transformForBackend(profileData);
      await onSave(backendData as ProfileData);

      setSaveMessage({
        type: 'success',
        message: 'Profile saved successfully!'
      });
    } catch (error) {
      setSaveMessage({
        type: 'error',
        message: error instanceof Error ? error.message : 'Failed to save profile'
      });
    } finally {
      setIsSaving(false);
    }
  }, [profileData, validateProfile, transformForBackend, onSave, setValidationState]);

  // Handle sync
  const handleSync = useCallback(async () => {
    if (!onSync) return;

    setIsSyncing(true);
    setSaveMessage(null);

    try {
      const backendData = transformForBackend(profileData);
      await onSync(backendData as ProfileData);

      setSaveMessage({
        type: 'success',
        message: 'Profile synced successfully!'
      });
    } catch (error) {
      setSaveMessage({
        type: 'error',
        message: error instanceof Error ? error.message : 'Failed to sync profile'
      });
    } finally {
      setIsSyncing(false);
    }
  }, [profileData, transformForBackend, onSync]);

  // Get field errors
  const getFieldErrors = (fieldName: string): ValidationError[] => {
    return validationState.errors.filter(error => error.field === fieldName);
  };

  // Render field with validation
  const renderField = (
    fieldName: string,
    label: string,
    type: 'text' | 'email' | 'tel' | 'date' | 'number' | 'select' | 'textarea' = 'text',
    options?: { value: string; label: string }[],
    placeholder?: string
  ) => {
    const fieldErrors = getFieldErrors(fieldName);
    const hasError = fieldErrors.length > 0;
    const value = profileData[fieldName] || '';

    return (
      <div className="space-y-2">
        <Label htmlFor={fieldName} className={hasError ? 'text-red-600' : ''}>
          {label}
          {validationState.errors.some(e => e.field === fieldName) && (
            <span className="text-red-500 ml-1">*</span>
          )}
        </Label>

        {type === 'select' && options ? (
          <Select
            value={value}
            onValueChange={(newValue) => handleFieldChange(fieldName, newValue)}
          >
            <SelectTrigger className={hasError ? 'border-red-500' : ''}>
              <SelectValue placeholder={placeholder || `Select ${label.toLowerCase()}`} />
            </SelectTrigger>
            <SelectContent>
              {options.map(option => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        ) : type === 'textarea' ? (
          <Textarea
            id={fieldName}
            value={value}
            onChange={(e) => handleFieldChange(fieldName, e.target.value)}
            placeholder={placeholder}
            className={hasError ? 'border-red-500' : ''}
            rows={3}
          />
        ) : (
          <Input
            id={fieldName}
            type={type}
            value={value}
            onChange={(e) => handleFieldChange(fieldName, e.target.value)}
            placeholder={placeholder}
            className={hasError ? 'border-red-500' : ''}
          />
        )}

        {fieldErrors.map((error, index) => (
          <p key={index} className="text-sm text-red-600 flex items-center gap-1">
            <AlertCircle className="h-4 w-4" />
            {error.message}
          </p>
        ))}
      </div>
    );
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Progress Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Profile Completion</CardTitle>
            <Badge variant={completionStatus.overallCompletion >= 80 ? 'default' : 'secondary'}>
              {completionStatus.overallCompletion.toFixed(1)}% Complete
            </Badge>
          </div>
          <Progress value={completionStatus.overallCompletion} className="w-full" />
        </CardHeader>
        {completionStatus.recommendedNextSteps.length > 0 && (
          <CardContent>
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Recommended Next Steps:</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                {completionStatus.recommendedNextSteps.map((step, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <Info className="h-3 w-3" />
                    {step}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Validation Messages */}
      {saveMessage && (
        <div className={`p-4 rounded-md ${saveMessage.type === 'error' ? 'bg-red-50 text-red-800 border border-red-200' : 'bg-green-50 text-green-800 border border-green-200'}`}>
          {saveMessage.message}
        </div>
      )}

      {validationState.warnings.length > 0 && (
        <div className="p-4 rounded-md bg-yellow-50 text-yellow-800 border border-yellow-200">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            <div className="space-y-1">
              {validationState.warnings.map((warning, index) => (
                <p key={index}>{warning.message}</p>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Form Tabs */}
      <Tabs defaultValue="basic">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="basic">Basic</TabsTrigger>
          <TabsTrigger value="medical">Medical</TabsTrigger>
          <TabsTrigger value="dietary">Dietary</TabsTrigger>
          <TabsTrigger value="lifestyle">Lifestyle</TabsTrigger>
          <TabsTrigger value="goals">Goals</TabsTrigger>
          <TabsTrigger value="symptoms">Symptoms</TabsTrigger>
        </TabsList>

        {/* Basic Information Tab */}
        <TabsContent value="basic">
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {renderField('first_name', 'First Name', 'text', undefined, 'Enter your first name')}
                {renderField('last_name', 'Last Name', 'text', undefined, 'Enter your last name')}
                {renderField('email', 'Email', 'email', undefined, 'Enter your email address')}
                {renderField('phone_number', 'Phone Number', 'tel', undefined, 'Enter your phone number')}
                {renderField('date_of_birth', 'Date of Birth', 'date')}
                {renderField('gender', 'Gender', 'select', [
                  { value: 'male', label: 'Male' },
                  { value: 'female', label: 'Female' },
                  { value: 'other', label: 'Other' },
                  { value: 'prefer_not_to_say', label: 'Prefer not to say' }
                ])}
                {renderField('height_cm', 'Height (cm)', 'number', undefined, 'Enter your height in centimeters')}
                {renderField('weight_kg', 'Weight (kg)', 'number', undefined, 'Enter your weight in kilograms')}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Medical History Tab */}
        <TabsContent value="medical">
          <Card>
            <CardHeader>
              <CardTitle>Medical History</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {renderField('ibs_type', 'IBS Type', 'select', [
                  { value: 'ibs-d', label: 'IBS-D (Diarrhea-predominant)' },
                  { value: 'ibs-c', label: 'IBS-C (Constipation-predominant)' },
                  { value: 'ibs-m', label: 'IBS-M (Mixed)' },
                  { value: 'ibs-u', label: 'IBS-U (Unsubtyped)' }
                ])}
                {renderField('diagnosis_date', 'Diagnosis Date', 'date')}
                {renderField('severity_level', 'Severity Level (1-10)', 'number', undefined, 'Rate from 1 (mild) to 10 (severe)')}
              </div>
              {renderField('medical_notes', 'Medical Notes', 'textarea', undefined, 'Any additional medical information or notes')}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Dietary Preferences Tab */}
        <TabsContent value="dietary">
          <Card>
            <CardHeader>
              <CardTitle>Dietary Preferences</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {renderField('meal_frequency', 'Meals per Day', 'number', undefined, 'Number of meals you typically eat per day')}
                {renderField('water_intake_goal', 'Water Intake Goal (L)', 'number', undefined, 'Daily water intake goal in liters')}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Lifestyle Factors Tab */}
        <TabsContent value="lifestyle">
          <Card>
            <CardHeader>
              <CardTitle>Lifestyle Factors</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {renderField('exercise_frequency', 'Exercise Days/Week', 'number', undefined, 'Days per week you exercise')}
                {renderField('sleep_quality', 'Sleep Quality (1-10)', 'number', undefined, 'Rate your sleep quality')}
                {renderField('stress_level', 'Stress Level (1-10)', 'number', undefined, 'Rate your stress level')}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Goals & Preferences Tab */}
        <TabsContent value="goals">
          <Card>
            <CardHeader>
              <CardTitle>Goals & Preferences</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                This section will be expanded with goal-setting and preference options.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Initial Symptom Log Tab */}
        <TabsContent value="symptoms">
          <Card>
            <CardHeader>
              <CardTitle>Initial Symptom Log</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                This section will be expanded with symptom logging functionality.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Action Buttons */}
      <div className="flex gap-4 justify-end">
        {onSync && (
          <Button
            variant="outline"
            onClick={handleSync}
            disabled={isSyncing || isLoading}
          >
            {isSyncing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Syncing...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Sync Profile
              </>
            )}
          </Button>
        )}
        
        {onSave && (
          <Button
            onClick={handleSave}
            disabled={isSaving || isLoading || validationState.errors.length > 0}
          >
            {isSaving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save Profile
              </>
            )}
          </Button>
        )}
      </div>

      {/* Suggestions */}
      {validationState.suggestions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Suggestions</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="text-sm text-muted-foreground space-y-1">
              {validationState.suggestions.map((suggestion, index) => (
                <li key={index} className="flex items-center gap-2">
                  <Info className="h-3 w-3" />
                  {suggestion}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ProfileForm;