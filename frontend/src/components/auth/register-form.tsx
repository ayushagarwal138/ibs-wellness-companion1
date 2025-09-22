"use client"

import { useState } from "react"
import { useAuth } from "@/contexts/auth-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { OAuthButtons } from "./oauth-buttons"
import Link from "next/link"
import { toast } from "react-hot-toast"

export function RegisterForm() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    fullName: ""
  })
  const [isLoading, setIsLoading] = useState(false)
  const { register } = useAuth()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.email || !formData.password || !formData.fullName) return

    if (formData.password !== formData.confirmPassword) {
      toast.error("Passwords don't match")
      return
    }

    if (formData.password.length < 8) {
      toast.error("Password must be at least 8 characters long")
      return
    }

    // Check password strength requirements
    if (!/[A-Z]/.test(formData.password)) {
      toast.error("Password must contain at least one uppercase letter")
      return
    }

    if (!/[a-z]/.test(formData.password)) {
      toast.error("Password must contain at least one lowercase letter")
      return
    }

    if (!/\d/.test(formData.password)) {
      toast.error("Password must contain at least one digit")
      return
    }

    if (!/[!@#$%^&*(),.?":{}|<>]/.test(formData.password)) {
      toast.error("Password must contain at least one special character")
      return
    }

    try {
      setIsLoading(true)
      await register(formData.email, formData.password, formData.fullName)
    } catch (error) {
      // Error handling is done in the auth context with toast
      console.error("Registration error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const isFormValid = formData.email && formData.password && formData.confirmPassword && 
                     formData.fullName && formData.password === formData.confirmPassword

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl text-center">Create Account</CardTitle>
        <CardDescription className="text-center">
          Enter your information to create your IBS wellness account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <OAuthButtons callbackUrl="/dashboard" />
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="fullName">Full Name</Label>
            <Input
              id="fullName"
              name="fullName"
              type="text"
              placeholder="Enter your full name"
              value={formData.fullName}
              onChange={handleChange}
              required
              disabled={isLoading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
              required
              disabled={isLoading}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              name="password"
              type="password"
              placeholder="Create a password (min. 8 chars, 1 upper, 1 lower, 1 digit, 1 special)"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={isLoading}
              minLength={8}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword">Confirm Password</Label>
            <Input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              placeholder="Confirm your password"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              disabled={isLoading}
            />
          </div>

          <Button 
            type="submit" 
            className="w-full" 
            disabled={isLoading || !isFormValid}
          >
            {isLoading ? "Creating account..." : "Create Account"}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm">
          <span className="text-muted-foreground">Already have an account? </span>
          <Link 
            href="/login" 
            className="text-primary hover:underline font-medium"
          >
            Sign in
          </Link>
        </div>
      </CardContent>
    </Card>
  )
}