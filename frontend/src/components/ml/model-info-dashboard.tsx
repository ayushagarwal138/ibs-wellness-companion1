'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Database, 
  Activity, 
  CheckCircle, 
  AlertTriangle, 
  Clock,
  RefreshCw,
  TrendingUp,
  BarChart3,
  Settings,
  Cpu,
  Zap,
  Target
} from 'lucide-react';
import { mlService, ModelInfoResponse, ModelMetrics, TrainingStatusResponse } from '@/services/ml-service';
import { toast } from 'react-hot-toast';

interface ModelInfoDashboardProps {
  className?: string;
}

export function ModelInfoDashboard({ className }: ModelInfoDashboardProps) {
  const [modelInfo, setModelInfo] = useState<ModelInfoResponse | null>(null);
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedModel, setSelectedModel] = useState<string>('all');

  // Get models from API response or fallback to empty array
  const modelMetrics: ModelMetrics[] = modelInfo?.models || [];

  const loadModelInfo = async () => {
    try {
      setLoading(true);
      const [modelData, trainingData] = await Promise.all([
        mlService.getModelInfo(),
        mlService.getTrainingStatus()
      ]);
      setModelInfo(modelData);
      setTrainingStatus(trainingData);
    } catch (error) {
      console.error('Failed to load model info:', error);
      toast.error('Failed to load model information');
    } finally {
      setLoading(false);
    }
  };

  const refreshModelInfo = async () => {
    try {
      setRefreshing(true);
      await loadModelInfo();
      toast.success('Model information refreshed');
    } catch (error) {
      console.error('Failed to refresh model info:', error);
      toast.error('Failed to refresh model information');
    } finally {
      setRefreshing(false);
    }
  };

  const reloadModels = async () => {
    try {
      await mlService.reloadModels();
      toast.success('Models reloaded successfully');
      await refreshModelInfo();
    } catch (error) {
      console.error('Failed to reload models:', error);
      toast.error('Failed to reload models');
    }
  };

  useEffect(() => {
    loadModelInfo();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 border-green-200';
      case 'training': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'error': return 'bg-red-100 text-red-800 border-red-200';
      case 'outdated': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4" />;
      case 'training': return <Clock className="h-4 w-4" />;
      case 'error': return <AlertTriangle className="h-4 w-4" />;
      case 'outdated': return <RefreshCw className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  const getPerformanceScore = (model: ModelMetrics) => {
    if (model.type === 'classifier') {
      return model.accuracy ? Math.round(model.accuracy * 100) : 0;
    } else {
      return model.r2_score ? Math.round(model.r2_score * 100) : 0;
    }
  };

  const filteredModels = selectedModel === 'all' 
    ? modelMetrics 
    : modelMetrics.filter((model: ModelMetrics) => 
        model.type === selectedModel || 
        model.name.toLowerCase().includes(selectedModel.toLowerCase())
      );

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Database className="h-6 w-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">ML Model Dashboard</h2>
        </div>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Models</option>
            <option value="classifier">Classifiers</option>
            <option value="regressor">Regressors</option>
          </select>
          <div className="flex gap-2">
            <Button
              onClick={refreshModelInfo}
              disabled={refreshing}
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button
              onClick={reloadModels}
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              <Settings className="h-4 w-4" />
              Reload Models
            </Button>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">Total Models</h4>
              <Cpu className="h-4 w-4 text-blue-500" />
            </div>
            <div className="text-2xl font-bold text-blue-600">
              {modelMetrics.length}
            </div>
            <p className="text-sm text-gray-600">Active models</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">Training Jobs</h4>
              <Activity className="h-4 w-4 text-orange-500" />
            </div>
            <div className="text-2xl font-bold text-orange-600">
              {trainingStatus?.current_jobs?.length || 0}
            </div>
            <p className="text-sm text-gray-600">Currently running</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">Avg Performance</h4>
              <TrendingUp className="h-4 w-4 text-green-500" />
            </div>
            <div className="text-2xl font-bold text-green-600">
              {modelMetrics.length > 0 ? Math.round(modelMetrics.reduce((acc: number, model: ModelMetrics) => acc + getPerformanceScore(model), 0) / modelMetrics.length) : 0}%
            </div>
            <p className="text-sm text-gray-600">Accuracy/R² score</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">Active Models</h4>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </div>
            <div className="text-2xl font-bold text-green-600">
              {modelMetrics.filter((m: ModelMetrics) => m.status === 'active').length}
            </div>
            <p className="text-sm text-gray-600">Ready for inference</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">System Health</h4>
              <Zap className="h-4 w-4 text-green-500" />
            </div>
            <div className="text-2xl font-bold text-green-600">
              {trainingStatus?.system_health?.cpu_usage ? 
                `${Math.round(trainingStatus.system_health.cpu_usage)}%` : 
                'N/A'
              }
            </div>
            <p className="text-sm text-gray-600">CPU usage</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">Last Updated</h4>
              <Clock className="h-4 w-4 text-gray-500" />
            </div>
            <div className="text-2xl font-bold text-gray-600">
              {new Date().toLocaleDateString()}
            </div>
            <p className="text-sm text-gray-600">Training timestamp</p>
          </CardContent>
        </Card>
      </div>

      {/* Model Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredModels.map((model: ModelMetrics, index: number) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-semibold truncate">
                  {model.name}
                </CardTitle>
                <Badge className={`${getStatusColor(model.status)} flex items-center gap-1`}>
                  {getStatusIcon(model.status)}
                  {model.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Performance Metrics */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Performance</span>
                  <span className="text-sm font-bold text-blue-600">
                    {getPerformanceScore(model)}%
                  </span>
                </div>
                <Progress value={getPerformanceScore(model)} className="h-2" />
                
                {model.type === 'classifier' && model.accuracy && (
                  <div className="text-xs text-gray-600">
                    Accuracy: {(model.accuracy * 100).toFixed(1)}%
                  </div>
                )}
                
                {model.type === 'regressor' && (
                  <div className="text-xs text-gray-600 space-y-1">
                    {model.r2_score && <div>R² Score: {model.r2_score.toFixed(3)}</div>}
                    {model.rmse && <div>RMSE: {model.rmse.toFixed(3)}</div>}
                  </div>
                )}
              </div>

              {/* Model Details */}
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Type:</span>
                  <span className="font-medium capitalize">{model.type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Version:</span>
                  <span className="font-medium">{model.version}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Features:</span>
                  <span className="font-medium">{model.features_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Training Samples:</span>
                  <span className="font-medium">{model.training_samples.toLocaleString()}</span>
                </div>
                {model.confidence_threshold && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Confidence Threshold:</span>
                    <span className="font-medium">{model.confidence_threshold}</span>
                  </div>
                )}
              </div>

              {/* Last Trained */}
              <div className="pt-2 border-t border-gray-200">
                <div className="text-xs text-gray-500">
                  Last trained: {new Date(model.last_trained).toLocaleDateString()}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Model Performance Chart Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            Performance Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredModels.map((model: ModelMetrics, index: number) => (
              <div key={index} className="flex items-center gap-4">
                <div className="w-32 text-sm font-medium truncate">
                  {model.name}
                </div>
                <div className="flex-1">
                  <Progress value={getPerformanceScore(model)} className="h-3" />
                </div>
                <div className="w-16 text-sm font-bold text-right">
                  {getPerformanceScore(model)}%
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}