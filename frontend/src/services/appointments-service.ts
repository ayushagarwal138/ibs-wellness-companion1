'use client';

import { API_CONFIG } from '@/lib/config';

export enum AppointmentType {
  CONSULTATION = 'consultation',
  FOLLOW_UP = 'follow_up',
  EMERGENCY = 'emergency',
  ROUTINE_CHECKUP = 'routine_checkup',
  SPECIALIST = 'specialist',
  THERAPY = 'therapy',
  DIAGNOSTIC = 'diagnostic'
}

export enum AppointmentStatus {
  SCHEDULED = 'scheduled',
  CONFIRMED = 'confirmed',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  NO_SHOW = 'no_show',
  RESCHEDULED = 'rescheduled'
}

export enum ReminderType {
  EMAIL = 'email',
  SMS = 'sms',
  PUSH = 'push',
  CALL = 'call'
}

export interface AppointmentBase {
  title: string;
  description?: string;
  appointment_type: AppointmentType;
  appointment_date: string; // ISO date string
  appointment_time: string; // HH:MM format
  duration_minutes: number;
  provider_name?: string;
  provider_specialty?: string;
  location?: string;
  is_virtual: boolean;
  virtual_link?: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  notes?: string;
  preparation_instructions?: string;
}

export interface AppointmentCreate extends AppointmentBase {}

export interface AppointmentUpdate {
  title?: string;
  description?: string;
  appointment_type?: AppointmentType;
  appointment_date?: string;
  appointment_time?: string;
  duration_minutes?: number;
  provider_name?: string;
  provider_specialty?: string;
  location?: string;
  is_virtual?: boolean;
  virtual_link?: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  notes?: string;
  preparation_instructions?: string;
  status?: AppointmentStatus;
}

export interface AppointmentResponse extends AppointmentBase {
  id: string;
  user_id: string;
  status: AppointmentStatus;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  cancelled_at?: string;
  cancellation_reason?: string;
}

export interface AppointmentListResponse {
  appointments: AppointmentResponse[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface AppointmentSummaryResponse {
  total_appointments: number;
  upcoming_appointments: number;
  completed_appointments: number;
  cancelled_appointments: number;
  appointments_this_month: number;
  next_appointment?: AppointmentResponse;
  recent_appointments: AppointmentResponse[];
  appointments_by_type: Record<string, number>;
  average_cost: number;
  total_cost: number;
}

export interface AppointmentReminderResponse {
  id: string;
  appointment_id: string;
  reminder_type: ReminderType;
  reminder_time: string;
  message: string;
  sent: boolean;
  sent_at?: string;
  created_at: string;
}

export interface AppointmentResultCreate {
  diagnosis?: string;
  treatment_plan?: string;
  medications_prescribed?: string[];
  follow_up_required: boolean;
  follow_up_date?: string;
  notes?: string;
  satisfaction_rating?: number;
  cost_actual?: number;
}

export interface AppointmentResultResponse extends AppointmentResultCreate {
  id: string;
  appointment_id: string;
  created_at: string;
  updated_at: string;
}

export interface AppointmentStatsResponse {
  total_appointments: number;
  completion_rate: number;
  average_satisfaction: number;
  most_common_type: string;
  average_cost: number;
  provider_ratings: Record<string, number>;
  monthly_trends: Array<{
    month: string;
    count: number;
    cost: number;
  }>;
}

class AppointmentsService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  async getAppointments(
    skip: number = 0,
    limit: number = 10,
    status?: AppointmentStatus,
    appointmentType?: AppointmentType,
    upcoming?: boolean
  ): Promise<AppointmentListResponse> {
    const startTime = performance.now();
    
    try {
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString(),
        ...(status && { status }),
        ...(appointmentType && { appointment_type: appointmentType }),
        ...(upcoming !== undefined && { upcoming: upcoming.toString() })
      });

      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/appointments/?${params}`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Get Appointments API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Get Appointments API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Get Appointments API call failed after ${duration.toFixed(2)}ms`);
      
      // Return mock data as fallback
      return this.getMockAppointmentsList();
    }
  }

  async getAppointment(appointmentId: string): Promise<AppointmentResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/appointments/${appointmentId}`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Get Appointment API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Get Appointment API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Get Appointment API call failed after ${duration.toFixed(2)}ms`);
      
      // Return mock data as fallback
      return this.getMockAppointment();
    }
  }

  async createAppointment(appointment: AppointmentCreate): Promise<AppointmentResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/appointments/`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(appointment),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Create Appointment API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Create Appointment API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Create Appointment API call failed after ${duration.toFixed(2)}ms`);
      
      throw error;
    }
  }

  async updateAppointment(appointmentId: string, updates: AppointmentUpdate): Promise<AppointmentResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/appointments/${appointmentId}`, {
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
      console.log(`Update Appointment API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Update Appointment API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Update Appointment API call failed after ${duration.toFixed(2)}ms`);
      
      throw error;
    }
  }

  async deleteAppointment(appointmentId: string): Promise<void> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/appointments/${appointmentId}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Delete Appointment API call completed in ${duration.toFixed(2)}ms`);
    } catch (error) {
      console.error('Delete Appointment API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Delete Appointment API call failed after ${duration.toFixed(2)}ms`);
      
      throw error;
    }
  }

  async getAppointmentsSummary(): Promise<AppointmentSummaryResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/appointments/summary`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Appointments Summary API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Appointments Summary API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Appointments Summary API call failed after ${duration.toFixed(2)}ms`);
      
      // Return mock data as fallback
      return this.getMockAppointmentsSummary();
    }
  }

  async addAppointmentResult(appointmentId: string, result: AppointmentResultCreate): Promise<AppointmentResultResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/appointments/${appointmentId}/result`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(result),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Add Appointment Result API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Add Appointment Result API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Add Appointment Result API call failed after ${duration.toFixed(2)}ms`);
      
      throw error;
    }
  }

  async getAppointmentStats(): Promise<AppointmentStatsResponse> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/appointments/stats`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Log performance
      const duration = performance.now() - startTime;
      console.log(`Appointment Stats API call completed in ${duration.toFixed(2)}ms`);
      
      return data;
    } catch (error) {
      console.error('Appointment Stats API error:', error);
      const duration = performance.now() - startTime;
      console.log(`Appointment Stats API call failed after ${duration.toFixed(2)}ms`);
      
      // Return mock data as fallback
      return this.getMockAppointmentStats();
    }
  }

  private getMockAppointment(): AppointmentResponse {
    return {
      id: "mock-appointment-1",
      user_id: "mock-user-id",
      title: "Gastroenterologist Consultation",
      description: "Follow-up consultation for IBS management",
      appointment_type: AppointmentType.FOLLOW_UP,
      appointment_date: "2024-02-15",
      appointment_time: "14:00",
      duration_minutes: 30,
      provider_name: "Dr. Sarah Johnson",
      provider_specialty: "Gastroenterology",
      location: "Downtown Medical Center",
      is_virtual: false,
      priority: "medium",
      notes: "Follow-up for IBS management",
      preparation_instructions: "Bring recent symptom diary and medication list",
      status: AppointmentStatus.SCHEDULED,
      created_at: "2024-01-20T00:00:00Z",
      updated_at: "2024-01-20T00:00:00Z"
    };
  }

  private getMockAppointmentsList(): AppointmentListResponse {
    return {
      appointments: [
        this.getMockAppointment(),
        {
          id: "mock-appointment-2",
          user_id: "mock-user-id",
          title: "Nutritionist Consultation",
          description: "Dietary planning session",
          appointment_type: AppointmentType.CONSULTATION,
          appointment_date: "2024-02-20",
          appointment_time: "10:00",
          duration_minutes: 45,
          provider_name: "Lisa Chen, RD",
          provider_specialty: "Nutrition",
          location: "Virtual",
          is_virtual: true,
          virtual_link: "https://zoom.us/j/123456789",
          priority: "medium",
          notes: "Dietary planning session",
          preparation_instructions: "Complete food diary for past week",
          status: AppointmentStatus.CONFIRMED,
          created_at: "2024-01-18T00:00:00Z",
          updated_at: "2024-01-19T00:00:00Z"
        }
      ],
      total: 2,
      page: 1,
      size: 10,
      pages: 1
    };
  }

  private getMockAppointmentsSummary(): AppointmentSummaryResponse {
    return {
      total_appointments: 8,
      upcoming_appointments: 2,
      completed_appointments: 5,
      cancelled_appointments: 1,
      appointments_this_month: 3,
      next_appointment: this.getMockAppointment(),
      recent_appointments: [this.getMockAppointment()],
      appointments_by_type: {
        [AppointmentType.CONSULTATION]: 3,
        [AppointmentType.FOLLOW_UP]: 2,
        [AppointmentType.ROUTINE_CHECKUP]: 2,
        [AppointmentType.SPECIALIST]: 1
      },
      average_cost: 125,
      total_cost: 1000
    };
  }

  private getMockAppointmentStats(): AppointmentStatsResponse {
    return {
      total_appointments: 8,
      completion_rate: 87.5,
      average_satisfaction: 4.2,
      most_common_type: AppointmentType.CONSULTATION,
      average_cost: 125,
      provider_ratings: {
        "Dr. Sarah Johnson": 4.5,
        "Lisa Chen, RD": 4.8,
        "Dr. Michael Brown": 4.0
      },
      monthly_trends: [
        { month: "2024-01", count: 3, cost: 375 },
        { month: "2024-02", count: 2, cost: 250 },
        { month: "2024-03", count: 3, cost: 375 }
      ]
    };
  }
}

export const appointmentsService = new AppointmentsService();