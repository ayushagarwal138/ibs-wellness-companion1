'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Utensils, 
  Coffee, 
  Sun, 
  Moon, 
  Apple,
  Clock,
  Star,
  Heart,
  Leaf,
  Zap,
  CheckCircle,
  Info
} from 'lucide-react';

interface NutritionalInfo {
  calories: number;
  protein: number;
  carbs: number;
  fiber: number;
  fat: number;
}

interface IndianDishRecommendation {
  name: string;
  description: string;
  ingredients: string[];
  nutritionalInfo: NutritionalInfo;
  benefits: string[];
  preparationTime: string;
  difficulty: 'easy' | 'medium' | 'hard';
  ibsFriendly: boolean;
  spiceLevel: 'mild' | 'medium' | 'spicy';
  region: string;
  imageUrl?: string;
}

interface MealRecommendations {
  breakfast: IndianDishRecommendation[];
  lunch: IndianDishRecommendation[];
  dinner: IndianDishRecommendation[];
  snacks: IndianDishRecommendation[];
}

interface IndianDietRecommendationsProps {
  userProfile?: {
    ibsType: string;
    severityLevel: string;
    triggers: string[];
    preferences: string[];
  };
}

const mockRecommendations: MealRecommendations = {
  breakfast: [
    {
      name: "Oats Upma",
      description: "A healthy South Indian breakfast made with oats, vegetables, and mild spices",
      ingredients: ["Rolled oats", "Carrots", "Green beans", "Curry leaves", "Ginger", "Turmeric"],
      nutritionalInfo: { calories: 220, protein: 8, carbs: 35, fiber: 6, fat: 5 },
      benefits: ["High fiber", "Easy digestion", "Low FODMAP", "Anti-inflammatory"],
      preparationTime: "15 minutes",
      difficulty: 'easy',
      ibsFriendly: true,
      spiceLevel: 'mild',
      region: "South India",
      imageUrl: "/api/placeholder/300/200"
    },
    {
      name: "Moong Dal Chilla",
      description: "Protein-rich pancakes made from yellow lentils with vegetables",
      ingredients: ["Yellow moong dal", "Ginger", "Green chilies", "Coriander", "Turmeric"],
      nutritionalInfo: { calories: 180, protein: 12, carbs: 25, fiber: 5, fat: 3 },
      benefits: ["High protein", "Gluten-free", "Easy to digest", "Probiotic friendly"],
      preparationTime: "20 minutes",
      difficulty: 'medium',
      ibsFriendly: true,
      spiceLevel: 'mild',
      region: "North India"
    }
  ],
  lunch: [
    {
      name: "Quinoa Khichdi",
      description: "A nutritious one-pot meal combining quinoa with lentils and vegetables",
      ingredients: ["Quinoa", "Yellow moong dal", "Carrots", "Spinach", "Cumin", "Ginger"],
      nutritionalInfo: { calories: 320, protein: 15, carbs: 45, fiber: 8, fat: 6 },
      benefits: ["Complete protein", "High fiber", "Anti-inflammatory", "Gut healing"],
      preparationTime: "25 minutes",
      difficulty: 'easy',
      ibsFriendly: true,
      spiceLevel: 'mild',
      region: "Modern Indian"
    },
    {
      name: "Bottle Gourd Curry",
      description: "Light and digestible curry made with bottle gourd in coconut base",
      ingredients: ["Bottle gourd", "Coconut", "Ginger", "Curry leaves", "Turmeric"],
      nutritionalInfo: { calories: 150, protein: 4, carbs: 18, fiber: 4, fat: 8 },
      benefits: ["Low calorie", "Cooling effect", "Easy digestion", "Hydrating"],
      preparationTime: "20 minutes",
      difficulty: 'easy',
      ibsFriendly: true,
      spiceLevel: 'mild',
      region: "South India"
    }
  ],
  dinner: [
    {
      name: "Steamed Rice with Dal",
      description: "Simple and soothing combination of steamed rice with yellow lentil curry",
      ingredients: ["Basmati rice", "Toor dal", "Turmeric", "Ginger", "Ghee"],
      nutritionalInfo: { calories: 280, protein: 10, carbs: 50, fiber: 3, fat: 4 },
      benefits: ["Easy digestion", "Comfort food", "Balanced nutrition", "Sleep promoting"],
      preparationTime: "30 minutes",
      difficulty: 'easy',
      ibsFriendly: true,
      spiceLevel: 'mild',
      region: "Pan-Indian"
    },
    {
      name: "Vegetable Soup",
      description: "Nourishing soup with seasonal vegetables and healing spices",
      ingredients: ["Mixed vegetables", "Ginger", "Turmeric", "Coriander", "Black pepper"],
      nutritionalInfo: { calories: 120, protein: 5, carbs: 20, fiber: 6, fat: 2 },
      benefits: ["Hydrating", "Low calorie", "Nutrient dense", "Healing"],
      preparationTime: "25 minutes",
      difficulty: 'easy',
      ibsFriendly: true,
      spiceLevel: 'mild',
      region: "Modern Indian"
    }
  ],
  snacks: [
    {
      name: "Roasted Makhana",
      description: "Crunchy fox nuts roasted with mild spices - perfect healthy snack",
      ingredients: ["Fox nuts (makhana)", "Ghee", "Rock salt", "Turmeric", "Black pepper"],
      nutritionalInfo: { calories: 90, protein: 4, carbs: 15, fiber: 2, fat: 2 },
      benefits: ["Low calorie", "High protein", "Gluten-free", "Digestive friendly"],
      preparationTime: "10 minutes",
      difficulty: 'easy',
      ibsFriendly: true,
      spiceLevel: 'mild',
      region: "North India"
    },
    {
      name: "Coconut Laddu",
      description: "Sweet and nutritious balls made with coconut and jaggery",
      ingredients: ["Fresh coconut", "Jaggery", "Cardamom", "Ghee"],
      nutritionalInfo: { calories: 110, protein: 2, carbs: 12, fiber: 3, fat: 6 },
      benefits: ["Natural sweetener", "Healthy fats", "Energy boosting", "Digestive aid"],
      preparationTime: "15 minutes",
      difficulty: 'medium',
      ibsFriendly: true,
      spiceLevel: 'mild',
      region: "South India"
    }
  ]
};

const getMealIcon = (mealType: string) => {
  switch (mealType) {
    case 'breakfast': return <Coffee className="h-5 w-5" />;
    case 'lunch': return <Sun className="h-5 w-5" />;
    case 'dinner': return <Moon className="h-5 w-5" />;
    case 'snacks': return <Apple className="h-5 w-5" />;
    default: return <Utensils className="h-5 w-5" />;
  }
};

const getMealColor = (mealType: string) => {
  switch (mealType) {
    case 'breakfast': return 'text-orange-500';
    case 'lunch': return 'text-yellow-500';
    case 'dinner': return 'text-purple-500';
    case 'snacks': return 'text-green-500';
    default: return 'text-gray-500';
  }
};

const DishCard: React.FC<{ dish: IndianDishRecommendation }> = ({ dish }) => (
  <Card className="h-full hover:shadow-lg transition-shadow duration-200">
    <CardHeader className="pb-3">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <CardTitle className="text-lg font-semibold text-gray-900 mb-1">
            {dish.name}
          </CardTitle>
          <p className="text-sm text-gray-600 mb-2">{dish.description}</p>
          <div className="flex items-center gap-2 mb-2">
            <Badge variant={dish.ibsFriendly ? 'default' : 'secondary'} className="text-xs">
              {dish.ibsFriendly ? 'IBS Friendly' : 'Moderate'}
            </Badge>
            <Badge variant="outline" className="text-xs">
              {dish.region}
            </Badge>
            <Badge 
              variant={dish.spiceLevel === 'mild' ? 'default' : 'secondary'} 
              className="text-xs"
            >
              {dish.spiceLevel} spice
            </Badge>
          </div>
        </div>
        {dish.ibsFriendly && (
          <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 ml-2" />
        )}
      </div>
    </CardHeader>
    
    <CardContent className="pt-0">
      {/* Nutritional Information */}
      <div className="bg-blue-50 p-3 rounded-lg mb-4">
        <h4 className="text-sm font-medium text-blue-900 mb-2 flex items-center gap-1">
          <Zap className="h-4 w-4" />
          Nutritional Info (per serving)
        </h4>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="flex justify-between">
            <span className="text-blue-700">Calories:</span>
            <span className="font-medium">{dish.nutritionalInfo.calories}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-blue-700">Protein:</span>
            <span className="font-medium">{dish.nutritionalInfo.protein}g</span>
          </div>
          <div className="flex justify-between">
            <span className="text-blue-700">Carbs:</span>
            <span className="font-medium">{dish.nutritionalInfo.carbs}g</span>
          </div>
          <div className="flex justify-between">
            <span className="text-blue-700">Fiber:</span>
            <span className="font-medium">{dish.nutritionalInfo.fiber}g</span>
          </div>
        </div>
      </div>

      {/* Benefits */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center gap-1">
          <Heart className="h-4 w-4 text-red-500" />
          Health Benefits
        </h4>
        <div className="flex flex-wrap gap-1">
          {dish.benefits.map((benefit, index) => (
            <span 
              key={index}
              className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full"
            >
              {benefit}
            </span>
          ))}
        </div>
      </div>

      {/* Ingredients */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center gap-1">
          <Leaf className="h-4 w-4 text-green-500" />
          Key Ingredients
        </h4>
        <div className="flex flex-wrap gap-1">
          {dish.ingredients.slice(0, 4).map((ingredient, index) => (
            <span 
              key={index}
              className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded"
            >
              {ingredient}
            </span>
          ))}
          {dish.ingredients.length > 4 && (
            <span className="text-xs text-gray-500">+{dish.ingredients.length - 4} more</span>
          )}
        </div>
      </div>

      {/* Preparation Info */}
      <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
        <div className="flex items-center gap-1">
          <Clock className="h-4 w-4" />
          <span>{dish.preparationTime}</span>
        </div>
        <div className="flex items-center gap-1">
          <Star className="h-4 w-4" />
          <span className="capitalize">{dish.difficulty}</span>
        </div>
      </div>

      <Button variant="outline" size="sm" className="w-full">
        View Recipe
      </Button>
    </CardContent>
  </Card>
);

const MealSection: React.FC<{ 
  mealType: string; 
  dishes: IndianDishRecommendation[];
  title: string;
}> = ({ mealType, dishes, title }) => (
  <div className="mb-8">
    <div className="flex items-center gap-3 mb-4">
      <div className={`p-2 rounded-lg bg-gray-100 ${getMealColor(mealType)}`}>
        {getMealIcon(mealType)}
      </div>
      <div>
        <h3 className="text-xl font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-600">
          {dishes.length} personalized recommendations
        </p>
      </div>
    </div>
    
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {dishes.map((dish, index) => (
        <DishCard key={index} dish={dish} />
      ))}
    </div>
  </div>
);

export const IndianDietRecommendations: React.FC<IndianDietRecommendationsProps> = ({ 
  userProfile 
}) => {
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Utensils className="h-5 w-5 text-orange-500" />
          Personalized Indian Diet Recommendations
        </CardTitle>
        <p className="text-sm text-gray-600">
          Curated meal suggestions based on your IBS profile and dietary preferences
        </p>
      </CardHeader>
      
      <CardContent>
        {/* User Profile Summary */}
        {userProfile && (
          <div className="bg-gradient-to-r from-orange-50 to-yellow-50 p-4 rounded-lg mb-6 border border-orange-200">
            <div className="flex items-start gap-3">
              <Info className="h-5 w-5 text-orange-500 mt-0.5" />
              <div>
                <h4 className="font-medium text-orange-900 mb-1">
                  Recommendations tailored for your profile
                </h4>
                <div className="text-sm text-orange-800 space-y-1">
                  <p>IBS Type: <span className="font-medium">{userProfile.ibsType}</span></p>
                  <p>Severity: <span className="font-medium">{userProfile.severityLevel}</span></p>
                  <p>Focus: Low FODMAP, anti-inflammatory, easily digestible foods</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Meal Sections */}
        <MealSection 
          mealType="breakfast" 
          dishes={mockRecommendations.breakfast}
          title="Breakfast Options"
        />
        
        <MealSection 
          mealType="lunch" 
          dishes={mockRecommendations.lunch}
          title="Lunch Recommendations"
        />
        
        <MealSection 
          mealType="dinner" 
          dishes={mockRecommendations.dinner}
          title="Dinner Suggestions"
        />
        
        <MealSection 
          mealType="snacks" 
          dishes={mockRecommendations.snacks}
          title="Healthy Snacks"
        />

        {/* Additional Tips */}
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 mt-6">
          <h4 className="font-medium text-blue-900 mb-2 flex items-center gap-2">
            <Leaf className="h-4 w-4" />
            Dietary Tips for IBS Management
          </h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Eat smaller, more frequent meals throughout the day</li>
            <li>• Chew food thoroughly and eat slowly to aid digestion</li>
            <li>• Stay hydrated with warm water and herbal teas</li>
            <li>• Avoid eating large meals close to bedtime</li>
            <li>• Keep a food diary to identify personal triggers</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};