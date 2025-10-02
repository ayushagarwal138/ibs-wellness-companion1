import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../../lib/auth';

interface BasicInfoData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  gender: string;
  height_cm?: number;
  weight_kg?: number;
  emergencyContact: string;
  emergencyPhone: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
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
    const data: BasicInfoData = await request.json();

    // Validate required fields
    if (!data || typeof data !== 'object') {
      return NextResponse.json(
        { error: 'Invalid data format' },
        { status: 400 }
      );
    }

    // Validate required fields
    if (!data.firstName || !data.lastName || !data.email) {
      return NextResponse.json(
        { error: 'First name, last name, and email are required' },
        { status: 400 }
      );
    }

    try {
      // For now, we'll simulate saving to a backend API
      // In a real implementation, you would:
      // 1. Get the user's access token from the session
      // 2. Make a request to your backend API
      // 3. Handle the response appropriately

      console.log('Saving basic info for user:', userEmail);
      console.log('Data:', JSON.stringify(data, null, 2));

      // Simulate successful save
      await new Promise(resolve => setTimeout(resolve, 500));

      return NextResponse.json(
        { 
          message: 'Basic info saved successfully',
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
    const defaultData: BasicInfoData = {
      firstName: '',
      lastName: '',
      email: userEmail,
      phone: '',
      dateOfBirth: '',
      gender: '',
      height_cm: undefined,
      weight_kg: undefined,
      emergencyContact: '',
      emergencyPhone: '',
      address: '',
      city: '',
      state: '',
      zipCode: ''
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