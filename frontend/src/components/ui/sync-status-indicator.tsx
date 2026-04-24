/**
 * SyncStatusIndicator Component
 * 
 * Displays real-time synchronization status with visual feedback
 * and user interaction capabilities.
 */

import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  CheckCircle, 
  AlertCircle, 
  RefreshCw, 
  Wifi, 
  WifiOff,
  Clock,
  Zap
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface SyncStatus {
  syncing: boolean
  lastSync: Date | null
  error: string | null
  pendingChanges: boolean
}

interface SyncStatusIndicatorProps {
  status: SyncStatus
  onRetry?: () => void
  onClearError?: () => void
  className?: string
  compact?: boolean
  showDetails?: boolean
}

export function SyncStatusIndicator({
  status,
  onRetry,
  onClearError,
  className,
  compact = false,
  showDetails = true
}: SyncStatusIndicatorProps) {
  const { syncing, lastSync, error, pendingChanges } = status

  const getStatusInfo = () => {
    if (error) {
      return {
        icon: AlertCircle,
        color: 'text-red-500',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        message: 'Sync Error',
        description: error,
        action: 'Retry'
      }
    }

    if (syncing) {
      return {
        icon: RefreshCw,
        color: 'text-blue-500',
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        message: 'Syncing...',
        description: 'Updating your profile',
        action: null
      }
    }

    if (pendingChanges) {
      return {
        icon: Clock,
        color: 'text-yellow-500',
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
        message: 'Pending Changes',
        description: 'Changes waiting to sync',
        action: 'Sync Now'
      }
    }

    if (lastSync) {
      return {
        icon: CheckCircle,
        color: 'text-green-500',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        message: 'Synced',
        description: `Last sync: ${formatLastSync(lastSync)}`,
        action: null
      }
    }

    return {
      icon: WifiOff,
      color: 'text-gray-400',
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
      message: 'Not Synced',
      description: 'No recent sync activity',
      action: 'Sync Now'
    }
  }

  const formatLastSync = (date: Date) => {
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  const statusInfo = getStatusInfo()
  const Icon = statusInfo.icon

  const handleAction = () => {
    if (error && onRetry) {
      onRetry()
    } else if (pendingChanges && onRetry) {
      onRetry()
    }
  }

  if (compact) {
    return (
      <div className={cn('flex items-center gap-2', className)}>
        <motion.div
          animate={{ rotate: syncing ? 360 : 0 }}
          transition={{ duration: 1, repeat: syncing ? Infinity : 0, ease: 'linear' }}
        >
          <Icon className={cn('h-4 w-4', statusInfo.color)} />
        </motion.div>
        {showDetails && (
          <span className={cn('text-sm font-medium', statusInfo.color)}>
            {statusInfo.message}
          </span>
        )}
      </div>
    )
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={`${syncing}-${error}-${pendingChanges}`}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        className={cn(
          'flex items-center gap-3 p-3 rounded-lg border transition-all duration-200',
          statusInfo.bgColor,
          statusInfo.borderColor,
          className
        )}
      >
        <motion.div
          animate={{ rotate: syncing ? 360 : 0 }}
          transition={{ duration: 1, repeat: syncing ? Infinity : 0, ease: 'linear' }}
        >
          <Icon className={cn('h-5 w-5', statusInfo.color)} />
        </motion.div>

        <div className="flex-1 min-w-0">
          <div className={cn('font-medium text-sm', statusInfo.color)}>
            {statusInfo.message}
          </div>
          {showDetails && statusInfo.description && (
            <div className="text-xs text-gray-600 mt-1">
              {statusInfo.description}
            </div>
          )}
        </div>

        {statusInfo.action && (error || pendingChanges) && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleAction}
            className={cn(
              'px-3 py-1 text-xs font-medium rounded-md transition-colors',
              error 
                ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
            )}
          >
            {statusInfo.action}
          </motion.button>
        )}

        {error && onClearError && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onClearError}
            className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
            title="Dismiss error"
          >
            ×
          </motion.button>
        )}
      </motion.div>
    </AnimatePresence>
  )
}

/**
 * NetworkStatusIndicator - Shows online/offline status
 */
interface NetworkStatusIndicatorProps {
  className?: string
}

export function NetworkStatusIndicator({ className }: NetworkStatusIndicatorProps) {
  const [isOnline, setIsOnline] = React.useState(true)

  React.useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn(
        'flex items-center gap-2 px-2 py-1 rounded-full text-xs font-medium',
        isOnline 
          ? 'bg-green-100 text-green-700' 
          : 'bg-red-100 text-red-700',
        className
      )}
    >
      {isOnline ? (
        <Wifi className="h-3 w-3" />
      ) : (
        <WifiOff className="h-3 w-3" />
      )}
      {isOnline ? 'Online' : 'Offline'}
    </motion.div>
  )
}

/**
 * MLStatusIndicator - Shows ML prediction status
 */
interface MLStatusIndicatorProps {
  predictions?: any
  loading?: boolean
  error?: string
  className?: string
}

export function MLStatusIndicator({ 
  predictions, 
  loading, 
  error, 
  className 
}: MLStatusIndicatorProps) {
  const getStatus = () => {
    if (error) {
      return {
        icon: AlertCircle,
        color: 'text-red-500',
        message: 'AI Error',
        bgColor: 'bg-red-50'
      }
    }

    if (loading) {
      return {
        icon: RefreshCw,
        color: 'text-blue-500',
        message: 'AI Thinking...',
        bgColor: 'bg-blue-50'
      }
    }

    if (predictions) {
      return {
        icon: Zap,
        color: 'text-purple-500',
        message: 'AI Ready',
        bgColor: 'bg-purple-50'
      }
    }

    return {
      icon: Zap,
      color: 'text-gray-400',
      message: 'AI Inactive',
      bgColor: 'bg-gray-50'
    }
  }

  const status = getStatus()
  const Icon = status.icon

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={cn(
        'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium',
        status.bgColor,
        status.color,
        className
      )}
    >
      <motion.div
        animate={{ rotate: loading ? 360 : 0 }}
        transition={{ duration: 1, repeat: loading ? Infinity : 0, ease: 'linear' }}
      >
        <Icon className="h-3 w-3" />
      </motion.div>
      {status.message}
    </motion.div>
  )
}