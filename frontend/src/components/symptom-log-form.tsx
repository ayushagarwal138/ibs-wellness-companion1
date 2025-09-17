"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface SymptomLogFormProps {
  onSubmit?: (data: SymptomLogData) => void
}

interface SymptomLogData {
  severity: number
  notes: string
  symptoms: string[]
  timestamp: Date
}

const COMMON_SYMPTOMS = [
  "Abdominal Pain",
  "Bloating",
  "Gas",
  "Diarrhea",
  "Constipation",
  "Nausea",
  "Cramping",
  "Urgency"
]

export function SymptomLogForm({ onSubmit }: SymptomLogFormProps) {
  const [severity, setSeverity] = useState(1)
  const [notes, setNotes] = useState("")
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([])

  const handleSymptomToggle = (symptom: string) => {
    setSelectedSymptoms(prev => 
      prev.includes(symptom) 
        ? prev.filter(s => s !== symptom)
        : [...prev, symptom]
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    const data: SymptomLogData = {
      severity,
      notes,
      symptoms: selectedSymptoms,
      timestamp: new Date()
    }

    onSubmit?.(data)
    
    // Reset form
    setSeverity(1)
    setNotes("")
    setSelectedSymptoms([])
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
        <form onSubmit={handleSubmit} className="space-y-6">
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

          {/* Symptoms Selection */}
          <div className="space-y-3">
            <Label>Select Symptoms</Label>
            <div className="grid grid-cols-2 gap-2">
              {COMMON_SYMPTOMS.map((symptom) => (
                <button
                  key={symptom}
                  type="button"
                  onClick={() => handleSymptomToggle(symptom)}
                  className={`p-3 text-sm rounded-md border transition-colors ${
                    selectedSymptoms.includes(symptom)
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-background hover:bg-accent hover:text-accent-foreground"
                  }`}
                >
                  {symptom}
                </button>
              ))}
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

          <Button type="submit" className="w-full">
            Log Symptoms
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}