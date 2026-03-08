export const dynamic = 'force-dynamic'
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../../lib/auth';

interface DietaryPreferencesData {
  dietaryRestrictions: string[];
  foodAllergies: string[];
  preferredDiets: string[];
  mealsPerDay: number;
  waterIntake: number;
  alcoholConsumption: string;
  caffeineIntake: string;
  cookingFrequency: string;
  eatingOutFrequency: string;
  favoritefoods: string[];
  dislikedFoods: string[];
  supplementsUsed: string[];
  mealTiming: string;
  snackingHabits: string;
  foodBudget: string;
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

    // Parse the request body
    const data: DietaryPreferencesData = await request.json();

    // Validate required fields
    if (!data || typeof data !== 'object') {
      return NextResponse.json(
        { error: 'Invalid data format' },
        { status: 400 }
      );
    }

    // Validate arrays
    if (!Array.isArray(data.dietaryRestrictions) || !Array.isArray(data.foodAllergies)) {
      return NextResponse.json(
        { error: 'Dietary restrictions and food allergies must be arrays' },
        { status: 400 }
      );
    }

    try {
      // For now, we'll simulate saving to a backend API
      // In a real implementation, you would:
      // 1. Get the user's access token from the session
      // 2. Make a request to your backend API
      // 3. Handle the response appropriately

      console.log('Saving dietary preferences for user:', userEmail);
      console.log('Data:', JSON.stringify(data, null, 2));

      // Simulate successful save
      await new Promise(resolve => setTimeout(resolve, 500));

      return NextResponse.json(
        { 
          message: 'Dietary preferences saved successfully',
          data: data
        },
        { status: 200 }
      );

    } catch (backendError) {
      console.error('Backend API error:', backendError);
      return NextResponse.json(
        { error: 'Failed to save to backend' },
        { status: 500 }
      );
    }

  } catch (error) {
    console.error('API route error:', error);
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

    // For now, return default/mock data
    // In a real implementation, you would fetch from your backend
    const defaultData: DietaryPreferencesData = {
      dietaryRestrictions: [],
      foodAllergies: [],
      preferredDiets: [],
      mealsPerDay: 3,
      waterIntake: 8,
      alcoholConsumption: 'none',
      caffeineIntake: 'moderate',
      cookingFrequency: 'few_times_week',
      eatingOutFrequency: 'weekly',
      favoritefoods: [],
      dislikedFoods: [],
      supplementsUsed: [],
      mealTiming: 'regular',
      snackingHabits: 'occasional',
      foodBudget: 'moderate',
      specialNotes: ''
    };

    return NextResponse.json(defaultData, { status: 200 });

  } catch (error) {
    console.error('API route error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}