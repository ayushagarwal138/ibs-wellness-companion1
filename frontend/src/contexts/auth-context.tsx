'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'react-hot-toast'
import { analyticsService } from '@/lib/analytics'
import { notificationService } from '@/lib/notifications'
import { API_CONFIG } from '@/lib/config'

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  avatar?: string
  is_verified: boolean
  created_at: string
  last_login?: string | null
  phone_number?: string | null
  date_of_birth?: string | null
  gender?: string | null
  height_cm?: number | null
  weight_kg?: number | null
  ibs_type?: string | null
  diagnosis_date?: string | null
  is_active: boolean
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
  updateProfile: (data: Partial<User>) => Promise<void>
  checkOnboardingStatus: () => Promise<boolean>
  deleteAccount: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)
  const router = useRouter()



  // Ensure component is mounted before accessing localStorage
  useEffect(() => {
    setMounted(true)
    // Clean up any stuck auth_redirecting flags
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem('auth_redirecting')
    }
  }, [])

  // Check if user is authenticated on mount
  useEffect(() => {
    if (mounted) {
      checkAuth()
    }
  }, [mounted])

  const checkAuth = async () => {
    try {
      // Only access localStorage on client side
      if (typeof window === 'undefined') {
        setLoading(false)
        return
      }

      const token = localStorage.getItem('access_token')
      if (!token) {
        setLoading(false)
        return
      }

      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      setLoading(true)
      
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || 'Login failed')
      }

      const data = await response.json()
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
      }
      
      setUser(data.user)
      
      // Set up analytics and notifications for the user
      try {
        analyticsService.setUser(data.user.id, {
          email: data.user.email,
          first_name: data.user.first_name,
          last_name: data.user.last_name,
          ibs_type: data.user.ibs_type,
        })
        
        // Initialize notifications (non-blocking)
        notificationService.requestPermission().catch(console.error)
        
        // Track login event
        analyticsService.trackUserAction('login', 'authentication', 'success')
      } catch (error) {
        console.error('Analytics/notification setup error:', error)
      }
      
      toast.success('Login successful!')
      
      // Check onboarding status after login
      const onboardingCompleted = await checkOnboardingStatus()
      
      // Use setTimeout to ensure state updates are processed before navigation
      setTimeout(() => {
        // Check for stored redirect path
        const redirectPath = sessionStorage.getItem('redirect_after_login')
        if (redirectPath && onboardingCompleted) {
          // Clear the stored redirect path
          sessionStorage.removeItem('redirect_after_login')
          // Validate the redirect path is safe
          if (redirectPath.startsWith('/') && !redirectPath.includes('//')) {
            router.push(redirectPath)
            return
          }
        }
        
        // Default navigation logic
        if (onboardingCompleted) {
          router.push('/dashboard')
        } else {
          router.push('/onboarding')
        }
      }, 100)
    } catch (error: any) {
      // Track failed login
      analyticsService.trackUserAction('login', 'authentication', 'failed')
      toast.error(error.message || 'Login failed')
      throw error
    } finally {
      setLoading(false)
    }
  }

  const register = async (email: string, password: string, fullName: string) => {
    try {
      setLoading(true)
      
      // Split fullName into first and last name
      const trimmedName = fullName.trim()
      if (!trimmedName) {
        throw new Error('Please enter your name')
      }
      
      const nameParts = trimmedName.split(' ').filter(part => part.length > 0)
      const firstName = nameParts[0] || ''
      const lastName = nameParts.slice(1).join(' ') || 'User' // Use 'User' as default last name if only one name provided
      
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          confirm_password: password,
          first_name: firstName,
          last_name: lastName,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        
        // Handle validation errors with more specific messages
        if (response.status === 422 && error.detail) {
          const validationErrors = Array.isArray(error.detail) ? error.detail : [error.detail]
          const passwordError = validationErrors.find((err: any) => err.loc && err.loc.includes('password'))
          
          if (passwordError && passwordError.msg) {
            throw new Error(passwordError.msg.replace('Value error, ', ''))
          }
          
          // Handle other validation errors
          const errorMessages = validationErrors.map((err: any) => err.msg || err.message || 'Validation error').join(', ')
          throw new Error(errorMessages)
        }
        
        throw new Error(error.message || error.detail || 'Registration failed')
      }

      const data = await response.json()
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
      }
      
      setUser(data.user)
      
      // Set up analytics for new user
      try {
        analyticsService.setUser(data.user.id, {
          email: data.user.email,
          first_name: data.user.first_name,
          last_name: data.user.last_name,
          registration_date: new Date().toISOString(),
        })
        
        // Track registration event
        analyticsService.trackUserAction('register', 'authentication', 'success')
      } catch (error) {
        console.error('Analytics setup error:', error)
      }
      
      toast.success('Registration successful!')
      
      // After registration, always redirect to onboarding
      setTimeout(() => {
        router.push('/onboarding')
      }, 100)
    } catch (error: any) {
      // Track failed registration
      analyticsService.trackUserAction('register', 'authentication', 'failed')
      toast.error(error.message || 'Registration failed')
      throw error
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      // Track logout event before clearing user data
      if (user) {
        analyticsService.trackUserAction('logout', 'authentication', 'success')
      }
      
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token')
        if (token) {
          await fetch(`${API_CONFIG.BASE_URL}/api/v1/auth/logout`, {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${token}`,
            },
          })
        }
      }
      
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
      setUser(null)
      toast.success('Logged out successfully')
      router.push('/login')
    }
  }

  const refreshToken = async () => {
    try {
      if (typeof window === 'undefined') {
        throw new Error('No refresh token')
      }

      const refresh = localStorage.getItem('refresh_token')
      if (!refresh) {
        throw new Error('No refresh token')
      }

      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refresh }),
      })

      if (!response.ok) {
        throw new Error('Token refresh failed')
      }

      const data = await response.json()
      localStorage.setItem('access_token', data.access_token)
      
      return data.access_token
    } catch (error) {
      console.error('Token refresh failed:', error)
      await logout()
      throw error
    }
  }

  const checkOnboardingStatus = async (): Promise<boolean> => {
    try {
      if (typeof window === 'undefined') {
        return false
      }

      const token = localStorage.getItem('access_token')
      if (!token) {
        return false
      }

      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/users/onboarding-status`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        return data.onboarding_completed || false
      }
      
      return false
    } catch (error) {
      console.error('Failed to check onboarding status:', error)
      return false
    }
  }

  const updateProfile = async (data: Partial<User>) => {
    try {
      if (typeof window === 'undefined') {
        throw new Error('Cannot update profile on server side')
      }

      // Convert frontend data to backend enum format
      const convertedData = { ...data }
      
      // Convert gender to uppercase enum
      if (convertedData.gender) {
        const genderMap: { [key: string]: string } = {
          'male': 'MALE',
          'female': 'FEMALE',
          'other': 'OTHER',
          'prefer_not_to_say': 'PREFER_NOT_TO_SAY'
        }
        convertedData.gender = genderMap[convertedData.gender.toLowerCase()] || convertedData.gender
      }
      
      // Convert IBS type to uppercase enum with underscores
      if (convertedData.ibs_type) {
        const ibsTypeMap: { [key: string]: string | null } = {
          'ibs-d': 'IBS_D',
          'ibs-c': 'IBS_C', 
          'ibs-m': 'IBS_M',
          'ibs-u': 'IBS_U',
          'not_diagnosed': null // Handle not diagnosed case
        }
        const mappedType = ibsTypeMap[convertedData.ibs_type.toLowerCase()]
        if (mappedType === null) {
          delete convertedData.ibs_type // Remove field if not diagnosed
        } else {
          convertedData.ibs_type = mappedType || convertedData.ibs_type
        }
      }

      const token = localStorage.getItem('access_token')
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/users/profile`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(convertedData),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || 'Profile update failed')
      }

      const updatedUser = await response.json()
      
      // Update user state with the response from server
      setUser(prevUser => ({
        ...prevUser,
        ...updatedUser
      }))
      
      toast.success('Profile updated successfully!')
      
      return updatedUser
    } catch (error: any) {
      toast.error(error.message || 'Profile update failed')
      throw error
    }
  }

  const deleteAccount = async () => {
    try {
      setLoading(true)
      
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token')
        if (!token) {
          throw new Error('No authentication token found')
        }

        const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/users/account`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        })

        if (!response.ok) {
          let errorMessage = 'Account deletion failed'
          
          try {
            const errorData = await response.json()
            errorMessage = errorData.detail || errorData.message || errorMessage
          } catch (parseError) {
            // If we can't parse the error response, use status-based messages
            if (response.status === 401) {
              errorMessage = 'Unauthorized - please log in again'
            } else if (response.status === 403) {
              errorMessage = 'Access denied - insufficient permissions'
            } else if (response.status === 404) {
              errorMessage = 'Account not found'
            } else if (response.status >= 500) {
              errorMessage = 'Server error - please try again later'
            }
          }
          
          throw new Error(errorMessage)
        }

        // Track account deletion event before clearing user data
        if (user) {
          analyticsService.trackUserAction('delete_account', 'account_management', 'success')
        }

        // Clear all user data and tokens
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        setUser(null)
        
        toast.success('Account deleted successfully')
        router.push('/')
      }
    } catch (error: any) {
      // Enhanced error handling with specific error types
      let errorMessage = 'Account deletion failed'
      
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessage = 'Network error - please check your connection'
      } else if (error.message) {
        errorMessage = error.message
      }
      
      console.error('Delete account error:', error)
      toast.error(errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    refreshToken,
    updateProfile,
    checkOnboardingStatus,
    deleteAccount,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}