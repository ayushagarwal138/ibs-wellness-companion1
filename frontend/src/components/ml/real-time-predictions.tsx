'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Activity, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown,
  Zap,
  Clock,
  RefreshCw,
  Wifi,
  WifiOff,
  Target,
  Shield
} from 'lucide-react';
import { mlService, RealtimePredictionResponse } from '@/services/ml-service';
import { toast } from 'react-hot-toast';

interface RealTimePredictionsProps {
  userId?: string;
  updateInterval?: number; // in milliseconds
  className?: string;
  onPredictionUpdate?: (prediction: RealtimePredictionResponse) => void;
}

interface PredictionTrend {
  timestamp: number;
  risk: number;
  confidence: number;
}

export function RealTimePredictions({ 
  userId, 
  updateInterval = 30000, // 30 seconds default
  className,
  onPredictionUpdate 
}: RealTimePredictionsProps) {
  const [currentPrediction, setCurrentPrediction] = useState<RealtimePredictionResponse | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [trends, setTrends] = useState<PredictionTrend[]>([]);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    startRealTimeUpdates();
    return () => stopRealTimeUpdates();
  }, [updateInterval]);

  const startRealTimeUpdates = async () => {
    setIsConnected(true);
    await fetchPrediction();
    
    intervalRef.current = setInterval(async () => {
      await fetchPrediction();
    }, updateInterval);
  };

  const stopRealTimeUpdates = () => {
    setIsConnected(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const fetchPrediction = async () => {
    try {
      const prediction = await mlService.getRealtimePredictions();
      setCurrentPrediction(prediction);
      setLastUpdate(new Date());
      setLoading(false);

      // Update trends
      const newTrend: PredictionTrend = {
        timestamp: Date.now(),
        risk: prediction.current_risk,
        confidence: prediction.confidence_score
      };
      
      setTrends(prev => {
        const updated = [...prev, newTrend];
        // Keep only last 20 data points
        return updated.slice(-20);
      });

      // Notify parent component
      if (onPredictionUpdate) {
        onPredictionUpdate(prediction);
      }

      // Show alerts for high risk
      if (prediction.current_risk > 70) {
        toast.error('High risk detected! Check your immediate recommendations.');
      }

    } catch (error) {
      console.error('Error fetching real-time prediction:', error);
      setIsConnected(false);
      if (loading) {
        setLoading(false);
      }
    }
  };

  const getRiskLevel = (risk: number): { level: string; color: string; bgColor: string; progressColor: string } => {
    if (risk >= 80) return { 
      level: 'Critical', 
      color: 'text-red-700', 
      bgColor: 'bg-gradient-to-br from-red-50 to-red-100 border-red-300 shadow-red-100', 
      progressColor: 'bg-red-500' 
    };
    if (risk >= 60) return { 
      level: 'High', 
      color: 'text-orange-700', 
      bgColor: 'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-300 shadow-orange-100', 
      progressColor: 'bg-orange-500' 
    };
    if (risk >= 40) return { 
      level: 'Medium', 
      color: 'text-yellow-700', 
      bgColor: 'bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-300 shadow-yellow-100', 
      progressColor: 'bg-yellow-500' 
    };
    return { 
      level: 'Low', 
      color: 'text-green-700', 
      bgColor: 'bg-gradient-to-br from-green-50 to-green-100 border-green-300 shadow-green-100', 
      progressColor: 'bg-green-500' 
    };
  };

  const getRiskTrend = (): { direction: 'up' | 'down' | 'stable'; percentage: number } => {
    if (trends.length < 2) return { direction: 'stable', percentage: 0 };
    
    const current = trends[trends.length - 1]?.risk;
    const previous = trends[trends.length - 2]?.risk;
    
    if (!current || !previous) return { direction: 'stable', percentage: 0 };
    
    const change = ((current - previous) / previous) * 100;
    
    if (Math.abs(change) < 5) return { direction: 'stable', percentage: 0 };
    return { 
      direction: change > 0 ? 'up' : 'down', 
      percentage: Math.abs(change) 
    };
  };

  const formatTimeAgo = (date: Date): string => {
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-1/3"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!currentPrediction) {
    return (
      <Card className={className}>
        <CardContent className="p-6 text-center">
          <WifiOff className="h-8 w-8 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-600">Unable to load real-time predictions</p>
          <Button onClick={fetchPrediction} variant="outline" size="sm" className="mt-2">
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  const riskInfo = getRiskLevel(currentPrediction.current_risk);
  const trend = getRiskTrend();

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Connection Status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {isConnected ? (
            <Wifi className="h-4 w-4 text-green-500" />
          ) : (
            <WifiOff className="h-4 w-4 text-red-500" />
          )}
          <span className="text-sm text-gray-600">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
          {lastUpdate && (
            <span className="text-xs text-gray-500">
              • Updated {formatTimeAgo(lastUpdate)}
            </span>
          )}
        </div>
        <Button
          onClick={fetchPrediction}
          variant="ghost"
          size="sm"
          className="flex items-center gap-1"
        >
          <RefreshCw className="h-3 w-3" />
          Refresh
        </Button>
      </div>

      {/* Current Risk Status */}
      <Card className={`border-2 shadow-lg ${riskInfo.bgColor}`}>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Current Risk Level
            </div>
            <Badge variant="outline" className={`${riskInfo.color} border-current font-semibold`}>
              {riskInfo.level}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Risk Percentage */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl lg:text-3xl xl:text-4xl font-bold text-gray-900 truncate">
                  {Math.round(currentPrediction.current_risk || 0)}%
                </span>
                <div className="flex items-center gap-1 text-sm flex-shrink-0 ml-2">
                  {trend.direction === 'up' && <TrendingUp className="h-4 w-4 text-red-500" />}
                  {trend.direction === 'down' && <TrendingDown className="h-4 w-4 text-green-500" />}
                  {trend.direction === 'stable' && <Activity className="h-4 w-4 text-gray-500" />}
                  {trend.percentage > 0 && (
                    <span className={`font-medium ${
                      trend.direction === 'up' ? 'text-red-600' : 
                      trend.direction === 'down' ? 'text-green-600' : 
                      'text-gray-600'
                    }`}>
                      {trend.percentage.toFixed(1)}%
                    </span>
                  )}
                </div>
              </div>
              <div className="w-full">
                <Progress 
                  value={currentPrediction.current_risk || 0} 
                  className="h-3"
                />
              </div>
            </div>

            {/* Confidence Score */}
            <div className="flex items-center justify-between p-4 bg-white/60 backdrop-blur-sm rounded-lg border border-white/20 shadow-sm">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-blue-500 flex-shrink-0" />
                <span className="text-sm font-medium text-gray-700">Confidence</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-blue-600">
                  {Math.round(currentPrediction.confidence_score || 0)}%
                </span>
                <div className="w-16 lg:w-20">
                  <Progress value={currentPrediction.confidence_score || 0} className="h-2" />
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Risk Factors */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-orange-500" />
            Active Risk Factors
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {currentPrediction.risk_factors.map((factor, index) => (
              <div key={index} className="flex items-center gap-2 p-2 bg-orange-50 rounded border border-orange-200">
                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                <span className="text-sm text-orange-800">{factor}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Immediate Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-blue-500" />
            Immediate Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {currentPrediction.immediate_recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start gap-2 p-3 bg-blue-50 rounded border border-blue-200">
                <Clock className="h-4 w-4 text-blue-500 flex-shrink-0 mt-0.5" />
                <span className="text-sm text-blue-800">{recommendation}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Mini Trend Chart */}
      {trends.length > 1 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-purple-500" />
              Risk Trend (Last {trends.length} Updates)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="w-full overflow-hidden">
              <div className="h-16 flex items-end justify-between gap-1 max-w-full">
                {trends.map((trend, index) => (
                  <div
                    key={index}
                    className="bg-purple-500 rounded-t flex-shrink-0"
                    style={{
                      height: `${Math.max(trend.risk * 100, 5)}%`,
                      width: `${Math.min(100 / trends.length, 20)}%`,
                      maxWidth: '20px',
                      opacity: 0.3 + (index / trends.length) * 0.7
                    }}
                    title={`Risk: ${Math.round(trend.risk * 100)}%`}
                  />
                ))}
              </div>
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-2">
              <span>Oldest</span>
              <span>Latest</span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}