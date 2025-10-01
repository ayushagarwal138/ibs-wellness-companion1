#!/bin/bash

# IBS Wellness Companion - Backend Environment Setup Script
# This script sets up the complete development environment with all dependencies

set -e  # Exit on any error

echo "🚀 Setting up IBS Wellness Companion Backend Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found. Please run this script from the backend directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_status "Creating virtual environment with Python 3.11..."
    python3.11 -m venv .venv
    print_success "Virtual environment created at .venv/"
else
    print_warning "Virtual environment already exists at .venv/"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install wheel and setuptools first
print_status "Installing build tools..."
pip install wheel setuptools

# Install dependencies with specific versions to avoid conflicts
print_status "Installing backend dependencies..."

# Install core dependencies first
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install pydantic==2.5.2
pip install sqlalchemy==2.0.23

# Install the missing JSON logger
print_status "Installing python-json-logger..."
pip install python-json-logger==2.0.7

# Install all requirements
print_status "Installing all requirements from requirements.txt..."
pip install -r requirements.txt

# Install shared requirements
if [ -f "../shared-requirements.txt" ]; then
    print_status "Installing shared dependencies..."
    pip install -r ../shared-requirements.txt
else
    print_warning "shared-requirements.txt not found, skipping shared dependencies"
fi

# Create logs directory
print_status "Creating logs directory..."
mkdir -p logs

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file template..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/ibs_wellness
TEST_DATABASE_URL=postgresql://username:password@localhost:5432/ibs_wellness_test

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# External Services
SENDGRID_API_KEY=your-sendgrid-api-key
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json

# ML Models
ML_MODEL_PATH=../ml-models/
ENABLE_ML_PREDICTIONS=true

# Redis (for caching and background tasks)
REDIS_URL=redis://localhost:6379/0

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
EOF
    print_success ".env file created. Please update with your actual configuration."
else
    print_warning ".env file already exists"
fi

# Test the installation
print_status "Testing the installation..."
python -c "
try:
    from app.main import app
    print('✅ FastAPI app import successful!')
    
    from app.models import User, SymptomLog, DietLog
    print('✅ Models import successful!')
    
    from app.services.ibs_assessment_service import IBSAssessmentService
    print('✅ IBS Assessment service import successful!')
    
    from app.api.v1 import api_router
    print('✅ API router import successful!')
    
    print('🎉 All critical components are working!')
    
except Exception as e:
    print(f'❌ Import test failed: {e}')
    exit(1)
"

print_success "Environment setup completed successfully!"
print_status "Virtual environment is located at: $(pwd)/.venv"
print_status "To activate the environment manually, run: source .venv/bin/activate"
print_status "To start the development server, run: uvicorn app.main:app --reload"

echo ""
echo "🎯 Next steps:"
echo "1. Update the .env file with your actual configuration"
echo "2. Set up your PostgreSQL database"
echo "3. Run database migrations: alembic upgrade head"
echo "4. Start the development server: uvicorn app.main:app --reload"