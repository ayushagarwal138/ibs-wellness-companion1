// Test script to simulate the frontend DELETE request
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjNDY0ZDEyOS0zYzVmLTQyY2EtOGVlMC1jNmEwZWQxYWVjM2YiLCJleHAiOjE3NTkzODUyODh9.oGilFem83rXT4wDZ8wRQ-oKSUm0HtAV-NLrRkYUigqM";
const API_BASE_URL = "http://localhost:8000";

async function testDeleteAccount() {
  try {
    console.log("Making DELETE request to:", `${API_BASE_URL}/api/v1/users/account`);
    
    const response = await fetch(`${API_BASE_URL}/api/v1/users/account`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    });

    console.log("Response status:", response.status);
    console.log("Response ok:", response.ok);
    console.log("Response headers:", Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      console.log("Response not ok, trying to parse error...");
      try {
        const errorData = await response.json();
        console.log("Error data:", errorData);
      } catch (parseError) {
        console.log("Could not parse error response:", parseError);
      }
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    console.log("Success response:", data);
    
  } catch (error) {
    console.error("Delete account error:", error);
    console.error("Error type:", error.constructor.name);
    console.error("Error message:", error.message);
  }
}

testDeleteAccount();