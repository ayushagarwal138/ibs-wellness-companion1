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
      const startDate = new Date(dateRange.start || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000));
      const endDate = new Date(dateRange.end || new Date());
      const daysDiff = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));

      const apiUrl = process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000';
      const token = localStorage.getItem('access_token');

      // Fetch real data from backend APIs
      const [symptomLogsResponse, dietStatsResponse, foodReactionsResponse] = await Promise.all([
        // Fetch symptom logs
        fetch(`${apiUrl}/api/v1/symptom-logs/?days=${daysDiff}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }).catch(() => null),
        
        // Fetch diet stats
        fetch(`${apiUrl}/api/v1/diet/stats/diet?days=${daysDiff}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }).catch(() => null),
        
        // Fetch food reactions
        fetch(`${apiUrl}/api/v1/diet/reactions?days=${daysDiff}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }).catch(() => null),
      ]);

      // Process symptom logs data
      let symptomTrends: TrendData[] = [];
      if (symptomLogsResponse && symptomLogsResponse.ok) {
        const symptomData = await symptomLogsResponse.json();
        const logs = symptomData?.data || [];
        
        // Group logs by date and calculate averages
        const dateGroups: { [key: string]: any[] } = {};
        logs.forEach((log: any) => {
          if (log?.logged_at) {
            const logDate = new Date(log.logged_at).toISOString().split('T')[0];
            if (logDate && !dateGroups[logDate]) dateGroups[logDate] = [];
            if (logDate) dateGroups[logDate].push(log);
          }
        });

        // Create trend data for each day in the range
        for (let i = 0; i < daysDiff; i++) {
          const date = new Date(startDate.getTime() + i * 24 * 60 * 60 * 1000);
          const dateString = date.toISOString().split('T')[0];
          if (!dateString) continue;
          const dayLogs = dateGroups[dateString] || [];
          
          symptomTrends.push({
            date: dateString,
            symptom_severity: dayLogs.length > 0 ? 
              dayLogs.reduce((sum: number, log: any) => sum + (log.severity || 0), 0) / dayLogs.length : 0,
            mood_rating: dayLogs.length > 0 ? 
              dayLogs.reduce((sum: number, log: any) => sum + (log.mood_rating || 5), 0) / dayLogs.length : 5,
            bristol_scale: dayLogs.length > 0 ? 
              dayLogs.reduce((sum: number, log: any) => sum + (log.bristol_stool_type || 4), 0) / dayLogs.length : 4,
          });
        }
      }

      // Process food reaction patterns
      let foodReactionPatterns: FoodReactionPattern[] = [];
      if (foodReactionsResponse && foodReactionsResponse.ok) {
        const reactionData = await foodReactionsResponse.json();
        const reactions = reactionData?.data || [];
        
        // Group reactions by food and calculate stats
        const foodGroups: { [key: string]: any[] } = {};
        reactions.forEach((reaction: any) => {
          const foodName = reaction.food_name || 'Unknown';
          if (!foodGroups[foodName]) foodGroups[foodName] = [];
          foodGroups[foodName].push(reaction);
        });

        foodReactionPatterns = Object.entries(foodGroups).map(([foodName, reactions]) => ({
          food_name: foodName,
          reaction_count: reactions.length,
          avg_severity: reactions.length > 0 ? reactions.reduce((sum: number, r: any) => sum + (r.severity || 0), 0) / reactions.length : 0,
          common_symptoms: Array.from(new Set(reactions.flatMap((r: any) => r.symptoms || []))).slice(0, 3),
        })).sort((a, b) => b.reaction_count - a.reaction_count).slice(0, 10);
      }

      // Process diet stats for weekly summary
      let weeklySummary: any[] = [];
      if (dietStatsResponse && dietStatsResponse.ok) {
        const dietData = await dietStatsResponse.json();
        
        // Create weekly summary based on available data
        const weeksCount = Math.ceil(daysDiff / 7);
        for (let i = 0; i < weeksCount; i++) {
          weeklySummary.push({
            week: `Week ${i + 1}`,
            total_symptoms: Math.floor(symptomTrends.slice(i * 7, (i + 1) * 7)
              .reduce((sum, day) => sum + (day.symptom_severity > 0 ? 1 : 0), 0)),
            avg_severity: symptomTrends.slice(i * 7, (i + 1) * 7)
              .reduce((sum, day) => sum + day.symptom_severity, 0) / 7,
            total_meals: Math.floor((dietData?.total_meals_logged || 0) / weeksCount),
            reactions: Math.floor(foodReactionPatterns.reduce((sum, pattern) => sum + pattern.reaction_count, 0) / weeksCount),
          });
        }
      }

      // Fallback to empty data if no real data available
      if (symptomTrends.length === 0) {
        for (let i = 0; i < daysDiff; i++) {
          const date = new Date(startDate.getTime() + i * 24 * 60 * 60 * 1000);
          const dateString = date.toISOString().split('T')[0];
          if (dateString) {
            symptomTrends.push({
              date: dateString,
              symptom_severity: 0,
              mood_rating: 5,
              bristol_scale: 4,
            });
          }
        }
      }

      const visualizationData: VisualizationData = {
        symptom_trends: symptomTrends,
        food_reaction_patterns: foodReactionPatterns,
        weekly_summary: weeklySummary.length > 0 ? weeklySummary : [{
          week: 'Week 1',
          total_symptoms: 0,
          avg_severity: 0,
          total_meals: 0,
          reactions: 0,
        }],
      };

      setData(visualizationData);
    } catch (error) {
      console.error('Error fetching visualization data:', error);
      toast.error('Failed to load analytics data. Please try again.');
      
      // Provide fallback empty data
      setData({
        symptom_trends: [],
        food_reaction_patterns: [],
        weekly_summary: [],
      });
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