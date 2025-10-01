'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useRouter } from 'next/navigation';
// import { useAuth } from '@/hooks/useAuth';
import { apiService } from '@/lib/api';
import { SymptomLog } from '@ibs-wellness/shared-types';
import { 
  User, 
  Heart, 
  Utensils, 
  Activity, 
  Target, 
  FileText,
  Edit,
  Calendar,
  Phone,
  Mail,
  MapPin,
  Stethoscope,
  Pill,
  AlertTriangle,
  Clock,
  Dumbbell,
  Moon,
  Zap,
  Coffee,
  Apple,
  Shield,
  Bell,
  Settings,
  TrendingUp,
  RefreshCw,
  Plus,
  Star,
  ThumbsUp,
  ThumbsDown,
  ChefHat
} from 'lucide-react';

interface ProfileDataDisplayProps {
  className?: string;
}

// Extended interface for API response that includes symptom_name
interface SymptomLogResponse {
  id: number;
  symptom_id: number;
  symptom_name: string;
  severity: string;
  logged_at: string;
  duration_minutes?: number;
  notes?: string;
  bristol_stool_type?: string;
  bowel_movement_frequency?: number;
  pain_location?: string;
  pain_type?: string;
  stress_level?: number;
  sleep_quality?: number;
  exercise_minutes?: number;
  potential_triggers?: string;
  created_at: string;
}

interface ProfileData {
  basicInfo?: any;
  medicalHistory?: any;
  dietaryPreferences?: any;
  lifestyleFactors?: any;
  goalsPreferences?: any;
  initialSymptomLog?: {
    data?: SymptomLogResponse[];
  } | null;
}

export function ProfileDataDisplay({ className = "" }: ProfileDataDisplayProps) {
  const router = useRouter();
  // const { user } = useAuth();
  const [profileData, setProfileData] = useState<ProfileData>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProfileData();
  }, []);

  const loadProfileData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No access token found');
      }

      const apiUrl = process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000';
      
      // Load data from all profile sections
      const [basicInfo, medicalHistory, dietaryPreferences, lifestyleFactors, goalsPreferences, initialSymptomLog] = await Promise.allSettled([
        fetch(`${apiUrl}/api/v1/profile/basic-info`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }).then(res => res.ok ? res.json() : null),
        
        fetch(`${apiUrl}/api/v1/profile/medical-history`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }).then(res => res.ok ? res.json() : null),
        
        fetch(`${apiUrl}/api/v1/profile/dietary-preferences`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }).then(res => res.ok ? res.json() : null),
        
        fetch(`${apiUrl}/api/v1/profile/lifestyle-factors`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }).then(res => res.ok ? res.json() : null),
        
        fetch(`${apiUrl}/api/v1/profile/goals-preferences`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }).then(res => res.ok ? res.json() : null),
        
        apiService.getInitialSymptomLogs().then(data => data ? { data } : null)
      ]);

      setProfileData({
        basicInfo: basicInfo.status === 'fulfilled' ? basicInfo.value : null,
        medicalHistory: medicalHistory.status === 'fulfilled' ? medicalHistory.value : null,
        dietaryPreferences: dietaryPreferences.status === 'fulfilled' ? dietaryPreferences.value : null,
        lifestyleFactors: lifestyleFactors.status === 'fulfilled' ? lifestyleFactors.value : null,
        goalsPreferences: goalsPreferences.status === 'fulfilled' ? goalsPreferences.value : null,
        initialSymptomLog: initialSymptomLog.status === 'fulfilled' ? initialSymptomLog.value : null
      });
    } catch (error) {
      console.error('Failed to load profile data:', error);
      setError('Failed to load profile data');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Not specified';
    return new Date(dateString).toLocaleDateString();
  };

  const formatArray = (array: string[] | null) => {
    if (!array || array.length === 0) return 'None specified';
    return array.join(', ');
  };

  const renderBasicInfo = () => {
    const data = profileData.basicInfo;
    if (!data) return <p className="text-gray-500">No basic information available</p>;

    return (
      <div className="space-y-6">
        {/* Personal Information */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <User className="h-5 w-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Personal Information</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="text-sm font-medium text-gray-700">Full Name</label>
              <p className="mt-1 text-sm text-gray-900">{data.first_name} {data.last_name}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Email Address</label>
              <div className="flex items-center mt-1">
                <Mail className="h-4 w-4 text-gray-400 mr-2" />
                <p className="text-sm text-gray-900">{data.email}</p>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Phone Number</label>
              <div className="flex items-center mt-1">
                <Phone className="h-4 w-4 text-gray-400 mr-2" />
                <p className="text-sm text-gray-900">{data.phone_number || 'Not provided'}</p>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Date of Birth</label>
              <div className="flex items-center mt-1">
                <Calendar className="h-4 w-4 text-gray-400 mr-2" />
                <p className="text-sm text-gray-900">{formatDate(data.date_of_birth)}</p>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Gender</label>
              <p className="mt-1 text-sm text-gray-900">{data.gender || 'Not specified'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Age</label>
              <p className="mt-1 text-sm text-gray-900">
                {data.date_of_birth 
                  ? new Date().getFullYear() - new Date(data.date_of_birth).getFullYear() 
                  : 'Not calculated'} years
              </p>
            </div>
          </div>
        </div>

        {/* Physical Information */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Activity className="h-5 w-5 text-green-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Physical Information</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="text-sm font-medium text-gray-700">Height</label>
              <p className="mt-1 text-sm text-gray-900">
                {data.height_cm ? `${data.height_cm} cm` : 'Not provided'}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Weight</label>
              <p className="mt-1 text-sm text-gray-900">
                {data.weight_kg ? `${data.weight_kg} kg` : 'Not provided'}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">BMI</label>
              <p className="mt-1 text-sm text-gray-900">
                {data.height_cm && data.weight_kg 
                  ? ((data.weight_kg / Math.pow(data.height_cm / 100, 2)).toFixed(1))
                  : 'Not calculated'}
              </p>
            </div>
          </div>
        </div>

        {/* Emergency Contact */}
        {(data.emergency_contact_name || data.emergency_contact_phone) && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <AlertTriangle className="h-5 w-5 text-red-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Emergency Contact</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="text-sm font-medium text-gray-700">Contact Name</label>
                <p className="mt-1 text-sm text-gray-900">
                  {data.emergency_contact_name || 'Not provided'}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Contact Phone</label>
                <div className="flex items-center mt-1">
                  <Phone className="h-4 w-4 text-gray-400 mr-2" />
                  <p className="text-sm text-gray-900">
                    {data.emergency_contact_phone || 'Not provided'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderMedicalHistory = () => {
    const data = profileData.medicalHistory;
    if (!data) return <p className="text-gray-500">No medical history available</p>;

    return (
      <div className="space-y-6">
        {/* IBS Information */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Stethoscope className="h-5 w-5 text-red-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">IBS Information</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="text-sm font-medium text-gray-700">IBS Type</label>
              <p className="mt-1 text-sm text-gray-900">
                {data.ibs_type || 'Not specified'}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Diagnosis Date</label>
              <div className="flex items-center mt-1">
                <Calendar className="h-4 w-4 text-gray-400 mr-2" />
                <p className="text-sm text-gray-900">
                  {formatDate(data.diagnosis_date)}
                </p>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Severity Level</label>
              <div className="mt-1">
                <Badge variant={
                  data.severity_level === 'severe' ? 'destructive' :
                  data.severity_level === 'moderate' ? 'secondary' : 'default'
                }>
                  {data.severity_level || 'Not assessed'}
                </Badge>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Symptom Frequency</label>
              <p className="mt-1 text-sm text-gray-900">
                {data.symptom_frequency || 'Not tracked'}
              </p>
            </div>
          </div>
        </div>

        {/* Known Triggers */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <AlertTriangle className="h-5 w-5 text-orange-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Known Triggers</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Food Triggers</label>
              <div className="mt-2 flex flex-wrap gap-2">
                 {data.known_triggers && data.known_triggers.length > 0 ? (
                   data.known_triggers.map((trigger: string, index: number) => (
                     <Badge key={index} variant="outline" className="bg-red-50 text-red-700 border-red-200">
                       {trigger}
                     </Badge>
                   ))
                 ) : (
                   <p className="text-sm text-gray-500">No triggers identified yet</p>
                 )}
               </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Environmental Triggers</label>
              <p className="mt-1 text-sm text-gray-900">
                {data.environmental_triggers || 'None identified'}
              </p>
            </div>
          </div>
        </div>

        {/* Common Symptoms */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Heart className="h-5 w-5 text-pink-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Common Symptoms</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
             {data.common_symptoms && data.common_symptoms.length > 0 ? (
               data.common_symptoms.map((symptom: string, index: number) => (
                 <div key={index} className="flex items-center p-3 bg-blue-50 rounded-lg">
                   <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                   <span className="text-sm text-blue-900">{symptom}</span>
                 </div>
               ))
             ) : (
               <p className="text-sm text-gray-500 col-span-full">No symptoms recorded yet</p>
             )}
           </div>
        </div>

        {/* Current Medications */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Pill className="h-5 w-5 text-green-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Current Medications</h3>
          </div>
          <div className="space-y-3">
             {data.current_medications && data.current_medications.length > 0 ? (
               data.current_medications.map((medication: any, index: number) => (
                 <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                   <div>
                     <p className="font-medium text-green-900">{medication.name || medication}</p>
                     {typeof medication === 'object' && medication.dosage && (
                       <p className="text-sm text-green-700">Dosage: {medication.dosage}</p>
                     )}
                     {typeof medication === 'object' && medication.frequency && (
                       <p className="text-sm text-green-700">Frequency: {medication.frequency}</p>
                     )}
                   </div>
                   {typeof medication === 'object' && medication.prescribed_date && (
                     <span className="text-xs text-green-600">
                       Since {formatDate(medication.prescribed_date)}
                     </span>
                   )}
                 </div>
               ))
             ) : (
               <p className="text-sm text-gray-500">No medications currently recorded</p>
             )}
           </div>
        </div>

        {/* Medical Notes */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <FileText className="h-5 w-5 text-indigo-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Medical Notes</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Doctor's Notes</label>
              <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-900">
                  {data.medical_notes || 'No medical notes available'}
                </p>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Additional Health Conditions</label>
              <div className="mt-2">
                 {data.other_conditions && data.other_conditions.length > 0 ? (
                   <div className="flex flex-wrap gap-2">
                     {data.other_conditions.map((condition: string, index: number) => (
                       <Badge key={index} variant="secondary">
                         {condition}
                       </Badge>
                     ))}
                   </div>
                 ) : (
                   <p className="text-sm text-gray-500">No additional conditions reported</p>
                 )}
               </div>
            </div>
          </div>
        </div>

        {/* Healthcare Provider */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <User className="h-5 w-5 text-purple-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Healthcare Provider</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="text-sm font-medium text-gray-700">Primary Doctor</label>
              <p className="mt-1 text-sm text-gray-900">
                {data.primary_doctor || 'Not specified'}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Specialist</label>
              <p className="mt-1 text-sm text-gray-900">
                {data.specialist || 'Not specified'}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Last Appointment</label>
              <div className="flex items-center mt-1">
                <Calendar className="h-4 w-4 text-gray-400 mr-2" />
                <p className="text-sm text-gray-900">
                  {data.last_appointment ? formatDate(data.last_appointment) : 'Not recorded'}
                </p>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Next Appointment</label>
              <div className="flex items-center mt-1">
                <Calendar className="h-4 w-4 text-gray-400 mr-2" />
                <p className="text-sm text-gray-900">
                  {data.next_appointment ? formatDate(data.next_appointment) : 'Not scheduled'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderDietaryPreferences = () => {
    const data = profileData.dietaryPreferences;
    if (!data) return <p className="text-gray-500">No dietary preferences available</p>;

    return (
      <div className="space-y-6">
        {/* Dietary Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div className="flex items-center gap-3 mb-2">
              <Utensils className="h-5 w-5 text-blue-600" />
              <h4 className="font-medium text-blue-800">Meal Pattern</h4>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-blue-700">Meals per Day:</span>
                <span className="font-medium text-blue-900">{data.mealsPerDay || 3}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-blue-700">Meal Timing:</span>
                <span className="font-medium text-blue-900">{data.mealTiming || 'Regular'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-blue-700">Snacking:</span>
                <span className="font-medium text-blue-900">{data.snackingHabits || 'Moderate'}</span>
              </div>
            </div>
          </div>

          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <div className="flex items-center gap-3 mb-2">
              <Coffee className="h-5 w-5 text-green-600" />
              <h4 className="font-medium text-green-800">Hydration & Intake</h4>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-green-700">Water Intake:</span>
                <span className="font-medium text-green-900">{data.waterIntake ? `${data.waterIntake}L` : '2.5L'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-green-700">Caffeine:</span>
                <span className="font-medium text-green-900">{data.caffeineIntake || 'Moderate'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-green-700">Alcohol:</span>
                <span className="font-medium text-green-900">{data.alcoholConsumption || 'Occasional'}</span>
              </div>
            </div>
          </div>

          <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
            <div className="flex items-center gap-3 mb-2">
              <ChefHat className="h-5 w-5 text-purple-600" />
              <h4 className="font-medium text-purple-800">Cooking Habits</h4>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-purple-700">Cooking:</span>
                <span className="font-medium text-purple-900">{data.cookingFrequency || 'Often'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-purple-700">Eating Out:</span>
                <span className="font-medium text-purple-900">{data.eatingOutFrequency || 'Sometimes'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-purple-700">Budget:</span>
                <span className="font-medium text-purple-900">{data.foodBudget || 'Moderate'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Dietary Restrictions & Allergies */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-red-50 p-4 rounded-lg border border-red-200">
            <div className="flex items-center gap-3 mb-3">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <h4 className="font-medium text-red-800">Dietary Restrictions</h4>
            </div>
            {data.dietaryRestrictions && data.dietaryRestrictions.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {data.dietaryRestrictions.map((restriction: string, index: number) => (
                  <Badge key={index} variant="destructive" className="bg-red-100 text-red-800 border-red-300">
                    {restriction}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-sm text-red-600">No dietary restrictions reported</p>
            )}
          </div>

          <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
            <div className="flex items-center gap-3 mb-3">
              <Shield className="h-5 w-5 text-orange-600" />
              <h4 className="font-medium text-orange-800">Food Allergies</h4>
            </div>
            {data.foodAllergies && data.foodAllergies.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {data.foodAllergies.map((allergy: string, index: number) => (
                  <Badge key={index} variant="secondary" className="bg-orange-100 text-orange-800 border-orange-300">
                    {allergy}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-sm text-orange-600">No food allergies reported</p>
            )}
          </div>
        </div>

        {/* Preferred Diets & Food Preferences */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <div className="flex items-center gap-3 mb-3">
              <Heart className="h-5 w-5 text-green-600" />
              <h4 className="font-medium text-green-800">Preferred Diets</h4>
            </div>
            {data.preferredDiets && data.preferredDiets.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {data.preferredDiets.map((diet: string, index: number) => (
                  <Badge key={index} variant="secondary" className="bg-green-100 text-green-800 border-green-300">
                    {diet}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-sm text-green-600">No specific diet preferences</p>
            )}
          </div>

          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <div className="flex items-center gap-3 mb-3">
              <Star className="h-5 w-5 text-yellow-600" />
              <h4 className="font-medium text-yellow-800">Supplements</h4>
            </div>
            {data.supplementsUsed && data.supplementsUsed.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {data.supplementsUsed.map((supplement: string, index: number) => (
                  <Badge key={index} variant="outline" className="bg-yellow-100 text-yellow-800 border-yellow-300">
                    {supplement}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-sm text-yellow-600">No supplements currently used</p>
            )}
          </div>
        </div>

        {/* Food Preferences */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-emerald-50 p-4 rounded-lg border border-emerald-200">
            <div className="flex items-center gap-3 mb-3">
              <ThumbsUp className="h-5 w-5 text-emerald-600" />
              <h4 className="font-medium text-emerald-800">Favorite Foods</h4>
            </div>
            {data.favoritefoods && data.favoritefoods.length > 0 ? (
              <div className="space-y-1">
                {data.favoritefoods.slice(0, 5).map((food: string, index: number) => (
                  <div key={index} className="flex items-center text-sm text-emerald-700">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full mr-2"></div>
                    {food}
                  </div>
                ))}
                {data.favoritefoods.length > 5 && (
                  <p className="text-xs text-emerald-600 mt-2">+{data.favoritefoods.length - 5} more</p>
                )}
              </div>
            ) : (
              <p className="text-sm text-emerald-600">No favorite foods listed</p>
            )}
          </div>

          <div className="bg-red-50 p-4 rounded-lg border border-red-200">
            <div className="flex items-center gap-3 mb-3">
              <ThumbsDown className="h-5 w-5 text-red-600" />
              <h4 className="font-medium text-red-800">Disliked Foods</h4>
            </div>
            {data.dislikedFoods && data.dislikedFoods.length > 0 ? (
              <div className="space-y-1">
                {data.dislikedFoods.slice(0, 5).map((food: string, index: number) => (
                  <div key={index} className="flex items-center text-sm text-red-700">
                    <div className="w-2 h-2 bg-red-500 rounded-full mr-2"></div>
                    {food}
                  </div>
                ))}
                {data.dislikedFoods.length > 5 && (
                  <p className="text-xs text-red-600 mt-2">+{data.dislikedFoods.length - 5} more</p>
                )}
              </div>
            ) : (
              <p className="text-sm text-red-600">No disliked foods listed</p>
            )}
          </div>
        </div>

        {/* Special Notes */}
        {data.specialNotes && (
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <div className="flex items-center gap-3 mb-2">
              <FileText className="h-5 w-5 text-gray-600" />
              <h4 className="font-medium text-gray-800">Special Notes</h4>
            </div>
            <p className="text-sm text-gray-700">{data.specialNotes}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t border-gray-200">
          <Button variant="outline" size="sm" className="flex items-center gap-2">
            <Edit className="h-4 w-4" />
            Edit Preferences
          </Button>
          <Button variant="outline" size="sm" className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Add Food Item
          </Button>
        </div>
      </div>
    );
  };

  const renderLifestyleFactors = () => {
    const data = profileData.lifestyleFactors;
    if (!data) return <p className="text-gray-500">No lifestyle factors available</p>;

    return (
      <div className="space-y-6">
        {/* Activity & Exercise Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
            <div className="flex items-center gap-3 mb-2">
              <Activity className="h-5 w-5 text-purple-600" />
              <h4 className="font-medium text-purple-800">Physical Activity</h4>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-purple-700">Exercise Frequency:</span>
                <span className="font-medium text-purple-900">{data.exerciseFrequency || 'Moderate'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-purple-700">Activity Level:</span>
                <span className="font-medium text-purple-900">{data.activityLevel || 'Active'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-purple-700">Duration:</span>
                <span className="font-medium text-purple-900">{data.exerciseDuration || '30-45 min'}</span>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div className="flex items-center gap-3 mb-2">
              <Heart className="h-5 w-5 text-blue-600" />
              <h4 className="font-medium text-blue-800">Sleep & Recovery</h4>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-blue-700">Sleep Hours:</span>
                <span className="font-medium text-blue-900">{data.sleepHours || 7.5}h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-blue-700">Sleep Quality:</span>
                <span className="font-medium text-blue-900">{data.sleepQuality || 7}/10</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-blue-700">Bedtime:</span>
                <span className="font-medium text-blue-900">{data.bedtime || '10:30 PM'}</span>
              </div>
            </div>
          </div>

          <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
            <div className="flex items-center gap-3 mb-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              <h4 className="font-medium text-orange-800">Stress & Mental Health</h4>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-orange-700">Stress Level:</span>
                <span className="font-medium text-orange-900">{data.stressLevel || 4}/10</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-orange-700">Work-Life Balance:</span>
                <span className="font-medium text-orange-900">{data.workLifeBalance || 'Good'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-orange-700">Mood:</span>
                <span className="font-medium text-orange-900">{data.overallMood || 'Positive'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Exercise Types & Stress Management */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <div className="flex items-center gap-3 mb-3">
              <Activity className="h-5 w-5 text-green-600" />
              <h4 className="font-medium text-green-800">Exercise Types</h4>
            </div>
            {data.exerciseTypes && data.exerciseTypes.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {data.exerciseTypes.map((exercise: string, index: number) => (
                  <Badge key={index} variant="secondary" className="bg-green-100 text-green-800 border-green-300">
                    {exercise}
                  </Badge>
                ))}
              </div>
            ) : (
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary" className="bg-green-100 text-green-800 border-green-300">Walking</Badge>
                <Badge variant="secondary" className="bg-green-100 text-green-800 border-green-300">Yoga</Badge>
                <Badge variant="secondary" className="bg-green-100 text-green-800 border-green-300">Swimming</Badge>
              </div>
            )}
          </div>

          <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
            <div className="flex items-center gap-3 mb-3">
              <Heart className="h-5 w-5 text-indigo-600" />
              <h4 className="font-medium text-indigo-800">Stress Management</h4>
            </div>
            {data.stressManagement && data.stressManagement.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {data.stressManagement.map((method: string, index: number) => (
                  <Badge key={index} variant="secondary" className="bg-indigo-100 text-indigo-800 border-indigo-300">
                    {method}
                  </Badge>
                ))}
              </div>
            ) : (
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary" className="bg-indigo-100 text-indigo-800 border-indigo-300">Meditation</Badge>
                <Badge variant="secondary" className="bg-indigo-100 text-indigo-800 border-indigo-300">Deep Breathing</Badge>
                <Badge variant="secondary" className="bg-indigo-100 text-indigo-800 border-indigo-300">Journaling</Badge>
              </div>
            )}
          </div>
        </div>

        {/* Work & Social Factors */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <div className="flex items-center gap-3 mb-3">
              <Coffee className="h-5 w-5 text-yellow-600" />
              <h4 className="font-medium text-yellow-800">Work Environment</h4>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-yellow-700">Work Schedule:</span>
                <span className="font-medium text-yellow-900">{data.workSchedule || 'Regular Hours'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-yellow-700">Work Stress:</span>
                <span className="font-medium text-yellow-900">{data.workStress || 'Moderate'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-yellow-700">Remote Work:</span>
                <span className="font-medium text-yellow-900">{data.remoteWork || 'Hybrid'}</span>
              </div>
            </div>
          </div>

          <div className="bg-pink-50 p-4 rounded-lg border border-pink-200">
            <div className="flex items-center gap-3 mb-3">
              <Heart className="h-5 w-5 text-pink-600" />
              <h4 className="font-medium text-pink-800">Social & Support</h4>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-pink-700">Social Activity:</span>
                <span className="font-medium text-pink-900">{data.socialActivity || 'Regular'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-pink-700">Support System:</span>
                <span className="font-medium text-pink-900">{data.supportSystem || 'Strong'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-pink-700">Family Support:</span>
                <span className="font-medium text-pink-900">{data.familySupport || 'Excellent'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Habits & Routines */}
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3 mb-3">
            <FileText className="h-5 w-5 text-gray-600" />
            <h4 className="font-medium text-gray-800">Daily Habits & Routines</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Morning Routine</p>
              <div className="space-y-1">
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                  Wake up at {data.wakeUpTime || '7:00 AM'}
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                  Morning exercise: {data.morningExercise || 'Light stretching'}
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                  Breakfast timing: {data.breakfastTime || '8:00 AM'}
                </div>
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Evening Routine</p>
              <div className="space-y-1">
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                  Dinner time: {data.dinnerTime || '7:00 PM'}
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                  Wind down: {data.windDownActivity || 'Reading'}
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                  Screen time limit: {data.screenTimeLimit || '9:00 PM'}
                </div>
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Health Habits</p>
              <div className="space-y-1">
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                  Hydration goal: {data.hydrationGoal || '8 glasses/day'}
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                  Meditation: {data.meditationFrequency || 'Daily, 10 min'}
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                  Symptom tracking: {data.symptomTracking || 'Daily'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t border-gray-200">
          <Button variant="outline" size="sm" className="flex items-center gap-2">
            <Edit className="h-4 w-4" />
            Update Lifestyle
          </Button>
          <Button variant="outline" size="sm" className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Add Activity
          </Button>
        </div>
      </div>
    );
  };

  const renderGoalsPreferences = () => {
    const data = profileData.goalsPreferences;
    if (!data) return <p className="text-gray-500">No goals and preferences available</p>;

    return (
      <div className="space-y-4">
        {data.health_goals && data.health_goals.length > 0 && (
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="font-medium text-green-800 mb-2">Health Goals</h4>
            <p className="text-green-700">{formatArray(data.health_goals)}</p>
          </div>
        )}
        
        {data.symptom_management_goals && data.symptom_management_goals.length > 0 && (
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h4 className="font-medium text-blue-800 mb-2">Symptom Management Goals</h4>
            <p className="text-blue-700">{formatArray(data.symptom_management_goals)}</p>
          </div>
        )}
        
        {data.notification_settings && (
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h4 className="font-medium text-gray-800 mb-2">Notification Preferences</h4>
            <div className="space-y-2">
              {Object.entries(data.notification_settings).map(([key, value]) => (
                <div key={key} className="flex justify-between items-center">
                  <span className="text-gray-700 capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                  <Badge variant={value ? "default" : "secondary"}>
                    {value ? 'Enabled' : 'Disabled'}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderInitialSymptomLog = () => {
    const data: SymptomLogResponse[] = profileData.initialSymptomLog?.data || [];
    
    // If no data is available, show a message
    if (!data || data.length === 0) {
      return (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Recent Symptom Logs</h3>
              <p className="text-sm text-gray-600">No symptom logs found</p>
            </div>
            <Button 
              onClick={() => router.push('/dashboard/log-symptoms')}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Log New Symptoms
            </Button>
          </div>
          
          <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <h4 className="text-lg font-medium text-gray-700 mb-2">No symptom logs yet</h4>
            <p className="text-sm text-gray-600 mb-4">Start tracking your symptoms to see patterns and insights</p>
            <Button 
              onClick={() => router.push('/dashboard/log-symptoms')}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Log Your First Symptoms
            </Button>
          </div>
        </div>
      );
    }

    const getSeverityColor = (severity: string) => {
      switch (severity.toLowerCase()) {
        case 'mild': return 'text-green-600 bg-green-50';
        case 'moderate': return 'text-yellow-600 bg-yellow-50';
        case 'severe': return 'text-red-600 bg-red-50';
        default: return 'text-gray-600 bg-gray-50';
      }
    };

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Recent Symptom Logs</h3>
            <p className="text-sm text-gray-600">Your latest symptom tracking entries</p>
          </div>
          <Button 
            onClick={() => router.push('/dashboard/log-symptoms')}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Log New Symptoms
          </Button>
        </div>

        <div className="space-y-4">
          {data.map((log) => (
            <div key={log.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <Calendar className="h-4 w-4 text-gray-400" />
                  <span className="text-sm font-medium text-gray-900">
                    {log.logged_at ? new Date(log.logged_at).toLocaleDateString('en-US', { 
                      weekday: 'short', 
                      year: 'numeric', 
                      month: 'short', 
                      day: 'numeric' 
                    }) : 'Date not available'}
                  </span>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(log.severity)}`}>
                  {log.severity}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">Symptom</h4>
                  <div className="flex flex-wrap gap-1">
                    <span className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">
                      {log.symptom_name}
                    </span>
                  </div>
                </div>

                {log.stress_level && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-1">Stress Level</h4>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-orange-500 h-2 rounded-full" 
                          style={{ width: `${(log.stress_level / 10) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-600">{log.stress_level}/10</span>
                    </div>
                  </div>
                )}

                {log.sleep_quality && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-1">Sleep Quality</h4>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-purple-500 h-2 rounded-full" 
                          style={{ width: `${(log.sleep_quality / 10) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-600">{log.sleep_quality}/10</span>
                    </div>
                  </div>
                )}
              </div>

              {log.notes && (
                <div className="mt-3 p-3 bg-gray-50 rounded-md">
                  <h4 className="text-sm font-medium text-gray-700 mb-1">Notes</h4>
                  <p className="text-sm text-gray-600">{log.notes}</p>
                </div>
              )}
              
              {log.duration_minutes && (
                <div className="mt-3 flex items-center text-sm text-gray-600">
                  <Clock className="h-4 w-4 mr-2 text-gray-400" />
                  Duration: {log.duration_minutes} minutes
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="text-center py-4">
          <Button 
            variant="outline"
            onClick={() => router.push('/dashboard/log-symptoms')}
            className="text-blue-600 border-blue-600 hover:bg-blue-50"
          >
            View All Symptom Logs
          </Button>
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <Card className={className}>
        <CardContent className="p-8 text-center">
          <RefreshCw className="h-8 w-8 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading profile data...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardContent className="p-8 text-center">
          <AlertTriangle className="h-8 w-8 text-red-600 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={loadProfileData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Profile Data</span>
          <Button 
            onClick={() => router.push('/profile/settings')}
            variant="outline"
            size="sm"
          >
            <Edit className="h-4 w-4 mr-2" />
            Edit Profile
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="basic" className="w-full">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="basic" className="text-xs">Basic</TabsTrigger>
            <TabsTrigger value="medical" className="text-xs">Medical</TabsTrigger>
            <TabsTrigger value="dietary" className="text-xs">Dietary</TabsTrigger>
            <TabsTrigger value="lifestyle" className="text-xs">Lifestyle</TabsTrigger>
            <TabsTrigger value="goals" className="text-xs">Goals</TabsTrigger>
            <TabsTrigger value="symptoms" className="text-xs">Symptoms</TabsTrigger>
          </TabsList>
          
          <TabsContent value="basic" className="mt-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2 mb-4">
                <User className="h-5 w-5 text-blue-600" />
                <h3 className="text-lg font-semibold">Basic Information</h3>
              </div>
              {renderBasicInfo()}
            </div>
          </TabsContent>
          
          <TabsContent value="medical" className="mt-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2 mb-4">
                <Heart className="h-5 w-5 text-red-600" />
                <h3 className="text-lg font-semibold">Medical History</h3>
              </div>
              {renderMedicalHistory()}
            </div>
          </TabsContent>
          
          <TabsContent value="dietary" className="mt-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2 mb-4">
                <Utensils className="h-5 w-5 text-green-600" />
                <h3 className="text-lg font-semibold">Dietary Preferences</h3>
              </div>
              {renderDietaryPreferences()}
            </div>
          </TabsContent>
          
          <TabsContent value="lifestyle" className="mt-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2 mb-4">
                <Activity className="h-5 w-5 text-purple-600" />
                <h3 className="text-lg font-semibold">Lifestyle Factors</h3>
              </div>
              {renderLifestyleFactors()}
            </div>
          </TabsContent>
          
          <TabsContent value="goals" className="mt-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2 mb-4">
                <Target className="h-5 w-5 text-indigo-600" />
                <h3 className="text-lg font-semibold">Goals & Preferences</h3>
              </div>
              {renderGoalsPreferences()}
            </div>
          </TabsContent>
          
          <TabsContent value="symptoms" className="mt-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2 mb-4">
                <FileText className="h-5 w-5 text-orange-600" />
                <h3 className="text-lg font-semibold">Initial Symptom Log</h3>
              </div>
              {renderInitialSymptomLog()}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}