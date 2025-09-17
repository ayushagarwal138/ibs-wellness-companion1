"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface DietLogFormProps {
  onSubmit?: (data: DietLogData) => void
}

interface DietLogData {
  foodName: string
  quantity: string
  mealType: string
  timestamp: Date
  notes: string
}

const MEAL_TYPES = [
  "Breakfast",
  "Lunch", 
  "Dinner",
  "Snack"
]

export function DietLogForm({ onSubmit }: DietLogFormProps) {
  const [foodName, setFoodName] = useState("")
  const [quantity, setQuantity] = useState("")
  const [mealType, setMealType] = useState("Breakfast")
  const [notes, setNotes] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!foodName.trim()) return

    const data: DietLogData = {
      foodName: foodName.trim(),
      quantity: quantity.trim(),
      mealType,
      timestamp: new Date(),
      notes: notes.trim()
    }

    onSubmit?.(data)
    
    // Reset form
    setFoodName("")
    setQuantity("")
    setMealType("Breakfast")
    setNotes("")
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Log Your Food</CardTitle>
        <CardDescription>
          Track what you eat to identify potential trigger foods
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Food Name */}
          <div className="space-y-2">
            <Label htmlFor="foodName">Food Item *</Label>
            <Input
              id="foodName"
              type="text"
              value={foodName}
              onChange={(e) => setFoodName(e.target.value)}
              placeholder="e.g., Grilled chicken salad"
              required
            />
          </div>

          {/* Quantity */}
          <div className="space-y-2">
            <Label htmlFor="quantity">Quantity/Portion</Label>
            <Input
              id="quantity"
              type="text"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              placeholder="e.g., 1 cup, 2 slices, 1 medium bowl"
            />
          </div>

          {/* Meal Type */}
          <div className="space-y-3">
            <Label>Meal Type</Label>
            <div className="grid grid-cols-2 gap-2">
              {MEAL_TYPES.map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setMealType(type)}
                  className={`p-3 text-sm rounded-md border transition-colors ${
                    mealType === type
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-background hover:bg-accent hover:text-accent-foreground"
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any additional details about preparation, ingredients, or how you felt..."
              className="w-full min-h-[80px] p-3 rounded-md border border-input bg-background text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
          </div>

          <Button type="submit" className="w-full" disabled={!foodName.trim()}>
            Log Food
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}