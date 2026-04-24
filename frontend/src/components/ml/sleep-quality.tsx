'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Loader2, RefreshCw, Moon, Clock, AlertTriangle, TrendingUp } from 'lucide-react'
import { mlService } from '@/services/ml-service'
import { sleepQualityDataService } from '@/services/sleep-quality-data-service'
import type { SleepQualityImpactResponse } from '@/services/ml-service'
import { toast } from 'sonner'

interface SleepQualityProps {
  className?: string
}

export function SleepQuality({ className }: SleepQualityProps) {
  const [sleepData, setSleepData] = useState<SleepQualityImpactResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadSleepQuality = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Fetch real user sleep and symptom data for the last 30 days
      const sleepData = await sleepQualityDataService.fetchUserSleepSymptomData(30)
      
      const response = await mlService.predictSleepQualityImpact(sleepData)
      
      setSleepData(response)
      toast.success('Sleep quality analysis completed')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze sleep quality impact'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSleepQuality()
  }, [])

  const getImpactLevel = (score: number) => {
    if (score >= 0.7) return { level: 'High Impact', color: 'text-red-600', variant: 'destructive' as const }
    if (score >= 0.4) return { level: 'Moderate Impact', color: 'text-yellow-600', variant: 'secondary' as const }
    return { level: 'Low Impact', color: 'text-green-600', variant: 'default' as const }
  }

  const getSleepQuality = (hours: number) => {
    if (hours >= 7 && hours <= 9) return { quality: 'Optimal', color: 'text-green-600' }
    if (hours >= 6 && hours < 7) return { quality: 'Adequate', color: 'text-yellow-600' }
    if (hours > 9) return { quality: 'Excessive', color: 'text-blue-600' }
    return { quality: 'Insufficient', color: 'text-red-600' }
  }

  return (
    <div className={className}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Moon className="h-5 w-5" />
              Sleep Quality Impact
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadSleepQuality}
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
              <span className="ml-2">Analyzing sleep patterns...</span>
            </div>
          )}

          {sleepData && !loading && (
            <>
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold mb-2">
                        {(sleepData.sleep_impact_score * 100).toFixed(0)}%
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">Sleep Impact Score</p>
                      <Badge variant={getImpactLevel(sleepData.sleep_impact_score).variant}>
                        {getImpactLevel(sleepData.sleep_impact_score).level}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold mb-2 flex items-center justify-center gap-1">
                        <Clock className="h-6 w-6" />
                        {sleepData.optimal_sleep_hours}h
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">Optimal Sleep Duration</p>
                      <Badge variant="outline" className={getSleepQuality(sleepData.optimal_sleep_hours).color}>
                        {getSleepQuality(sleepData.optimal_sleep_hours).quality}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Sleep Impact Analysis */}
              <div>
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Sleep Impact Analysis
                </h3>
                <div className="space-y-4">
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">Sleep Quality Impact on Symptoms</span>
                      <span className={`text-sm font-medium ${getImpactLevel(sleepData.sleep_impact_score).color}`}>
                        {(sleepData.sleep_impact_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress 
                      value={sleepData.sleep_impact_score * 100} 
                      className="h-3"
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      {sleepData.sleep_impact_score >= 0.7 
                        ? 'Poor sleep quality significantly worsens your IBS symptoms'
                        : sleepData.sleep_impact_score >= 0.4
                        ? 'Sleep quality has moderate impact on your symptom severity'
                        : 'Sleep quality has minimal direct impact on your symptoms'
                      }
                    </p>
                  </div>

                  {/* Sleep Duration Recommendation */}
                  <div className="border rounded-lg p-4 bg-blue-50">
                    <div className="flex items-center gap-2 mb-2">
                      <Clock className="h-4 w-4 text-blue-600" />
                      <span className="font-medium text-blue-800">Optimal Sleep Duration</span>
                    </div>
                    <p className="text-blue-700 text-sm mb-2">
                      Based on your symptom patterns, {sleepData.optimal_sleep_hours} hours of sleep per night 
                      appears to be optimal for minimizing IBS symptoms.
                    </p>
                    <div className="flex items-center gap-4 text-xs text-blue-600">
                      <span>Current recommendation: {sleepData.optimal_sleep_hours} hours</span>
                      <span>•</span>
                      <span>Quality matters as much as quantity</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Sleep Quality Tips */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border rounded-lg p-4">
                  <h4 className="font-medium mb-2 text-green-700">Good Sleep Habits</h4>
                  <ul className="text-sm space-y-1 text-green-600">
                    <li>• Consistent sleep schedule</li>
                    <li>• Cool, dark environment</li>
                    <li>• Avoid screens before bed</li>
                    <li>• Regular exercise (not before bed)</li>
                  </ul>
                </div>
                
                <div className="border rounded-lg p-4">
                  <h4 className="font-medium mb-2 text-red-700">Sleep Disruptors</h4>
                  <ul className="text-sm space-y-1 text-red-600">
                    <li>• Late meals or caffeine</li>
                    <li>• Irregular bedtime</li>
                    <li>• Stress and anxiety</li>
                    <li>• IBS symptoms at night</li>
                  </ul>
                </div>
              </div>

              {/* Recommendations */}
              {sleepData.recommendations && sleepData.recommendations.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3">Sleep Improvement Recommendations</h3>
                  <div className="space-y-2">
                    {sleepData.recommendations.map((rec: string, index: number) => (
                      <div key={index} className="p-3 bg-purple-50 border border-purple-200 rounded-lg text-purple-800">
                        {rec}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Confidence Score */}
              <div className="border-t pt-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Analysis Confidence</span>
                  <div className="flex items-center gap-2">
                    <Progress 
                      value={sleepData.confidence * 100} 
                      className="h-2 w-24"
                    />
                    <span className="text-sm font-medium">
                      {(sleepData.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Based on sleep duration, quality scores, and symptom correlation analysis
                </p>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}