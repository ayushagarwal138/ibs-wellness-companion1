"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Loader2 } from "lucide-react"
import { apiService } from "@/lib/api"
import { SeverityLevel } from "@ibs-wellness/shared-types"

// Custom interface that matches the backend's actual SymptomLogCreate expectations
interface SymptomLogCreateData {
  symptom_id: number
  severity: SeverityLevel
  logged_at: string
  duration_minutes?: number
  notes?: string
  stress_level?: number
  sleep_quality?: number
  bristol_stool_type?: string
  bowel_movement_frequency?: number
  pain_location?: string
  pain_type?: string
  exercise_minutes?: number
  potential_triggers?: string
}

interface SymptomLogFormProps {
  onSubmit?: (data: SymptomLogCreateData) => void
}

interface Symptom {
  id: number
  name: string
  description: string | null
  category: string
}

export function SymptomLogForm({ onSubmit }: SymptomLogFormProps) {
  const [severity, setSeverity] = useState(5)
  const [notes, setNotes] = useState("")
  const [stressLevel, setStressLevel] = useState(5)
  const [sleepQuality, setSleepQuality] = useState(5)
  const [duration, setDuration] = useState(30)
  const [selectedSymptomId, setSelectedSymptomId] = useState<number | null>(null)
  const [availableSymptoms, setAvailableSymptoms] = useState<Symptom[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Fetch available symptoms from API
  useEffect(() => {
    const fetchSymptoms = async () => {
      setIsLoading(true)
      try {
        const data = await apiService.getAvailableSymptoms()
        setAvailableSymptoms(data)
      } catch (error) {
        console.error('Error fetching symptoms:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchSymptoms()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedSymptomId) {
      alert('Please select a symptom')
      return
    }
    
    setIsSubmitting(true)
    
    // Map 1-10 scale to SeverityLevel enum values
    const severityMap: Record<number, SeverityLevel> = {
      1: SeverityLevel.MILD,
      2: SeverityLevel.MILD,
      3: SeverityLevel.MILD,
      4: SeverityLevel.MODERATE,
      5: SeverityLevel.MODERATE,
      6: SeverityLevel.MODERATE,
      7: SeverityLevel.SEVERE,
      8: SeverityLevel.SEVERE,
      9: SeverityLevel.SEVERE,
      10: SeverityLevel.SEVERE
    }
    
    const data: SymptomLogCreateData = {
      symptom_id: selectedSymptomId,
      severity: severityMap[severity] || SeverityLevel.MODERATE,
      notes,
      stress_level: stressLevel,
      sleep_quality: sleepQuality,
      duration_minutes: duration,
      logged_at: new Date().toISOString()
    }

    try {
      // If onSubmit is provided, use it (for local state management)
      if (onSubmit) {
        onSubmit(data)
      } else {
        // Otherwise submit directly to API
        await apiService.createSymptomLog(data as any) // Type assertion since API types are misaligned
        
        alert('Symptom logged successfully!')
        // Reset form
        setSeverity(5)
        setNotes("")
        setStressLevel(5)
        setSleepQuality(5)
        setDuration(30)
        setSelectedSymptomId(null)
      }
    } catch (error) {
      console.error('Error submitting symptom log:', error)
      alert('Failed to submit symptom log. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Log Your Symptoms</CardTitle>
        <CardDescription>
          Track your IBS symptoms to help identify patterns and triggers
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <span className="ml-2">Loading symptoms...</span>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Symptom Selection */}
            <div className="space-y-3">
              <Label htmlFor="symptom">Select Symptom</Label>
              <div className="grid grid-cols-2 gap-2 max-h-[200px] overflow-y-auto">
                {availableSymptoms.map((symptom) => (
                  <button
                    key={symptom.id}
                    type="button"
                    onClick={() => setSelectedSymptomId(symptom.id)}
                    className={`p-3 text-sm rounded-md border transition-colors ${
                      selectedSymptomId === symptom.id
                        ? "bg-primary text-primary-foreground border-primary"
                        : "bg-background hover:bg-accent hover:text-accent-foreground"
                    }`}
                  >
                    {symptom.name}
                  </button>
                ))}
              </div>
              {availableSymptoms.length === 0 && !isLoading && (
                <p className="text-sm text-muted-foreground">No symptoms available. Please try again later.</p>
              )}
            </div>

            {/* Severity Scale */}
            <div className="space-y-2">
              <Label htmlFor="severity">Severity (1-10)</Label>
              <div className="flex items-center space-x-4">
                <Input
                  id="severity"
                  type="range"
                  min="1"
                  max="10"
                  value={severity}
                  onChange={(e) => setSeverity(Number(e.target.value))}
                  className="flex-1"
                />
                <span className="text-lg font-semibold w-8 text-center">
                  {severity}
                </span>
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Mild</span>
                <span>Severe</span>
              </div>
            </div>

            {/* Duration */}
            <div className="space-y-2">
              <Label htmlFor="duration">Duration (minutes)</Label>
              <Input
                id="duration"
                type="number"
                min="1"
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
              />
            </div>

            {/* Stress Level */}
            <div className="space-y-2">
              <Label htmlFor="stressLevel">Stress Level (1-10)</Label>
              <div className="flex items-center space-x-4">
                <Input
                  id="stressLevel"
                  type="range"
                  min="1"
                  max="10"
                  value={stressLevel}
                  onChange={(e) => setStressLevel(Number(e.target.value))}
                  className="flex-1"
                />
                <span className="text-lg font-semibold w-8 text-center">
                  {stressLevel}
                </span>
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Low</span>
                <span>High</span>
              </div>
            </div>

            {/* Sleep Quality */}
            <div className="space-y-2">
              <Label htmlFor="sleepQuality">Sleep Quality (1-10)</Label>
              <div className="flex items-center space-x-4">
                <Input
                  id="sleepQuality"
                  type="range"
                  min="1"
                  max="10"
                  value={sleepQuality}
                  onChange={(e) => setSleepQuality(Number(e.target.value))}
                  className="flex-1"
                />
                <span className="text-lg font-semibold w-8 text-center">
                  {sleepQuality}
                </span>
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Poor</span>
                <span>Excellent</span>
              </div>
            </div>

            {/* Notes */}
            <div className="space-y-2">
              <Label htmlFor="notes">Additional Notes</Label>
              <textarea
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Describe any additional details about your symptoms..."
                className="w-full min-h-[100px] p-3 rounded-md border border-input bg-background text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
            </div>

            <Button 
              type="submit" 
              className="w-full"
              disabled={isSubmitting || !selectedSymptomId}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Logging Symptom...
                </>
              ) : (
                'Log Symptom'
              )}
            </Button>
          </form>
        )}
      </CardContent>
    </Card>
  )
}