'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Doughnut, Bar } from 'react-chartjs-2';
import { toast } from 'react-hot-toast';
import { UI_CONFIG } from '@/lib/config';
import { dietService, DietStats } from '@/services/diet-service';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

export default function DietStats() {
  const [stats, setStats] = useState<DietStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [dateRange, setDateRange] = useState('30'); // days

  useEffect(() => {
    fetchStats();
  }, [dateRange]);

  const fetchStats = async () => {
    setIsLoading(true);
    try {
      const days = parseInt(dateRange);
      const dietStats = await dietService.getDietStats(days);
      
      // Transform the data to match the expected format
      const transformedStats: DietStats = {
        total_meals_logged: dietStats.total_meals_logged,
        meals_by_type: dietStats.meals_by_type,
        average_daily_calories: dietStats.average_daily_calories,
        mood_correlation: dietStats.mood_correlation,
        most_consumed_foods: dietStats.most_consumed_foods
      };
      
      setStats(transformedStats);
    } catch (error) {
      console.error('Error fetching diet stats:', error);
      toast.error('Failed to load diet statistics');
      
      // Fallback to empty data structure instead of mock data
      setStats({
        total_meals_logged: 0,
        meals_by_type: {},
        average_daily_calories: 0,
        mood_correlation: {},
        most_consumed_foods: []
      });
    } finally {
      setIsLoading(false);
    }
  };

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

  if (!stats) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center text-gray-500">No diet data available</p>
        </CardContent>
      </Card>
    );
  }

  // Meals by Type Chart
  const mealTypes = Object.keys(stats.meals_by_type || {});
  const hasMealData = mealTypes.length > 0;
  
  const mealsChartData = {
    labels: hasMealData 
      ? mealTypes.map(key => key.charAt(0).toUpperCase() + key.slice(1))
      : ['No Data'],
    datasets: [
      {
        label: 'Number of Meals',
        data: hasMealData 
          ? Object.values(stats.meals_by_type)
          : [0],
        backgroundColor: hasMealData ? [
          'rgba(255, 206, 84, 0.8)',   // Yellow for breakfast
          'rgba(54, 162, 235, 0.8)',   // Blue for lunch
          'rgba(255, 99, 132, 0.8)',   // Red for dinner
          'rgba(75, 192, 192, 0.8)',   // Teal for snack
        ] : ['rgba(200, 200, 200, 0.8)'],
        borderColor: hasMealData ? [
          'rgba(255, 206, 84, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 99, 132, 1)',
          'rgba(75, 192, 192, 1)',
        ] : ['rgba(200, 200, 200, 1)'],
        borderWidth: 1,
      },
    ],
  };

  // Mood Correlation Chart
  const moodKeys = Object.keys(stats.mood_correlation || {});
  const hasMoodData = moodKeys.length > 0;
  
  const moodChartData = {
    labels: hasMoodData 
      ? moodKeys
      : ['No Data'],
    datasets: [
      {
        label: 'Average Mood Rating',
        data: hasMoodData 
          ? Object.values(stats.mood_correlation)
          : [0],
        backgroundColor: hasMoodData 
          ? 'rgba(153, 102, 255, 0.8)'
          : 'rgba(200, 200, 200, 0.8)',
        borderColor: hasMoodData 
          ? 'rgba(153, 102, 255, 1)'
          : 'rgba(200, 200, 200, 1)',
        borderWidth: 1,
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

  const doughnutOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* Header with Date Range Selector */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Diet Statistics</h2>
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
            <CardTitle className="text-sm font-medium">Total Meals Logged</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_meals_logged}</div>
            <p className="text-xs text-gray-500">meal entries</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Average Daily Calories</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.average_daily_calories !== null && stats.average_daily_calories !== undefined 
                ? Math.round(stats.average_daily_calories) 
                : 'N/A'}
            </div>
            <p className="text-xs text-gray-500">calories per day</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Most Consumed Foods</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {stats.most_consumed_foods && stats.most_consumed_foods.length > 0 ? (
                stats.most_consumed_foods.slice(0, 3).map((food, index) => (
                  <div key={index} className="text-sm">
                    {index + 1}. {food}
                  </div>
                ))
              ) : (
                <div className="text-sm text-gray-500">No food data available</div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Meals by Type */}
        <Card>
          <CardHeader>
            <CardTitle>Meals by Type</CardTitle>
          </CardHeader>
          <CardContent>
            <Doughnut data={mealsChartData} options={doughnutOptions} />
          </CardContent>
        </Card>

        {/* Mood Correlation */}
        <Card>
          <CardHeader>
            <CardTitle>Mood Before vs After Eating</CardTitle>
          </CardHeader>
          <CardContent>
            <Bar data={moodChartData} options={chartOptions} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}