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
import { Slider } from "@/components/ui/slider";
import { Utensils, Save, ArrowLeft, Plus, X } from "lucide-react";
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';

interface DietaryPreferencesData {
  dietaryRestrictions: string[];
  foodAllergies: string[];
  preferredDiets: string[];
  mealsPerDay: number;
  waterIntake: number;
  alcoholConsumption: string;
  caffeineIntake: string;
  cookingFrequency: string;
  eatingOutFrequency: string;
  favoritefoods: string[];
  dislikedFoods: string[];
  supplementsUsed: string[];
  mealTiming: string;
  snackingHabits: string;
  foodBudget: string;
  specialNotes: string;
}

const dietaryRestrictionOptions = [
  'Low FODMAP', 'Gluten-free', 'Dairy-free', 'Lactose-free', 'Vegetarian', 
  'Vegan', 'Pescatarian', 'Keto', 'Paleo', 'Mediterranean', 'Low-carb', 
  'Low-fat', 'High-protein', 'Sugar-free', 'Nut-free'
];

const allergyOptions = [
  'Nuts', 'Shellfish', 'Fish', 'Eggs', 'Dairy', 'Soy', 'Wheat/Gluten',
  'Sesame', 'Sulfites', 'Food dyes', 'Preservatives'
];

const alcoholOptions = [
  { value: 'none', label: 'None' },
  { value: 'occasional', label: 'Occasional (1-2 drinks/week)' },
  { value: 'moderate', label: 'Moderate (3-7 drinks/week)' },
  { value: 'frequent', label: 'Frequent (8+ drinks/week)' }
];

const caffeineOptions = [
  { value: 'none', label: 'None' },
  { value: 'low', label: 'Low (1 cup coffee/day)' },
  { value: 'moderate', label: 'Moderate (2-3 cups/day)' },
  { value: 'high', label: 'High (4+ cups/day)' }
];

const cookingFrequencyOptions = [
  { value: 'daily', label: 'Daily' },
  { value: 'few_times_week', label: 'Few times a week' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'rarely', label: 'Rarely' },
  { value: 'never', label: 'Never' }
];

const eatingOutOptions = [
  { value: 'daily', label: 'Daily' },
  { value: 'few_times_week', label: 'Few times a week' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'rarely', label: 'Rarely' }
];

const mealTimingOptions = [
  { value: 'regular', label: 'Regular meal times' },
  { value: 'irregular', label: 'Irregular meal times' },
  { value: 'intermittent_fasting', label: 'Intermittent fasting' },
  { value: 'grazing', label: 'Frequent small meals' }
];

const snackingOptions = [
  { value: 'none', label: 'No snacking' },
  { value: 'healthy', label: 'Healthy snacks only' },
  { value: 'occasional', label: 'Occasional snacking' },
  { value: 'frequent', label: 'Frequent snacking' }
];

const budgetOptions = [
  { value: 'low', label: 'Low budget' },
  { value: 'moderate', label: 'Moderate budget' },
  { value: 'high', label: 'High budget' },
  { value: 'unlimited', label: 'Budget not a concern' }
];

const commonSupplements = [
  'Probiotics', 'Fiber supplements', 'Digestive enzymes', 'Peppermint oil',
  'Vitamin D', 'B-complex', 'Magnesium', 'Omega-3', 'Iron', 'Calcium'
];

export default function DietaryPreferencesPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [formData, setFormData] = useState<DietaryPreferencesData>({
    dietaryRestrictions: [],
    foodAllergies: [],
    preferredDiets: [],
    mealsPerDay: 3,
    waterIntake: 8,
    alcoholConsumption: '',
    caffeineIntake: '',
    cookingFrequency: '',
    eatingOutFrequency: '',
    favoritefoods: [],
    dislikedFoods: [],
    supplementsUsed: [],
    mealTiming: '',
    snackingHabits: '',
    foodBudget: '',
    specialNotes: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [newFavoriteFood, setNewFavoriteFood] = useState('');
  const [newDislikedFood, setNewDislikedFood] = useState('');

  useEffect(() => {
    if (user) {
      // First try to load from backend API, fallback to user context
      loadDietaryPreferences();
    }
  }, [user]);

  const loadDietaryPreferencesFromUser = () => {
    if (user) {
      // Note: User preferences will be loaded from API since they're not in the User type
      setFormData({
        dietaryRestrictions: [],
        foodAllergies: [],
        preferredDiets: [],
        mealsPerDay: 3,
        waterIntake: 8,
        alcoholConsumption: '',
        caffeineIntake: '',
        cookingFrequency: '',
        eatingOutFrequency: '',
        favoritefoods: [],
        dislikedFoods: [],
        supplementsUsed: [],
        mealTiming: '',
        snackingHabits: '',
        foodBudget: '',
        specialNotes: ''
      });
    }
  };

  const loadDietaryPreferences = async () => {
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
      const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000'}/api/v1/profile/dietary-preferences`, {
        headers,
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        // Transform backend data to form format
        setFormData({
          dietaryRestrictions: data.dietary_restrictions || [],
          foodAllergies: data.food_allergies || [],
          preferredDiets: data.special_diets || [],
          mealsPerDay: data.meal_frequency || 3,
          waterIntake: data.water_intake_goal || 8,
          alcoholConsumption: '',
          caffeineIntake: '',
          cookingFrequency: '',
          eatingOutFrequency: '',
          favoritefoods: data.safe_foods || [],
          dislikedFoods: data.trigger_foods || [],
          supplementsUsed: [],
          mealTiming: '',
          snackingHabits: '',
          foodBudget: '',
          specialNotes: ''
        });
        setHasUnsavedChanges(false);
      } else {
        // Fallback to user context data if API fails
        loadDietaryPreferencesFromUser();
      }
    } catch (error) {
      console.error('Failed to load dietary preferences from API, falling back to user context:', error);
      // Fallback to user context data
      loadDietaryPreferencesFromUser();
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: keyof DietaryPreferencesData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleArrayToggle = (field: keyof DietaryPreferencesData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: (prev[field] as string[]).includes(value)
        ? (prev[field] as string[]).filter(item => item !== value)
        : [...(prev[field] as string[]), value]
    }));
  };

  const addToArray = (field: keyof DietaryPreferencesData, value: string) => {
    if (value.trim() && !(formData[field] as string[]).includes(value.trim())) {
      setFormData(prev => ({
        ...prev,
        [field]: [...(prev[field] as string[]), value.trim()]
      }));
    }
  };

  const removeFromArray = (field: keyof DietaryPreferencesData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: (prev[field] as string[]).filter(item => item !== value)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

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
      
      const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000'}/api/v1/profile/dietary-preferences`, {
        method: 'PUT',
        headers,
        credentials: 'include', // Send both session cookies and Bearer token
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Dietary preferences saved successfully:', result);
        alert('Dietary preferences saved successfully!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save dietary preferences');
      }
    } catch (error) {
      console.error('Failed to save dietary preferences:', error);
      alert(`Failed to save dietary preferences: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50">
          <DashboardHeader title="Dietary Preferences" showBackButton />
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
        <DashboardHeader title="Dietary Preferences" showBackButton />
        
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
                <div className="p-2 bg-green-100 rounded-full">
                  <Utensils className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Dietary Preferences</h1>
                  <p className="text-gray-600">Food preferences, restrictions, and eating habits</p>
                </div>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Dietary Restrictions */}
              <Card>
                <CardHeader>
                  <CardTitle>Dietary Restrictions & Preferences</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {dietaryRestrictionOptions.map(restriction => (
                      <div key={restriction} className="flex items-center space-x-2">
                        <Checkbox
                          id={`restriction-${restriction}`}
                          checked={formData.dietaryRestrictions.includes(restriction)}
                          onCheckedChange={() => handleArrayToggle('dietaryRestrictions', restriction)}
                        />
                        <Label htmlFor={`restriction-${restriction}`} className="text-sm">
                          {restriction}
                        </Label>
                      </div>
                    ))}
                  </div>
                  {formData.dietaryRestrictions.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-4">
                      {formData.dietaryRestrictions.map(restriction => (
                        <Badge key={restriction} variant="secondary" className="flex items-center gap-1">
                          {restriction}
                          <X
                            className="h-3 w-3 cursor-pointer"
                            onClick={() => removeFromArray('dietaryRestrictions', restriction)}
                          />
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Food Allergies */}
              <Card>
                <CardHeader>
                  <CardTitle>Food Allergies</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {allergyOptions.map(allergy => (
                      <div key={allergy} className="flex items-center space-x-2">
                        <Checkbox
                          id={`allergy-${allergy}`}
                          checked={formData.foodAllergies.includes(allergy)}
                          onCheckedChange={() => handleArrayToggle('foodAllergies', allergy)}
                        />
                        <Label htmlFor={`allergy-${allergy}`} className="text-sm">
                          {allergy}
                        </Label>
                      </div>
                    ))}
                  </div>
                  {formData.foodAllergies.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-4">
                      {formData.foodAllergies.map(allergy => (
                        <Badge key={allergy} variant="destructive" className="flex items-center gap-1">
                          {allergy}
                          <X
                            className="h-3 w-3 cursor-pointer"
                            onClick={() => removeFromArray('foodAllergies', allergy)}
                          />
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Eating Habits */}
              <Card>
                <CardHeader>
                  <CardTitle>Eating Habits</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label>Meals per day: {formData.mealsPerDay}</Label>
                      <Slider
                        value={[formData.mealsPerDay]}
                        onValueChange={(value) => handleInputChange('mealsPerDay', value[0])}
                        max={6}
                        min={1}
                        step={1}
                        className="mt-2"
                      />
                    </div>
                    <div>
                      <Label>Water intake (glasses/day): {formData.waterIntake}</Label>
                      <Slider
                        value={[formData.waterIntake]}
                        onValueChange={(value) => handleInputChange('waterIntake', value[0])}
                        max={15}
                        min={1}
                        step={1}
                        className="mt-2"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="alcoholConsumption">Alcohol Consumption</Label>
                      <Select value={formData.alcoholConsumption} onValueChange={(value) => handleInputChange('alcoholConsumption', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select alcohol consumption" />
                        </SelectTrigger>
                        <SelectContent>
                          {alcoholOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="caffeineIntake">Caffeine Intake</Label>
                      <Select value={formData.caffeineIntake} onValueChange={(value) => handleInputChange('caffeineIntake', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select caffeine intake" />
                        </SelectTrigger>
                        <SelectContent>
                          {caffeineOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="cookingFrequency">Cooking Frequency</Label>
                      <Select value={formData.cookingFrequency} onValueChange={(value) => handleInputChange('cookingFrequency', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="How often do you cook?" />
                        </SelectTrigger>
                        <SelectContent>
                          {cookingFrequencyOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="eatingOutFrequency">Eating Out Frequency</Label>
                      <Select value={formData.eatingOutFrequency} onValueChange={(value) => handleInputChange('eatingOutFrequency', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="How often do you eat out?" />
                        </SelectTrigger>
                        <SelectContent>
                          {eatingOutOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="mealTiming">Meal Timing</Label>
                      <Select value={formData.mealTiming} onValueChange={(value) => handleInputChange('mealTiming', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select meal timing pattern" />
                        </SelectTrigger>
                        <SelectContent>
                          {mealTimingOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="snackingHabits">Snacking Habits</Label>
                      <Select value={formData.snackingHabits} onValueChange={(value) => handleInputChange('snackingHabits', value)}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select snacking habits" />
                        </SelectTrigger>
                        <SelectContent>
                          {snackingOptions.map(option => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Food Preferences */}
              <Card>
                <CardHeader>
                  <CardTitle>Food Preferences</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Favorite Foods</Label>
                    <div className="flex gap-2 mt-2">
                      <Input
                        placeholder="Add favorite food..."
                        value={newFavoriteFood}
                        onChange={(e) => setNewFavoriteFood(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            addToArray('favoritefoods', newFavoriteFood);
                            setNewFavoriteFood('');
                          }
                        }}
                      />
                      <Button
                        type="button"
                        onClick={() => {
                          addToArray('favoritefoods', newFavoriteFood);
                          setNewFavoriteFood('');
                        }}
                      >
                        <Plus className="h-4 w-4" />
                      </Button>
                    </div>
                    {formData.favoritefoods.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {formData.favoritefoods.map(food => (
                          <Badge key={food} variant="outline" className="flex items-center gap-1">
                            {food}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('favoritefoods', food)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>

                  <div>
                    <Label>Disliked Foods</Label>
                    <div className="flex gap-2 mt-2">
                      <Input
                        placeholder="Add disliked food..."
                        value={newDislikedFood}
                        onChange={(e) => setNewDislikedFood(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            addToArray('dislikedFoods', newDislikedFood);
                            setNewDislikedFood('');
                          }
                        }}
                      />
                      <Button
                        type="button"
                        onClick={() => {
                          addToArray('dislikedFoods', newDislikedFood);
                          setNewDislikedFood('');
                        }}
                      >
                        <Plus className="h-4 w-4" />
                      </Button>
                    </div>
                    {formData.dislikedFoods.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {formData.dislikedFoods.map(food => (
                          <Badge key={food} variant="secondary" className="flex items-center gap-1">
                            {food}
                            <X
                              className="h-3 w-3 cursor-pointer"
                              onClick={() => removeFromArray('dislikedFoods', food)}
                            />
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Supplements */}
              <Card>
                <CardHeader>
                  <CardTitle>Supplements & Vitamins</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {commonSupplements.map(supplement => (
                      <div key={supplement} className="flex items-center space-x-2">
                        <Checkbox
                          id={`supplement-${supplement}`}
                          checked={formData.supplementsUsed.includes(supplement)}
                          onCheckedChange={() => handleArrayToggle('supplementsUsed', supplement)}
                        />
                        <Label htmlFor={`supplement-${supplement}`} className="text-sm">
                          {supplement}
                        </Label>
                      </div>
                    ))}
                  </div>
                  {formData.supplementsUsed.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-4">
                      {formData.supplementsUsed.map(supplement => (
                        <Badge key={supplement} variant="outline" className="flex items-center gap-1">
                          {supplement}
                          <X
                            className="h-3 w-3 cursor-pointer"
                            onClick={() => removeFromArray('supplementsUsed', supplement)}
                          />
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Additional Information */}
              <Card>
                <CardHeader>
                  <CardTitle>Additional Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="foodBudget">Food Budget</Label>
                    <Select value={formData.foodBudget} onValueChange={(value) => handleInputChange('foodBudget', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select food budget range" />
                      </SelectTrigger>
                      <SelectContent>
                        {budgetOptions.map(option => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="specialNotes">Special Notes</Label>
                    <Textarea
                      id="specialNotes"
                      placeholder="Any additional dietary information, cultural preferences, or special considerations..."
                      value={formData.specialNotes}
                      onChange={(e) => handleInputChange('specialNotes', e.target.value)}
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