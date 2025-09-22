#!/usr/bin/env python3
"""
Test script to verify profile data flow from backend API to frontend form.
This will help identify where the data population issue occurs.
"""

import requests
import json

def test_profile_data_flow():
    base_url = "http://localhost:8000"
    
    # Test user credentials
    login_data = {
        "email": "api_test@example.com",
        "password": "testpass123"
    }
    
    print("=== Testing Profile Data Flow ===\n")
    
    # Step 1: Login and get token
    print("1. Logging in...")
    login_response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    login_result = login_response.json()
    token = login_result.get("access_token")
    user_data = login_result.get("user", {})
    
    print("✅ Login successful!")
    print(f"Token: {token[:20]}...")
    print(f"User ID: {user_data.get('id')}")
    print()
    
    # Step 2: Get profile data from /auth/me
    print("2. Getting profile data from /auth/me...")
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
    
    if profile_response.status_code != 200:
        print(f"❌ Profile fetch failed: {profile_response.status_code}")
        print(f"Response: {profile_response.text}")
        return
    
    profile_data = profile_response.json()
    print("✅ Profile data retrieved!")
    print("Raw backend data:")
    print(json.dumps(profile_data, indent=2, default=str))
    print()
    
    # Step 3: Simulate frontend transformation
    print("3. Simulating frontend data transformation...")
    
    def transform_from_backend(backend_data):
        """Simulate the frontend transformFromBackend function"""
        transformed = dict(backend_data)
        
        # Transform gender
        if transformed.get('gender'):
            gender_mapping = {
                'MALE': 'male',
                'FEMALE': 'female',
                'OTHER': 'other',
                'PREFER_NOT_TO_SAY': 'prefer_not_to_say'
            }
            transformed['gender'] = gender_mapping.get(transformed['gender'], transformed['gender'].lower())
        
        # Transform IBS type
        if transformed.get('ibs_type'):
            ibs_mapping = {
                'IBS_D': 'ibs-d',
                'IBS_C': 'ibs-c',
                'IBS_M': 'ibs-m',
                'IBS_U': 'ibs-u'
            }
            transformed['ibs_type'] = ibs_mapping.get(transformed['ibs_type'], transformed['ibs_type'].lower().replace('_', '-'))
        
        return transformed
    
    transformed_data = transform_from_backend(profile_data)
    print("Transformed data for frontend:")
    print(json.dumps(transformed_data, indent=2, default=str))
    print()
    
    # Step 4: Check specific fields that should populate the form
    print("4. Checking form field population...")
    
    form_fields = {
        'first_name': transformed_data.get('first_name'),
        'last_name': transformed_data.get('last_name'),
        'email': transformed_data.get('email'),
        'phone_number': transformed_data.get('phone_number'),
        'date_of_birth': transformed_data.get('date_of_birth'),
        'gender': transformed_data.get('gender'),
        'height_cm': transformed_data.get('height_cm'),
        'weight_kg': transformed_data.get('weight_kg'),
        'ibs_type': transformed_data.get('ibs_type'),
        'diagnosis_date': transformed_data.get('diagnosis_date'),
    }
    
    print("Form field values:")
    for field, value in form_fields.items():
        status = "✅" if value is not None else "❌"
        print(f"  {status} {field}: {value}")
    
    print()
    
    # Step 5: Check if any fields are missing or null
    missing_fields = [field for field, value in form_fields.items() if value is None]
    populated_fields = [field for field, value in form_fields.items() if value is not None]
    
    print("5. Summary:")
    print(f"✅ Populated fields ({len(populated_fields)}): {', '.join(populated_fields)}")
    if missing_fields:
        print(f"❌ Missing/null fields ({len(missing_fields)}): {', '.join(missing_fields)}")
    else:
        print("✅ All fields have values!")
    
    print()
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_profile_data_flow()