'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Loader2, RefreshCw, Activity, Target, AlertTriangle, TrendingUp, Heart } from 'lucide-react'
import { mlService } from '@/services/ml-service'
import { exerciseToleranceDataService } from '@/services/exercise-tolerance-data-service'
import type { ExerciseToleranceResponse } from '@/services/ml-service'
import { toast } from 'sonner'

interface ExerciseToleranceProps {
  className?: string
}

export function ExerciseTolerance({ className }: ExerciseToleranceProps) {
  const [exerciseData, setExerciseData] = useState<ExerciseToleranceResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadExerciseTolerance = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Fetch real user exercise and symptom data for the last 30 days
      const exerciseData = await exerciseToleranceDataService.fetchUserExerciseSymptomData(30)
      
      const response = await mlService.predictExerciseTolerance(exerciseData)
      
      setExerciseData(response)
      toast.success('Exercise tolerance analysis completed')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze exercise tolerance'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadExerciseTolerance()
  }, [])

  const getToleranceLevel = (score: number) => {
    if (score >= 0.8) return { level: 'Excellent', color: 'text-green-600', variant: 'default' as const }
    if (score >= 0.6) return { level: 'Good', color: 'text-blue-600', variant: 'secondary' as const }
    if (score >= 0.4) return { level: 'Moderate', color: 'text-yellow-600', variant: 'secondary' as const }
    return { level: 'Limited', color: 'text-red-600', variant: 'destructive' as const }
  }

  const getIntensityColor = (intensity: string) => {
    switch (intensity.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-50 border-green-200'
      case 'moderate': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'high': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  return (
    <div className={className}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Exercise Tolerance Analysis
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadExerciseTolerance}
              disabled={loading}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
              Refresh
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <div className="flex items-center gap-2 p-4 border border-red-200 bg-red-50 rounded-lg text-red-700">
              <AlertTriangle className="h-4 w-4" />
              <span>{error}</span>
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin" />
              <span className="ml-2">Analyzing exercise patterns...</span>
            </div>
          )}

          {exerciseData && !loading && (
            <>
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold mb-2">
                        {(exerciseData.tolerance_score * 100).toFixed(0)}%
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">Tolerance Score</p>
                      <Badge variant={getToleranceLevel(exerciseData.tolerance_score).variant}>
                        {getToleranceLevel(exerciseData.tolerance_score).level}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold mb-2">
                        {exerciseData.recommended_exercises.length}
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">Recommended Exercises</p>
                      <Badge variant="outline" className="text-green-600">
                        Available Options
                      </Badge>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold mb-2 flex items-center justify-center gap-1">
                        <Target className="h-6 w-6" />
                        {exerciseData.exercises_to_avoid.length}
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">Exercises to Avoid</p>
                      <Badge variant="outline" className="text-red-600">
                        Caution Items
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Recommended Exercises */}
              {exerciseData.recommended_exercises && exerciseData.recommended_exercises.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                    <Heart className="h-5 w-5" />
                    Recommended Exercises for You
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {exerciseData.recommended_exercises.map((exercise, index: number) => (
                      <div key={index} className="p-3 border rounded-lg bg-green-50 border-green-200">
                        <div className="flex items-center gap-2">
                          <Activity className="h-4 w-4 text-green-600" />
                          <span className="font-medium text-green-800 capitalize">{exercise.type}</span>
                        </div>
                        <div className="text-xs text-green-600 mt-1 space-y-1">
                          <p>Intensity: {exercise.intensity}/5</p>
                          <p>Duration: {exercise.duration} minutes</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Exercises to Avoid */}
              {exerciseData.exercises_to_avoid && exerciseData.exercises_to_avoid.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-red-600" />
                    Exercises to Avoid
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {exerciseData.exercises_to_avoid.map((exercise: string, index: number) => (
                      <div key={index} className="p-3 border rounded-lg bg-red-50 border-red-200">
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="h-4 w-4 text-red-600" />
                          <span className="font-medium text-red-800 capitalize">{exercise}</span>
                        </div>
                        <p className="text-xs text-red-600 mt-1">
                          May trigger or worsen symptoms
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Exercise Tolerance Analysis */}
              <div>
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Tolerance Analysis
                </h3>
                <div className="space-y-4">
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">Overall Exercise Tolerance</span>
                      <span className={`text-sm font-medium ${getToleranceLevel(exerciseData.tolerance_score).color}`}>
                        {(exerciseData.tolerance_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress 
                      value={exerciseData.tolerance_score * 100} 
                      className="h-3"
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      {exerciseData.tolerance_score >= 0.8 
                        ? 'You have excellent exercise tolerance with minimal symptom impact'
                        : exerciseData.tolerance_score >= 0.6
                        ? 'Good exercise tolerance - most activities are well tolerated'
                        : exerciseData.tolerance_score >= 0.4
                        ? 'Moderate tolerance - some exercises may trigger symptoms'
                        : 'Limited tolerance - exercise may significantly impact symptoms'
                      }
                    </p>
                  </div>

                  {/* Exercise Recommendations */}
                  <div className="border rounded-lg p-4 bg-blue-50 border-blue-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="h-4 w-4 text-blue-600" />
                      <span className="font-medium text-blue-800">Exercise Recommendations</span>
                    </div>
                    <p className="text-sm mb-2 text-blue-700">
                      Based on your tolerance analysis, we've identified {exerciseData.recommended_exercises.length} suitable 
                      exercises and {exerciseData.exercises_to_avoid.length} exercises to avoid.
                    </p>
                    <div className="flex items-center gap-4 text-xs text-blue-600">
                      <span>Recommended: {exerciseData.recommended_exercises.length}</span>
                      <span>•</span>
                      <span>To Avoid: {exerciseData.exercises_to_avoid.length}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Exercise Guidelines */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border rounded-lg p-4">
                  <h4 className="font-medium mb-2 text-green-700">Exercise Benefits</h4>
                  <ul className="text-sm space-y-1 text-green-600">
                    <li>• Improves gut motility</li>
                    <li>• Reduces stress and anxiety</li>
                    <li>• Enhances sleep quality</li>
                    <li>• Boosts overall well-being</li>
                  </ul>
                </div>
                
                <div className="border rounded-lg p-4">
                  <h4 className="font-medium mb-2 text-red-700">Exercise Precautions</h4>
                  <ul className="text-sm space-y-1 text-red-600">
                    <li>• Avoid exercising during flare-ups</li>
                    <li>• Stay hydrated but not overly full</li>
                    <li>• Listen to your body's signals</li>
                    <li>• Start slowly and build gradually</li>
                  </ul>
                </div>
              </div>



              {/* Confidence Score */}
              <div className="border-t pt-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Analysis Confidence</span>
                  <div className="flex items-center gap-2">
                    <Progress 
                      value={exerciseData.confidence * 100} 
                      className="h-2 w-24"
                    />
                    <span className="text-sm font-medium">
                      {(exerciseData.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Based on exercise type, intensity, duration, and symptom response correlation
                </p>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}