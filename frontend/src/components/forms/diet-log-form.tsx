'use client';

import React, { useState, useEffect, useRef } from 'react';
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
import { Clock, Plus, X, Utensils, AlertTriangle, Search } from 'lucide-react';

interface DietLogFormData {
  meal_type: MealType | '';
  foods: string[];
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

interface FoodSuggestion {
  name: string;
  category: string;
  fodmap_level: string;
  is_common_trigger: boolean;
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
    foods: [],
    portion_size: '',
    calories: undefined,
    notes: '',
    consumed_at: new Date().toISOString().slice(0, 16),
    mood_before: 5,
    mood_after: 5,
    food_categories: [],
    preparation_method: '',
    eating_speed: 'normal',
    hydration_level: 5,
    supplements_taken: []
  });

  const [isLoading, setIsLoading] = useState(false);
  const [foodItemInput, setFoodItemInput] = useState('');
  const [suggestions, setSuggestions] = useState<FoodSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  const handleInputChange = (field: keyof DietLogFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Fetch food suggestions
  useEffect(() => {
    const fetchSuggestions = async () => {
      // Always fetch suggestions, even for empty input to show popular foods
      try {
        console.log('Fetching food suggestions for:', foodItemInput.trim());
        const response = await apiService.getFoodSuggestions(foodItemInput.trim());
        console.log('Food suggestions response:', response);
        setSuggestions(response.suggestions || []);
        setShowSuggestions(true);
        setSelectedSuggestionIndex(-1);
      } catch (error: any) {
        console.error('Error fetching food suggestions:', error);
        console.error('Error details:', {
          message: error?.message,
          status: error?.response?.status,
          data: error?.response?.data
        });
        setSuggestions([]);
        setShowSuggestions(false);
        
        // Show user-friendly error message for authentication issues
        if (error?.response?.status === 401 || error?.response?.status === 403) {
          console.warn('Authentication required for food suggestions');
        }
      }
    };

    // Reduce debounce time for faster response and fetch immediately for empty input
    const timeoutId = setTimeout(fetchSuggestions, foodItemInput.trim() ? 150 : 0);
    return () => clearTimeout(timeoutId);
  }, [foodItemInput]);

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const addFoodItem = (foodName?: string) => {
    const itemToAdd = foodName || foodItemInput.trim();
    if (itemToAdd && !formData.foods.includes(itemToAdd)) {
      setFormData(prev => ({
        ...prev,
        foods: [...prev.foods, itemToAdd]
      }));
      setFoodItemInput('');
      setShowSuggestions(false);
      setSelectedSuggestionIndex(-1);
    }
  };

  const handleSuggestionClick = (suggestion: FoodSuggestion) => {
    addFoodItem(suggestion.name);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions || suggestions.length === 0) {
      if (e.key === 'Enter') {
        e.preventDefault();
        addFoodItem();
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedSuggestionIndex >= 0 && suggestions[selectedSuggestionIndex]) {
          handleSuggestionClick(suggestions[selectedSuggestionIndex]);
        } else {
          addFoodItem();
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedSuggestionIndex(-1);
        break;
    }
  };

  const removeFoodItem = (index: number) => {
    setFormData(prev => ({
      ...prev,
      foods: prev.foods.filter((_, i) => i !== index)
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
    
    if (formData.foods.length === 0) {
      toast.error('Please add at least one food item');
      return;
    }

    setIsLoading(true);
    
    try {
      const submitData = {
        meal_type: formData.meal_type,
        foods: formData.foods,
        portion_size: formData.portion_size || undefined,
        calories: formData.calories || undefined,
        notes: formData.notes || undefined,
        consumed_at: formData.consumed_at ? new Date(formData.consumed_at).toISOString() : new Date().toISOString()
      };

      await apiService.createDietLog(submitData);
      
      toast.success('Diet log created successfully!');
      
      // Reset form
      setFormData({
        meal_type: '',
        foods: [],
        portion_size: '',
        calories: undefined,
        notes: '',
        consumed_at: new Date().toISOString().slice(0, 16),
        mood_before: 5,
        mood_after: 5,
        food_categories: [],
        preparation_method: '',
        eating_speed: 'normal',
        hydration_level: 5,
        supplements_taken: []
      });
      
      if (onSuccess) {
        onSuccess();
      } else {
        router.push('/dashboard');
      }
    } catch (error) {
      toast.error('Failed to create diet log. Please try again.');
      console.error('Error creating diet log:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Utensils className="h-5 w-5" />
          Log Your Meal
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Meal Type */}
          <div className="space-y-2">
            <Label htmlFor="meal_type">Meal Type *</Label>
            <Select
              value={formData.meal_type}
              onValueChange={(value) => handleInputChange('meal_type', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select meal type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={MealType.BREAKFAST}>Breakfast</SelectItem>
                <SelectItem value={MealType.LUNCH}>Lunch</SelectItem>
                <SelectItem value={MealType.DINNER}>Dinner</SelectItem>
                <SelectItem value={MealType.SNACK}>Snack</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Consumed At */}
          <div className="space-y-2">
            <Label htmlFor="consumed_at" className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              When did you eat this?
            </Label>
            <Input
              id="consumed_at"
              type="datetime-local"
              value={formData.consumed_at}
              onChange={(e) => handleInputChange('consumed_at', e.target.value)}
              className="w-full"
            />
          </div>

          {/* Food Items with Autocomplete */}
          <div className="space-y-2">
            <Label htmlFor="food_items">Food Items *</Label>
            <div className="relative" ref={suggestionsRef}>
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <Input
                    id="food_items"
                    type="text"
                    placeholder="Start typing to search for foods or click to see popular foods..."
                    value={foodItemInput}
                    onChange={(e) => setFoodItemInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onFocus={() => {
                      // Show suggestions when input is focused, even if empty
                      if (suggestions.length > 0 || !foodItemInput.trim()) {
                        setShowSuggestions(true);
                      }
                    }}
                    className="pr-10"
                  />
                  <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                </div>
                <Button
                  type="button"
                  onClick={() => addFoodItem()}
                  disabled={!foodItemInput.trim()}
                  size="sm"
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              
              {/* Suggestions Dropdown */}
              {showSuggestions && suggestions.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-y-auto">
                  {suggestions.map((suggestion, index) => (
                    <div
                      key={index}
                      className={`px-4 py-3 cursor-pointer hover:bg-gray-50 border-b border-gray-100 last:border-b-0 ${
                        selectedSuggestionIndex === index ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => handleSuggestionClick(suggestion)}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{suggestion.name}</span>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 rounded text-xs ${
                            suggestion.category === 'database' ? 'bg-green-100 text-green-800' :
                            suggestion.category === 'user_history' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {suggestion.category}
                          </span>
                          {suggestion.is_common_trigger && (
                            <span className="flex items-center gap-1 px-2 py-1 bg-red-100 text-red-800 rounded text-xs">
                              <AlertTriangle className="h-3 w-3" />
                              Trigger
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {/* Added Food Items */}
            {formData.foods.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.foods.map((item: string, index: number) => (
                  <div
                    key={index}
                    className="flex items-center gap-1 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                  >
                    <span>{item}</span>
                    <button
                      type="button"
                      onClick={() => removeFoodItem(index)}
                      className="ml-1 hover:bg-blue-200 rounded-full p-1"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Portion Size */}
          <div className="space-y-2">
            <Label htmlFor="portion_size">Portion Size</Label>
            <Input
              id="portion_size"
              type="text"
              placeholder="e.g., 1 cup, 2 slices, medium bowl"
              value={formData.portion_size}
              onChange={(e) => handleInputChange('portion_size', e.target.value)}
            />
          </div>

          {/* Calories */}
          <div className="space-y-2">
            <Label htmlFor="calories">Estimated Calories</Label>
            <Input
              id="calories"
              type="number"
              placeholder="Optional"
              value={formData.calories || ''}
              onChange={(e) => handleInputChange('calories', e.target.value ? parseInt(e.target.value) : undefined)}
            />
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">Additional Notes</Label>
            <Textarea
              id="notes"
              placeholder="Any additional observations, context, or details about this meal..."
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              rows={3}
            />
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={isLoading}
            className="w-full"
          >
            {isLoading ? 'Saving...' : 'Save Diet Log'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}