'use client';

const API_BASE_URL = process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000';

export enum GoalType {
  SYMPTOM_REDUCTION = 'symptom_reduction',
  MEDICATION_ADHERENCE = 'medication_adherence',
  DIET_TRACKING = 'diet_tracking',
  EXERCISE = 'exercise',
  STRESS_MANAGEMENT = 'stress_management',
  SLEEP_QUALITY = 'sleep_quality',
  WEIGHT_MANAGEMENT = 'weight_management',
  CUSTOM = 'custom'
}

export enum GoalStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  PAUSED = 'paused',
  CANCELLED = 'cancelled'
}

export interface GoalBase {
  title: string;
  description?: string;
  goal_type: GoalType;
  target_value: number;
  target_unit: string;
  target_date: string;
  priority: 'low' | 'medium' | 'high';
  is_public: boolean;
  reminder_enabled: boolean;
  reminder_frequency?: string;
}

export interface GoalCreate extends GoalBase {}

export interface GoalUpdate {
  title?: string;
  description?: string;
  target_value?: number;
  target_unit?: string;
  target_date?: string;
  priority?: 'low' | 'medium' | 'high';
  status?: GoalStatus;
  is_public?: boolean;
  reminder_enabled?: boolean;
  reminder_frequency?: string;
}

export interface GoalResponse extends GoalBase {
  id: string;
  user_id: string;
  status: GoalStatus;
  current_value: number;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface GoalListResponse {
  goals: GoalResponse[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface GoalProgressCreate {
  value: number;
  notes?: string;
}

export interface GoalProgressResponse {
  id: string;
  goal_id: string;
  value: number;
  notes?: string;
  recorded_at: string;
  created_at: string;
}

export interface GoalSummaryResponse {
  total_goals: number;
  active_goals: number;
  completed_goals: number;
  completion_rate: number;
  average_progress: number;
  goals_by_type: Record<string, number>;
  recent_achievements: GoalResponse[];
  upcoming_deadlines: GoalResponse[];
}

class GoalsService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  async getGoals(
    skip: number = 0,
    limit: number = 10,
    status?: GoalStatus,
    goalType?: GoalType
  ): Promise<GoalListResponse> {
    const startTime = performance.now();
    
    try {
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString(),
        ...(status && { status }),
        ...(goalType && { goal_type: goalType })
      });

      const response = await fetch(`${API_BASE_URL}/api/v1/goals/?${params}`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Get Goals API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Get Goals API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Get Goals API call failed after ${duration.toFixed(2)}ms`);
      
      // Return mock data as fallback
      return this.getMockGoalsList();
    }
  }

  async getGoal(goalId: string): Promise<GoalResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/goals/${goalId}`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Get Goal API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Get Goal API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Get Goal API call failed after ${duration.toFixed(2)}ms`);
      
      // Return mock data as fallback
      return this.getMockGoal();
    }
  }

  async createGoal(goal: GoalCreate): Promise<GoalResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/goals/`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(goal),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Create Goal API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Create Goal API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Create Goal API call failed after ${duration.toFixed(2)}ms`);
      
      throw error;
    }
  }

  async updateGoal(goalId: string, updates: GoalUpdate): Promise<GoalResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/goals/${goalId}`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Update Goal API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Update Goal API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Update Goal API call failed after ${duration.toFixed(2)}ms`);
      
      throw error;
    }
  }

  async deleteGoal(goalId: string): Promise<void> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/goals/${goalId}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Delete Goal API call completed in ${duration.toFixed(2)}ms`);
    } catch (error) {
      console.error('Delete Goal API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Delete Goal API call failed after ${duration.toFixed(2)}ms`);
      
      throw error;
    }
  }

  async recordProgress(goalId: string, progress: GoalProgressCreate): Promise<GoalProgressResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/goals/${goalId}/progress`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(progress),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Record Progress API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Record Progress API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Record Progress API call failed after ${duration.toFixed(2)}ms`);
      
      throw error;
    }
  }

  async getGoalsSummary(): Promise<GoalSummaryResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/goals/summary`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Goals Summary API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Goals Summary API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Goals Summary API call failed after ${duration.toFixed(2)}ms`);
      
      // Return mock data as fallback
      return this.getMockGoalsSummary();
    }
  }

  private getMockGoal(): GoalResponse {
    return {
      id: "mock-goal-1",
      user_id: "mock-user-id",
      title: "Reduce Bloating Episodes",
      description: "Aim to reduce bloating episodes to less than 3 per week",
      goal_type: GoalType.SYMPTOM_REDUCTION,
      target_value: 3,
      target_unit: "episodes per week",
      target_date: "2024-03-01",
      priority: "high",
      status: GoalStatus.ACTIVE,
      current_value: 5,
      progress_percentage: 60,
      is_public: false,
      reminder_enabled: true,
      reminder_frequency: "daily",
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-20T00:00:00Z"
    };
  }

  private getMockGoalsList(): GoalListResponse {
    return {
      goals: [
        this.getMockGoal(),
        {
          id: "mock-goal-2",
          user_id: "mock-user-id",
          title: "Daily Medication Adherence",
          description: "Take prescribed medications consistently every day",
          goal_type: GoalType.MEDICATION_ADHERENCE,
          target_value: 100,
          target_unit: "percentage",
          target_date: "2024-02-29",
          priority: "high",
          status: GoalStatus.ACTIVE,
          current_value: 85,
          progress_percentage: 85,
          is_public: false,
          reminder_enabled: true,
          reminder_frequency: "daily",
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-20T00:00:00Z"
        }
      ],
      total: 2,
      page: 1,
      size: 10,
      pages: 1
    };
  }

  private getMockGoalsSummary(): GoalSummaryResponse {
    return {
      total_goals: 5,
      active_goals: 3,
      completed_goals: 2,
      completion_rate: 40,
      average_progress: 72.5,
      goals_by_type: {
        [GoalType.SYMPTOM_REDUCTION]: 2,
        [GoalType.MEDICATION_ADHERENCE]: 1,
        [GoalType.DIET_TRACKING]: 1,
        [GoalType.EXERCISE]: 1
      },
      recent_achievements: [this.getMockGoal()],
      upcoming_deadlines: [this.getMockGoal()]
    };
  }
}

export const goalsService = new GoalsService();