# Manual Frontend Authentication Testing Guide

## Test Registration Flow

1. **Open Browser**: Navigate to http://localhost:3000/register

2. **Fill Registration Form**:
   - Full Name: Test User
   - Email: testuser@example.com
   - Password: TestPass123!
   - Confirm Password: TestPass123!

3. **Submit Form**: Click "Create Account" button

4. **Expected Behavior**:
   - Should redirect to /onboarding page
   - Should show success toast notification
   - User should be created in PostgreSQL database

5. **Verify Database**:
   ```sql
   SELECT id, email, first_name, last_name, created_at FROM users WHERE email = 'testuser@example.com';
   ```

## Test Login Flow

1. **Navigate to Login**: Go to http://localhost:3000/login

2. **Fill Login Form**:
   - Email: testuser@example.com
   - Password: TestPass123!

3. **Submit Form**: Click "Sign In" button

4. **Expected Behavior**:
   - Should redirect to /dashboard or /onboarding
   - Should show success toast notification
   - Should store JWT tokens in localStorage

## Debugging Steps

1. **Check Browser Console**: Look for JavaScript errors
2. **Check Network Tab**: Verify API requests are being made
3. **Check Backend Logs**: Look for registration/login requests
4. **Check Database**: Verify user creation

## Common Issues

1. **Form Validation**: Ensure password meets requirements
2. **CORS Issues**: Check if frontend can communicate with backend
3. **Firebase Auth**: Verify Firebase configuration
4. **Database Connection**: Ensure PostgreSQL is accessible
