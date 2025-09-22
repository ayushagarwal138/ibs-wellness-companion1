'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Lightbulb, 
  Star, 
  Clock, 
  CheckCircle,
  X,
  RefreshCw,
  Target,
  TrendingUp,
  Heart,
  Utensils,
  Activity
} from 'lucide-react';
import { mlService, PersonalizedRecommendationsResponse } from '@/services/ml-service';
import { toast } from 'react-hot-toast';

interface PersonalizedRecommendation {
  id: string;
  type: string;
  title: string;
  description: string;
  priority: string;
  confidence: number;
  expectedImpact: string;
}

interface PersonalizedRecommendationsProps {
  userId?: string;
  className?: string;
  maxRecommendations?: number;
  onRecommendationAction?: (recommendationId: string, action: 'accept' | 'dismiss') => void;
}

export function PersonalizedRecommendations({ 
  userId, 
  className,
  maxRecommendations = 6,
  onRecommendationAction 
}: PersonalizedRecommendationsProps) {
  const [recommendations, setRecommendations] = useState<PersonalizedRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [dismissedIds, setDismissedIds] = useState<Set<string>>(new Set());

  const fetchRecommendations = async (showRefreshToast = false) => {
    try {
      setRefreshing(true);
      const response = await mlService.getPersonalizedRecommendations();
      
      // Transform the response into our expected format
      const transformedRecommendations: PersonalizedRecommendation[] = [
        ...response.dietary_recommendations.map((rec, index) => ({
          id: `dietary-${index}`,
          type: 'dietary',
          title: rec.title,
          description: rec.description,
          priority: rec.priority,
          confidence: 85,
          expectedImpact: 'Improved digestive health'
        })),
        ...response.lifestyle_insights.map((insight, index) => ({
          id: `lifestyle-${index}`,
          type: 'lifestyle',
          title: insight.category,
          description: insight.recommendation,
          priority: insight.priority,
          confidence: 80,
          expectedImpact: 'Better symptom management'
        }))
      ];
      
      setRecommendations(transformedRecommendations.slice(0, maxRecommendations));
      
      if (showRefreshToast) {
        toast.success('Recommendations updated!');
      }
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
      toast.error('Failed to load recommendations');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [userId, maxRecommendations]);

  const handleRefresh = () => {
    fetchRecommendations(true);
  };

  const handleAccept = (recommendation: PersonalizedRecommendation) => {
    toast.success(`Great! We'll help you track "${recommendation.title}"`);
    onRecommendationAction?.(recommendation.id, 'accept');
  };

  const handleDismiss = (recommendation: PersonalizedRecommendation) => {
    setDismissedIds(prev => new Set(prev).add(recommendation.id));
    onRecommendationAction?.(recommendation.id, 'dismiss');
    toast.success('Recommendation dismissed');
  };

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'dietary':
        return <Utensils className="w-5 h-5" />;
      case 'lifestyle':
        return <Activity className="w-5 h-5" />;
      case 'wellness':
        return <Heart className="w-5 h-5" />;
      default:
        return <Lightbulb className="w-5 h-5" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const visibleRecommendations = recommendations.filter(rec => !dismissedIds.has(rec.id));

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-blue-500" />
            Personalized Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-blue-500" />
            Personalized Recommendations
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
            className="h-8 w-8 p-0"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {visibleRecommendations.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Target className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No recommendations available at the moment.</p>
            <p className="text-sm">Check back later for personalized insights!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {visibleRecommendations.map((recommendation) => (
              <div
                key={recommendation.id}
                className="border rounded-lg p-4 hover:shadow-sm transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="text-blue-500">
                      {getRecommendationIcon(recommendation.type)}
                    </div>
                    <h4 className="font-medium text-gray-900">{recommendation.title}</h4>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={getPriorityColor(recommendation.priority)}>
                      {recommendation.priority}
                    </Badge>
                    <div className="flex items-center gap-1 text-yellow-500">
                      <Star className="w-4 h-4 fill-current" />
                      <span className="text-sm font-medium">{recommendation.confidence}%</span>
                    </div>
                  </div>
                </div>
                
                <p className="text-gray-600 text-sm mb-3">{recommendation.description}</p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Clock className="w-3 h-3" />
                    <span>Expected impact: {recommendation.expectedImpact}</span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDismiss(recommendation)}
                      className="h-8 px-3 text-xs"
                    >
                      <X className="w-3 h-3 mr-1" />
                      Dismiss
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handleAccept(recommendation)}
                      className="h-8 px-3 text-xs bg-blue-500 hover:bg-blue-600"
                    >
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Try This
                    </Button>
                  </div>
                </div>
              </div>
            ))}
            
            {visibleRecommendations.length > 0 && (
              <div className="text-center pt-4 border-t">
                <p className="text-xs text-gray-500">
                  Recommendations are personalized based on your health data and patterns
                </p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}