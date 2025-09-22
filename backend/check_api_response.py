import asyncio
import aiohttp
import json

async def check_api_response():
    # Test user credentials (adjust as needed)
    login_data = {
        "email": "api_test@example.com",
        "password": "testpass123"
    }
    
    async with aiohttp.ClientSession() as session:
        # Login to get token
        try:
            async with session.post('http://localhost:8000/api/v1/auth/login', 
                                  json=login_data) as response:
                if response.status == 200:
                    login_result = await response.json()
                    token = login_result['access_token']
                    print("Login successful!")
                    print("User data from login:", json.dumps(login_result['user'], indent=2))
                    
                    # Get user profile
                    headers = {'Authorization': f'Bearer {token}'}
                    async with session.get('http://localhost:8000/api/v1/auth/me', 
                                         headers=headers) as profile_response:
                        if profile_response.status == 200:
                            profile_data = await profile_response.json()
                            print("\nProfile data from /auth/me:", json.dumps(profile_data, indent=2))
                        else:
                            print(f"Profile fetch failed: {profile_response.status}")
                            print(await profile_response.text())
                else:
                    print(f"Login failed: {response.status}")
                    print(await response.text())
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_api_response())
