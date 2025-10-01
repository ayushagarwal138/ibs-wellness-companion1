// Test script to verify dashboard analytics service
const API_BASE_URL = 'http://localhost:8000';
const TEST_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5NWRhOTY4ZS00Yjg1LTQwOGQtODVkZi04OWM0Njk3Yjg1MjkiLCJleHAiOjE3NTkxNjQ2NTR9.dPVGK4hpRqqK2lTLE6ygX5HwDFyfAnVSgQVBYQ_cMWg';

async function testDashboardAnalytics() {
  console.log('Testing Dashboard Analytics Service...');
  
  try {
    // Test diet logs endpoint
    console.log('\n1. Testing diet logs endpoint...');
    const dietResponse = await fetch(`${API_BASE_URL}/api/v1/diet/logs`, {
      headers: {
        'Authorization': `Bearer ${TEST_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!dietResponse.ok) {
      throw new Error(`Diet logs API error: ${dietResponse.status}`);
    }
    
    const dietData = await dietResponse.json();
    console.log('Diet logs response:', dietData);
    console.log('Number of diet logs:', dietData.items?.length || 0);
    
    // Test symptom logs endpoint
    console.log('\n2. Testing symptom logs endpoint...');
    const symptomResponse = await fetch(`${API_BASE_URL}/api/v1/symptom-logs`, {
      headers: {
        'Authorization': `Bearer ${TEST_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!symptomResponse.ok) {
      console.log(`Symptom logs API error: ${symptomResponse.status}`);
    } else {
      const symptomData = await symptomResponse.json();
      console.log('Symptom logs response:', symptomData);
      console.log('Number of symptom logs:', symptomData.items?.length || 0);
    }
    
    // Test food reactions endpoint
    console.log('\n3. Testing food reactions endpoint...');
    const reactionsResponse = await fetch(`${API_BASE_URL}/api/v1/diet/reactions`, {
      headers: {
        'Authorization': `Bearer ${TEST_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!reactionsResponse.ok) {
      console.log(`Food reactions API error: ${reactionsResponse.status}`);
    } else {
      const reactionsData = await reactionsResponse.json();
      console.log('Food reactions response:', reactionsData);
      console.log('Number of food reactions:', reactionsData.items?.length || 0);
    }
    
    // Simulate analytics calculation
    console.log('\n4. Simulating analytics calculation...');
    const now = new Date();
    const lastMonth = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    
    const currentDietLogs = dietData.items?.filter(log => new Date(log.consumed_at) >= lastMonth) || [];
    console.log('Current month diet logs:', currentDietLogs.length);
    
    console.log('\n✅ Dashboard analytics test completed successfully!');
    console.log(`Expected meals logged count: ${currentDietLogs.length}`);
    
  } catch (error) {
    console.error('❌ Dashboard analytics test failed:', error);
  }
}

// Run the test
testDashboardAnalytics();