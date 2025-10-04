/**
 * useUserSync Hook
 * 
 * Provides real-time user synchronization with optimistic updates,
 * error handling, and ML prediction integration.
 */

import { useState, useCallback, useEffect, useRef } from 'react'
import { toast } from 'react-hot-toast'
import { useAuth } from '@/contexts/auth-context'
import { UI_CONFIG } from '@/lib/config'

interface SyncStatus {
  syncing: boolean
  lastSync: Date | null
  error: string | null
  pendingChanges: boolean
}

interface MLPredictions {
  risk_assessment?: any
  recommendations?: any
  generated_at?: string
  model_version?: string
  error?: string
}

interface SyncResult {
  success: boolean
  user?: any
  changes?: any
  ml_predictions?: MLPredictions
  timestamp?: string
  sync_id?: string
  error?: string
  details?: any
}

interface ValidationResult {
  valid: boolean
  errors: string[]
  warnings: string[]
  suggestions: string[]
}

interface UseUserSyncReturn {
  syncStatus: SyncStatus
  syncProfile: (data: any, options?: SyncOptions) => Promise<SyncResult>
  validateUpdate: (data: any) => Promise<ValidationResult>
  triggerMLUpdate: () => Promise<any>
  getSyncStatus: () => Promise<any>
  clearError: () => void
  retryLastSync: () => Promise<void>
}

interface SyncOptions {
  optimistic?: boolean
  triggerML?: boolean
  showToast?: boolean
  validateFirst?: boolean
}

const DEFAULT_SYNC_OPTIONS: SyncOptions = {
  optimistic: true,
  triggerML: true,
  showToast: true,
  validateFirst: true
}

export function useUserSync(): UseUserSyncReturn {
  const { user, updateProfile } = useAuth()
  const [syncStatus, setSyncStatus] = useState<SyncStatus>({
    syncing: false,
    lastSync: null,
    error: null,
    pendingChanges: false
  })

  const lastSyncDataRef = useRef<any>(null)
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const API_BASE_URL = process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000'

  // Clear retry timeout on unmount
  useEffect(() => {
    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current)
      }
    }
  }, [])

  const getAuthHeaders = useCallback(async () => {
    let token = null
    
    // First try to get token from localStorage (custom auth)
    if (typeof window !== 'undefined') {
      token = localStorage.getItem('access_token')
    }
    
    // If no localStorage token, try NextAuth session
    if (!token) {
      try {
        const { getSession } = await import('next-auth/react')
        const session = await getSession()
        if (session?.accessToken) {
          token = session.accessToken
        }
      } catch (error) {
        console.warn('Failed to get NextAuth session:', error)
      }
    }
    
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    }
  }, [])

  const clearError = useCallback(() => {
    setSyncStatus(prev => ({ ...prev, error: null }))
  }, [])

  const validateUpdate = useCallback(async (data: any): Promise<ValidationResult> => {
    try {
      const headers = await getAuthHeaders()
      const response = await fetch(`${API_BASE_URL}/api/v1/sync/validate-update`, {
        method: 'POST',
        headers,
        body: JSON.stringify(data)
      })

      if (!response.ok) {
        throw new Error('Validation request failed')
      }

      return await response.json()
    } catch (error) {
      console.error('Validation error:', error)
      return {
        valid: false,
        errors: ['Validation service unavailable'],
        warnings: [],
        suggestions: []
      }
    }
  }, [API_BASE_URL, getAuthHeaders])

  const syncProfile = useCallback(async (
    data: any, 
    options: SyncOptions = {}
  ): Promise<SyncResult> => {
    const opts = { ...DEFAULT_SYNC_OPTIONS, ...options }
    
    // Store data for potential retry
    lastSyncDataRef.current = { data, options: opts }

    setSyncStatus(prev => ({ 
      ...prev, 
      syncing: true, 
      error: null, 
      pendingChanges: true 
    }))

    try {
      // Validate first if requested
      if (opts.validateFirst) {
        const validation = await validateUpdate(data)
        if (!validation.valid) {
          const errorMsg = validation.errors.join(', ')
          setSyncStatus(prev => ({ 
            ...prev, 
            syncing: false, 
            error: errorMsg,
            pendingChanges: false 
          }))
          
          if (opts.showToast) {
            toast.error(`Validation failed: ${errorMsg}`)
          }
          
          return {
            success: false,
            error: 'validation_failed',
            details: validation.errors
          }
        }

        // Show warnings if any
        if (validation.warnings.length > 0 && opts.showToast) {
          validation.warnings.forEach(warning => {
            toast(warning, { icon: '⚠️' })
          })
        }
      }

      // Optimistic update
      if (opts.optimistic && user) {
        try {
          await updateProfile(data)
        } catch (error) {
          console.warn('Optimistic update failed:', error)
        }
      }

      // Perform sync with backend
      const headers = await getAuthHeaders()
      const response = await fetch(`${API_BASE_URL}/api/v1/sync/sync-profile`, {
        method: 'POST',
        headers,
        body: JSON.stringify(data)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail?.message || 'Sync failed')
      }

      const responseData = await response.json()
      const result: SyncResult = responseData.data || responseData
      
      if (!result.success) {
        throw new Error(result.error || 'Sync failed')
      }

      // Update auth context with fresh user data from server
      if (result.user) {
        try {
          await updateProfile(result.user)
        } catch (error) {
          console.warn('Failed to update auth context after sync:', error)
        }
      }

      // Update sync status
      setSyncStatus(prev => ({
        ...prev,
        syncing: false,
        lastSync: new Date(),
        error: null,
        pendingChanges: false
      }))

      // Show success message
      if (opts.showToast) {
        toast.success('Profile synchronized successfully!')
        
        // Show ML predictions if available
        if (result.ml_predictions && !result.ml_predictions.error) {
          toast.success('AI insights updated!', { icon: '🤖' })
        }
      }

      return result

    } catch (error: any) {
      console.error('Sync error:', error)
      
      const errorMessage = error.message || 'Synchronization failed'
      
      setSyncStatus(prev => ({
        ...prev,
        syncing: false,
        error: errorMessage,
        pendingChanges: true // Keep pending since sync failed
      }))

      if (opts.showToast) {
        toast.error(errorMessage)
      }

      // Auto-retry after delay for network errors
      if (error.message.includes('fetch') || error.message.includes('network')) {
        retryTimeoutRef.current = setTimeout(() => {
          retryLastSync()
        }, 5000)
      }

      return {
        success: false,
        error: errorMessage,
        details: error
      }
    }
  }, [user, updateProfile, API_BASE_URL, getAuthHeaders, validateUpdate])

  const triggerMLUpdate = useCallback(async () => {
    try {
      setSyncStatus(prev => ({ ...prev, syncing: true }))

      const headers = await getAuthHeaders()
      const response = await fetch(`${API_BASE_URL}/api/v1/sync/trigger-ml-update`, {
        method: 'POST',
        headers
      })

      if (!response.ok) {
        throw new Error('ML update failed')
      }

      const result = await response.json()
      
      setSyncStatus(prev => ({ 
        ...prev, 
        syncing: false, 
        lastSync: new Date() 
      }))

      toast.success('AI insights updated!', { icon: '🤖' })
      return result

    } catch (error: any) {
      console.error('ML update error:', error)
      setSyncStatus(prev => ({ 
        ...prev, 
        syncing: false, 
        error: error.message 
      }))
      toast.error('Failed to update AI insights')
      throw error
    }
  }, [API_BASE_URL, getAuthHeaders])

  const getSyncStatus = useCallback(async () => {
    try {
      const headers = await getAuthHeaders()
      const response = await fetch(`${API_BASE_URL}/api/v1/sync/sync-status`, {
        headers
      })

      if (!response.ok) {
        throw new Error('Failed to get sync status')
      }

      return await response.json()
    } catch (error) {
      console.error('Get sync status error:', error)
      return null
    }
  }, [API_BASE_URL, getAuthHeaders])

  const retryLastSync = useCallback(async () => {
    if (!lastSyncDataRef.current) {
      return
    }

    const { data, options } = lastSyncDataRef.current
    await syncProfile(data, { ...options, showToast: false })
  }, [syncProfile])

  // Periodic sync status check
  useEffect(() => {
    if (!user) return

    const checkSyncStatus = async () => {
      const status = await getSyncStatus()
      if (status?.pending_updates?.length > 0) {
        setSyncStatus(prev => ({ ...prev, pendingChanges: true }))
      }
    }

    // Check at configurable interval
    const interval = setInterval(checkSyncStatus, UI_CONFIG.SYNC_CHECK_INTERVAL)
    
    return () => clearInterval(interval)
  }, [user, getSyncStatus])

  return {
    syncStatus,
    syncProfile,
    validateUpdate,
    triggerMLUpdate,
    getSyncStatus,
    clearError,
    retryLastSync
  }
}