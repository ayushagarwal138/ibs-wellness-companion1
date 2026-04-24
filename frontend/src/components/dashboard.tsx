"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { SymptomLogForm } from "./symptom-log-form"
import { DietLogForm } from "./diet-log-form"

interface SymptomLog {
  id: string
  severity: number
  symptoms: string[]
  notes: string
  timestamp: Date
}

interface DietLog {
  id: string
  foodName: string
  quantity: string
  mealType: string
  notes: string
  timestamp: Date
}

export function Dashboard() {
  const [activeTab, setActiveTab] = useState<"overview" | "log-symptoms" | "log-diet">("overview")
  const [symptomLogs, setSymptomLogs] = useState<SymptomLog[]>([])
  const [dietLogs, setDietLogs] = useState<DietLog[]>([])

  // Load data from localStorage on component mount
  useEffect(() => {
    const savedSymptomLogs = localStorage.getItem("symptom-logs")
    const savedDietLogs = localStorage.getItem("diet-logs")
    
    if (savedSymptomLogs) {
      setSymptomLogs(JSON.parse(savedSymptomLogs).map((log: any) => ({
        ...log,
        timestamp: new Date(log.timestamp)
      })))
    }
    
    if (savedDietLogs) {
      setDietLogs(JSON.parse(savedDietLogs).map((log: any) => ({
        ...log,
        timestamp: new Date(log.timestamp)
      })))
    }
  }, [])

  const handleSymptomSubmit = (data: any) => {
    const newLog: SymptomLog = {
      id: Date.now().toString(),
      ...data
    }
    
    const updatedLogs = [...symptomLogs, newLog]
    setSymptomLogs(updatedLogs)
    localStorage.setItem("symptom-logs", JSON.stringify(updatedLogs))
    setActiveTab("overview")
  }

  const handleDietSubmit = (data: any) => {
    const newLog: DietLog = {
      id: Date.now().toString(),
      ...data
    }
    
    const updatedLogs = [...dietLogs, newLog]
    setDietLogs(updatedLogs)
    localStorage.setItem("diet-logs", JSON.stringify(updatedLogs))
    setActiveTab("overview")
  }

  const getRecentLogs = (logs: any[], count: number = 5) => {
    return logs
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, count)
  }

  const getAverageSeverity = () => {
    if (symptomLogs.length === 0) return 0
    const total = symptomLogs.reduce((sum, log) => sum + log.severity, 0)
    return (total / symptomLogs.length).toFixed(1)
  }

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Symptom Logs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{symptomLogs.length}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Average Severity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{getAverageSeverity()}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Food Items Logged</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dietLogs.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Symptoms */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Symptoms</CardTitle>
            <CardDescription>Your latest symptom entries</CardDescription>
          </CardHeader>
          <CardContent>
            {symptomLogs.length === 0 ? (
              <p className="text-muted-foreground text-center py-4">
                No symptoms logged yet. Start tracking to see patterns!
              </p>
            ) : (
              <div className="space-y-3">
                {getRecentLogs(symptomLogs).map((log) => (
                  <div key={log.id} className="border rounded-lg p-3">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium">Severity: {log.severity}/10</span>
                      <span className="text-xs text-muted-foreground">
                        {log.timestamp.toLocaleDateString()}
                      </span>
                    </div>
                    <div className="text-sm text-muted-foreground mb-1">
                      {log.symptoms.join(", ")}
                    </div>
                    {log.notes && (
                      <div className="text-xs text-muted-foreground">
                        {log.notes}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Diet */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Foods</CardTitle>
            <CardDescription>Your latest food entries</CardDescription>
          </CardHeader>
          <CardContent>
            {dietLogs.length === 0 ? (
              <p className="text-muted-foreground text-center py-4">
                No foods logged yet. Start tracking your diet!
              </p>
            ) : (
              <div className="space-y-3">
                {getRecentLogs(dietLogs).map((log) => (
                  <div key={log.id} className="border rounded-lg p-3">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium">{log.foodName}</span>
                      <span className="text-xs text-muted-foreground">
                        {log.timestamp.toLocaleDateString()}
                      </span>
                    </div>
                    <div className="text-sm text-muted-foreground mb-1">
                      {log.mealType} {log.quantity && `• ${log.quantity}`}
                    </div>
                    {log.notes && (
                      <div className="text-xs text-muted-foreground">
                        {log.notes}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Navigation */}
      <div className="flex flex-wrap gap-2 mb-8">
        <Button
          variant={activeTab === "overview" ? "default" : "outline"}
          onClick={() => setActiveTab("overview")}
        >
          Dashboard
        </Button>
        <Button
          variant={activeTab === "log-symptoms" ? "default" : "outline"}
          onClick={() => setActiveTab("log-symptoms")}
        >
          Log Symptoms
        </Button>
        <Button
          variant={activeTab === "log-diet" ? "default" : "outline"}
          onClick={() => setActiveTab("log-diet")}
        >
          Log Food
        </Button>
      </div>

      {/* Content */}
      {activeTab === "overview" && renderOverview()}
      {activeTab === "log-symptoms" && <SymptomLogForm onSubmit={handleSymptomSubmit} />}
      {activeTab === "log-diet" && <DietLogForm onSubmit={handleDietSubmit} />}
    </div>
  )
}