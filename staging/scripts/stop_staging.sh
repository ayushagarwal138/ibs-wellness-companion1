#!/bin/bash
echo "Stopping IBS Wellness Companion - Staging Environment"
echo "=================================================="

# Stop backend
if [ -f staging/backend.pid ]; then
    BACKEND_PID=$(cat staging/backend.pid)
    echo "Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || echo "Backend already stopped"
    rm staging/backend.pid
fi

# Stop frontend
if [ -f staging/frontend.pid ]; then
    FRONTEND_PID=$(cat staging/frontend.pid)
    echo "Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || echo "Frontend already stopped"
    rm staging/frontend.pid
fi

echo "Staging environment stopped successfully!"
