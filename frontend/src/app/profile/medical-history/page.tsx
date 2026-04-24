'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
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
import { Heart, Save, ArrowLeft, Plus, X } from "lucide-react";
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';

interface MedicalHistoryData {
  diagnosisYear: number;
  ibsType: string;
  severityLevel: string;
  knownTriggers: string[];
  commonSymptoms: string[];
  symptomPatterns: string[];
  medications: string[];
  allergies: string[];
  otherConditions: string[];
  familyHistory: string;
  previousTreatments: string[];
  doctorNotes: string;
}

const ibsTypeOptions = [
  { value: 'ibs_d', label: 'IBS-D (Diarrhea predominant)' },
  { value: 'ibs_c', label: 'IBS-C (Constipation predominant)' },
  { value: 'ibs_m', label: 'IBS-M (Mixed)' },
  { value: 'ibs_u', label: 'IBS-U (Unsubtyped)' },
  { value: 'not_diagnosed', label: 'Not formally diagnosed' }
];

const severityOptions = [
  { value: 'mild', label: 'Mild - Occasional symptoms' },
  { value: 'moderate', label: 'Moderate - Regular symptoms' },
  { value: 'severe', label: 'Severe - Daily symptoms' }
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

const treatmentOptions = [
  'Low FODMAP diet', 'Probiotics', 'Antispasmodics', 'Loperamide',
  'Fiber supplements', 'Peppermint oil', 'Cognitive behavioral therapy',
  'Stress management', 'Exercise therapy', 'Alternative medicine'
];

export default function MedicalHistoryPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [formData, setFormData] = useState<MedicalHistoryData>({
    diagnosisYear: new Date().getFullYear(),
    ibsType: '',
    severityLevel: '',
    knownTriggers: [],
    commonSymptoms: [],
    symptomPatterns: [],
    medications: [],
    allergies: [],
    otherConditions: [],
    familyHistory: '',
    previousTreatments: [],
    doctorNotes: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [newMedication, setNewMedication] = useState('');
  const [newAllergy, setNewAllergy] = useState('');
  const [newCondition, setNewCondition] = useState('');

  useEffect(() => {
    if (user) {
      // First try to load from backend API, fallback to user context
      loadMedicalHistory();
    }
  }, [user]);

  const loadMedicalHistoryFromUser = () => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        diagnosisYear: user.diagnosis_date ? new Date(user.diagnosis_date).getFullYear() : new Date().getFullYear(),
        ibsType: user.ibs_type || '',
        // Other fields will be loaded from API as they're not in the User type
        severityLevel: '',
        knownTriggers: [],
        commonSymptoms: [],
        symptomPatterns: [],
        medications: [],
        allergies: [],
        otherConditions: [],
        familyHistory: '',
        previousTreatments: [],
        doctorNotes: ''
      }));
    }
  };

  const loadMedicalHistory = async () => {
    try {
      setIsLoading(true);
      
      // Get token from localStorage if available
      const token = localStorage.getItem('access_token');
      
      // Prepare headers
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      // Try to load from backend API first
      const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000'}/api/v1/profile/medical-history`, {
        headers,
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        // Transform backend data to form format
        setFormData({
          diagnosisYear: data.diagnosis_date ? new Date(data.diagnosis_date).getFullYear() : new Date().getFullYear(),
          ibsType: data.ibs_type || '',
          severityLevel: '',
          knownTriggers: [],
          commonSymptoms: [],
          symptomPatterns: [],
          medications: [],
          allergies: [],
          otherConditions: [],
          familyHistory: '',
          previousTreatments: [],
          doctorNotes: data.medical_notes || ''
        });
        setHasUnsavedChanges(false);
      } else {
        // Fallback to user context data if API fails
        loadMedicalHistoryFromUser();
      }
    } catch (error) {
      console.error('Failed to load medical history from API, falling back to user context:', error);
      // Fallback to user context data
      loadMedicalHistoryFromUser();
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: keyof MedicalHistoryData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleArrayToggle = (field: keyof MedicalHistoryData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: (prev[field] as string[]).includes(value)
        ? (prev[field] as string[]).filter(item => item !== value)
        : [...(prev[field] as string[]), value]
    }));
  };

  const addToArray = (field: keyof MedicalHistoryData, value: string) => {
    if (value.trim() && !(formData[field] as string[]).includes(value.trim())) {
      setFormData(prev => ({
        ...prev,
        [field]: [...(prev[field] as string[]), value.trim()]
      }));
    }
  };

  const removeFromArray = (field: keyof MedicalHistoryData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: (prev[field] as string[]).filter(item => item !== value)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      // Get token from localStorage if available
      const token = localStorage.getItem('access_token');
      
      // Prepare headers
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
         headers['Authorization'] = `Bearer ${token}`;
       }
      
      // Convert form data to backend format - only send fields that exist in the User model
      const profileData = {
        diagnosis_date: `${formData.diagnosisYear}-01-01`,
        ibs_type: formData.ibsType,
        medical_notes: formData.doctorNotes,
        // Note: Other fields like triggers, symptoms, etc. are not stored in the User model
        // They would need separate tables or JSONB fields to be implemented
      };
      
      const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000'}/api/v1/profile/medical-history`, {
        method: 'PUT',
        headers,
        credentials: 'include', // Send both session cookies and Bearer token
        body: JSON.stringify(profileData),
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Medical history saved successfully:', result);
        // Don't redirect, just show success message
        alert('Medical history saved successfully!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save medical history');
      }
    } catch (error) {
      console.error('Failed to save medical history:', error);
      alert(`Failed to save medical history: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50">
          <DashboardHeader title="Medical History" showBackButton />
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
        <DashboardHeader title="Medical History" showBackButton />
        
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
                <div className="p-2 bg-red-100 rounded-full">
                  <Heart className="h-6 w-6 text-red-600" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Medical History</h1>
                  <p className="text-gray-600">IBS diagnosis, symptoms, and medical background</p>
                </div>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* IBS Diagnosis */}
              <Card>
                <CardHeader>
                  <CardTitle>IBS Diagnosis</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="diagnosisYear">Year of Diagnosis</Label>
                      <Input
                        id="diagnosisYear"
                        type="number"
                        min="1950"
                        max={new Date().getFullYear()}
                        value={formData.diagnosisYear}
                        onChange={(e) => handleInputChange('diagnosisYear', Number(e.target.value))}
                      />
                    </div>
                    <div>
                      <Label htmlFor="ibsType">IBS Type</Label>
                      <Select value={formData.ibsType} onValueChange={(value) => handleInputChange('ibsType', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select IBS type" />
                        </SelectTrigger>
                        <SelectContent>
                          {ibsTypeOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="severityLevel">Severity Level</Label>
                    <Select value={formData.severityLevel} onValueChange={(value) => handleInputChange('severityLevel', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select severity level" />
                      </SelectTrigger>
                      <SelectContent>
                        {severityOptions.map(option => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>

              {/* Known Triggers */}
              <Card>
                <CardHeader>
                  <CardTitle>Known Triggers</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {triggerOptions.map(trigger => (
                      <div key={trigger} className="flex items-center space-x-2">
                        <Checkbox
                          id={`trigger-${trigger}`}
                          checked={formData.knownTriggers.includes(trigger)}
                          onCheckedChange={() => handleArrayToggle('knownTriggers', trigger)}
                        />
                        <Label htmlFor={`trigger-${trigger}`} className="text-sm">
                          {trigger}
                        </Label>
                      </div>
                    ))}
                  </div>
                  {formData.knownTriggers.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-4">
                      {formData.knownTriggers.map(trigger => (
                        <Badge key={trigger} variant="secondary" className="flex items-center gap-1">
                          {trigger}
                          <X
                            className="h-3 w-3 cursor-pointer"
                            onClick={() => removeFromArray('knownTriggers', trigger)}
                          />
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Common Symptoms */}
              <Card>
                <CardHeader>
                  <CardTitle>Common Symptoms</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {symptomOptions.map(symptom => (
                      <div key={symptom} className="flex items-center space-x-2">
                        <Checkbox
                          id={`symptom-${symptom}`}
                          checked={formData.commonSymptoms.includes(symptom)}
                          onCheckedChange={() => handleArrayToggle('commonSymptoms', symptom)}
                        />
                        <Label htmlFor={`symptom-${symptom}`} className="text-sm">
                          {symptom}
                        </Label>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Symptom Patterns */}
              <Card>
                <CardHeader>
                  <CardTitle>Symptom Patterns</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {patternOptions.map(pattern => (
                      <div key={pattern} className="flex items-center space-x-2">
                        <Checkbox
                          id={`pattern-${pattern}`}
                          checked={formData.symptomPatterns.includes(pattern)}
                          onCheckedChange={() => handleArrayToggle('symptomPatterns', pattern)}
                        />
                        <Label htmlFor={`pattern-${pattern}`} className="text-sm">
                          {pattern}
                        </Label>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Current Medications */}
              <Card>
                <CardHeader>
                  <CardTitle>Current Medications</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add medication..."
                      value={newMedication}
                      onChange={(e) => setNewMedication(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          addToArray('medications', newMedication);
                          setNewMedication('');
                        }
                      }}
                    />
                    <Button
                      type="button"
                      onClick={() => {
                        addToArray('medications', newMedication);
                        setNewMedication('');
                      }}
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  {formData.medications.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {formData.medications.map(medication => (
                        <Badge key={medication} variant="outline" className="flex items-center gap-1">
                          {medication}
                          <X
                            className="h-3 w-3 cursor-pointer"
                            onClick={() => removeFromArray('medications', medication)}
                          />
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Allergies */}
              <Card>
                <CardHeader>
                  <CardTitle>Allergies</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add allergy..."
                      value={newAllergy}
                      onChange={(e) => setNewAllergy(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          addToArray('allergies', newAllergy);
                          setNewAllergy('');
                        }
                      }}
                    />
                    <Button
                      type="button"
                      onClick={() => {
                        addToArray('allergies', newAllergy);
                        setNewAllergy('');
                      }}
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  {formData.allergies.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {formData.allergies.map(allergy => (
                        <Badge key={allergy} variant="destructive" className="flex items-center gap-1">
                          {allergy}
                          <X
                            className="h-3 w-3 cursor-pointer"
                            onClick={() => removeFromArray('allergies', allergy)}
                          />
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Other Medical Conditions */}
              <Card>
                <CardHeader>
                  <CardTitle>Other Medical Conditions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add condition..."
                      value={newCondition}
                      onChange={(e) => setNewCondition(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          addToArray('otherConditions', newCondition);
                          setNewCondition('');
                        }
                      }}
                    />
                    <Button
                      type="button"
                      onClick={() => {
                        addToArray('otherConditions', newCondition);
                        setNewCondition('');
                      }}
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  {formData.otherConditions.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {formData.otherConditions.map(condition => (
                        <Badge key={condition} variant="outline" className="flex items-center gap-1">
                          {condition}
                          <X
                            className="h-3 w-3 cursor-pointer"
                            onClick={() => removeFromArray('otherConditions', condition)}
                          />
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Previous Treatments */}
              <Card>
                <CardHeader>
                  <CardTitle>Previous Treatments</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {treatmentOptions.map(treatment => (
                      <div key={treatment} className="flex items-center space-x-2">
                        <Checkbox
                          id={`treatment-${treatment}`}
                          checked={formData.previousTreatments.includes(treatment)}
                          onCheckedChange={() => handleArrayToggle('previousTreatments', treatment)}
                        />
                        <Label htmlFor={`treatment-${treatment}`} className="text-sm">
                          {treatment}
                        </Label>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Additional Information */}
              <Card>
                <CardHeader>
                  <CardTitle>Additional Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="familyHistory">Family History</Label>
                    <Textarea
                      id="familyHistory"
                      placeholder="Any family history of IBS or digestive issues..."
                      value={formData.familyHistory}
                      onChange={(e) => handleInputChange('familyHistory', e.target.value)}
                      rows={3}
                    />
                  </div>
                  <div>
                    <Label htmlFor="doctorNotes">Doctor's Notes</Label>
                    <Textarea
                      id="doctorNotes"
                      placeholder="Any additional notes from your healthcare provider..."
                      value={formData.doctorNotes}
                      onChange={(e) => handleInputChange('doctorNotes', e.target.value)}
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