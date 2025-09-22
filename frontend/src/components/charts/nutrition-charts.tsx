'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { TrendingUp, TrendingDown, Minus, Target, Calendar, Activity } from 'lucide-react'

interface MacronutrientData {
  carbs: number
  protein: number
  fat: number
  fiber: number
  sugar: number
  sodium: number
}

interface DailyNutritionData {
  date: string
  calories: number
  macros: MacronutrientData
  meals: number
  quality_score: number
}

interface NutritionTrend {
  metric: string
  current: number
  previous: number
  change: number
  unit: string
  target?: number
}

interface NutritionChartsProps {
  dailyData?: DailyNutritionData
  weeklyTrends?: NutritionTrend[]
  monthlyAverage?: MacronutrientData & { calories: number }
  isLoading?: boolean
}

const MacronutrientCard: React.FC<{
  name: string
  current: number
  target: number
  unit: string
  color: string
  icon: React.ReactNode
}> = ({ name, current, target, unit, color, icon }) => {
  const percentage = target > 0 ? Math.min((current / target) * 100, 100) : 0
  const isOver = current > target && target > 0

  return (
    <Card className="relative overflow-hidden">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            {icon}
            {name}
          </CardTitle>
          <Badge variant={isOver ? "destructive" : percentage >= 80 ? "default" : "secondary"}>
            {current}{unit}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Target: {target}{unit}</span>
            <span className={`font-medium ${isOver ? 'text-red-600' : 'text-green-600'}`}>
              {percentage.toFixed(0)}%
            </span>
          </div>
          <Progress 
            value={percentage} 
            className={`h-2 ${color}`}
          />
          {isOver && (
            <p className="text-xs text-red-600">
              {(current - target).toFixed(1)}{unit} over target
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

const TrendCard: React.FC<{ trend: NutritionTrend }> = ({ trend }) => {
  const isPositive = trend.change > 0
  const isNeutral = trend.change === 0
  const changeIcon = isNeutral ? Minus : isPositive ? TrendingUp : TrendingDown
  const changeColor = isNeutral ? 'text-gray-500' : isPositive ? 'text-green-600' : 'text-red-600'

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{trend.metric}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold">
              {trend.current.toFixed(1)}{trend.unit}
            </span>
            <div className={`flex items-center gap-1 ${changeColor}`}>
              {React.createElement(changeIcon, { className: "h-4 w-4" })}
              <span className="text-sm font-medium">
                {Math.abs(trend.change).toFixed(1)}{trend.unit}
              </span>
            </div>
          </div>
          <div className="text-xs text-muted-foreground">
            Previous: {trend.previous.toFixed(1)}{trend.unit}
            {trend.target && (
              <span className="ml-2">
                • Target: {trend.target.toFixed(1)}{trend.unit}
              </span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

const CalorieOverview: React.FC<{
  current: number
  target: number
  burned?: number
}> = ({ current, target, burned = 0 }) => {
  const net = current - burned
  const remaining = target - net
  const percentage = target > 0 ? (net / target) * 100 : 0

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5" />
          Daily Calorie Overview
        </CardTitle>
        <CardDescription>
          Track your daily calorie intake vs. target
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{current}</div>
              <div className="text-sm text-muted-foreground">Consumed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{target}</div>
              <div className="text-sm text-muted-foreground">Target</div>
            </div>
            {burned > 0 && (
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{burned}</div>
                <div className="text-sm text-muted-foreground">Burned</div>
              </div>
            )}
            <div className="text-center">
              <div className={`text-2xl font-bold ${remaining > 0 ? 'text-gray-600' : 'text-red-600'}`}>
                {remaining > 0 ? remaining : Math.abs(remaining)}
              </div>
              <div className="text-sm text-muted-foreground">
                {remaining > 0 ? 'Remaining' : 'Over'}
              </div>
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progress to target</span>
              <span className="font-medium">{percentage.toFixed(0)}%</span>
            </div>
            <Progress value={Math.min(percentage, 100)} className="h-3" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

const QualityScoreCard: React.FC<{ score: number }> = ({ score }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Fair'
    return 'Needs Improvement'
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Activity className="h-4 w-4" />
          Nutrition Quality
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="text-center">
            <div className={`text-3xl font-bold ${getScoreColor(score)}`}>
              {score.toFixed(0)}
            </div>
            <div className="text-sm text-muted-foreground">
              {getScoreLabel(score)}
            </div>
          </div>
          <Progress value={score} className="h-2" />
          <p className="text-xs text-muted-foreground text-center">
            Based on nutrient density and balance
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

const NutritionCharts: React.FC<NutritionChartsProps> = ({
  dailyData,
  weeklyTrends = [],
  monthlyAverage,
  isLoading = false
}) => {
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 rounded mb-2"></div>
                <div className="h-2 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (!dailyData) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center">
            <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No nutrition data available</h3>
            <p className="text-gray-500">Start logging your meals to see nutritional insights</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Default targets (these could be user-configurable)
  const targets = {
    calories: 2000,
    carbs: 250,
    protein: 150,
    fat: 65,
    fiber: 25,
    sugar: 50,
    sodium: 2300
  }

  return (
    <div className="space-y-6">
      {/* Calorie Overview */}
      <CalorieOverview 
        current={dailyData.calories} 
        target={targets.calories}
      />

      {/* Macronutrient Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <MacronutrientCard
          name="Carbohydrates"
          current={dailyData.macros.carbs}
          target={targets.carbs}
          unit="g"
          color="bg-green-500"
          icon={<div className="w-3 h-3 bg-green-500 rounded-full" />}
        />
        <MacronutrientCard
          name="Protein"
          current={dailyData.macros.protein}
          target={targets.protein}
          unit="g"
          color="bg-red-500"
          icon={<div className="w-3 h-3 bg-red-500 rounded-full" />}
        />
        <MacronutrientCard
          name="Fat"
          current={dailyData.macros.fat}
          target={targets.fat}
          unit="g"
          color="bg-yellow-500"
          icon={<div className="w-3 h-3 bg-yellow-500 rounded-full" />}
        />
        <MacronutrientCard
          name="Fiber"
          current={dailyData.macros.fiber}
          target={targets.fiber}
          unit="g"
          color="bg-purple-500"
          icon={<div className="w-3 h-3 bg-purple-500 rounded-full" />}
        />
        <MacronutrientCard
          name="Sugar"
          current={dailyData.macros.sugar}
          target={targets.sugar}
          unit="g"
          color="bg-pink-500"
          icon={<div className="w-3 h-3 bg-pink-500 rounded-full" />}
        />
        <MacronutrientCard
          name="Sodium"
          current={dailyData.macros.sodium}
          target={targets.sodium}
          unit="mg"
          color="bg-orange-500"
          icon={<div className="w-3 h-3 bg-orange-500 rounded-full" />}
        />
      </div>

      {/* Quality Score */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <QualityScoreCard score={dailyData.quality_score} />
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Meals Today</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {dailyData.meals}
              </div>
              <div className="text-sm text-muted-foreground">
                Logged meals
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Date</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-lg font-medium text-gray-900">
                {new Date(dailyData.date).toLocaleDateString('en-US', {
                  weekday: 'short',
                  month: 'short',
                  day: 'numeric'
                })}
              </div>
              <div className="text-sm text-muted-foreground">
                Today's data
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Weekly Trends */}
      {weeklyTrends.length > 0 && (
        <div>
          <h3 className="text-lg font-medium mb-4">Weekly Trends</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {weeklyTrends.map((trend, index) => (
              <TrendCard key={index} trend={trend} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default NutritionCharts