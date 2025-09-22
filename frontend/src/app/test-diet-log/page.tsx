'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'react-hot-toast';
import { MealType } from '@ibs-wellness/shared-types';

export default function TestDietLogPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [testResults, setTestResults] = useState<any[]>([]);

  const testFoods = [
    'Paratha',
    'Aloo Paratha', 
    'Gobi Paratha',
    'Pav Bhaji',
    'Biryani',
    'Dal Tadka',
    'Chapati'
  ];

  const testDietLog = async (foods: string[], mealType: MealType) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/diet/logs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          meal_type: mealType,
          foods: foods,
          portion_size: '1 serving',
          notes: `Test log for ${foods.join(', ')}`,
          consumed_at: new Date().toISOString()
        }),
      });

      const result = await response.json();
      
      if (response.ok) {
        toast.success(`Successfully logged: ${foods.join(', ')}`);
        setTestResults(prev => [...prev, {
          success: true,
          foods: foods,
          result: result,
          timestamp: new Date().toISOString()
        }]);
      } else {
        toast.error(`Failed to log: ${foods.join(', ')} - ${result.detail || 'Unknown error'}`);
        setTestResults(prev => [...prev, {
          success: false,
          foods: foods,
          error: result.detail || 'Unknown error',
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (error) {
      console.error('Error logging diet:', error);
      toast.error(`Error logging: ${foods.join(', ')}`);
      setTestResults(prev => [...prev, {
        success: false,
        foods: foods,
        error: error instanceof Error ? error.message : 'Network error',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDietLogs = async () => {
    try {
      const response = await fetch('/api/v1/diet/logs');
      const result = await response.json();
      
      if (response.ok) {
        toast.success(`Fetched ${result.items?.length || 0} diet logs`);
        setTestResults(prev => [...prev, {
          success: true,
          action: 'fetch',
          result: result,
          timestamp: new Date().toISOString()
        }]);
      } else {
        toast.error('Failed to fetch diet logs');
      }
    } catch (error) {
      console.error('Error fetching diet logs:', error);
      toast.error('Error fetching diet logs');
    }
  };

  const clearResults = () => {
    setTestResults([]);
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle>Diet Log Testing - Indian Menu Items</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Single Food Tests */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Test Single Food Items</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {testFoods.map((food) => (
                <Button
                  key={food}
                  onClick={() => testDietLog([food], MealType.LUNCH)}
                  disabled={isLoading}
                  variant="outline"
                  size="sm"
                >
                  Log {food}
                </Button>
              ))}
            </div>
          </div>

          {/* Multiple Foods Test */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Test Multiple Food Items</h3>
            <div className="space-y-2">
              <Button
                onClick={() => testDietLog(['Paratha', 'Dal Tadka', 'Pickle'], MealType.LUNCH)}
                disabled={isLoading}
                className="w-full"
              >
                Log Complete Meal: Paratha + Dal Tadka + Pickle
              </Button>
              <Button
                onClick={() => testDietLog(['Aloo Paratha', 'Yogurt', 'Butter'], MealType.BREAKFAST)}
                disabled={isLoading}
                className="w-full"
              >
                Log Breakfast: Aloo Paratha + Yogurt + Butter
              </Button>
            </div>
          </div>

          {/* Fetch Logs */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Fetch Diet Logs</h3>
            <Button onClick={fetchDietLogs} disabled={isLoading} className="w-full">
              Fetch All Diet Logs
            </Button>
          </div>

          {/* Clear Results */}
          <div>
            <Button onClick={clearResults} variant="destructive" className="w-full">
              Clear Test Results
            </Button>
          </div>

          {/* Test Results */}
          {testResults.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Test Results</h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {testResults.map((result, index) => (
                  <Card key={index} className={result.success ? 'border-green-200' : 'border-red-200'}>
                    <CardContent className="p-3">
                      <div className="flex justify-between items-start mb-2">
                        <span className={`font-medium ${result.success ? 'text-green-600' : 'text-red-600'}`}>
                          {result.success ? '✅ Success' : '❌ Failed'}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(result.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      
                      {result.foods && (
                        <div className="text-sm mb-2">
                          <strong>Foods:</strong> {result.foods.join(', ')}
                        </div>
                      )}
                      
                      {result.action && (
                        <div className="text-sm mb-2">
                          <strong>Action:</strong> {result.action}
                        </div>
                      )}
                      
                      {result.error && (
                        <div className="text-sm text-red-600">
                          <strong>Error:</strong> {result.error}
                        </div>
                      )}
                      
                      {result.result && (
                        <details className="text-xs">
                          <summary className="cursor-pointer text-gray-600">View Response</summary>
                          <pre className="mt-2 p-2 bg-gray-100 rounded overflow-x-auto">
                            {JSON.stringify(result.result, null, 2)}
                          </pre>
                        </details>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}