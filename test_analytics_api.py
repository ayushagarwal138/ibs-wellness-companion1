import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
# Create a new test user
TEST_EMAIL = "analytics_test@example.com"
TEST_PASSWORD = "TestPassword123!"


def register_user():
    """Register a new test user"""
    url = f"{BASE_URL}/api/v1/auth/register"
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "confirm_password": TEST_PASSWORD,
        "first_name": "Analytics",
        "last_name": "Test"
    }
    
    response = requests.post(url, json=data)
    print(f"Registration status: {response.status_code}")
    
    if response.status_code == 201:
        return True
    else:
        print(f"Registration failed: {response.text}")
        return False


def login_user():
    """Login and get access token"""
    url = f"{BASE_URL}/api/v1/auth/login"
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(url, json=data)
    print(f"Login status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print(f"Login failed: {response.text}")
        return None


def test_analytics_api():
    """Test the analytics API endpoints"""
    try:
        print("📝 Registering test user...")
        register_user()  # Try to register, ignore if user already exists
        
        print("🔐 Logging in...")
        access_token = login_user()
        
        if not access_token:
            print("❌ Failed to get access token")
            return
            
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print("\n📊 Testing symptom stats endpoint...")
        stats_url = f"{BASE_URL}/api/v1/symptom-logs/stats/summary?days=30"
        stats_response = requests.get(stats_url, headers=headers)
        print(f"Stats status: {stats_response.status_code}")
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print("✅ Successfully retrieved stats data")
            print(f"📋 Stats keys: {list(stats_data.keys())}")
            
            # Check for weekly_trends specifically
            if 'weekly_trends' in stats_data:
                weekly_trends = stats_data['weekly_trends']
                print(f"📈 Weekly trends type: {type(weekly_trends)}")
                print(f"📈 Weekly trends data: {weekly_trends}")
            else:
                print("⚠️ No weekly_trends found in response")
                print(f"📋 Full response: {json.dumps(stats_data, indent=2)}")
        else:
            print(f"❌ Stats request failed: {stats_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_analytics_api()