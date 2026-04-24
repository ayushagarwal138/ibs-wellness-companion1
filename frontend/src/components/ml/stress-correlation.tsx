'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Loader2, RefreshCw, Brain, TrendingUp, AlertTriangle } from 'lucide-react'
import { mlService } from '@/services/ml-service'
import type { StressSymptomCorrelationResponse } from '@/services/ml-service'
import { toast } from 'sonner'

interface StressCorrelationProps {
  className?: string
}

export function StressCorrelation({ className }: StressCorrelationProps) {
  const [stressData, setStressData] = useState<StressSymptomCorrelationResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadStressCorrelation = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Use sample data for the stress-symptom correlation analysis
      const response = await mlService.predictStressSymptomCorrelation({
        stress_levels: {
          'day1': 7,
          'day2': 5,
          'day3': 8,
          'day4': 6,
          'day5': 9,
          'day6': 4,
          'day7': 7
        },
        symptoms: {
          'abdominal_pain': 6,
          'bloating': 7,
          'diarrhea': 5,
          'constipation': 4,
          'nausea': 3,
          'fatigue': 6,
          'cramping': 7
        },
        timeframe_days: 30
      })
      
      setStressData(response)
      toast.success('Stress correlation analysis completed successfully')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze stress correlation'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStressCorrelation()
  }, [])

  const getCorrelationLevel = (strength: number) => {
    if (strength >= 0.7) return { level: 'Strong', color: 'text-red-600', variant: 'destructive' as const }
    if (strength >= 0.4) return { level: 'Moderate', color: 'text-yellow-600', variant: 'secondary' as const }
    return { level: 'Weak', color: 'text-green-600', variant: 'default' as const }
  }

  return (
    <div className={className}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Stress-Symptom Correlation
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadStressCorrelation}
              disabled={loading}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-800">
              <AlertTriangle className="h-4 w-4" />
              {error}
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin" />
              <span className="ml-2">Analyzing stress-symptom correlation...</span>
            </div>
          )}

          {stressData && !loading && (
            <>
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold mb-2">
                        {(stressData.correlation_score * 100).toFixed(0)}%
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">Correlation Strength</p>
                      <Badge variant={getCorrelationLevel(stressData.correlation_score).variant}>
                        {getCorrelationLevel(stressData.correlation_score).level}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold mb-2">
                        {stressData.stress_triggers.length}
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">Stress Triggers Identified</p>
                      <Badge variant="outline" className="text-blue-600">
                        {stressData.stress_triggers.length > 0 ? 'Triggers Found' : 'No Triggers'}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Correlation Visualization */}
              <div>
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Correlation Analysis
                </h3>
                <div className="space-y-4">
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">Stress-Symptom Correlation</span>
                      <span className={`text-sm font-medium ${getCorrelationLevel(stressData.correlation_score).color}`}>
                        {(stressData.correlation_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress 
                      value={stressData.correlation_score * 100} 
                      className="h-3"
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      {stressData.correlation_score >= 0.7 
                        ? 'Strong correlation indicates stress significantly affects your symptoms'
                        : stressData.correlation_score >= 0.4
                        ? 'Moderate correlation suggests stress has some impact on symptoms'
                        : 'Weak correlation indicates stress has minimal direct impact on symptoms'
                      }
                    </p>
                  </div>
                </div>
              </div>

              {/* Stress Triggers */}
              {stressData.stress_triggers && stressData.stress_triggers.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3">Identified Stress Triggers</h3>
                  <div className="space-y-2">
                    {stressData.stress_triggers.map((trigger: string, index: number) => (
                      <div key={index} className="p-3 bg-orange-50 border border-orange-200 rounded-lg text-orange-800">
                        • {trigger}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Management Strategies */}
              {stressData.management_strategies && stressData.management_strategies.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3">Stress Management Strategies</h3>
                  <div className="space-y-2">
                    {stressData.management_strategies.map((strategy: string, index: number) => (
                      <div key={index} className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-800">
                        • {strategy}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Analysis Summary */}
              <div className="border-t pt-4">
                <div className="text-sm text-muted-foreground">
                  <p>
                    Analysis based on stress level and symptom severity data over the past 30 days. 
                    {stressData.correlation_score >= 0.4 
                      ? ' Consider implementing the suggested stress management strategies to help reduce symptom severity.'
                      : ' While stress correlation is low, maintaining good stress management practices is still beneficial for overall health.'
                    }
                  </p>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}