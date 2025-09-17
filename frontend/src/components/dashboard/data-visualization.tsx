'use client';

import React, { useState, useEffect } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CalendarDays, TrendingUp, Activity, AlertCircle } from 'lucide-react';
import { format, subDays, parseISO } from 'date-fns';
import { apiService } from '@/lib/api';
import { toast } from 'react-hot-toast';

// Import shared types
import {
  TrendData,
  FoodReactionPattern,
  VisualizationData
} from '@ibs-wellness/shared-types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

export default function DataVisualization() {
  const [data, setData] = useState<VisualizationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    fetchVisualizationData();
  }, [dateRange]);

  const fetchVisualizationData = async () => {
    setLoading(true);
    try {
      // Mock data for now - replace with actual API calls
      const mockData: VisualizationData = {
        symptom_trends: Array.from({ length: 30 }, (_, i): TrendData => {
          const date = new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000);
          const dateString: string = date.toISOString().split('T')[0] || '';
          return {
            date: dateString,
            symptom_severity: Math.floor(Math.random() * 10) + 1,
            mood_rating: Math.floor(Math.random() * 10) + 1,
            bristol_scale: Math.floor(Math.random() * 7) + 1,
          };
        }),
        food_reaction_patterns: [
          { food_name: 'Dairy', reaction_count: 15, avg_severity: 7.2, common_symptoms: ['Bloating', 'Cramping'] },
          { food_name: 'Gluten', reaction_count: 12, avg_severity: 6.8, common_symptoms: ['Diarrhea', 'Fatigue'] },
          { food_name: 'Spicy Food', reaction_count: 8, avg_severity: 5.5, common_symptoms: ['Burning', 'Urgency'] },
          { food_name: 'Caffeine', reaction_count: 6, avg_severity: 4.2, common_symptoms: ['Anxiety', 'Cramping'] },
          { food_name: 'Alcohol', reaction_count: 4, avg_severity: 8.1, common_symptoms: ['Diarrhea', 'Nausea'] },
        ],
        weekly_summary: Array.from({ length: 12 }, (_, i) => ({
          week: `Week ${i + 1}`,
          total_symptoms: Math.floor(Math.random() * 20) + 5,
          avg_severity: Math.random() * 5 + 3,
          total_meals: Math.floor(Math.random() * 15) + 15,
          reactions: Math.floor(Math.random() * 8) + 1,
        })),
      };
      setData(mockData);
    } catch (error) {
      console.error('Error fetching visualization data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="h-64 bg-gray-200 rounded"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return <div>No data available</div>;
  }

  // Symptom Trends Chart Data
  const symptomTrendsData = {
    labels: data.symptom_trends.map(item => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Symptom Severity',
        data: data.symptom_trends.map(item => item.symptom_severity),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.1,
      },
      {
        label: 'Mood Rating',
        data: data.symptom_trends.map(item => item.mood_rating),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.1,
      },
      {
        label: 'Bristol Scale',
        data: data.symptom_trends.map(item => item.bristol_scale),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.1,
      },
    ],
  };

  // Food Reaction Patterns Chart Data
  const foodReactionData = {
    labels: data.food_reaction_patterns.map(item => item.food_name),
    datasets: [
      {
        label: 'Reaction Count',
        data: data.food_reaction_patterns.map(item => item.reaction_count),
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(168, 85, 247, 0.8)',
        ],
      },
    ],
  };

  // Weekly Summary Chart Data
  const weeklySummaryData = {
    labels: data.weekly_summary.map(item => item.week),
    datasets: [
      {
        label: 'Total Symptoms',
        data: data.weekly_summary.map(item => item.total_symptoms),
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
        yAxisID: 'y',
      },
      {
        label: 'Average Severity',
        data: data.weekly_summary.map(item => item.avg_severity),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        yAxisID: 'y1',
      },
    ],
  };

  // Severity Distribution Data
  const severityDistribution = {
    labels: ['Mild (1-3)', 'Moderate (4-6)', 'Severe (7-10)'],
    datasets: [
      {
        data: [
          data.food_reaction_patterns.filter(p => p.avg_severity <= 3).length,
          data.food_reaction_patterns.filter(p => p.avg_severity > 3 && p.avg_severity <= 6).length,
          data.food_reaction_patterns.filter(p => p.avg_severity > 6).length,
        ],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
        ],
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const multiAxisOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        beginAtZero: true,
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        beginAtZero: true,
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* Date Range Selector */}
      <Card>
        <CardHeader>
          <CardTitle>Data Visualization</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex-1">
              <Label htmlFor="start-date">Start Date</Label>
              <Input
                id="start-date"
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
              />
            </div>
            <div className="flex-1">
              <Label htmlFor="end-date">End Date</Label>
              <Input
                id="end-date"
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
              />
            </div>
            <Button onClick={fetchVisualizationData}>Update</Button>
          </div>
        </CardContent>
      </Card>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Symptom Trends Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Symptom Trends Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <Line data={symptomTrendsData} options={chartOptions} />
            </div>
          </CardContent>
        </Card>

        {/* Food Reaction Patterns */}
        <Card>
          <CardHeader>
            <CardTitle>Food Reaction Frequency</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <Bar data={foodReactionData} options={chartOptions} />
            </div>
          </CardContent>
        </Card>

        {/* Weekly Summary */}
        <Card>
          <CardHeader>
            <CardTitle>Weekly Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <Bar data={weeklySummaryData} options={multiAxisOptions} />
            </div>
          </CardContent>
        </Card>

        {/* Severity Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Reaction Severity Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <Doughnut data={severityDistribution} options={chartOptions} />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Trigger Foods Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Trigger Foods Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.food_reaction_patterns.map((pattern, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <h4 className="font-medium">{pattern.food_name}</h4>
                  <p className="text-sm text-gray-600">
                    Common symptoms: {pattern.common_symptoms.join(', ')}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold">{pattern.reaction_count}</div>
                  <div className="text-sm text-gray-600">reactions</div>
                </div>
                <div className="text-right ml-4">
                  <div className="text-lg font-bold">{pattern.avg_severity.toFixed(1)}</div>
                  <div className="text-sm text-gray-600">avg severity</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}