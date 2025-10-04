'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { apiService, type SymptomStats as ApiSymptomStats } from '@/lib/api';
import { useAuth } from '@/contexts/auth-context';
import { toast } from 'react-hot-toast';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler,
} from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
);

export default function SymptomStats() {
  const { user, loading: authLoading } = useAuth();
  const [stats, setStats] = useState<ApiSymptomStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [dateRange, setDateRange] = useState('30'); // days

  const fetchStats = React.useCallback(async () => {
    // Only fetch if user is authenticated
    if (!user) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiService.getSymptomStats(parseInt(dateRange));
      setStats(response);
    } catch (error) {
      console.error('Error fetching symptom stats:', error);
      
      // Check if it's an authentication error
      if (error instanceof Error && error.message.includes('403')) {
        toast.error('Please log in to view symptom statistics');
      } else {
        toast.error('Failed to load symptom statistics');
      }
    } finally {
      setIsLoading(false);
    }
  }, [dateRange, user]);

  useEffect(() => {
    // Only fetch when auth is complete and user is authenticated
    if (!authLoading && user) {
      fetchStats();
    } else if (!authLoading && !user) {
      // User is not authenticated, stop loading
      setIsLoading(false);
    }
  }, [fetchStats, authLoading, user]);

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </CardHeader>
            <CardContent>
              <div className="h-32 bg-gray-200 rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  // Show authentication message if user is not logged in
  if (!authLoading && !user) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center text-gray-500">Please log in to view symptom statistics</p>
        </CardContent>
      </Card>
    );
  }

  if (!stats) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center text-gray-500">No symptom data available</p>
        </CardContent>
      </Card>
    );
  }

  // Severity Distribution Chart
  const severityChartData = {
    labels: Object.keys(stats?.severity_distribution || {}),
    datasets: [
      {
        label: 'Number of Logs',
        data: Object.values(stats?.severity_distribution || {}),
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',   // Green for mild
          'rgba(251, 191, 36, 0.8)',  // Yellow for moderate
          'rgba(239, 68, 68, 0.8)',   // Red for severe
        ],
        borderColor: [
          'rgba(34, 197, 94, 1)',
          'rgba(251, 191, 36, 1)',
          'rgba(239, 68, 68, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  // Bristol Stool Chart Data
  const bristolChartData = {
    labels: Object.keys(stats?.bristol_distribution || {}),
    datasets: [
      {
        label: 'Bristol Stool Scale Distribution',
        data: Object.values(stats?.bristol_distribution || {}),
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
          '#FF9F40',
          '#FF6384',
        ],
      },
    ],
  };

  // Pain Location Chart Data
  const painLocationChartData = {
    labels: Object.keys(stats?.pain_locations || {}),
    datasets: [
      {
        label: 'Pain Location Distribution',
        data: Object.values(stats?.pain_locations || {}),
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
          '#FF9F40',
        ],
      },
    ],
  };

  // Weekly Trends Chart
  const weeklyTrendsData = {
    labels: Object.keys(stats?.weekly_trends || {}),
    datasets: [
      {
        label: 'Symptom Logs',
        data: Object.values(stats?.weekly_trends || {}),
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      filler: {
        propagate: true,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  };

  const lineChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      filler: {
        propagate: true,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
    elements: {
      line: {
        tension: 0.4,
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* Header with Date Range Selector */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Symptom Statistics</h2>
        <select
          value={dateRange}
          onChange={(e) => setDateRange(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
          <option value="365">Last year</option>
        </select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Logs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_logs}</div>
            <p className="text-xs text-gray-500">symptom entries</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Average Severity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.average_severity?.toFixed(1) || 'N/A'}/3</div>
            <p className="text-xs text-gray-500">severity rating</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Most Common Symptoms</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {stats?.most_common_symptoms && stats.most_common_symptoms.length > 0 ? (
                stats.most_common_symptoms.slice(0, 3).map((symptom, index) => (
                  <div key={symptom} className="text-sm">
                    {index + 1}. {symptom}
                  </div>
                ))
              ) : (
                <div className="text-sm text-gray-500">No data available</div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Severity Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Severity Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <Bar data={severityChartData} options={chartOptions} />
          </CardContent>
        </Card>

        {/* Bristol Stool Distribution */}
        {stats?.bristol_distribution && Object.keys(stats.bristol_distribution).length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Bristol Stool Scale Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <Bar data={bristolChartData} options={chartOptions} />
            </CardContent>
          </Card>
        )}

        {/* Pain Locations */}
        {stats?.pain_locations && Object.keys(stats.pain_locations).length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Pain Locations</CardTitle>
            </CardHeader>
            <CardContent>
              <Doughnut data={painLocationChartData} options={doughnutOptions} />
            </CardContent>
          </Card>
        )}

        {/* Weekly Trends */}
        <Card>
          <CardHeader>
            <CardTitle>Weekly Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <Line data={weeklyTrendsData} options={lineChartOptions} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}