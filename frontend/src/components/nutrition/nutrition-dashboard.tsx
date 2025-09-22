'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Calendar, TrendingUp, Activity, Target, RefreshCw, Download } from 'lucide-react'
import { format, subDays, startOfDay } from 'date-fns'
import NutritionCharts from '@/components/charts/nutrition-charts'

interface NutritionData {
  calories: number
  protein_g: number
  carbs_g: number
  fat_g: number
  fiber_g: number
  sugar_g: number
  sodium_mg: number
  calcium_mg: number
  iron_mg: number
  vitamin_c_mg: number
  vitamin_d_ug: number
}

interface MacronutrientBreakdown {
  carbohydrates: number
  protein: number
  fat: number
  fiber: number
}

interface DailyNutritionSummary {
  total_nutrition: NutritionData
  macronutrient_breakdown: MacronutrientBreakdown
  meals_count: number
  target_calories?: number
  calorie_deficit_surplus?: number
  nutrition_quality_score?: number
}

interface NutritionTrends {
  period_days: number
  daily_summaries: Array<{
    date: string
    summary: DailyNutritionSummary
  }>
  averages: {
    calories: number
    protein_g: number
    carbs_g: number
    fat_g: number
    fiber_g: number
  }
  recommendations: string[]
}

const NutritionDashboard: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<string>(format(new Date(), 'yyyy-MM-dd'))
  const [dailySummary, setDailySummary] = useState<DailyNutritionSummary | null>(null)
  const [trends, setTrends] = useState<NutritionTrends | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('daily')

  // Nutrition targets (can be made configurable)
  const nutritionTargets = {
    calories: 2000,
    protein_g: 150,
    carbs_g: 250,
    fat_g: 67,
    fiber_g: 25
  }

  useEffect(() => {
    if (activeTab === 'daily') {
      fetchDailySummary(selectedDate)
    } else if (activeTab === 'trends') {
      fetchNutritionTrends()
    }
  }, [selectedDate, activeTab])

  const fetchDailySummary = async (date: string) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/diet/nutrition/daily/${date}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setDailySummary(data)
      }
    } catch (error) {
      console.error('Error fetching daily summary:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchNutritionTrends = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/diet/nutrition/trends?days=30', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setTrends(data)
      }
    } catch (error) {
      console.error('Error fetching nutrition trends:', error)
    } finally {
      setLoading(false)
    }
  }

  const getProgressColor = (current: number, target: number): string => {
    const percentage = (current / target) * 100
    if (percentage < 50) return 'bg-red-500'
    if (percentage < 80) return 'bg-yellow-500'
    if (percentage <= 120) return 'bg-green-500'
    return 'bg-orange-500'
  }

  const MacronutrientCard: React.FC<{
    title: string
    current: number
    target: number
    unit: string
    percentage: number
    color: string
  }> = ({ title, current, target, unit, percentage, color }) => (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-2xl font-bold">{current.toFixed(1)}{unit}</span>
            <Badge variant="outline">{percentage.toFixed(1)}%</Badge>
          </div>
          <Progress 
            value={Math.min((current / target) * 100, 100)} 
            className="h-2"
          />
          <div className="text-xs text-muted-foreground">
            Target: {target}{unit}
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const MacronutrientPieChart: React.FC<{ breakdown: MacronutrientBreakdown }> = ({ breakdown }) => (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Macronutrient Distribution</h3>
      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-blue-500 rounded"></div>
          <span className="text-sm">Carbs: {breakdown.carbohydrates.toFixed(1)}%</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span className="text-sm">Protein: {breakdown.protein.toFixed(1)}%</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-yellow-500 rounded"></div>
          <span className="text-sm">Fat: {breakdown.fat.toFixed(1)}%</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-purple-500 rounded"></div>
          <span className="text-sm">Fiber: {breakdown.fiber.toFixed(1)}%</span>
        </div>
      </div>
    </div>
  )

  const NutritionQualityScore: React.FC<{ score?: number }> = ({ score }) => {
    if (!score) return null

    const getScoreColor = (score: number): string => {
      if (score >= 80) return 'text-green-600'
      if (score >= 60) return 'text-yellow-600'
      return 'text-red-600'
    }

    const getScoreLabel = (score: number): string => {
      if (score >= 80) return 'Excellent'
      if (score >= 60) return 'Good'
      if (score >= 40) return 'Fair'
      return 'Needs Improvement'
    }

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Target className="h-5 w-5" />
            <span>Nutrition Quality Score</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center space-y-2">
            <div className={`text-4xl font-bold ${getScoreColor(score)}`}>
              {score.toFixed(1)}
            </div>
            <div className="text-sm text-muted-foreground">
              {getScoreLabel(score)}
            </div>
            <Progress value={score} className="h-2" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Nutrition Dashboard</h1>
        <div className="flex items-center space-x-2">
          <Calendar className="h-4 w-4" />
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="px-3 py-2 border rounded-md"
          />
        </div>
      </div>

      <Tabs defaultValue="daily">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="daily">Daily Overview</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="daily" className="space-y-6">
          <NutritionCharts
            dailyData={dailySummary ? {
              date: format(new Date(selectedDate), 'yyyy-MM-dd'),
              calories: dailySummary.total_nutrition.calories,
              macros: {
                carbs: dailySummary.total_nutrition.carbs_g,
                protein: dailySummary.total_nutrition.protein_g,
                fat: dailySummary.total_nutrition.fat_g,
                fiber: dailySummary.total_nutrition.fiber_g || 0,
                sugar: dailySummary.total_nutrition.sugar_g || 0,
                sodium: dailySummary.total_nutrition.sodium_mg || 0
              },
              meals: dailySummary.meals_count || 0,
              quality_score: dailySummary.nutrition_quality_score || 0
            } : undefined}
            isLoading={loading}
          />
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          {loading ? (
            <div className="text-center py-8">Loading trends...</div>
          ) : trends ? (
            <>
              {/* Average Nutrition */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <TrendingUp className="h-5 w-5" />
                    <span>30-Day Averages</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold">{trends.averages.calories.toFixed(0)}</div>
                      <div className="text-sm text-muted-foreground">Avg Calories</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold">{trends.averages.protein_g.toFixed(1)}g</div>
                      <div className="text-sm text-muted-foreground">Avg Protein</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold">{trends.averages.carbs_g.toFixed(1)}g</div>
                      <div className="text-sm text-muted-foreground">Avg Carbs</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold">{trends.averages.fat_g.toFixed(1)}g</div>
                      <div className="text-sm text-muted-foreground">Avg Fat</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold">{trends.averages.fiber_g.toFixed(1)}g</div>
                      <div className="text-sm text-muted-foreground">Avg Fiber</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Recommendations */}
              <Card>
                <CardHeader>
                  <CardTitle>Personalized Recommendations</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {trends.recommendations.map((recommendation, index) => (
                      <div key={index} className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                        <p className="text-sm">{recommendation}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <p>No trend data available</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="analysis" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Nutritional Analysis</CardTitle>
              <CardDescription>
                Detailed analysis and insights about your nutrition patterns
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Advanced nutritional analysis features coming soon...
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default NutritionDashboard