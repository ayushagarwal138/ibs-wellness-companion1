'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Loader2, RefreshCw, Brain, TrendingUp, AlertTriangle } from 'lucide-react'
import { mlService } from '@/services/ml-service'
import type { StressSymptomCorrelationResponse } from '@/services/ml-service'
import { stressCorrelationDataService } from '@/services/stress-correlation-data-service'
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
      // Fetch real user data instead of using hardcoded values
      const userData = await stressCorrelationDataService.fetchUserStressSymptomData(30)
      
      const response = await mlService.predictStressSymptomCorrelation({
        stress_levels: userData.stress_levels,
        symptom_severity: userData.symptom_severity,
        timeframe_days: userData.timeframe_days
      })
      
      setStressData(response)
      toast.success(`Stress correlation analysis completed using ${userData.data_points} data points`)
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

  const getImpactLevel = (score: number) => {
    if (score >= 0.7) return { level: 'High Impact', color: 'text-red-600' }
    if (score >= 0.4) return { level: 'Moderate Impact', color: 'text-yellow-600' }
    return { level: 'Low Impact', color: 'text-green-600' }
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
              <span className="ml-2">Analyzing stress patterns...</span>
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
                        {(stressData.correlation_strength * 100).toFixed(0)}%
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">Correlation Strength</p>
                      <Badge variant={getCorrelationLevel(stressData.correlation_strength).variant}>
                        {getCorrelationLevel(stressData.correlation_strength).level}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold mb-2">
                        {(stressData.stress_impact_score * 100).toFixed(0)}%
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">Impact Score</p>
                      <Badge variant="outline" className={getImpactLevel(stressData.stress_impact_score).color}>
                        {getImpactLevel(stressData.stress_impact_score).level}
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
                      <span className={`text-sm font-medium ${getCorrelationLevel(stressData.correlation_strength).color}`}>
                        {(stressData.correlation_strength * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress 
                      value={stressData.correlation_strength * 100} 
                      className="h-3"
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      {stressData.correlation_strength >= 0.7 
                        ? 'Strong correlation indicates stress significantly affects your symptoms'
                        : stressData.correlation_strength >= 0.4
                        ? 'Moderate correlation suggests stress has some impact on symptoms'
                        : 'Weak correlation indicates stress has minimal direct impact on symptoms'
                      }
                    </p>
                  </div>

                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">Stress Impact on Symptoms</span>
                      <span className={`text-sm font-medium ${getImpactLevel(stressData.stress_impact_score).color}`}>
                        {(stressData.stress_impact_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress 
                      value={stressData.stress_impact_score * 100} 
                      className="h-3"
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      This score represents how much stress contributes to your symptom severity
                    </p>
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              {stressData.recommendations && stressData.recommendations.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3">Stress Management Recommendations</h3>
                  <div className="space-y-2">
                    {stressData.recommendations.map((rec: string, index: number) => (
                      <div key={index} className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-800">
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
                      value={stressData.confidence * 100} 
                      className="h-2 w-24"
                    />
                    <span className="text-sm font-medium">
                      {(stressData.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Based on stress level and symptom severity data analysis over the past 30 days
                </p>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}