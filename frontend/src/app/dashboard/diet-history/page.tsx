'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Calendar, Clock, Utensils, Search, Filter, TrendingUp } from 'lucide-react';
import { apiService } from '@/lib/api';
import { DietLog } from '@/lib/api';
import { toast } from 'react-hot-toast';

interface DietHistoryPageProps {}

export default function DietHistoryPage({}: DietHistoryPageProps) {
  const [dietLogs, setDietLogs] = useState<DietLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [mealTypeFilter, setMealTypeFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'date' | 'meal_type'>('date');

  useEffect(() => {
    fetchDietLogs();
  }, []);

  const fetchDietLogs = async () => {
    try {
      setLoading(true);
      const response = await apiService.getDietLogs({
        limit: 100, // Get more records for history
        skip: 0
      });
      setDietLogs(response.items);
    } catch (error) {
      console.error('Error fetching diet logs:', error);
      toast.error('Failed to load diet history');
    } finally {
      setLoading(false);
    }
  };

  // Filter and sort diet logs
  const filteredAndSortedLogs = dietLogs
    .filter(log => {
      const matchesSearch = log.foods.some((item: string) => 
        item.toLowerCase().includes(searchTerm.toLowerCase())
      ) || log.notes?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesMealType = mealTypeFilter === 'all' || log.meal_type === mealTypeFilter;
      
      return matchesSearch && matchesMealType;
    })
    .sort((a, b) => {
      if (sortBy === 'date') {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      } else {
        return a.meal_type.localeCompare(b.meal_type);
      }
    });

  // Calculate statistics
  const totalLogs = dietLogs.length;
  const mealTypeCounts = dietLogs.reduce((acc, log) => {
    acc[log.meal_type] = (acc[log.meal_type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const getMealTypeColor = (mealType: string) => {
    const colors = {
      breakfast: 'bg-yellow-100 text-yellow-800',
      lunch: 'bg-green-100 text-green-800',
      dinner: 'bg-blue-100 text-blue-800',
      snack: 'bg-purple-100 text-purple-800'
    };
    return colors[mealType as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Diet History</h1>
          <p className="text-gray-600 mt-1">Track and review your dietary patterns</p>
        </div>
        <Button onClick={fetchDietLogs} variant="outline">
          <TrendingUp className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Logs</p>
                <p className="text-2xl font-bold text-gray-900">{totalLogs}</p>
              </div>
              <Utensils className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        {Object.entries(mealTypeCounts).map(([mealType, count]) => (
          <Card key={mealType}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 capitalize">{mealType}</p>
                  <p className="text-2xl font-bold text-gray-900">{count}</p>
                </div>
                <Badge className={getMealTypeColor(mealType)}>
                  {mealType}
                </Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Search food items or notes..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={mealTypeFilter} onValueChange={setMealTypeFilter}>
              <SelectTrigger className="w-full md:w-48">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filter by meal type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Meals</SelectItem>
                <SelectItem value="breakfast">Breakfast</SelectItem>
                <SelectItem value="lunch">Lunch</SelectItem>
                <SelectItem value="dinner">Dinner</SelectItem>
                <SelectItem value="snack">Snack</SelectItem>
              </SelectContent>
            </Select>

            <Select value={sortBy} onValueChange={(value) => setSortBy(value as 'date' | 'meal_type')}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="date">Sort by Date</SelectItem>
                <SelectItem value="meal_type">Sort by Meal Type</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Diet Logs List */}
      <div className="space-y-4">
        {filteredAndSortedLogs.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <Utensils className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No diet logs found</h3>
              <p className="text-gray-600">
                {searchTerm || mealTypeFilter !== 'all' 
                  ? 'Try adjusting your search or filters'
                  : 'Start logging your meals to see them here'
                }
              </p>
            </CardContent>
          </Card>
        ) : (
          filteredAndSortedLogs.map((log) => (
            <Card key={log.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Badge className={getMealTypeColor(log.meal_type)}>
                      {log.meal_type}
                    </Badge>
                    <div className="flex items-center text-sm text-gray-600">
                      <Calendar className="w-4 h-4 mr-1" />
                      {formatDate(log.created_at)}
                    </div>
                  </div>
                  {log.portion_size && (
                    <div className="text-sm text-gray-600">
                      Portion: {log.portion_size}
                    </div>
                  )}
                </div>

                <div className="mb-3">
                  <h3 className="font-medium text-gray-900 mb-2">Food Items:</h3>
                  <div className="flex flex-wrap gap-2">
                    {log.foods.map((item: string, index: number) => (
                      <Badge key={index} variant="outline">
                        {item}
                      </Badge>
                    ))}
                  </div>
                </div>

                {log.notes && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-700">{log.notes}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}