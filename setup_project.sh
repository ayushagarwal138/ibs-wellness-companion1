#!/bin/bash

# IBS Wellness Companion - Complete Project Setup Script
# This script sets up the entire project with all environments and dependencies

set -e  # Exit on any error

echo "🏥 Setting up IBS Wellness Companion - Complete Project Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if we're in the project root
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Please run this script from the project root directory (ibs-wellness-companion/)"
    exit 1
fi

print_status "Setting up project structure..."

# Setup Backend Environment
print_status "Setting up Backend Environment..."
cd backend

if [ ! -f "setup_environment.sh" ]; then
    print_error "Backend setup script not found. Please ensure setup_environment.sh exists in the backend directory."
    exit 1
fi

# Run backend setup
./setup_environment.sh

cd ..

# Setup ML Models Environment
print_status "Setting up ML Models Environment..."
cd ml-models

if [ ! -d ".venv" ]; then
    print_status "Creating ML models virtual environment..."
    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install wheel setuptools
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # Install shared requirements
    if [ -f "../shared-requirements.txt" ]; then
        pip install -r ../shared-requirements.txt
    fi
    
    print_success "ML models environment setup completed!"
else
    print_warning "ML models virtual environment already exists"
fi

cd ..

# Setup Frontend Environment (if Node.js is available)
print_status "Checking Frontend Environment..."
cd frontend

if command -v node &> /dev/null; then
    print_status "Node.js found. Setting up frontend dependencies..."
    
    if [ -f "package.json" ]; then
        if command -v npm &> /dev/null; then
            npm install
            print_success "Frontend dependencies installed!"
        elif command -v yarn &> /dev/null; then
            yarn install
            print_success "Frontend dependencies installed with Yarn!"
        else
            print_warning "Neither npm nor yarn found. Please install Node.js package manager."
        fi
    else
        print_warning "package.json not found in frontend directory"
    fi
else
    print_warning "Node.js not found. Frontend setup skipped."
    print_status "To setup frontend later, install Node.js and run 'npm install' in the frontend directory"
fi

cd ..

# Create development scripts
print_status "Creating development scripts..."

# Backend development script
cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting IBS Wellness Companion Backend..."
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
EOF

# Frontend development script
cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "🎨 Starting IBS Wellness Companion Frontend..."
cd frontend
npm run dev
EOF

# Combined development script
cat > start_dev.sh << 'EOF'
#!/bin/bash
echo "🏥 Starting IBS Wellness Companion - Full Development Environment..."

# Function to run commands in background and track PIDs
run_service() {
    local service_name=$1
    local command=$2
    echo "Starting $service_name..."
    $command &
    local pid=$!
    echo "$service_name started with PID: $pid"
    echo $pid >> .dev_pids
}

# Clean up any existing PID file
rm -f .dev_pids

echo "Starting all services..."

# Start backend
run_service "Backend API" "./start_backend.sh"

# Wait a moment for backend to start
sleep 3

# Start frontend (if Node.js is available)
if command -v node &> /dev/null && [ -f "frontend/package.json" ]; then
    run_service "Frontend" "./start_frontend.sh"
fi

echo ""
echo "🎉 Development environment started!"
echo "📊 Backend API: http://localhost:8000"
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "To stop all services, run: ./stop_dev.sh"
echo "To view logs, check the terminal output above"

# Wait for user input to stop
echo "Press Ctrl+C to stop all services..."
trap 'echo "Stopping services..."; ./stop_dev.sh; exit' INT
wait
EOF

# Stop development script
cat > stop_dev.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping IBS Wellness Companion Development Environment..."

if [ -f ".dev_pids" ]; then
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "Stopping process $pid..."
            kill $pid
        fi
    done < .dev_pids
    rm -f .dev_pids
    echo "All services stopped!"
else
    echo "No running services found."
fi
EOF

# Make scripts executable
chmod +x start_backend.sh start_frontend.sh start_dev.sh stop_dev.sh

print_success "Development scripts created!"

# Create project status script
cat > check_status.sh << 'EOF'
#!/bin/bash
echo "🏥 IBS Wellness Companion - Project Status Check"
echo "================================================"

# Check Backend
echo ""
echo "🔧 Backend Status:"
if [ -d "backend/.venv" ]; then
    echo "✅ Backend virtual environment exists"
    cd backend
    source .venv/bin/activate
    python -c "
try:
    from app.main import app
    print('✅ FastAPI app can be imported')
    from app.models import User
    print('✅ Database models accessible')
    from app.services.ibs_assessment_service import IBSAssessmentService
    print('✅ IBS Assessment service accessible')
except Exception as e:
    print(f'❌ Backend import error: {e}')
" 2>/dev/null
    cd ..
else
    echo "❌ Backend virtual environment not found"
fi

# Check ML Models
echo ""
echo "🤖 ML Models Status:"
if [ -d "ml-models/.venv" ]; then
    echo "✅ ML models virtual environment exists"
else
    echo "❌ ML models virtual environment not found"
fi

# Check Frontend
echo ""
echo "🎨 Frontend Status:"
if [ -d "frontend/node_modules" ]; then
    echo "✅ Frontend dependencies installed"
else
    echo "❌ Frontend dependencies not installed"
fi

# Check Database
echo ""
echo "🗄️  Database Status:"
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL client available"
else
    echo "❌ PostgreSQL client not found"
fi

echo ""
echo "📋 Available Commands:"
echo "  ./start_backend.sh  - Start backend only"
echo "  ./start_frontend.sh - Start frontend only"
echo "  ./start_dev.sh      - Start full development environment"
echo "  ./stop_dev.sh       - Stop all development services"
echo "  ./check_status.sh   - Check project status (this script)"
EOF

chmod +x check_status.sh

print_success "Project setup completed successfully!"

echo ""
echo "🎯 Project Setup Summary:"
echo "========================"
echo "✅ Backend environment configured with Python 3.11"
echo "✅ All Python dependencies installed"
echo "✅ Development scripts created"
echo "✅ Environment templates created"
echo ""
echo "📋 Next Steps:"
echo "1. Select Python 3.11.10 in your IDE dialog"
echo "2. Update backend/.env with your database configuration"
echo "3. Set up PostgreSQL database"
echo "4. Run: ./check_status.sh to verify everything is working"
echo "5. Run: ./start_dev.sh to start the development environment"
echo ""
echo "🚀 Quick Start:"
echo "  ./start_backend.sh  # Start backend API server"
echo "  ./check_status.sh   # Check if everything is working"