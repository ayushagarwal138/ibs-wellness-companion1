#!/bin/bash
set -e

echo "Starting IBS Wellness Companion - Staging Environment"
echo "=================================================="

# Load staging environment
export $(cat staging/config/.env.staging | xargs)

# Start backend
echo "Starting backend server..."
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001 \
    --env-file ../staging/config/.env.staging &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Start frontend (if it exists)
if [ -d "../frontend" ]; then
    echo "Starting frontend server..."
    cd ../frontend
    npm start -- --port 3001 &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
else
    echo "Frontend directory not found, skipping frontend startup"
    FRONTEND_PID=""
fi

# Save PIDs for cleanup
echo $BACKEND_PID > ../staging/backend.pid
if [ -n "$FRONTEND_PID" ]; then
    echo $FRONTEND_PID > ../staging/frontend.pid
fi

echo "Staging environment started successfully!"
echo "Backend: http://localhost:8001"
if [ -n "$FRONTEND_PID" ]; then
    echo "Frontend: http://localhost:3001"
fi
echo "API Docs: http://localhost:8001/docs"

# Wait for services to be ready
sleep 5

# Run health checks
echo "Running health checks..."
curl -f http://localhost:8001/health || echo "Backend health check failed"
if [ -n "$FRONTEND_PID" ]; then
    curl -f http://localhost:3001 || echo "Frontend health check failed"
fi

echo "Staging environment is ready for testing!"
