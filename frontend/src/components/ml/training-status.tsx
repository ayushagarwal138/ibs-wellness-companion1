'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Play, 
  Pause, 
  Square, 
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Clock,
  Cpu,
  Database,
  TrendingUp,
  Activity,
  Zap,
  HardDrive,
  MemoryStick
} from 'lucide-react';
import { mlService, TrainingJob, TrainingStatusResponse } from '@/services/ml-service';

interface TrainingStatusProps {
  className?: string;
}

export function TrainingStatus({ className }: TrainingStatusProps) {
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatusResponse | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load initial data
    loadTrainingStatus();

    // Set up auto-refresh interval
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(() => {
        refreshTrainingStatus();
      }, 5000); // Refresh every 5 seconds
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const loadTrainingStatus = async () => {
    setLoading(true);
    try {
      const status = await mlService.getTrainingStatus();
      setTrainingStatus(status);
    } catch (error) {
      console.error('Failed to load training status:', error);
      // Fallback to empty state
      setTrainingStatus({
        queue_size: 0,
        is_training: false,
        current_jobs: [],
        completed_jobs: [],
        system_health: {
          cpu_usage: 0,
          memory_usage: 0,
          disk_space: 0
        },
        performance_metrics: {
          average_training_time: 0,
          success_rate: 0,
          total_models_trained: 0
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const refreshTrainingStatus = async () => {
    setIsRefreshing(true);
    try {
      const status = await mlService.getTrainingStatus();
      setTrainingStatus(status);
    } catch (error) {
      console.error('Failed to refresh training status:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const getStatusIcon = (status: TrainingJob['status']) => {
    switch (status) {
      case 'running':
        return <Activity className="h-4 w-4 text-blue-600 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      case 'cancelled':
        return <Pause className="h-4 w-4 text-yellow-600" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-gray-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: TrainingJob['status']) => {
    switch (status) {
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'cancelled':
        return 'bg-yellow-100 text-yellow-800';
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDuration = (startTime: string, endTime?: string) => {
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const diff = end.getTime() - start.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  const handleJobAction = (jobId: string, action: 'start' | 'pause' | 'stop') => {
    // In a real implementation, this would call the API to control training jobs
    console.log(`Action ${action} on job ${jobId}`);
  };

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="space-y-4">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!trainingStatus) {
    return (
      <div className={`space-y-6 ${className}`}>
        <Card>
          <CardContent className="p-8 text-center">
            <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to Load Training Status</h3>
            <p className="text-gray-600 mb-4">Unable to connect to the training service.</p>
            <Button onClick={loadTrainingStatus}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const allJobs = [...trainingStatus.current_jobs, ...trainingStatus.completed_jobs];
  const runningJobs = trainingStatus.current_jobs.filter(job => job.status === 'running');
  const completedJobs = trainingStatus.completed_jobs.filter(job => job.status === 'completed');
  const pendingJobs = trainingStatus.current_jobs.filter(job => job.status === 'pending');

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Cpu className="h-6 w-6 text-purple-600" />
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Training Status</h2>
            <p className="text-sm text-gray-600">Monitor ML model training progress</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={autoRefresh ? 'bg-green-50 border-green-200' : ''}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
            Auto Refresh
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={refreshTrainingStatus}
            disabled={isRefreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Activity className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Running</p>
                <p className="text-2xl font-bold text-blue-600">{runningJobs.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-green-600">{completedJobs.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gray-100 rounded-lg">
                <Clock className="h-5 w-5 text-gray-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-gray-600">{pendingJobs.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <TrendingUp className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-purple-600">
                  {trainingStatus.performance_metrics.success_rate.toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Health */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Cpu className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">CPU Usage</p>
                <p className="text-2xl font-bold text-orange-600">
                  {trainingStatus.system_health.cpu_usage.toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <MemoryStick className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Memory Usage</p>
                <p className="text-2xl font-bold text-indigo-600">
                  {trainingStatus.system_health.memory_usage.toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-teal-100 rounded-lg">
                <HardDrive className="h-5 w-5 text-teal-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Disk Space</p>
                <p className="text-2xl font-bold text-teal-600">
                  {trainingStatus.system_health.disk_space.toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Training Jobs */}
      <div className="space-y-4">
        {allJobs.map((job) => (
          <Card key={job.id}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {getStatusIcon(job.status)}
                  <div>
                    <CardTitle className="text-lg">{job.model_name}</CardTitle>
                    <p className="text-sm text-gray-600">Job ID: {job.id}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={getStatusColor(job.status)}>
                    {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                  </Badge>
                  <div className="flex gap-1">
                    {job.status === 'pending' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleJobAction(job.id, 'start')}
                      >
                        <Play className="h-3 w-3" />
                      </Button>
                    )}
                    {job.status === 'running' && (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleJobAction(job.id, 'pause')}
                        >
                          <Pause className="h-3 w-3" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleJobAction(job.id, 'stop')}
                        >
                          <Square className="h-3 w-3" />
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Progress Bar */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Progress</span>
                    <span className="font-medium">{job.progress.toFixed(1)}%</span>
                  </div>
                  <Progress value={job.progress} className="h-2" />
                </div>

                {/* Training Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  {job.epochs_completed && job.total_epochs && (
                    <div>
                      <p className="text-gray-600">Epoch</p>
                      <p className="font-medium">{job.epochs_completed}/{job.total_epochs}</p>
                    </div>
                  )}
                  {job.loss && (
                    <div>
                      <p className="text-gray-600">Current Loss</p>
                      <p className="font-medium">{job.loss.toFixed(4)}</p>
                    </div>
                  )}
                  {job.accuracy && (
                    <div>
                      <p className="text-gray-600">Accuracy</p>
                      <p className="font-medium">{(job.accuracy * 100).toFixed(2)}%</p>
                    </div>
                  )}
                  <div>
                    <p className="text-gray-600">Duration</p>
                    <p className="font-medium">{formatDuration(job.start_time, job.end_time)}</p>
                  </div>
                </div>

                {/* Dataset Info */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Training Samples</p>
                    <p className="font-medium">{job.training_samples?.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Validation Samples</p>
                    <p className="font-medium">{job.validation_samples?.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Batch Size</p>
                    <p className="font-medium">{job.batch_size}</p>
                  </div>
                  {job.learning_rate && (
                    <div>
                      <p className="text-gray-600">Learning Rate</p>
                      <p className="font-medium">{job.learning_rate}</p>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {allJobs.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center">
            <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Training Jobs</h3>
            <p className="text-gray-600">Start training a new model to see progress here.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}