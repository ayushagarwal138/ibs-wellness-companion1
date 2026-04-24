'use client';

import { useState, useEffect, useCallback } from 'react';

interface PerformanceMetric {
  operation: string;
  startTime: number;
  endTime?: number;
  duration?: number;
  success: boolean;
  error?: string;
  metadata?: Record<string, any>;
}

interface PerformanceStats {
  totalOperations: number;
  successRate: number;
  averageDuration: number;
  slowestOperation: PerformanceMetric | null;
  fastestOperation: PerformanceMetric | null;
  recentErrors: PerformanceMetric[];
}

export function usePerformanceMonitor() {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [isMonitoring, setIsMonitoring] = useState(true);

  const startOperation = useCallback((operation: string, metadata?: Record<string, any>) => {
    if (!isMonitoring) return null;

    const metric: PerformanceMetric = {
      operation,
      startTime: performance.now(),
      success: false,
      metadata
    };

    const operationId = `${operation}-${Date.now()}-${Math.random()}`;
    
    return {
      operationId,
      complete: (success: boolean = true, error?: string) => {
        const endTime = performance.now();
        const completedMetric: PerformanceMetric = {
          ...metric,
          endTime,
          duration: endTime - metric.startTime,
          success,
          error
        };

        setMetrics(prev => {
          const updated = [...prev, completedMetric];
          // Keep only last 100 metrics to prevent memory issues
          return updated.slice(-100);
        });

        // Log slow operations (> 2 seconds)
        if (completedMetric.duration && completedMetric.duration > 2000) {
          console.warn(`Slow operation detected: ${operation} took ${completedMetric.duration.toFixed(2)}ms`);
        }

        // Log errors
        if (!success && error) {
          console.error(`Operation failed: ${operation} - ${error}`);
        }
      }
    };
  }, [isMonitoring]);

  const getStats = useCallback((): PerformanceStats => {
    const completedMetrics = metrics.filter(m => m.duration !== undefined);
    
    if (completedMetrics.length === 0) {
      return {
        totalOperations: 0,
        successRate: 0,
        averageDuration: 0,
        slowestOperation: null,
        fastestOperation: null,
        recentErrors: []
      };
    }

    const successfulOps = completedMetrics.filter(m => m.success);
    const durations = completedMetrics.map(m => m.duration!);
    const recentErrors = completedMetrics
      .filter(m => !m.success)
      .slice(-5); // Last 5 errors

    return {
      totalOperations: completedMetrics.length,
      successRate: (successfulOps.length / completedMetrics.length) * 100,
      averageDuration: durations.reduce((sum, d) => sum + d, 0) / durations.length,
      slowestOperation: completedMetrics.reduce((slowest, current) => 
        !slowest || (current.duration! > slowest.duration!) ? current : slowest
      ),
      fastestOperation: completedMetrics.reduce((fastest, current) => 
        !fastest || (current.duration! < fastest.duration!) ? current : fastest
      ),
      recentErrors
    };
  }, [metrics]);

  const getOperationStats = useCallback((operationType: string) => {
    const operationMetrics = metrics.filter(m => 
      m.operation === operationType && m.duration !== undefined
    );

    if (operationMetrics.length === 0) {
      return null;
    }

    const durations = operationMetrics.map(m => m.duration!);
    const successfulOps = operationMetrics.filter(m => m.success);

    return {
      count: operationMetrics.length,
      successRate: (successfulOps.length / operationMetrics.length) * 100,
      averageDuration: durations.reduce((sum, d) => sum + d, 0) / durations.length,
      minDuration: Math.min(...durations),
      maxDuration: Math.max(...durations),
      lastExecution: operationMetrics[operationMetrics.length - 1]
    };
  }, [metrics]);

  const clearMetrics = useCallback(() => {
    setMetrics([]);
  }, []);

  const toggleMonitoring = useCallback(() => {
    setIsMonitoring(prev => !prev);
  }, []);

  // Auto-clear old metrics every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => {
        const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
        return prev.filter(metric => 
          metric.startTime > fiveMinutesAgo || 
          (metric.endTime && metric.endTime > fiveMinutesAgo)
        );
      });
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, []);

  return {
    startOperation,
    getStats,
    getOperationStats,
    clearMetrics,
    toggleMonitoring,
    isMonitoring,
    metrics: metrics.slice(-20) // Return only recent metrics for display
  };
}