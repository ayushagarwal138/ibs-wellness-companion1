'use client';

import React, { useState, useEffect } from 'react';
import { ProtectedRoute } from "@/components/protected-route";
import { DashboardHeader } from "@/components/layout/dashboard-header";
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { apiService, DietLog } from '@/lib/api';
import { toast } from 'react-hot-toast';
import { 
  Calendar, 
  Search, 
  Filter, 
  Utensils, 
  Clock, 
  TrendingUp,
  Plus,
  Eye,
  Trash2,
  Download
} from 'lucide-react';
import Link from 'next/link';

export default function DietHistoryPage() {
  const [dietLogs, setDietLogs] = useState<DietLog[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<DietLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [mealTypeFilter, setMealTypeFilter] = useState<string>('all');
  const [dateFilter, setDateFilter] = useState<string>('all');

  const [sortBy, setSortBy] = useState<'date' | 'meal_type' | 'calories'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    fetchDietLogs();
  }, []);

  useEffect(() => {
    filterAndSortLogs();
  }, [dietLogs, searchTerm, mealTypeFilter, dateFilter, sortBy, sortOrder]);

  const fetchDietLogs = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getDietLogs();
      setDietLogs(response.items);
    } catch (error) {
      console.error('Error fetching diet logs:', error);
      toast.error('Failed to load diet history');
    } finally {
      setIsLoading(false);
    }
  };

  const filterAndSortLogs = () => {
    let filtered = dietLogs.filter(log => {
      const matchesSearch = log.foods.some((food: string) => 
        food.toLowerCase().includes(searchTerm.toLowerCase())
      ) || (log.notes && log.notes.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesMealType = mealTypeFilter === 'all' || log.meal_type === mealTypeFilter;
      
      let matchesDate = true;
      if (dateFilter !== 'all' && log.created_at) {
        const logDate = new Date(log.created_at);
        const now = new Date();
        const daysDiff = Math.floor((now.getTime() - logDate.getTime()) / (1000 * 60 * 60 * 24));
        
        switch (dateFilter) {
          case 'today':
            matchesDate = daysDiff === 0;
            break;
          case 'week':
            matchesDate = daysDiff <= 7;
            break;
          case 'month':
            matchesDate = daysDiff <= 30;
            break;
        }
      }
      
      return matchesSearch && matchesMealType && matchesDate;
    });

    // Sort logs
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'date':
          const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
          const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
          comparison = dateA - dateB;
          break;
        case 'meal_type':
          comparison = a.meal_type.localeCompare(b.meal_type);
          break;
        case 'calories':
          comparison = (a.calories || 0) - (b.calories || 0);
          break;
      }
      
      return sortOrder === 'desc' ? -comparison : comparison;
    });

    setFilteredLogs(filtered);
  };

  const deleteDietLog = async (id: string | number) => {
    if (!confirm('Are you sure you want to delete this diet log?')) return;

    try {
      setIsLoading(true);
      await apiService.deleteDietLog(Number(id));
      toast.success('Diet log deleted successfully');
      fetchDietLogs();
    } catch (error) {
      console.error('Error deleting diet log:', error);
      toast.error('Failed to delete diet log');
    } finally {
      setIsLoading(false);
    }
  };

  const getMealTypeIcon = (mealType: string) => {
    switch (mealType) {
      case 'breakfast': return '🌅';
      case 'lunch': return '☀️';
      case 'dinner': return '🌙';
      case 'snack': return '🍎';
      default: return '🍽️';
    }
  };

  const getMealTypeColor = (mealType: string) => {
    switch (mealType) {
      case 'breakfast': return 'bg-yellow-100 text-yellow-800';
      case 'lunch': return 'bg-orange-100 text-orange-800';
      case 'dinner': return 'bg-purple-100 text-purple-800';
      case 'snack': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown date';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStats = () => {
    // Use the filtered logs that are actually displayed to the user
    // This ensures statistics match what the user can see
    const statsLogs = filteredLogs;
    
    const totalLogs = statsLogs.length;
    const totalCalories = statsLogs.reduce((sum, log) => sum + (log.calories || 0), 0);
    const avgCaloriesPerMeal = totalLogs > 0 ? Math.round(totalCalories / totalLogs) : 0;
    
    const mealTypeCounts = statsLogs.reduce((acc, log) => {
      acc[log.meal_type] = (acc[log.meal_type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return { totalLogs, totalCalories, avgCaloriesPerMeal, mealTypeCounts };
  };

  const stats = getStats();

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50">
          <DashboardHeader title="Diet History" showBackButton />
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Loading your diet history...</p>
              </div>
            </div>
          </main>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <DashboardHeader title="Diet History" showBackButton />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header with Stats */}
          <div className="mb-8">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <Utensils className="h-6 w-6 text-green-600" />
                  Your Diet History
                </h1>
                <p className="text-gray-600 mt-1">Track and analyze your eating patterns</p>
              </div>
              <Link href="/dashboard/log-diet">
                <Button className="flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  Log New Meal
                </Button>
              </Link>
            </div>

            {/* Statistics Overview */}
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Statistics Overview</h2>
              <p className="text-sm text-gray-600 mt-1">Statistics reflect your currently filtered data</p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Total Meals</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.totalLogs}</p>
                    </div>
                    <Utensils className="h-8 w-8 text-blue-600" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Total Calories</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.totalCalories.toLocaleString()}</p>
                    </div>
                    <TrendingUp className="h-8 w-8 text-green-600" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Avg per Meal</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.avgCaloriesPerMeal}</p>
                    </div>
                    <Calendar className="h-8 w-8 text-purple-600" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Most Common</p>
                      <p className="text-lg font-bold text-gray-900">
                        {Object.entries(stats.mealTypeCounts).sort(([,a], [,b]) => b - a)[0]?.[0] || 'N/A'}
                      </p>
                    </div>
                    <Clock className="h-8 w-8 text-orange-600" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Filters */}
          <Card className="mb-6">
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search foods or notes..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                
                <Select value={mealTypeFilter} onValueChange={setMealTypeFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Meal Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Meals</SelectItem>
                    <SelectItem value="breakfast">🌅 Breakfast</SelectItem>
                    <SelectItem value="lunch">☀️ Lunch</SelectItem>
                    <SelectItem value="dinner">🌙 Dinner</SelectItem>
                    <SelectItem value="snack">🍎 Snack</SelectItem>
                  </SelectContent>
                </Select>
                
                <Select value={dateFilter} onValueChange={setDateFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Time Period" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Time</SelectItem>
                    <SelectItem value="today">Today</SelectItem>
                    <SelectItem value="week">Last Week</SelectItem>
                    <SelectItem value="month">Last Month</SelectItem>
                  </SelectContent>
                </Select>
                
                <Select value={sortBy} onValueChange={(value: 'date' | 'meal_type' | 'calories') => setSortBy(value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sort By" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="date">Date</SelectItem>
                    <SelectItem value="meal_type">Meal Type</SelectItem>
                    <SelectItem value="calories">Calories</SelectItem>
                  </SelectContent>
                </Select>
                
                <Button
                  variant="outline"
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  className="flex items-center gap-2"
                >
                  <Filter className="h-4 w-4" />
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Diet Logs */}
          {filteredLogs.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Utensils className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No diet logs found</h3>
                <p className="text-gray-600 mb-6">
                  {dietLogs.length === 0 
                    ? "Start tracking your meals to see your diet history here."
                    : "Try adjusting your filters to see more results."
                  }
                </p>
                <Link href="/dashboard/log-diet">
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Log Your First Meal
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {filteredLogs.map((log) => (
                <Card key={log.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <Badge className={`${getMealTypeColor(log.meal_type)} font-medium`}>
                            {getMealTypeIcon(log.meal_type)} {log.meal_type.charAt(0).toUpperCase() + log.meal_type.slice(1)}
                          </Badge>
                          <div className="flex items-center text-sm text-gray-500 gap-1">
                            <Clock className="h-4 w-4" />
                            {formatDate(log.consumed_at)}
                          </div>
                        </div>
                        
                        <div className="mb-3">
                          <h3 className="font-medium text-gray-900 mb-1">Foods:</h3>
                          <div className="flex flex-wrap gap-2">
                            {log.foods.map((food, index) => (
                              <Badge key={index} variant="secondary" className="text-xs">
                                {food}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                          {log.portion_size && (
                            <div>
                              <span className="text-gray-500">Portion:</span>
                              <span className="ml-1 font-medium">{log.portion_size}</span>
                            </div>
                          )}
                          {log.calories && (
                            <div>
                              <span className="text-gray-500">Calories:</span>
                              <span className="ml-1 font-medium">{log.calories}</span>
                            </div>
                          )}

                        </div>
                        
                        {log.notes && (
                          <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-700">{log.notes}</p>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => deleteDietLog(log.id)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </main>
      </div>
    </ProtectedRoute>
  );
}