import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { toast } from 'react-hot-toast';
import { API_CONFIG } from './config';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: `${API_CONFIG.BASE_URL}/api/v1`,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Enhanced error types for better error handling
export interface ApiError extends Error {
  type: 'network' | 'auth' | 'server' | 'validation' | 'timeout' | 'unknown';
  status?: number;
  originalError?: AxiosError;
  retryable: boolean;
}

// Retry configuration
const RETRY_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000, // Base delay in ms
  retryableStatuses: [408, 429, 500, 502, 503, 504],
  retryableNetworkErrors: ['ECONNRESET', 'ENOTFOUND', 'ECONNABORTED', 'ETIMEDOUT']
};

// Helper function to determine if error is retryable
const isRetryableError = (error: AxiosError): boolean => {
  // Network errors
  if (!error.response && error.code) {
    return RETRY_CONFIG.retryableNetworkErrors.includes(error.code);
  }
  
  // HTTP status codes
  if (error.response?.status) {
    return RETRY_CONFIG.retryableStatuses.includes(error.response.status);
  }
  
  return false;
};

// Helper function to create ApiError
const createApiError = (error: AxiosError): ApiError => {
  let type: ApiError['type'] = 'unknown';
  let retryable = false;
  
  if (!error.response) {
    // Network error
    type = 'network';
    retryable = isRetryableError(error);
  } else {
    const status = error.response.status;
    
    if (status === 401 || status === 403) {
      type = 'auth';
      retryable = status === 401; // 401 can be retried with refresh, 403 cannot
    } else if (status === 422) {
      type = 'validation';
      retryable = false;
    } else if (status >= 500) {
      type = 'server';
      retryable = true;
    } else if (status === 408 || status === 429) {
      type = status === 408 ? 'timeout' : 'server';
      retryable = true;
    }
  }
  
  const apiError = new Error(error.message) as ApiError;
  apiError.type = type;
  apiError.status = error.response?.status;
  apiError.originalError = error;
  apiError.retryable = retryable;
  
  return apiError;
};

// Helper function to determine error category for contextual messages
const getErrorCategory = (error: AxiosError): string => {
  if (!error.response) {
    return 'network';
  }
  
  const status = error.response.status;
  if (status === 401 || status === 403) {
    return 'auth';
  } else if (status >= 500) {
    return 'server';
  } else if (status === 408 || status === 429) {
    return 'timeout';
  }
  
  return 'server';
};

// Enhanced error message generation with context-aware messages
const getErrorMessage = (error: AxiosError, context?: string): string => {
  const data = error.response?.data as any;
  const status = error.response?.status;
  
  // Context-specific error messages for dashboard components
  const getContextualMessage = (baseMessage: string): string => {
    if (!context) return baseMessage;
    
    const contextMessages: Record<string, Record<string, string>> = {
      'dashboard': {
        'network': 'Unable to load dashboard data. Please check your internet connection.',
        'auth': 'Your session has expired. Please log in again to view your dashboard.',
        'server': 'Dashboard service is temporarily unavailable. Please try again in a few moments.',
        'timeout': 'Dashboard is taking longer than usual to load. Please try again.',
      },
      'predictions': {
        'network': 'Unable to load AI predictions. Please check your connection.',
        'auth': 'Authentication required to access AI predictions.',
        'server': 'AI prediction service is temporarily unavailable.',
        'timeout': 'AI predictions are taking longer than usual to generate.',
      },
      'symptoms': {
        'network': 'Unable to load recent symptoms. Please check your connection.',
        'auth': 'Please log in to view your symptom history.',
        'server': 'Symptom tracking service is temporarily unavailable.',
        'timeout': 'Symptom data is taking longer than usual to load.',
      },
      'stats': {
        'network': 'Unable to load weekly statistics. Please check your connection.',
        'auth': 'Please log in to view your health statistics.',
        'server': 'Statistics service is temporarily unavailable.',
        'timeout': 'Statistics are taking longer than usual to calculate.',
      },
      'insights': {
        'network': 'Unable to load personalized insights. Please check your connection.',
        'auth': 'Please log in to view your health insights.',
        'server': 'Insights service is temporarily unavailable.',
        'timeout': 'Insights are taking longer than usual to generate.',
      },
      'reminders': {
        'network': 'Unable to load upcoming reminders. Please check your connection.',
        'auth': 'Please log in to view your reminders.',
        'server': 'Reminder service is temporarily unavailable.',
        'timeout': 'Reminders are taking longer than usual to load.',
      },
      'recommendations': {
        'network': 'Unable to load personalized recommendations. Please check your connection.',
        'auth': 'Please log in to view your recommendations.',
        'server': 'Recommendation service is temporarily unavailable.',
        'timeout': 'Recommendations are taking longer than usual to generate.',
      },
    };
    
    return contextMessages[context]?.[getErrorCategory(error)] || baseMessage;
  };
  
  // Handle specific HTTP status codes with enhanced messages
  if (status) {
    switch (status) {
      case 400:
        return getContextualMessage('Invalid request. Please check your input and try again.');
      case 401:
        return getContextualMessage('Your session has expired. Please log in again.');
      case 403:
        return getContextualMessage('Access denied. You don\'t have permission to access this data.');
      case 404:
        return getContextualMessage('The requested data was not found. It may have been moved or deleted.');
      case 409:
        return getContextualMessage('Data conflict detected. Please refresh and try again.');
      case 422:
        // Handle validation errors with more detail
        if (Array.isArray(data?.detail)) {
          const validationErrors = data.detail.map((err: any) => {
            if (err.loc && err.msg) {
              const field = err.loc[err.loc.length - 1];
              return `${field}: ${err.msg}`;
            }
            return err.msg || 'Validation error';
          }).join('; ');
          return `Validation failed: ${validationErrors}`;
        }
        return getContextualMessage('Invalid data format. Please check your input.');
      case 429:
        return getContextualMessage('Too many requests. Please wait a moment before trying again.');
      case 500:
        return getContextualMessage('Internal server error. Our team has been notified.');
      case 502:
        return getContextualMessage('Service gateway error. Please try again in a few moments.');
      case 503:
        return getContextualMessage('Service temporarily unavailable due to maintenance.');
      case 504:
        return getContextualMessage('Request timeout. The server took too long to respond.');
      default:
        break;
    }
  }
  
  // Handle API error responses with more detail
  if (data) {
    if (typeof data.detail === 'string') {
      return getContextualMessage(data.detail);
    } else if (data.message) {
      return getContextualMessage(data.message);
    } else if (data.error) {
      return getContextualMessage(data.error);
    }
  }
  
  // Enhanced network error messages
  if (!error.response) {
    if (error.code === 'ECONNABORTED') {
      return getContextualMessage('Request timeout. The server is taking too long to respond.');
    } else if (error.code === 'ENOTFOUND') {
      return getContextualMessage('Unable to connect to server. Please check your internet connection.');
    } else if (error.code === 'ECONNRESET') {
      return getContextualMessage('Connection was interrupted. Please try again.');
    } else if (error.code === 'ECONNREFUSED') {
      return getContextualMessage('Connection refused. The server may be down for maintenance.');
    } else if (error.code === 'ENETUNREACH') {
      return getContextualMessage('Network unreachable. Please check your internet connection.');
    } else if (error.message?.includes('Network Error')) {
      return getContextualMessage('Network error. Please check your internet connection and try again.');
    }
  }
  
  // Fallback message with context
  const fallbackMessage = error.message || 'An unexpected error occurred';
  return getContextualMessage(fallbackMessage);
};

// Enhanced authentication failure handler with edge case management
const handleAuthenticationFailure = (refreshError: any): Promise<never> => {
  // Clear all authentication data
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  
  // Clear any cached user data
  if (typeof window !== 'undefined') {
    // Clear session storage as well
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('auth_state');
    
    // Enhanced redirect logic with edge case handling
    const currentPath = window.location.pathname;
    const isOnLoginPage = currentPath.includes('/login');
    const isOnRegisterPage = currentPath.includes('/register');
    const isOnPublicPage = ['/'].includes(currentPath);
    
    // Only redirect if not already on auth pages or public pages
    if (!isOnLoginPage && !isOnRegisterPage && !isOnPublicPage) {
      // Store the current path for redirect after login (excluding sensitive pages)
      const sensitivePages = ['/profile', '/settings', '/admin'];
      const isSensitivePage = sensitivePages.some(page => currentPath.startsWith(page));
      
      if (!isSensitivePage) {
        sessionStorage.setItem('redirect_after_login', currentPath + window.location.search);
      }
      
      // Use setTimeout to avoid blocking the current execution
      setTimeout(() => {
        window.location.href = '/login';
      }, 100);
    }
  }
  
  const authError = new Error('Authentication failed. Please log in again.') as ApiError;
  authError.type = 'auth';
  authError.retryable = false;
  return Promise.reject(authError);
};

// Response interceptor for error handling with retry logic
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    const apiError = createApiError(error);

    // Handle 401 errors (unauthorized) with token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_CONFIG.BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, handle logout and redirect
        return handleAuthenticationFailure(refreshError);
      }
    }

    // Handle retryable errors (network issues, server errors, timeouts)
    if (apiError.retryable && !originalRequest._retryCount) {
      originalRequest._retryCount = 0;
    }

    if (apiError.retryable && originalRequest._retryCount < RETRY_CONFIG.maxRetries) {
      originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;
      
      // Exponential backoff with jitter
      const delay = RETRY_CONFIG.retryDelay * Math.pow(2, originalRequest._retryCount - 1);
      const jitter = Math.random() * 0.1 * delay;
      
      await new Promise(resolve => setTimeout(resolve, delay + jitter));
      
      return api(originalRequest);
    }

    // Show appropriate error message with context if available
    const context = originalRequest.url?.includes('/dashboard') ? 'dashboard' :
                   originalRequest.url?.includes('/predictions') ? 'predictions' :
                   originalRequest.url?.includes('/symptoms') ? 'symptoms' :
                   originalRequest.url?.includes('/stats') ? 'stats' :
                   originalRequest.url?.includes('/insights') ? 'insights' :
                   originalRequest.url?.includes('/reminders') ? 'reminders' :
                   originalRequest.url?.includes('/recommendations') ? 'recommendations' :
                   undefined;
    
    const errorMessage = getErrorMessage(error, context);
    
    // Only show toast for non-auth errors or if we're not redirecting
    if (apiError.type !== 'auth' || typeof window === 'undefined' || window.location.pathname.includes('/login')) {
      toast.error(errorMessage);
    }
    
    return Promise.reject(apiError);
  }
);

// Import shared types
import {
  ApiResponse,
  PaginatedResponse,
  SymptomLog,
  SymptomLogBase,
  SymptomStats,
  DietLog,
  DietLogBase,
  FoodReaction,
  FoodReactionBase,
  DietStats,
  CreateRequest
} from '@ibs-wellness/shared-types';

// Re-export for backward compatibility
export type {
  ApiResponse,
  PaginatedResponse,
  SymptomLog,
  SymptomStats,
  DietLog,
  FoodReaction,
  DietStats
};

// Create types for API requests
export type SymptomLogCreate = CreateRequest<SymptomLogBase>;
export type DietLogCreate = CreateRequest<DietLogBase>;
export type FoodReactionCreate = CreateRequest<FoodReactionBase>;

// API Service Class
class ApiService {
  // Symptom endpoints
  async createSymptomLog(data: SymptomLogCreate): Promise<SymptomLog> {
    const response = await api.post<SymptomLog>('/symptom-logs', data);
    return response.data;
  }

  async getSymptomLogs(params?: {
    skip?: number;
    limit?: number;
    severity?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<PaginatedResponse<SymptomLog>> {
    const response = await api.get<PaginatedResponse<SymptomLog>>('/symptom-logs', { params });
    return response.data;
  }

  async getSymptomLog(id: number): Promise<SymptomLog> {
    const response = await api.get<SymptomLog>(`/symptom-logs/${id}`);
    return response.data;
  }

  async updateSymptomLog(id: number, data: Partial<SymptomLogCreate>): Promise<SymptomLog> {
    const response = await api.put<SymptomLog>(`/symptom-logs/${id}`, data);
    return response.data;
  }

  async deleteSymptomLog(id: number): Promise<void> {
    await api.delete(`/symptom-logs/${id}`);
  }

  async getSymptomStats(days: number = 30): Promise<SymptomStats | null> {
    try {
      // Backend returns StandardResponse<SymptomStats>, so we need to extract the data property
      const response = await api.get<ApiResponse<SymptomStats>>(`/symptom-logs/stats/summary?days=${days}`);
      return response.data.data || null;
    } catch (error: any) {
      if (error.response?.status === 403) {
        console.warn('Authentication required for symptom stats (403). User may not be logged in.');
        // Don't show toast here - let the component handle it
        throw new Error('403: Authentication required');
      } else if (error.response?.status === 404) {
        console.warn('Symptom stats endpoint not found (404). This may be expected if the endpoint is not yet implemented.');
        toast.error('Symptom statistics feature is currently unavailable');
        return null;
      } else if (error.response?.status === 500) {
        console.error('Server error when fetching symptom stats:', error);
        toast.error('Unable to load symptom statistics due to a server error');
        return null;
      }
      // Re-throw other errors to be handled by the global interceptor
      throw error;
    }
  }

  async getInitialSymptomLogs(): Promise<Array<{
    id: number;
    symptom_id: number;
    symptom_name: string;
    severity: string;
    logged_at: string;
    duration_minutes?: number;
    notes?: string;
    bristol_stool_type?: string;
    bowel_movement_frequency?: number;
    pain_location?: string;
    pain_type?: string;
    stress_level?: number;
    sleep_quality?: number;
    exercise_minutes?: number;
    potential_triggers?: string;
    created_at: string;
  }> | null> {
    try {
      const response = await api.get<{ data: Array<{
        id: number;
        symptom_id: number;
        symptom_name: string;
        severity: string;
        logged_at: string;
        duration_minutes?: number;
        notes?: string;
        bristol_stool_type?: string;
        bowel_movement_frequency?: number;
        pain_location?: string;
        pain_type?: string;
        stress_level?: number;
        sleep_quality?: number;
        exercise_minutes?: number;
        potential_triggers?: string;
        created_at: string;
      }> }>('/symptom-logs/initial');
      return response.data.data || [];
    } catch (error: any) {
      if (error.response?.status === 404) {
        console.warn('Initial symptom logs endpoint not found (404). This may be expected if the endpoint is not yet implemented.');
        toast.error('Unable to load recent symptom logs - feature unavailable');
        return null;
      } else if (error.response?.status === 500) {
        console.error('Server error when fetching initial symptom logs:', error);
        toast.error('Unable to load recent symptom logs due to a server error');
        return null;
      }
      // Re-throw other errors to be handled by the global interceptor
      throw error;
    }
  }

  async getAvailableSymptoms(): Promise<Array<{ id: number; name: string; description: string | null; category: string }>> {
    const response = await api.get('/symptom-logs/symptoms');
    return response.data.data || response.data;
  }

  // Diet endpoints
  async createDietLog(data: DietLogCreate): Promise<DietLog> {
    const response = await api.post<DietLog>('/diet/logs', data);
    return response.data;
  }

  async getDietLogs(params?: {
    skip?: number;
    limit?: number;
    meal_type?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<PaginatedResponse<DietLog>> {
    // Add authentication headers
    const token = localStorage.getItem('access_token');
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000'}/api/v1/diet/logs`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  async getDietLog(id: number): Promise<DietLog> {
    const response = await api.get<DietLog>(`/diet/logs/${id}`);
    return response.data;
  }

  async updateDietLog(id: number, data: Partial<DietLogCreate>): Promise<DietLog> {
    const response = await api.put<DietLog>(`/diet/logs/${id}`, data);
    return response.data;
  }

  async deleteDietLog(id: number): Promise<void> {
    await api.delete(`/diet/logs/${id}`);
  }

  async getDietStats(days: number = 30): Promise<DietStats> {
    const response = await api.get<DietStats>(`/diet/stats/diet?days=${days}`);
    return response.data;
  }

  // Food reaction endpoints
  async createFoodReaction(data: FoodReactionCreate): Promise<FoodReaction> {
    const response = await api.post<FoodReaction>('/diet/reactions', data);
    return response.data;
  }

  async getFoodReactions(params?: {
    skip?: number;
    limit?: number;
    severity?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<PaginatedResponse<FoodReaction>> {
    const response = await api.get<PaginatedResponse<FoodReaction>>('/diet/reactions', { params });
    return response.data;
  }

  async getFoodReaction(id: number): Promise<FoodReaction> {
    const response = await api.get<FoodReaction>(`/diet/reactions/${id}`);
    return response.data;
  }

  async updateFoodReaction(id: number, data: Partial<FoodReactionCreate>): Promise<FoodReaction> {
    const response = await api.put<FoodReaction>(`/diet/reactions/${id}`, data);
    return response.data;
  }

  async deleteFoodReaction(id: number): Promise<void> {
    await api.delete(`/diet/reactions/${id}`);
  }

  // Food suggestions endpoint
  async getFoodSuggestions(query: string): Promise<{ suggestions: Array<{ name: string; category: string; fodmap_level: string; is_common_trigger: boolean }> }> {
    const response = await api.get(`/diet/food-suggestions?query=${encodeURIComponent(query)}`);
    return response.data;
  }

  // Profile endpoints
  async getLifestyleFactors(): Promise<{
    exerciseFrequency: string;
    exerciseTypes: string[];
    sleepHours: number;
    sleepQuality: string;
    stressLevel: number;
    stressManagement: string[];
    smokingStatus: string;
    workSchedule: string;
    workStressLevel: number;
    socialSupport: string;
    hobbies: string[];
    travelFrequency: string;
    environmentalFactors: string[];
    dailyRoutine: string;
    specialNotes: string;
  }> {
    const response = await api.get('/profile/lifestyle-factors');
    return response.data;
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default api;