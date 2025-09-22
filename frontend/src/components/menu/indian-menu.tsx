'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Clock, Users, Flame, Leaf } from 'lucide-react'

interface MenuItem {
  id: string
  name: string
  description: string
  ingredients: string[]
  preparationTime: string
  servings: string
  spiceLevel: 'mild' | 'medium' | 'hot'
  isVegetarian: boolean
  isVegan?: boolean
  nutritionalHighlights?: string[]
  preparationMethod: string
}

const parathaMenu: MenuItem[] = [
  {
    id: 'aloo-paratha',
    name: 'Aloo Paratha',
    description: 'Classic stuffed flatbread filled with spiced mashed potatoes, served with butter, yogurt, and pickle.',
    ingredients: ['Whole wheat flour', 'Potatoes', 'Onions', 'Green chilies', 'Ginger', 'Cumin seeds', 'Coriander leaves', 'Ghee/Oil'],
    preparationTime: '45 minutes',
    servings: '4 pieces',
    spiceLevel: 'mild',
    isVegetarian: true,
    isVegan: false,
    nutritionalHighlights: ['High in carbohydrates', 'Good source of fiber', 'Contains potassium'],
    preparationMethod: 'Boiled potatoes are mashed and mixed with aromatic spices, then stuffed into wheat dough and rolled flat. Cooked on a hot griddle with ghee until golden brown and crispy.'
  },
  {
    id: 'gobi-paratha',
    name: 'Gobi Paratha',
    description: 'Nutritious flatbread stuffed with seasoned cauliflower, perfect for a healthy and filling meal.',
    ingredients: ['Whole wheat flour', 'Cauliflower', 'Onions', 'Ginger-garlic paste', 'Green chilies', 'Garam masala', 'Turmeric', 'Coriander leaves'],
    preparationTime: '40 minutes',
    servings: '4 pieces',
    spiceLevel: 'medium',
    isVegetarian: true,
    isVegan: true,
    nutritionalHighlights: ['Rich in vitamin C', 'High fiber content', 'Low in calories'],
    preparationMethod: 'Fresh cauliflower is grated and sautéed with spices until moisture evaporates. The mixture is then stuffed into dough, rolled, and cooked on a griddle with minimal oil.'
  },
  {
    id: 'paneer-paratha',
    name: 'Paneer Paratha',
    description: 'Protein-rich flatbread filled with crumbled cottage cheese and aromatic spices.',
    ingredients: ['Whole wheat flour', 'Fresh paneer', 'Onions', 'Green chilies', 'Ginger', 'Cumin powder', 'Red chili powder', 'Fresh mint'],
    preparationTime: '35 minutes',
    servings: '4 pieces',
    spiceLevel: 'mild',
    isVegetarian: true,
    isVegan: false,
    nutritionalHighlights: ['High protein content', 'Rich in calcium', 'Good source of phosphorus'],
    preparationMethod: 'Fresh paneer is crumbled and mixed with finely chopped onions and spices. The mixture is stuffed into wheat dough, rolled carefully, and cooked on a hot griddle until golden.'
  },
  {
    id: 'mooli-paratha',
    name: 'Mooli Paratha',
    description: 'Healthy flatbread stuffed with grated white radish and traditional spices.',
    ingredients: ['Whole wheat flour', 'White radish (mooli)', 'Green chilies', 'Ginger', 'Cumin seeds', 'Coriander leaves', 'Ajwain (carom seeds)'],
    preparationTime: '40 minutes',
    servings: '4 pieces',
    spiceLevel: 'mild',
    isVegetarian: true,
    isVegan: true,
    nutritionalHighlights: ['Rich in vitamin C', 'Good for digestion', 'Low in calories'],
    preparationMethod: 'Fresh radish is grated and excess water is squeezed out. Mixed with spices and herbs, then stuffed into dough and cooked on a griddle until crispy.'
  },
  {
    id: 'methi-paratha',
    name: 'Methi Paratha',
    description: 'Aromatic flatbread made with fresh fenugreek leaves, known for its distinctive flavor and health benefits.',
    ingredients: ['Whole wheat flour', 'Fresh fenugreek leaves', 'Onions', 'Green chilies', 'Ginger', 'Turmeric', 'Red chili powder', 'Ajwain'],
    preparationTime: '30 minutes',
    servings: '4 pieces',
    spiceLevel: 'medium',
    isVegetarian: true,
    isVegan: true,
    nutritionalHighlights: ['Rich in iron', 'Good for blood sugar control', 'High in antioxidants'],
    preparationMethod: 'Fresh methi leaves are cleaned, chopped, and mixed directly into the wheat flour with spices. The dough is kneaded, rolled, and cooked on a griddle with ghee.'
  },
  {
    id: 'keema-paratha',
    name: 'Keema Paratha',
    description: 'Non-vegetarian delight stuffed with spiced minced meat, perfect for meat lovers.',
    ingredients: ['Whole wheat flour', 'Minced mutton/chicken', 'Onions', 'Ginger-garlic paste', 'Tomatoes', 'Garam masala', 'Red chili powder', 'Fresh coriander'],
    preparationTime: '60 minutes',
    servings: '4 pieces',
    spiceLevel: 'hot',
    isVegetarian: false,
    isVegan: false,
    nutritionalHighlights: ['High protein content', 'Rich in iron', 'Good source of B vitamins'],
    preparationMethod: 'Minced meat is cooked with onions, tomatoes, and spices until dry. The cooked keema is then stuffed into wheat dough, rolled carefully, and cooked on a griddle.'
  }
]

const streetFoodMenu: MenuItem[] = [
  {
    id: 'pav-bhaji',
    name: 'Pav Bhaji',
    description: 'Mumbai\'s iconic street food - a thick vegetable curry served with buttered and toasted bread rolls.',
    ingredients: ['Mixed vegetables (potato, cauliflower, peas, carrots)', 'Tomatoes', 'Onions', 'Pav bhaji masala', 'Butter', 'Pav bread', 'Lemon', 'Coriander'],
    preparationTime: '45 minutes',
    servings: '4 servings',
    spiceLevel: 'medium',
    isVegetarian: true,
    isVegan: false,
    nutritionalHighlights: ['Rich in vegetables', 'Good source of vitamins', 'High in fiber'],
    preparationMethod: 'Mixed vegetables are boiled, mashed, and cooked with onions, tomatoes, and special pav bhaji masala. Served hot with buttered pav bread, garnished with onions and lemon.'
  },
  {
    id: 'chole-bhature',
    name: 'Chole Bhature',
    description: 'Popular North Indian combination of spicy chickpea curry with deep-fried bread.',
    ingredients: ['Chickpeas', 'Onions', 'Tomatoes', 'Ginger-garlic paste', 'Chole masala', 'All-purpose flour', 'Yogurt', 'Baking powder'],
    preparationTime: '90 minutes',
    servings: '4 servings',
    spiceLevel: 'hot',
    isVegetarian: true,
    isVegan: false,
    nutritionalHighlights: ['High protein from chickpeas', 'Rich in fiber', 'Good source of folate'],
    preparationMethod: 'Chickpeas are cooked with aromatic spices to make a thick curry. Bhature is made from fermented dough, rolled and deep-fried until puffy and golden.'
  },
  {
    id: 'vada-pav',
    name: 'Vada Pav',
    description: 'Mumbai\'s beloved "Indian burger" - spiced potato fritter served in a bread roll with chutneys.',
    ingredients: ['Potatoes', 'Gram flour (besan)', 'Mustard seeds', 'Curry leaves', 'Green chilies', 'Pav bread', 'Tamarind chutney', 'Green chutney'],
    preparationTime: '40 minutes',
    servings: '4 pieces',
    spiceLevel: 'medium',
    isVegetarian: true,
    isVegan: true,
    nutritionalHighlights: ['Good source of carbohydrates', 'Contains potassium', 'Energy-rich snack'],
    preparationMethod: 'Spiced mashed potatoes are shaped into balls, coated with gram flour batter, and deep-fried. Served in pav with various chutneys and fried green chilies.'
  }
]

const riceMenu: MenuItem[] = [
  {
    id: 'biryani',
    name: 'Hyderabadi Biryani',
    description: 'Aromatic basmati rice layered with marinated meat/vegetables and cooked with saffron and spices.',
    ingredients: ['Basmati rice', 'Meat/Vegetables', 'Yogurt', 'Onions', 'Saffron', 'Mint leaves', 'Biryani masala', 'Ghee'],
    preparationTime: '120 minutes',
    servings: '6 servings',
    spiceLevel: 'medium',
    isVegetarian: false,
    isVegan: false,
    nutritionalHighlights: ['Complete protein', 'Rich in aromatic spices', 'Good source of carbohydrates'],
    preparationMethod: 'Rice and meat are partially cooked separately, then layered with fried onions, mint, and saffron. Cooked on dum (slow cooking) method for perfect flavor infusion.'
  },
  {
    id: 'rajma-rice',
    name: 'Rajma Rice',
    description: 'Comfort food combination of kidney bean curry served with steamed basmati rice.',
    ingredients: ['Red kidney beans', 'Onions', 'Tomatoes', 'Ginger-garlic paste', 'Cumin', 'Coriander powder', 'Garam masala', 'Basmati rice'],
    preparationTime: '60 minutes',
    servings: '4 servings',
    spiceLevel: 'medium',
    isVegetarian: true,
    isVegan: true,
    nutritionalHighlights: ['High protein and fiber', 'Rich in iron', 'Good source of folate'],
    preparationMethod: 'Soaked kidney beans are pressure cooked and then simmered in a rich tomato-onion gravy with aromatic spices. Served with fluffy basmati rice.'
  }
]

const breadMenu: MenuItem[] = [
  {
    id: 'naan',
    name: 'Butter Naan',
    description: 'Soft, pillowy leavened bread cooked in tandoor and brushed with butter.',
    ingredients: ['All-purpose flour', 'Yogurt', 'Yeast', 'Sugar', 'Salt', 'Butter', 'Milk'],
    preparationTime: '3 hours (including fermentation)',
    servings: '6 pieces',
    spiceLevel: 'mild',
    isVegetarian: true,
    isVegan: false,
    nutritionalHighlights: ['Good source of carbohydrates', 'Contains probiotics from yogurt'],
    preparationMethod: 'Dough is fermented for 2-3 hours, then rolled and cooked in a hot tandoor or oven. Brushed with butter while hot for extra flavor.'
  },
  {
    id: 'roti',
    name: 'Tandoori Roti',
    description: 'Whole wheat flatbread cooked in tandoor, healthier alternative to naan.',
    ingredients: ['Whole wheat flour', 'Water', 'Salt', 'Oil'],
    preparationTime: '20 minutes',
    servings: '6 pieces',
    spiceLevel: 'mild',
    isVegetarian: true,
    isVegan: true,
    nutritionalHighlights: ['High in fiber', 'Good source of complex carbohydrates', 'Contains B vitamins'],
    preparationMethod: 'Simple dough is kneaded, rested, rolled thin, and cooked in a tandoor or on a hot griddle until slightly charred and puffy.'
  }
]

export default function IndianMenu() {
  const getSpiceLevelColor = (level: string) => {
    switch (level) {
      case 'mild': return 'bg-green-100 text-green-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'hot': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const MenuCard = ({ item }: { item: MenuItem }) => (
    <Card className="h-full hover:shadow-lg transition-shadow duration-300">
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle className="text-xl font-bold text-orange-800">{item.name}</CardTitle>
          <div className="flex gap-2">
            {item.isVegetarian && (
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                <Leaf className="w-3 h-3 mr-1" />
                Veg
              </Badge>
            )}
            {item.isVegan && (
              <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200">
                Vegan
              </Badge>
            )}
          </div>
        </div>
        <CardDescription className="text-gray-600 leading-relaxed">
          {item.description}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-2 items-center">
          <Badge className={getSpiceLevelColor(item.spiceLevel)}>
            <Flame className="w-3 h-3 mr-1" />
            {item.spiceLevel.charAt(0).toUpperCase() + item.spiceLevel.slice(1)}
          </Badge>
          <Badge variant="outline" className="text-blue-700 border-blue-200">
            <Clock className="w-3 h-3 mr-1" />
            {item.preparationTime}
          </Badge>
          <Badge variant="outline" className="text-purple-700 border-purple-200">
            <Users className="w-3 h-3 mr-1" />
            {item.servings}
          </Badge>
        </div>

        <div>
          <h4 className="font-semibold text-gray-800 mb-2">Key Ingredients:</h4>
          <div className="flex flex-wrap gap-1">
            {item.ingredients.map((ingredient, index) => (
              <Badge key={index} variant="secondary" className="text-xs bg-orange-50 text-orange-700">
                {ingredient}
              </Badge>
            ))}
          </div>
        </div>

        <div>
          <h4 className="font-semibold text-gray-800 mb-2">Preparation Method:</h4>
          <p className="text-sm text-gray-600 leading-relaxed">{item.preparationMethod}</p>
        </div>

        {item.nutritionalHighlights && (
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">Nutritional Highlights:</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              {item.nutritionalHighlights.map((highlight, index) => (
                <li key={index} className="flex items-center">
                  <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2"></span>
                  {highlight}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  )

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gradient-to-br from-orange-50 to-red-50 min-h-screen">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-orange-900 mb-4">
          🇮🇳 Authentic Indian Menu
        </h1>
        <p className="text-lg text-gray-700 max-w-3xl mx-auto">
          Discover the rich flavors and diverse culinary traditions of India. From stuffed parathas to street food favorites, 
          each dish is crafted with authentic spices and traditional cooking methods.
        </p>
      </div>

      <Tabs defaultValue="parathas" className="w-full">
        <TabsList className="grid w-full grid-cols-4 mb-8 bg-white shadow-sm">
          <TabsTrigger value="parathas" className="data-[state=active]:bg-orange-100 data-[state=active]:text-orange-800">
            Parathas
          </TabsTrigger>
          <TabsTrigger value="street-food" className="data-[state=active]:bg-orange-100 data-[state=active]:text-orange-800">
            Street Food
          </TabsTrigger>
          <TabsTrigger value="rice-dishes" className="data-[state=active]:bg-orange-100 data-[state=active]:text-orange-800">
            Rice Dishes
          </TabsTrigger>
          <TabsTrigger value="breads" className="data-[state=active]:bg-orange-100 data-[state=active]:text-orange-800">
            Breads
          </TabsTrigger>
        </TabsList>

        <TabsContent value="parathas" className="space-y-6">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-orange-800 mb-2">Stuffed Parathas</h2>
            <p className="text-gray-600">Traditional Indian flatbreads stuffed with various fillings and cooked to perfection</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {parathaMenu.map((item) => (
              <MenuCard key={item.id} item={item} />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="street-food" className="space-y-6">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-orange-800 mb-2">Street Food Favorites</h2>
            <p className="text-gray-600">Popular Indian street foods that capture the essence of local flavors and culture</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {streetFoodMenu.map((item) => (
              <MenuCard key={item.id} item={item} />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="rice-dishes" className="space-y-6">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-orange-800 mb-2">Rice Specialties</h2>
            <p className="text-gray-600">Aromatic rice dishes that form the heart of Indian cuisine</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {riceMenu.map((item) => (
              <MenuCard key={item.id} item={item} />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="breads" className="space-y-6">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-orange-800 mb-2">Traditional Breads</h2>
            <p className="text-gray-600">Freshly baked breads that complement every Indian meal</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {breadMenu.map((item) => (
              <MenuCard key={item.id} item={item} />
            ))}
          </div>
        </TabsContent>
      </Tabs>

      <div className="mt-12 bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-bold text-orange-800 mb-4">About Our Menu</h3>
        <div className="grid md:grid-cols-2 gap-6 text-gray-600">
          <div>
            <h4 className="font-semibold mb-2">Authentic Recipes</h4>
            <p className="text-sm leading-relaxed">
              All our dishes are prepared using traditional recipes passed down through generations, 
              ensuring authentic flavors and cooking techniques.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Fresh Ingredients</h4>
            <p className="text-sm leading-relaxed">
              We use only the freshest ingredients and authentic Indian spices to create 
              dishes that are both flavorful and nutritious.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Dietary Options</h4>
            <p className="text-sm leading-relaxed">
              Our menu includes various vegetarian and vegan options, clearly marked 
              to help you make informed choices based on your dietary preferences.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Spice Levels</h4>
            <p className="text-sm leading-relaxed">
              Each dish is marked with its spice level - mild, medium, or hot - 
              so you can choose according to your taste preferences.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}