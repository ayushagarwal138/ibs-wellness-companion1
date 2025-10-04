#!/bin/bash
echo "IBS Wellness Companion - Staging Health Check"
echo "============================================="

# Check backend
echo "Checking backend health..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    http://localhost:8001/health)
if [ "$BACKEND_STATUS" = "200" ]; then
    echo "✅ Backend: Healthy"
else
    echo "❌ Backend: Unhealthy (Status: $BACKEND_STATUS)"
fi

# Check frontend
echo "Checking frontend health..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    http://localhost:3001)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend: Healthy"
else
    echo "❌ Frontend: Unhealthy (Status: $FRONTEND_STATUS)"
fi

# Check ML models
echo "Checking ML models..."
ML_STATUS=$(curl -s -H "Authorization: Bearer test-token" \
    -o /dev/null -w "%{http_code}" \
    http://localhost:8001/api/v1/ml/models/info)
if [ "$ML_STATUS" = "200" ] || [ "$ML_STATUS" = "401" ]; then
    echo "✅ ML Models: Available"
else
    echo "❌ ML Models: Unavailable (Status: $ML_STATUS)"
fi

echo "Health check completed!"
