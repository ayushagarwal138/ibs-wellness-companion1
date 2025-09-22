import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../auth/[...nextauth]/route';

interface LifestyleFactorsData {
  exerciseFrequency: string;
  exerciseTypes: string[];
  exerciseDuration: number;
  exerciseIntensity: string;
  sleepHours: number;
  sleepQuality: string;
  bedtime: string;
  wakeupTime: string;
  stressLevel: number;
  stressManagement: string[];
  workSchedule: string;
  workStressLevel: number;
  smokingStatus: string;
  smokingFrequency: string;
  socialSupport: string;
  hobbies: string[];
  screenTime: number;
  outdoorTime: number;
  travelFrequency: string;
  livingEnvironment: string;
  petOwnership: string;
  relaxationActivities: string[];
  mentalHealthSupport: string;
  specialNotes: string;
}

export async function PUT(request: NextRequest) {
  try {
    // Check for NextAuth session first
    const session = await getServerSession(authOptions);
    
    // If no NextAuth session, check for Bearer token
    let userEmail: string | null = null;
    
    if (session?.user?.email) {
      userEmail = session.user.email;
    } else {
      // Check for Authorization header with Bearer token
      const authHeader = request.headers.get('authorization');
      if (authHeader?.startsWith('Bearer ')) {
        const token = authHeader.substring(7);
        
        // Verify the token with your backend API
        try {
          const API_BASE_URL = process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000';
          const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          
          if (response.ok) {
            const userData = await response.json();
            userEmail = userData.email;
          }
        } catch (error) {
          console.error('Token verification failed:', error);
        }
      }
    }
    
    if (!userEmail) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const data: LifestyleFactorsData = await request.json();

    // Validate required fields
    if (!data.exerciseFrequency || !data.sleepQuality || !data.workSchedule || !data.smokingStatus || !data.socialSupport || !data.travelFrequency || !data.livingEnvironment || !data.petOwnership || !data.mentalHealthSupport) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Validate array fields
    if (!Array.isArray(data.exerciseTypes) || !Array.isArray(data.stressManagement) || !Array.isArray(data.hobbies) || !Array.isArray(data.relaxationActivities)) {
      return NextResponse.json(
        { error: 'Invalid array fields' },
        { status: 400 }
      );
    }

    // Validate numeric fields
    if (typeof data.exerciseDuration !== 'number' || typeof data.sleepHours !== 'number' || typeof data.stressLevel !== 'number' || typeof data.workStressLevel !== 'number' || typeof data.screenTime !== 'number' || typeof data.outdoorTime !== 'number') {
      return NextResponse.json(
        { error: 'Invalid numeric fields' },
        { status: 400 }
      );
    }

    // Here you would typically save to your database
    // For now, we'll simulate a successful save
    console.log('Saving lifestyle factors data for user:', userEmail, data);

    return NextResponse.json(
      { 
        message: 'Lifestyle factors saved successfully',
        data: data
      },
      { status: 200 }
    );

  } catch (error) {
    console.error('Error saving lifestyle factors:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    // Check for NextAuth session first
    const session = await getServerSession(authOptions);
    
    // If no NextAuth session, check for Bearer token
    let userEmail: string | null = null;
    
    if (session?.user?.email) {
      userEmail = session.user.email;
    } else {
      // Check for Authorization header with Bearer token
      const authHeader = request.headers.get('authorization');
      if (authHeader?.startsWith('Bearer ')) {
        const token = authHeader.substring(7);
        
        // Verify the token with your backend API
        try {
          const API_BASE_URL = process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000';
          const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          
          if (response.ok) {
            const userData = await response.json();
            userEmail = userData.email;
          }
        } catch (error) {
          console.error('Token verification failed:', error);
        }
      }
    }
    
    if (!userEmail) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Here you would typically fetch from your database
    // For now, we'll return mock data
    const mockData: LifestyleFactorsData = {
      exerciseFrequency: '3-4_week',
      exerciseTypes: ['Walking', 'Yoga'],
      exerciseDuration: 45,
      exerciseIntensity: 'moderate',
      sleepHours: 7,
      sleepQuality: 'good',
      bedtime: '22:30',
      wakeupTime: '06:30',
      stressLevel: 5,
      stressManagement: ['Meditation', 'Exercise'],
      workSchedule: 'regular_day',
      workStressLevel: 6,
      smokingStatus: 'never',
      smokingFrequency: '',
      socialSupport: 'good',
      hobbies: ['Reading', 'Gardening'],
      screenTime: 4,
      outdoorTime: 2,
      travelFrequency: 'occasionally',
      livingEnvironment: 'suburban',
      petOwnership: 'dog',
      relaxationActivities: ['Reading', 'Meditation'],
      mentalHealthSupport: 'informal',
      specialNotes: ''
    };

    return NextResponse.json(mockData, { status: 200 });

  } catch (error) {
    console.error('Error fetching lifestyle factors:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}