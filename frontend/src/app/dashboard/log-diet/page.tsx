'use client';

// import { ProtectedRoute } from "@/components/protected-route"; // Temporarily disabled for testing
import DietLogForm from "@/components/forms/diet-log-form";
import { DashboardHeader } from "@/components/layout/dashboard-header";
import { useState, useEffect } from "react";
import { Plus, History, Search, Filter, Calendar, Trash2, Eye } from "lucide-react";
import { apiService } from "@/lib/api";
import type { DietLog } from "@/lib/api";

export default function LogDietPage() {
  const [activeTab, setActiveTab] = useState<'log' | 'history'>('log');
  const [dietLogs, setDietLogs] = useState<DietLog[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'calories'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const fetchDietLogs = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.getDietLogs();
      setDietLogs(response.items || []);
    } catch (error) {
      console.error('Failed to fetch diet logs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'history') {
      fetchDietLogs();
    }
  }, [activeTab]);

  const deleteDietLog = async (id: string | number) => {
    setIsLoading(true);
    try {
      await apiService.deleteDietLog(Number(id));
      await fetchDietLogs();
    } catch (error) {
      console.error('Failed to delete diet log:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filterAndSortLogs = () => {
    let filtered = dietLogs.filter(log => {
      const matchesSearch = log.foods?.join(' ').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           log.notes?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesDate = !dateFilter || (log.created_at && log.created_at.startsWith(dateFilter));
      return matchesSearch && matchesDate;
    });

    return filtered.sort((a, b) => {
      let aValue, bValue;
      
      if (sortBy === 'date') {
        aValue = new Date(a.created_at || 0).getTime();
        bValue = new Date(b.created_at || 0).getTime();
      } else {
        aValue = a.calories || 0;
        bValue = b.calories || 0;
      }
      
      return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
    });
  };

  const getStats = () => {
    const totalLogs = dietLogs.length;
    const totalCalories = dietLogs.reduce((sum, log) => sum + (log.calories || 0), 0);
    const avgCalories = totalLogs > 0 ? Math.round(totalCalories / totalLogs) : 0;
    
    const uniqueDays = new Set(
      dietLogs
        .filter(log => log.created_at)
        .map(log => log.created_at!.split('T')[0])
    ).size;
    
    const avgCaloriesPerDay = uniqueDays > 0 ? Math.round(totalCalories / uniqueDays) : 0;

    return { totalLogs, totalCalories, avgCalories, avgCaloriesPerDay };
  };

  const stats = getStats();
  const filteredLogs = filterAndSortLogs();

  return (
    // <ProtectedRoute>
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader title="Diet Tracker" showBackButton />
      
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Tab Navigation */}
          <div className="bg-white rounded-lg shadow-sm border mb-6">
            <div className="flex border-b">
              <button
                onClick={() => setActiveTab('log')}
                className={`flex items-center space-x-2 px-6 py-4 font-medium transition-colors ${
                  activeTab === 'log'
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Plus size={20} />
                <span>Log New Meal</span>
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`flex items-center space-x-2 px-6 py-4 font-medium transition-colors ${
                  activeTab === 'history'
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <History size={20} />
                <span>View History</span>
              </button>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {activeTab === 'log' ? (
                <DietLogForm onSuccess={fetchDietLogs} />
              ) : (
                <div className="space-y-6">
                  {/* Statistics Dashboard */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">{stats.totalLogs}</div>
                      <div className="text-sm text-blue-600">Total Meals Logged</div>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">{stats.totalCalories}</div>
                      <div className="text-sm text-green-600">Total Calories</div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">{stats.avgCalories}</div>
                      <div className="text-sm text-purple-600">Avg Calories/Meal</div>
                    </div>
                    <div className="bg-orange-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">{stats.avgCaloriesPerDay}</div>
                      <div className="text-sm text-orange-600">Avg Calories/Day</div>
                    </div>
                  </div>

                  {/* Filters and Search */}
                  <div className="flex flex-col sm:flex-row gap-4">
                    <div className="flex-1 relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                      <input
                        type="text"
                        placeholder="Search meals, foods, or notes..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div className="flex gap-2">
                      <input
                        type="date"
                        value={dateFilter}
                        onChange={(e) => setDateFilter(e.target.value)}
                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <select
                        value={`${sortBy}-${sortOrder}`}
                        onChange={(e) => {
                          const [sort, order] = e.target.value.split('-');
                          setSortBy(sort as 'date' | 'calories');
                          setSortOrder(order as 'asc' | 'desc');
                        }}
                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="date-desc">Newest First</option>
                        <option value="date-asc">Oldest First</option>
                        <option value="calories-desc">Highest Calories</option>
                        <option value="calories-asc">Lowest Calories</option>
                      </select>
                    </div>
                  </div>

                  {/* Diet Logs List */}
                  {isLoading ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                      <p className="mt-2 text-gray-500">Loading your diet history...</p>
                    </div>
                  ) : filteredLogs.length === 0 ? (
                    <div className="text-center py-8">
                      <History className="mx-auto h-12 w-12 text-gray-400" />
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No meals found</h3>
                      <p className="mt-1 text-sm text-gray-500">
                        {searchTerm || dateFilter ? 'Try adjusting your filters' : 'Start by logging your first meal!'}
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {filteredLogs.map((log) => (
                        <div key={log.id} className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              {/* Meal Type and Time */}
                              <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center space-x-2">
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                                    {log.meal_type || 'Meal'}
                                  </span>
                                  <span className="text-sm text-gray-600">{formatDate(log.created_at)}</span>
                                </div>
                                {log.calories && (
                                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                    {log.calories} cal
                                  </span>
                                )}
                              </div>
                              
                              {/* Food Items with Visual Separation */}
                              <div className="mb-3">
                                <h4 className="text-sm font-medium text-gray-700 mb-2">Food Items:</h4>
                                <div className="flex flex-wrap gap-2">
                                  {log.foods && log.foods.length > 0 ? (
                                    log.foods.map((food, index) => (
                                      <div
                                        key={index}
                                        className="inline-flex items-center px-3 py-1.5 bg-orange-50 text-orange-800 rounded-full text-sm font-medium border border-orange-200"
                                      >
                                        <span className="mr-1">🍽️</span>
                                        {food}
                                      </div>
                                    ))
                                  ) : (
                                    <span className="text-sm text-gray-500 italic">No food items recorded</span>
                                  )}
                                </div>
                              </div>

                              {/* Additional Details */}
                              <div className="space-y-2">
                                {log.portion_size && (
                                  <div className="flex items-center text-sm text-gray-600">
                                    <span className="font-medium mr-2">Portion:</span>
                                    <span>{log.portion_size}</span>
                                  </div>
                                )}
                                
                                {log.notes && (
                                  <div>
                                    <span className="text-sm font-medium text-gray-700">Notes:</span>
                                    <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded mt-1">{log.notes}</p>
                                  </div>
                                )}
                              </div>
                            </div>
                            <button
                              onClick={() => deleteDietLog(log.id)}
                              className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              title="Delete meal log"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
  );
}