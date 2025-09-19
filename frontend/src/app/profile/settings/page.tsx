'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { ProtectedRoute } from '@/components/protected-route';
import { DashboardHeader } from '@/components/layout/dashboard-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'react-hot-toast';
import { User, Save, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

interface ProfileData {
  first_name: string;
  last_name: string;
  email: string;
  phone_number?: string;
  date_of_birth?: string;
  gender?: string;
  height_cm?: number;
  weight_kg?: number;
  ibs_type?: string;
  diagnosis_date?: string;
  medical_notes?: string;
}

export default function ProfileSettingsPage() {
  const { user, updateProfile } = useAuth();
  const [profileData, setProfileData] = useState<ProfileData>({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    date_of_birth: '',
    gender: '',
    height_cm: undefined,
    weight_kg: undefined,
    ibs_type: '',
    diagnosis_date: '',
    medical_notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);

  useEffect(() => {
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone_number: user.phone_number || '',
        date_of_birth: user.date_of_birth || '',
        gender: user.gender || '',
        height_cm: user.height_cm || undefined,
        weight_kg: user.weight_kg || undefined,
        ibs_type: user.ibs_type || '',
        diagnosis_date: user.diagnosis_date || '',
        medical_notes: ''
      });
      setInitialLoad(false);
    }
  }, [user]);

  const handleInputChange = (field: keyof ProfileData, value: string | number | undefined) => {
    setProfileData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Filter out empty values and convert numbers
      const updateData: Partial<ProfileData> = {};
      
      Object.entries(profileData).forEach(([key, value]) => {
        if (value !== '' && value !== undefined && value !== null) {
          if (key === 'height_cm' || key === 'weight_kg') {
            const numValue = Number(value);
            if (!isNaN(numValue)) {
              (updateData as any)[key] = numValue;
            }
          } else {
            (updateData as any)[key] = value;
          }
        }
      });

      await updateProfile(updateData);
      toast.success('Profile updated successfully!');
    } catch (error) {
      console.error('Failed to update profile:', error);
      toast.error('Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (initialLoad) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50">
          <DashboardHeader />
          <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="animate-pulse space-y-4">
              <div className="h-8 bg-gray-200 rounded w-1/4"></div>
              <div className="h-64 bg-gray-200 rounded"></div>
            </div>
          </main>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader />
        
        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-6">
            <Link 
              href="/dashboard" 
              className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Link>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <User className="h-8 w-8" />
              Profile Settings
            </h1>
            <p className="text-gray-600 mt-2">
              Update your personal information and health profile
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="first_name">First Name</Label>
                    <Input
                      id="first_name"
                      value={profileData.first_name}
                      onChange={(e) => handleInputChange('first_name', e.target.value)}
                      placeholder="Enter your first name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="last_name">Last Name</Label>
                    <Input
                      id="last_name"
                      value={profileData.last_name}
                      onChange={(e) => handleInputChange('last_name', e.target.value)}
                      placeholder="Enter your last name"
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={profileData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    placeholder="Enter your email"
                  />
                </div>
                
                <div>
                  <Label htmlFor="phone_number">Phone Number</Label>
                  <Input
                    id="phone_number"
                    value={profileData.phone_number}
                    onChange={(e) => handleInputChange('phone_number', e.target.value)}
                    placeholder="Enter your phone number"
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="date_of_birth">Date of Birth</Label>
                    <Input
                      id="date_of_birth"
                      type="date"
                      value={profileData.date_of_birth}
                      onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="gender">Gender</Label>
                    <Select 
                      value={profileData.gender} 
                      onValueChange={(value) => handleInputChange('gender', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select gender" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="male">Male</SelectItem>
                        <SelectItem value="female">Female</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                        <SelectItem value="prefer_not_to_say">Prefer not to say</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Health Information */}
            <Card>
              <CardHeader>
                <CardTitle>Health Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="height_cm">Height (cm)</Label>
                    <Input
                      id="height_cm"
                      type="number"
                      value={profileData.height_cm || ''}
                      onChange={(e) => handleInputChange('height_cm', e.target.value ? Number(e.target.value) : undefined)}
                      placeholder="Enter your height in cm"
                    />
                  </div>
                  <div>
                    <Label htmlFor="weight_kg">Weight (kg)</Label>
                    <Input
                      id="weight_kg"
                      type="number"
                      value={profileData.weight_kg || ''}
                      onChange={(e) => handleInputChange('weight_kg', e.target.value ? Number(e.target.value) : undefined)}
                      placeholder="Enter your weight in kg"
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="ibs_type">IBS Type</Label>
                  <Select 
                    value={profileData.ibs_type} 
                    onValueChange={(value) => handleInputChange('ibs_type', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select IBS type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ibs-d">IBS-D (Diarrhea predominant)</SelectItem>
                      <SelectItem value="ibs-c">IBS-C (Constipation predominant)</SelectItem>
                      <SelectItem value="ibs-m">IBS-M (Mixed)</SelectItem>
                      <SelectItem value="ibs-u">IBS-U (Unsubtyped)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="diagnosis_date">Diagnosis Date</Label>
                  <Input
                    id="diagnosis_date"
                    type="date"
                    value={profileData.diagnosis_date}
                    onChange={(e) => handleInputChange('diagnosis_date', e.target.value)}
                  />
                </div>
                
                <div>
                  <Label htmlFor="medical_notes">Additional Medical Notes</Label>
                  <Textarea
                    id="medical_notes"
                    value={profileData.medical_notes}
                    onChange={(e) => handleInputChange('medical_notes', e.target.value)}
                    placeholder="Any additional medical information or notes..."
                    rows={4}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Save Button */}
            <div className="flex justify-end">
              <Button type="submit" disabled={loading} className="min-w-32">
                {loading ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Saving...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <Save className="h-4 w-4" />
                    Save Changes
                  </div>
                )}
              </Button>
            </div>
          </form>
        </main>
      </div>
    </ProtectedRoute>
  );
}