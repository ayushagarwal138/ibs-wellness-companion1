'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Loader2, RefreshCw, AlertTriangle, TrendingUp } from 'lucide-react'
import { mlService } from '@/services/ml-service'
import type { DietaryTriggerResponse } from '@/services/ml-service'
import { toast } from 'sonner'

interface DietaryTriggersProps {
  className?: string
}

export function DietaryTriggers({ className }: DietaryTriggersProps) {
  const [dietaryData, setDietaryData] = useState<DietaryTriggerResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadDietaryTriggers = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await mlService.predictDietaryTriggers({
        foods_consumed: ['dairy', 'gluten', 'spicy_food'],
        meal_timing: ['morning', 'afternoon', 'evening'],
        portion_sizes: ['medium', 'large', 'small'],
        timeframe_hours: 24
      })
      
      setDietaryData(response)
      toast.success('Dietary triggers analysis completed')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze dietary triggers'
      setError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDietaryTriggers()
  }, [])

  const getRiskColor = (probability: number) => {
    if (probability >= 0.7) return 'text-red-600'
    if (probability >= 0.4) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getRiskBadgeVariant = (probability: number) => {
    if (probability >= 0.7) return 'destructive'
    if (probability >= 0.4) return 'secondary'
    return 'default'
  }

  return (
    <div className={className}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Dietary Triggers Analysis
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadDietaryTriggers}
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
              <span className="ml-2">Analyzing dietary patterns...</span>
            </div>
          )}

          {dietaryData && !loading && (
            <>
              {/* Overall Analysis */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold">
                        {(dietaryData.confidence * 100).toFixed(0)}%
                      </div>
                      <p className="text-sm text-muted-foreground">Analysis Confidence</p>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold">
                        {dietaryData.trigger_foods?.length || 0}
                      </div>
                      <p className="text-sm text-muted-foreground">Potential Triggers</p>
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold">
                        {dietaryData.safe_foods?.length || 0}
                      </div>
                      <p className="text-sm text-muted-foreground">Safe Foods</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Trigger Foods */}
              {dietaryData.trigger_foods && dietaryData.trigger_foods.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-red-500" />
                    Potential Trigger Foods
                  </h3>
                  <div className="space-y-3">
                    {dietaryData.trigger_foods.map((trigger, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="font-medium capitalize">{trigger.food}</span>
                            <Badge variant={getRiskBadgeVariant(trigger.trigger_probability)}>
                              {(trigger.trigger_probability * 100).toFixed(0)}% Risk
                            </Badge>
                          </div>
                          <span className={`text-sm font-medium ${getRiskColor(trigger.trigger_probability)}`}>
                            {trigger.trigger_probability >= 0.7 ? 'High Risk' : 
                             trigger.trigger_probability >= 0.4 ? 'Medium Risk' : 'Low Risk'}
                          </span>
                        </div>
                        <Progress 
                          value={trigger.trigger_probability * 100} 
                          className="h-2"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Safe Foods */}
              {dietaryData.safe_foods && dietaryData.safe_foods.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3 text-green-600">
                    Safe Foods
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {dietaryData.safe_foods.map((food, index) => (
                      <Badge key={index} variant="outline" className="justify-center py-2">
                        {food}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {dietaryData.recommendations && dietaryData.recommendations.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3">Recommendations</h3>
                  <div className="space-y-2">
                    {dietaryData.recommendations.map((rec: string, index: number) => (
                      <div key={index} className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-800">
                        {rec}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Analysis Metadata */}
              <div className="text-xs text-muted-foreground border-t pt-4">
                <p>Analysis based on dietary history and symptom correlation</p>
                <p>Confidence: {(dietaryData.confidence * 100).toFixed(1)}%</p>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}