'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Checkbox } from '@/components/ui/checkbox';
import { apiService } from '@/lib/api';
import { toast } from 'react-hot-toast';
import { MealType } from '@ibs-wellness/shared-types';
import { Clock, Plus, X, Utensils, AlertTriangle } from 'lucide-react';

interface DietLogFormData {
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack' | '';
  food_items: string[];
  portion_size?: string;
  calories?: number;
  notes?: string;
  consumed_at?: string;
  mood_before?: number;
  mood_after?: number;
  food_categories?: string[];
  preparation_method?: string;
  eating_speed?: string;
  hydration_level?: number;
  supplements_taken?: string[];
}

const FOOD_CATEGORIES = [
  'Dairy', 'Gluten', 'High FODMAP', 'Spicy', 'Fatty/Fried', 'Processed', 
  'Raw Vegetables', 'Beans/Legumes', 'Nuts/Seeds', 'Artificial Sweeteners',
  'Caffeine', 'Alcohol', 'High Fiber', 'Citrus', 'Chocolate'
];

const COMMON_SUPPLEMENTS = [
  'Probiotics', 'Digestive Enzymes', 'Fiber Supplement', 'Peppermint Oil',
  'Simethicone', 'Loperamide', 'Psyllium Husk', 'Magnesium'
];

const PREPARATION_METHODS = [
  'Raw', 'Steamed', 'Boiled', 'Grilled', 'Fried', 'Baked', 'Roasted', 'Sautéed'
];

interface DietLogFormProps {
  onSuccess?: () => void;
}

export default function DietLogForm({ onSuccess }: DietLogFormProps) {
  const router = useRouter();
  const [formData, setFormData] = useState<DietLogFormData>({
    meal_type: '',
    food_items: [],
    portion_size: '',
    calories: undefined,
    notes: '',
    consumed_at: new Date().toISOString().slice(0, 16),
    mood_before: 5,
    mood_after: 5,
    food_categories: [],
    preparation_method: '',
    eating_speed: '',
    hydration_level: 5,
    supplements_taken: []
  });

  const [foodItemInput, setFoodItemInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (field: keyof DietLogFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addFoodItem = () => {
    if (foodItemInput.trim()) {
      setFormData(prev => ({
        ...prev,
        food_items: [...prev.food_items, foodItemInput.trim()]
      }));
      setFoodItemInput('');
    }
  };

  const removeFoodItem = (index: number) => {
    setFormData(prev => ({
      ...prev,
      food_items: prev.food_items.filter((_, i) => i !== index)
    }));
  };

  const toggleFoodCategory = (category: string) => {
    setFormData(prev => ({
      ...prev,
      food_categories: prev.food_categories?.includes(category)
        ? prev.food_categories.filter(c => c !== category)
        : [...(prev.food_categories || []), category]
    }));
  };

  const toggleSupplement = (supplement: string) => {
    setFormData(prev => ({
      ...prev,
      supplements_taken: prev.supplements_taken?.includes(supplement)
        ? prev.supplements_taken.filter(s => s !== supplement)
        : [...(prev.supplements_taken || []), supplement]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.meal_type) {
      toast.error('Please select a meal type');
      return;
    }

    if (formData.food_items.length === 0) {
      toast.error('Please add at least one food item');
      return;
    }

    setIsLoading(true);

    try {
      const submitData = {
        meal_type: formData.meal_type as MealType,
        foods: formData.food_items,
        portion_size: formData.portion_size,
        calories: formData.calories || undefined,
        notes: formData.notes,
        consumed_at: formData.consumed_at ? new Date(formData.consumed_at).toISOString() : undefined,
        mood_before: formData.mood_before,
        mood_after: formData.mood_after,
      };

      await apiService.createDietLog(submitData);
      toast.success('Diet log created successfully!');
      
      // Reset form
      setFormData({
        meal_type: '',
        food_items: [],
        portion_size: '',
        calories: undefined,
        notes: '',
        consumed_at: new Date().toISOString().slice(0, 16),
        mood_before: 5,
        mood_after: 5,
        food_categories: [],
        preparation_method: '',
        eating_speed: '',
        hydration_level: 5,
        supplements_taken: []
      });
      setFoodItemInput('');
      
      // Call onSuccess callback if provided, otherwise show success message and reset form
      if (onSuccess) {
        onSuccess();
      } else {
        toast.success('Meal logged successfully! You can log another meal or view your history.');
      }
    } catch (error) {
      console.error('Error creating diet log:', error);
      toast.error('Failed to create diet log. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader className="bg-gradient-to-r from-green-50 to-blue-50">
        <CardTitle className="flex items-center gap-2 text-xl">
          <Utensils className="h-6 w-6 text-green-600" />
          Log Your Meal
        </CardTitle>
        <p className="text-sm text-gray-600">Track your food intake to help identify triggers and patterns</p>
      </CardHeader>
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Meal Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Meal Type */}
            <div className="space-y-2">
              <Label htmlFor="meal_type" className="text-sm font-medium">Meal Type *</Label>
              <Select
                value={formData.meal_type}
                onValueChange={(value: string) => handleInputChange('meal_type', value as 'breakfast' | 'lunch' | 'dinner' | 'snack')}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select meal type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="breakfast">🌅 Breakfast</SelectItem>
                  <SelectItem value="lunch">☀️ Lunch</SelectItem>
                  <SelectItem value="dinner">🌙 Dinner</SelectItem>
                  <SelectItem value="snack">🍎 Snack</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Consumed At */}
            <div className="space-y-2">
              <Label htmlFor="consumed_at" className="text-sm font-medium flex items-center gap-1">
                <Clock className="h-4 w-4" />
                When did you eat this?
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

          {/* Food Items */}
          <div className="space-y-4">
            <Label htmlFor="food_items" className="text-sm font-medium">Food Items *</Label>
            <div className="flex gap-2">
              <Input
                id="food_items"
                value={foodItemInput}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFoodItemInput(e.target.value)}
                placeholder="Enter a food item (e.g., grilled chicken, brown rice)"
                onKeyPress={(e: React.KeyboardEvent) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addFoodItem();
                  }
                }}
                className="flex-1"
              />
              <Button type="button" onClick={addFoodItem} variant="outline" size="sm">
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            {formData.food_items.length > 0 && (
              <div className="flex flex-wrap gap-2 p-4 bg-gray-50 rounded-lg">
                {formData.food_items.map((item, index) => (
                  <div
                    key={index}
                    className="bg-white border border-gray-200 px-3 py-2 rounded-full text-sm flex items-center gap-2 shadow-sm"
                  >
                    {item}
                    <button
                      type="button"
                      onClick={() => removeFoodItem(index)}
                      className="text-red-500 hover:text-red-700 ml-1"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Food Categories & Triggers */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-500" />
              <Label className="text-sm font-medium">Potential Trigger Categories</Label>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
              {FOOD_CATEGORIES.map((category) => (
                <div key={category} className="flex items-center space-x-2">
                  <Checkbox
                    id={category}
                    checked={formData.food_categories?.includes(category) || false}
                    onCheckedChange={() => toggleFoodCategory(category)}
                  />
                  <Label htmlFor={category} className="text-xs cursor-pointer">
                    {category}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Meal Details */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Portion Size */}
            <div className="space-y-2">
              <Label htmlFor="portion_size" className="text-sm font-medium">Portion Size</Label>
              <Input
                id="portion_size"
                value={formData.portion_size}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('portion_size', e.target.value)}
                placeholder="e.g., 1 cup, medium bowl"
              />
            </div>

            {/* Preparation Method */}
            <div className="space-y-2">
              <Label htmlFor="preparation_method" className="text-sm font-medium">Preparation Method</Label>
              <Select
                value={formData.preparation_method}
                onValueChange={(value: string) => handleInputChange('preparation_method', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="How was it prepared?" />
                </SelectTrigger>
                <SelectContent>
                  {PREPARATION_METHODS.map((method) => (
                    <SelectItem key={method} value={method}>{method}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Eating Speed */}
            <div className="space-y-2">
              <Label htmlFor="eating_speed" className="text-sm font-medium">Eating Speed</Label>
              <Select
                value={formData.eating_speed}
                onValueChange={(value: string) => handleInputChange('eating_speed', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="How fast did you eat?" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="very_slow">Very Slow</SelectItem>
                  <SelectItem value="slow">Slow</SelectItem>
                  <SelectItem value="normal">Normal</SelectItem>
                  <SelectItem value="fast">Fast</SelectItem>
                  <SelectItem value="very_fast">Very Fast</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Calories */}
          <div className="space-y-2">
            <Label htmlFor="calories" className="text-sm font-medium">Estimated Calories</Label>
            <Input
              id="calories"
              type="number"
              min="0"
              max="5000"
              value={formData.calories || ''}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('calories', e.target.value ? parseInt(e.target.value) : undefined)}
              placeholder="Enter estimated calories"
              className="w-full md:w-48"
            />
          </div>

          {/* Mood Tracking */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Mood Before */}
            <div className="space-y-3">
              <Label htmlFor="mood_before" className="text-sm font-medium">Mood Before Eating</Label>
              <div className="px-3 py-4 bg-blue-50 rounded-lg">
                <Slider
                  value={[formData.mood_before || 5]}
                  onValueChange={(value: number[]) => handleInputChange('mood_before', value[0])}
                  max={10}
                  min={1}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-2">
                  <span>😞 Very Bad</span>
                  <span>😐 Neutral</span>
                  <span>😊 Excellent</span>
                </div>
                <div className="text-center mt-2 font-medium text-blue-700">
                  Score: {formData.mood_before}/10
                </div>
              </div>
            </div>

            {/* Mood After */}
            <div className="space-y-3">
              <Label htmlFor="mood_after" className="text-sm font-medium">Mood After Eating</Label>
              <div className="px-3 py-4 bg-green-50 rounded-lg">
                <Slider
                  value={[formData.mood_after || 5]}
                  onValueChange={(value: number[]) => handleInputChange('mood_after', value[0])}
                  max={10}
                  min={1}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-2">
                  <span>😞 Very Bad</span>
                  <span>😐 Neutral</span>
                  <span>😊 Excellent</span>
                </div>
                <div className="text-center mt-2 font-medium text-green-700">
                  Score: {formData.mood_after}/10
                </div>
              </div>
            </div>
          </div>

          {/* Hydration Level */}
          <div className="space-y-3">
            <Label htmlFor="hydration_level" className="text-sm font-medium">Hydration Level with Meal</Label>
            <div className="px-3 py-4 bg-cyan-50 rounded-lg">
              <Slider
                value={[formData.hydration_level || 5]}
                onValueChange={(value: number[]) => handleInputChange('hydration_level', value[0])}
                max={10}
                min={1}
                step={1}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-2">
                <span>💧 Very Little</span>
                <span>💧💧 Moderate</span>
                <span>💧💧💧 Lots of Water</span>
              </div>
              <div className="text-center mt-2 font-medium text-cyan-700">
                Level: {formData.hydration_level}/10
              </div>
            </div>
          </div>

          {/* Supplements */}
          <div className="space-y-4">
            <Label className="text-sm font-medium">Supplements Taken with Meal</Label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {COMMON_SUPPLEMENTS.map((supplement) => (
                <div key={supplement} className="flex items-center space-x-2">
                  <Checkbox
                    id={supplement}
                    checked={formData.supplements_taken?.includes(supplement) || false}
                    onCheckedChange={() => toggleSupplement(supplement)}
                  />
                  <Label htmlFor={supplement} className="text-xs cursor-pointer">
                    {supplement}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes" className="text-sm font-medium">Additional Notes</Label>
            <Textarea
              id="notes"
              value={formData.notes || ''}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleInputChange('notes', e.target.value)}
              placeholder="Any additional observations about this meal, how you felt, or other relevant details..."
              rows={4}
              className="resize-none"
            />
          </div>

          <Button type="submit" disabled={isLoading} className="w-full py-3 text-lg">
            {isLoading ? 'Logging Meal...' : 'Log Meal'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}