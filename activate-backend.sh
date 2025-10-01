#!/bin/bash

# IBS Wellness Companion - Backend Environment Activation Script
# This script activates the backend virtual environment and sets up the development environment

echo "🚀 Activating IBS Wellness Companion Backend Environment..."

# Check if we're in the correct directory
if [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "backend/.venv" ]; then
    echo "❌ Error: Backend virtual environment not found. Please run setup first."
    echo "   Run: cd backend && ./setup_environment.sh"
    exit 1
fi

# Activate the virtual environment
cd backend
source .venv/bin/activate

# Set environment variables for development
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export ENVIRONMENT="development"

# Display environment info
echo "✅ Backend environment activated!"
echo "📍 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"
echo "📦 FastAPI version: $(python -c 'import fastapi; print(fastapi.__version__)' 2>/dev/null || echo 'Not installed')"
echo ""
echo "🔧 Available commands:"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000  # Start development server"
echo "   python -m pytest tests/                                   # Run tests"
echo "   alembic upgrade head                                       # Run database migrations"
echo ""
echo "💡 To deactivate: type 'deactivate'"

# Start a new shell with the environment activated
exec $SHELL