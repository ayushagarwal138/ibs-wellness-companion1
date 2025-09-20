'use client';

import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Calendar, 
  BarChart3, 
  PieChart, 
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Target
} from 'lucide-react';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';

interface SymptomData {
  date: string;
  severity: number;
  symptoms: string[];
  triggers: string[];
}

interface DietData {
  date: string;
  foods: string[];
  reactions: { food: string; severity: number }[];
}

interface TrendData {
  period: string;
  value: number;
  change: number;
}

interface AnalyticsData {
  symptomTrends: TrendData[];
  dietPatterns: { food: string; frequency: number; avgReaction: number }[];
  triggerAnalysis: { trigger: string; frequency: number; impact: number }[];
  weeklyProgress: { week: string; avgSeverity: number; goodDays: number }[];
  monthlyInsights: {
    bestMonth: string;
    worstMonth: string;
    improvementTrend: number;
    consistencyScore: number;
  };
}

// Mock data for demonstration
const mockAnalyticsData: AnalyticsData = {
  symptomTrends: [
    { period: 'Week 1', value: 6.2, change: -0.5 },
    { period: 'Week 2', value: 5.8, change: -0.4 },
    { period: 'Week 3', value: 4.9, change: -0.9 },
    { period: 'Week 4', value: 4.2, change: -0.7 },
  ],
  dietPatterns: [
    { food: 'Dairy', frequency: 15, avgReaction: 7.2 },
    { food: 'Gluten', frequency: 12, avgReaction: 6.8 },
    { food: 'Spicy Foods', frequency: 8, avgReaction: 8.1 },
    { food: 'High-fat Foods', frequency: 10, avgReaction: 6.5 },
    { food: 'Beans', frequency: 6, avgReaction: 7.8 },
  ],
  triggerAnalysis: [
    { trigger: 'Stress', frequency: 18, impact: 8.5 },
    { trigger: 'Lack of Sleep', frequency: 12, impact: 7.2 },
    { trigger: 'Travel', frequency: 4, impact: 6.8 },
    { trigger: 'Hormonal Changes', frequency: 8, impact: 7.5 },
  ],
  weeklyProgress: [
    { week: 'Jan W1', avgSeverity: 6.2, goodDays: 3 },
    { week: 'Jan W2', avgSeverity: 5.8, goodDays: 4 },
    { week: 'Jan W3', avgSeverity: 4.9, goodDays: 5 },
    { week: 'Jan W4', avgSeverity: 4.2, goodDays: 6 },
  ],
  monthlyInsights: {
    bestMonth: 'December 2023',
    worstMonth: 'October 2023',
    improvementTrend: 23.5,
    consistencyScore: 78,
  }
};

export default function DataVisualization() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData>(mockAnalyticsData);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'week' | 'month' | 'quarter'>('month');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // In a real app, fetch analytics data based on selectedTimeframe
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  }, [selectedTimeframe]);

  const renderSymptomTrends = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Symptom Severity Trends</h3>
        <div className="flex space-x-2">
          {['week', 'month', 'quarter'].map((timeframe) => (
            <button
              key={timeframe}
              onClick={() => setSelectedTimeframe(timeframe as any)}
              className={`px-3 py-1 text-sm rounded-md capitalize ${
                selectedTimeframe === timeframe
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {timeframe}
            </button>
          ))}
        </div>
      </div>

      {/* Trend Chart Visualization */}
      <div className="bg-white border rounded-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {analyticsData.symptomTrends.map((trend, index) => (
            <div key={index} className="text-center">
              <div className="text-2xl font-bold text-gray-900">{trend.value}</div>
              <div className="text-sm text-gray-500">{trend.period}</div>
              <div className={`flex items-center justify-center mt-1 ${
                trend.change < 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {trend.change < 0 ? (
                  <TrendingDown size={16} className="mr-1" />
                ) : (
                  <TrendingUp size={16} className="mr-1" />
                )}
                <span className="text-sm">{Math.abs(trend.change)}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Simple Bar Chart Representation */}
        <div className="space-y-3">
          {analyticsData.symptomTrends.map((trend, index) => (
            <div key={index} className="flex items-center space-x-4">
              <div className="w-16 text-sm text-gray-600">{trend.period}</div>
              <div className="flex-1">
                <Progress value={(trend.value / 10) * 100} className="h-6" />
              </div>
              <div className="w-12 text-sm font-medium">{trend.value}/10</div>
            </div>
          ))}
        </div>
      </div>

      {/* Key Insights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="text-green-600 mr-2" size={20} />
            <span className="font-medium text-green-800">Improvement</span>
          </div>
          <p className="text-sm text-green-700 mt-2">
            {analyticsData.monthlyInsights.improvementTrend}% improvement over the last month
          </p>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <Target className="text-blue-600 mr-2" size={20} />
            <span className="font-medium text-blue-800">Consistency</span>
          </div>
          <p className="text-sm text-blue-700 mt-2">
            {analyticsData.monthlyInsights.consistencyScore}% consistency in tracking
          </p>
        </div>
        
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center">
            <Calendar className="text-purple-600 mr-2" size={20} />
            <span className="font-medium text-purple-800">Best Period</span>
          </div>
          <p className="text-sm text-purple-700 mt-2">
            {analyticsData.monthlyInsights.bestMonth}
          </p>
        </div>
      </div>
    </div>
  );

  const renderDietAnalysis = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Diet & Food Reaction Analysis</h3>
      
      {/* Food Trigger Rankings */}
      <div className="bg-white border rounded-lg p-6">
        <h4 className="font-medium text-gray-900 mb-4">Top Food Triggers</h4>
        <div className="space-y-4">
          {analyticsData.dietPatterns
            .sort((a, b) => b.avgReaction - a.avgReaction)
            .map((pattern, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${
                    index === 0 ? 'bg-red-500' : index === 1 ? 'bg-orange-500' : index === 2 ? 'bg-yellow-500' : 'bg-gray-400'
                  }`}>
                    {index + 1}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{pattern.food}</div>
                    <div className="text-sm text-gray-500">
                      {pattern.frequency} occurrences this month
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium text-gray-900">
                    {pattern.avgReaction.toFixed(1)}/10
                  </div>
                  <Badge variant={pattern.avgReaction > 7 ? 'destructive' : pattern.avgReaction > 5 ? 'warning' : 'success'}>
                    {pattern.avgReaction > 7 ? 'High Risk' : pattern.avgReaction > 5 ? 'Moderate' : 'Low Risk'}
                  </Badge>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Diet Recommendations */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h4 className="font-medium text-blue-900 mb-4">Personalized Recommendations</h4>
        <div className="space-y-3">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="text-blue-600 mt-0.5" size={16} />
            <div>
              <p className="text-sm text-blue-800 font-medium">Avoid High-Risk Foods</p>
              <p className="text-sm text-blue-700">
                Consider eliminating dairy and spicy foods for 2 weeks to see improvement
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <CheckCircle className="text-blue-600 mt-0.5" size={16} />
            <div>
              <p className="text-sm text-blue-800 font-medium">Safe Foods to Include</p>
              <p className="text-sm text-blue-700">
                Rice, bananas, and lean proteins show no negative reactions
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Indian Food Insights */}
      <div className="bg-gradient-to-r from-orange-50 to-yellow-50 border border-orange-200 rounded-lg p-6">
        <h4 className="font-medium text-orange-900 mb-4">Indian Food Analysis</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h5 className="text-sm font-medium text-orange-800 mb-3">IBS-Friendly Indian Dishes</h5>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-orange-700">Khichdi with Ghee</span>
                <Badge variant="success" className="text-xs">Safe</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-orange-700">Moong Dal Soup</span>
                <Badge variant="success" className="text-xs">Safe</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-orange-700">Curd Rice</span>
                <Badge variant="warning" className="text-xs">Monitor</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-orange-700">Bottle Gourd Curry</span>
                <Badge variant="success" className="text-xs">Safe</Badge>
              </div>
            </div>
          </div>
          <div>
            <h5 className="text-sm font-medium text-orange-800 mb-3">Spice Tolerance Analysis</h5>
            <div className="space-y-3">
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-orange-700">Cumin (Jeera)</span>
                  <span className="text-green-600">Well Tolerated</span>
                </div>
                <Progress value={85} className="h-2" />
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-orange-700">Turmeric (Haldi)</span>
                  <span className="text-green-600">Beneficial</span>
                </div>
                <Progress value={92} className="h-2" />
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-orange-700">Red Chili</span>
                  <span className="text-red-600">Trigger</span>
                </div>
                <Progress value={25} className="h-2" />
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-orange-700">Ginger (Adrak)</span>
                  <span className="text-green-600">Helpful</span>
                </div>
                <Progress value={88} className="h-2" />
              </div>
            </div>
          </div>
        </div>
        <div className="mt-4 p-3 bg-orange-100 rounded-lg">
          <p className="text-sm text-orange-800">
            <strong>Insight:</strong> Your data shows better tolerance for traditional Indian spices like cumin and turmeric. 
            Consider incorporating these into your meals while avoiding high-heat spices.
          </p>
        </div>
      </div>
    </div>
  );

  const renderTriggerAnalysis = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Trigger Pattern Analysis</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Lifestyle Triggers */}
        <div className="bg-white border rounded-lg p-6">
          <h4 className="font-medium text-gray-900 mb-4">Lifestyle Triggers</h4>
          <div className="space-y-4">
            {analyticsData.triggerAnalysis.map((trigger, index) => (
              <div key={index} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">{trigger.trigger}</span>
                  <span className="text-sm text-gray-500">{trigger.frequency} times</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Progress value={(trigger.impact / 10) * 100} className="flex-1 h-2" />
                  <span className="text-sm font-medium text-gray-600">
                    {trigger.impact.toFixed(1)}/10
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Weekly Progress */}
        <div className="bg-white border rounded-lg p-6">
          <h4 className="font-medium text-gray-900 mb-4">Weekly Progress</h4>
          <div className="space-y-4">
            {analyticsData.weeklyProgress.map((week, index) => (
              <div key={index} className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-gray-700">{week.week}</div>
                  <div className="text-xs text-gray-500">{week.goodDays} good days</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">
                    {week.avgSeverity.toFixed(1)}/10
                  </div>
                  <div className={`text-xs ${
                    week.avgSeverity < 5 ? 'text-green-600' : week.avgSeverity < 7 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {week.avgSeverity < 5 ? 'Good' : week.avgSeverity < 7 ? 'Moderate' : 'Challenging'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Correlation Insights */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h4 className="font-medium text-yellow-900 mb-4">Pattern Insights</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <p className="text-sm font-medium text-yellow-800">Strong Correlations</p>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Stress levels correlate with symptom severity (r=0.78)</li>
              <li>• Poor sleep increases next-day symptoms by 40%</li>
              <li>• Weekend symptoms are 25% lower on average</li>
            </ul>
          </div>
          <div className="space-y-2">
            <p className="text-sm font-medium text-yellow-800">Recommendations</p>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Focus on stress management techniques</li>
              <li>• Maintain consistent sleep schedule</li>
              <li>• Consider weekend routine for weekdays</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );

  const renderPredictiveInsights = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Predictive Insights & Forecasting</h3>
      
      {/* Risk Forecast */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-medium text-gray-900">Tomorrow's Risk</h4>
            <Activity className="text-blue-500" size={20} />
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">Low</div>
            <div className="text-sm text-gray-500">23% chance of flare-up</div>
            <Progress value={23} className="mt-3" />
          </div>
        </div>
        
        <div className="bg-white border rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-medium text-gray-900">This Week</h4>
            <Calendar className="text-orange-500" size={20} />
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-600">Moderate</div>
            <div className="text-sm text-gray-500">45% chance of symptoms</div>
            <Progress value={45} className="mt-3" />
          </div>
        </div>
        
        <div className="bg-white border rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-medium text-gray-900">Next Month</h4>
            <TrendingUp className="text-green-500" size={20} />
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">Improving</div>
            <div className="text-sm text-gray-500">15% reduction expected</div>
            <Progress value={85} className="mt-3" />
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
        <h4 className="font-medium text-purple-900 mb-4">AI-Powered Recommendations</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h5 className="text-sm font-medium text-purple-800 mb-2">Immediate Actions</h5>
            <ul className="text-sm text-purple-700 space-y-1">
              <li>• Reduce dairy intake for the next 3 days</li>
              <li>• Practice 10 minutes of meditation today</li>
              <li>• Ensure 8+ hours of sleep tonight</li>
              <li>• Take probiotics with breakfast</li>
            </ul>
          </div>
          <div>
            <h5 className="text-sm font-medium text-purple-800 mb-2">Long-term Strategy</h5>
            <ul className="text-sm text-purple-700 space-y-1">
              <li>• Start a 2-week elimination diet</li>
              <li>• Schedule stress management consultation</li>
              <li>• Increase fiber intake gradually</li>
              <li>• Consider FODMAP diet trial</li>
            </ul>
          </div>
          <div>
            <h5 className="text-sm font-medium text-purple-800 mb-2">Indian Cuisine Focus</h5>
            <ul className="text-sm text-purple-700 space-y-1">
              <li>• Try khichdi for easy digestion</li>
              <li>• Use ginger in daily cooking</li>
              <li>• Replace red chili with black pepper</li>
              <li>• Include fennel seeds after meals</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Success Metrics */}
      <div className="bg-white border rounded-lg p-6">
        <h4 className="font-medium text-gray-900 mb-4">Success Metrics</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">78%</div>
            <div className="text-sm text-gray-500">Symptom Control</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">6.2</div>
            <div className="text-sm text-gray-500">Quality of Life</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">85%</div>
            <div className="text-sm text-gray-500">Goal Achievement</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">23</div>
            <div className="text-sm text-gray-500">Streak (days)</div>
          </div>
        </div>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-gray-500 mt-4">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          IBS Analytics & Insights
        </h1>
        <p className="text-gray-600">
          Understand your patterns, track progress, and get personalized recommendations.
        </p>
      </div>

      <Tabs defaultValue="trends" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="trends" className="flex items-center space-x-2">
            <BarChart3 size={16} />
            <span>Trends</span>
          </TabsTrigger>
          <TabsTrigger value="diet" className="flex items-center space-x-2">
            <PieChart size={16} />
            <span>Diet Analysis</span>
          </TabsTrigger>
          <TabsTrigger value="triggers" className="flex items-center space-x-2">
            <AlertTriangle size={16} />
            <span>Triggers</span>
          </TabsTrigger>
          <TabsTrigger value="predictions" className="flex items-center space-x-2">
            <TrendingUp size={16} />
            <span>Predictions</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="trends">
          {renderSymptomTrends()}
        </TabsContent>

        <TabsContent value="diet">
          {renderDietAnalysis()}
        </TabsContent>

        <TabsContent value="triggers">
          {renderTriggerAnalysis()}
        </TabsContent>

        <TabsContent value="predictions">
          {renderPredictiveInsights()}
        </TabsContent>
      </Tabs>
    </div>
  );
}