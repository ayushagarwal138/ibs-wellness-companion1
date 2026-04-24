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
import { User, Save, ArrowLeft } from "lucide-react";
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { useUserSync } from '@/hooks/useUserSync';
import { toast } from 'react-hot-toast';
import { SyncStatusIndicator } from '@/components/ui/sync-status-indicator';

interface BasicInfoData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  gender: string;
  height_cm?: number;
  weight_kg?: number;
  emergencyContact: string;
  emergencyPhone: string;
}

export default function BasicInfoPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { data: session } = useSession();
  const { syncProfile, syncStatus } = useUserSync();
  const [formData, setFormData] = useState<BasicInfoData>({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    dateOfBirth: '',
    gender: '',
    height_cm: undefined,
    weight_kg: undefined,
    emergencyContact: '',
    emergencyPhone: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  useEffect(() => {
    if (user) {
      // First try to load from backend API, fallback to user context
      loadBasicInfo();
    }
  }, [user]);

  const loadBasicInfoFromUser = () => {
    if (user) {
      setFormData({
        firstName: user.first_name || '',
        lastName: user.last_name || '',
        email: user.email || '',
        phone: user.phone_number || '',
        dateOfBirth: user.date_of_birth || '',
        gender: user.gender || '',
        height_cm: user.height_cm || undefined,
        weight_kg: user.weight_kg || undefined,
        emergencyContact: '',
        emergencyPhone: ''
      });
    }
  };

  const loadBasicInfo = async () => {
    try {
      setIsLoading(true);
      
      // Get token from localStorage for custom auth
      const token = localStorage.getItem('access_token');
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      // Add Authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      // Try to load from backend API first
      const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000'}/api/v1/profile/basic-info`, {
        credentials: 'include',
        headers,
      });
      
      if (response.ok) {
        const data = await response.json();
        // Transform backend data to form format
        setFormData({
          firstName: data.first_name || '',
          lastName: data.last_name || '',
          email: data.email || '',
          phone: data.phone_number || '',
          dateOfBirth: data.date_of_birth || '',
          gender: data.gender || '',
          height_cm: data.height_cm || undefined,
          weight_kg: data.weight_kg || undefined,
          emergencyContact: data.emergency_contact_name || '',
          emergencyPhone: data.emergency_contact_phone || ''
        });
        setHasUnsavedChanges(false);
      } else {
        // Fallback to user context data if API fails
        loadBasicInfoFromUser();
      }
    } catch (error) {
      console.error('Failed to load basic info from API, falling back to user context:', error);
      // Fallback to user context data
      loadBasicInfoFromUser();
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: keyof BasicInfoData, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setHasUnsavedChanges(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      // Get token from localStorage for custom auth
      const token = localStorage.getItem('access_token');
      
      console.log('Authentication token:', token ? 'Present' : 'Missing');
      console.log('User context:', user ? 'Present' : 'Missing');
      
      if (!token) {
        console.error('No authentication token found');
        toast.error('Please log in again to save changes.');
        return;
      }
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      };

      // Convert form data to backend format
      const profileData = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        phone_number: formData.phone,
        date_of_birth: formData.dateOfBirth,
        gender: formData.gender,
        height_cm: formData.height_cm,
        weight_kg: formData.weight_kg,
        emergency_contact_name: formData.emergencyContact,
        emergency_contact_phone: formData.emergencyPhone,
      };

      console.log('Sending profile data:', profileData);
      console.log('Request headers:', headers);

      // Call the backend profile endpoint directly
      const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000'}/api/v1/profile/basic-info`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(profileData),
        credentials: 'include'
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Error:', errorData);
        
        if (response.status === 401) {
          toast.error('Authentication failed. Please log in again.');
          // Optionally redirect to login
          // router.push('/auth/login');
        } else {
          throw new Error(errorData.detail || errorData.message || 'Failed to update profile');
        }
        return;
      }

      const result = await response.json();
      console.log('Success response:', result);
      
      setHasUnsavedChanges(false);
      toast.success('Profile updated successfully!');
      
    } catch (error) {
      console.error('Failed to save basic info:', error);
      
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        toast.error('Network error. Please check your connection and try again.');
        alert('CORS or network error detected. Check browser console for details.');
      } else {
        toast.error(`Failed to save changes: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50">
          <DashboardHeader title="Basic Information" showBackButton />
          <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="animate-pulse space-y-6">
              <div className="h-8 bg-gray-200 rounded w-1/3"></div>
              <div className="space-y-4">
                {[1, 2, 3, 4, 5].map(i => (
                  <div key={i} className="h-12 bg-gray-200 rounded"></div>
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
        <DashboardHeader title="Basic Information" showBackButton />
        
        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
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
                    <User className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900">Basic Information</h1>
                    <p className="text-gray-600">Personal details, age, and contact information</p>
                  </div>
                </div>
              </div>
              
              {/* Sync Status Indicator */}
              <SyncStatusIndicator 
                status={syncStatus}
              />
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Personal Information */}
              <Card>
                <CardHeader>
                  <CardTitle>Personal Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="firstName">First Name *</Label>
                      <Input
                        id="firstName"
                        value={formData.firstName}
                        onChange={(e) => handleInputChange('firstName', e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="lastName">Last Name *</Label>
                      <Input
                        id="lastName"
                        value={formData.lastName}
                        onChange={(e) => handleInputChange('lastName', e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="email">Email Address *</Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="phone">Phone Number</Label>
                      <Input
                        id="phone"
                        type="tel"
                        value={formData.phone}
                        onChange={(e) => handleInputChange('phone', e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="dateOfBirth">Date of Birth *</Label>
                      <Input
                        id="dateOfBirth"
                        type="date"
                        value={formData.dateOfBirth}
                        onChange={(e) => handleInputChange('dateOfBirth', e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="gender">Gender</Label>
                      <Select value={formData.gender} onValueChange={(value) => handleInputChange('gender', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select gender" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="male">Male</SelectItem>
                          <SelectItem value="female">Female</SelectItem>
                          <SelectItem value="non_binary">Non-binary</SelectItem>
                          <SelectItem value="prefer_not_to_say">Prefer not to say</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Physical Information */}
              <Card>
                <CardHeader>
                  <CardTitle>Physical Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="height">Height (cm)</Label>
                      <Input
                        id="height"
                        type="number"
                        value={formData.height_cm || ''}
                        onChange={(e) => handleInputChange('height_cm', e.target.value ? Number(e.target.value) : '')}
                        placeholder="e.g., 170"
                      />
                    </div>
                    <div>
                      <Label htmlFor="weight">Weight (kg)</Label>
                      <Input
                        id="weight"
                        type="number"
                        value={formData.weight_kg || ''}
                        onChange={(e) => handleInputChange('weight_kg', e.target.value ? Number(e.target.value) : '')}
                        placeholder="e.g., 70"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Emergency Contact */}
              <Card>
                <CardHeader>
                  <CardTitle>Emergency Contact</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="emergencyContact">Emergency Contact Name</Label>
                      <Input
                        id="emergencyContact"
                        value={formData.emergencyContact}
                        onChange={(e) => handleInputChange('emergencyContact', e.target.value)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="emergencyPhone">Emergency Contact Phone</Label>
                      <Input
                        id="emergencyPhone"
                        type="tel"
                        value={formData.emergencyPhone}
                        onChange={(e) => handleInputChange('emergencyPhone', e.target.value)}
                      />
                    </div>
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
                  disabled={isSaving || syncStatus.syncing}
                  className="flex items-center gap-2"
                >
                  {(isSaving || syncStatus.syncing) ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      {syncStatus.syncing ? 'Syncing...' : 'Saving...'}
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