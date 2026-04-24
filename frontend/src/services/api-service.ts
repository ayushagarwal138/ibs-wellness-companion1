'use client';

import { API_CONFIG } from '@/lib/config';

export interface ApiError extends Error {
  status?: number;
  code?: string;
}

export interface RetryOptions {
  maxRetries?: number;
  retryDelay?: number;
  retryOn?: number[];
}

class ApiService {
  private isRefreshing = false;
  private refreshPromise: Promise<string> | null = null;

  private getAuthHeaders(): HeadersInit {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  private async refreshToken(): Promise<string> {
    if (this.isRefreshing && this.refreshPromise) {
      return this.refreshPromise;
    }

    this.isRefreshing = true;
    this.refreshPromise = this.performTokenRefresh();

    try {
      const newToken = await this.refreshPromise;
      return newToken;
    } finally {
      this.isRefreshing = false;
      this.refreshPromise = null;
    }
  }

  private async performTokenRefresh(): Promise<string> {
    if (typeof window === 'undefined') {
      throw new Error('Cannot refresh token on server side');
    }

    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      // Clear invalid tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // Redirect to login
      window.location.href = '/login';
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    const newToken = data.access_token;
    
    localStorage.setItem('access_token', newToken);
    return newToken;
  }

  private async fetchWithAuth(
    url: string, 
    options: RequestInit = {},
    retryOptions: RetryOptions = {}
  ): Promise<Response> {
    const {
      maxRetries = 3,
      retryDelay = 1000,
      retryOn = [401, 403, 500, 502, 503, 504]
    } = retryOptions;

    let lastError: ApiError;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const headers = {
          ...this.getAuthHeaders(),
          ...options.headers,
        };

        const response = await fetch(url, {
          ...options,
          headers,
          credentials: 'include',
        });

        // Handle authentication errors
        if (response.status === 401) {
          if (attempt < maxRetries) {
            try {
              // Try to refresh token
              await this.refreshToken();
              // Retry with new token
              continue;
            } catch (refreshError) {
              // Refresh failed, clear tokens and redirect
              if (typeof window !== 'undefined') {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
              }
              throw new Error('Authentication required. Please log in again.');
            }
          }
        }

        // Handle other errors that should trigger retry
        if (!response.ok && retryOn.includes(response.status) && attempt < maxRetries) {
          await this.delay(retryDelay * Math.pow(2, attempt)); // Exponential backoff
          continue;
        }

        // Handle non-retryable errors
        if (!response.ok) {
          const error: ApiError = new Error(`API request failed: ${response.status} ${response.statusText}`);
          error.status = response.status;
          
          if (response.status === 403) {
            error.message = 'Access denied. Please check your permissions.';
          } else if (response.status >= 500) {
            error.message = 'Server error. Please try again later.';
          }
          
          throw error;
        }

        return response;
      } catch (error) {
        lastError = error as ApiError;
        
        // Don't retry on network errors for the last attempt
        if (attempt === maxRetries) {
          throw lastError;
        }
        
        // Wait before retrying
        await this.delay(retryDelay * Math.pow(2, attempt));
      }
    }

    throw lastError!;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Public API methods
  async get<T>(url: string, options: RequestInit = {}, retryOptions?: RetryOptions): Promise<T> {
    const response = await this.fetchWithAuth(url, { ...options, method: 'GET' }, retryOptions);
    return response.json();
  }

  async post<T>(url: string, data?: any, options: RequestInit = {}, retryOptions?: RetryOptions): Promise<T> {
    const response = await this.fetchWithAuth(url, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }, retryOptions);
    return response.json();
  }

  async put<T>(url: string, data?: any, options: RequestInit = {}, retryOptions?: RetryOptions): Promise<T> {
    const response = await this.fetchWithAuth(url, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }, retryOptions);
    return response.json();
  }

  async delete<T>(url: string, options: RequestInit = {}, retryOptions?: RetryOptions): Promise<T> {
    const response = await this.fetchWithAuth(url, { ...options, method: 'DELETE' }, retryOptions);
    return response.json();
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    if (typeof window === 'undefined') return false;
    return !!localStorage.getItem('access_token');
  }

  // Clear authentication
  clearAuth(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }
}

export const apiService = new ApiService();
export default apiService;