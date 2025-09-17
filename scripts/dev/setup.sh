#!/bin/bash

# IBS Wellness Companion - Development Setup Script
# This script sets up the development environment for the IBS Wellness Companion

set -e  # Exit on any error

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
    else
        print_error "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi
    
    # Check npm
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        print_success "npm found: $NPM_VERSION"
    else
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
    else
        print_error "Python 3 is not installed. Please install Python 3.11+ from https://python.org/"
        exit 1
    fi
    
    # Check pip
    if command_exists pip3; then
        PIP_VERSION=$(pip3 --version)
        print_success "pip found: $PIP_VERSION"
    else
        print_error "pip is not installed. Please install pip."
        exit 1
    fi
    
    # Check Docker (optional)
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version)
        print_success "Docker found: $DOCKER_VERSION"
    else
        print_warning "Docker is not installed. Docker is optional but recommended for development."
    fi
    
    # Check PostgreSQL (optional)
    if command_exists psql; then
        PSQL_VERSION=$(psql --version)
        print_success "PostgreSQL found: $PSQL_VERSION"
    else
        print_warning "PostgreSQL is not installed. You can use Docker for the database."
    fi
    
    # Check Redis (optional)
    if command_exists redis-cli; then
        print_success "Redis CLI found"
    else
        print_warning "Redis is not installed. You can use Docker for Redis."
    fi
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing frontend dependencies..."
    npm install
    
    # Copy environment file
    if [ ! -f .env.local ]; then
        print_status "Creating frontend environment file..."
        cp .env.example .env.local
        print_warning "Please update .env.local with your configuration"
    fi
    
    cd ..
    print_success "Frontend setup completed"
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing backend dependencies..."
    pip install -r requirements.txt
    
    # Copy environment file
    if [ ! -f .env ]; then
        print_status "Creating backend environment file..."
        cp .env.example .env
        print_warning "Please update .env with your configuration"
    fi
    
    cd ..
    print_success "Backend setup completed"
}

# Function to setup ML models
setup_ml_models() {
    print_status "Setting up ML models..."
    
    cd ml-models
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating ML Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating ML virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing ML dependencies..."
    pip install -r requirements.txt
    
    # Create necessary directories
    mkdir -p data/raw data/processed data/external
    mkdir -p checkpoints
    mkdir -p logs
    
    cd ..
    print_success "ML models setup completed"
}

# Function to setup database
setup_database() {
    print_status "Setting up database..."
    
    if command_exists docker; then
        print_status "Starting PostgreSQL with TimescaleDB using Docker..."
        cd deployment/docker
        docker-compose up -d postgres
        
        # Wait for database to be ready
        print_status "Waiting for database to be ready..."
        sleep 10
        
        # Run database initialization
        print_status "Initializing database schema..."
        docker-compose exec postgres psql -U postgres -d ibs_wellness -f /docker-entrypoint-initdb.d/init.sql
        
        cd ../..
        print_success "Database setup completed"
    else
        print_warning "Docker not found. Please set up PostgreSQL manually and run the schema from database/schemas/init.sql"
    fi
}

# Function to setup development services
setup_dev_services() {
    print_status "Setting up development services..."
    
    if command_exists docker; then
        cd deployment/docker
        
        print_status "Starting Redis..."
        docker-compose up -d redis
        
        print_status "Starting ChromaDB..."
        docker-compose up -d chromadb
        
        cd ../..
        print_success "Development services setup completed"
    else
        print_warning "Docker not found. Please set up Redis and ChromaDB manually."
    fi
}

# Function to create development scripts
create_dev_scripts() {
    print_status "Creating development scripts..."
    
    # Create start script
    cat > scripts/dev/start.sh << 'EOF'
#!/bin/bash
# Start development servers

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait for Ctrl+C
echo "Development servers started. Press Ctrl+C to stop."
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
EOF

    chmod +x scripts/dev/start.sh
    
    # Create stop script
    cat > scripts/dev/stop.sh << 'EOF'
#!/bin/bash
# Stop development servers

echo "Stopping development servers..."
pkill -f "uvicorn app.main:app"
pkill -f "next dev"
echo "Development servers stopped."
EOF

    chmod +x scripts/dev/stop.sh
    
    print_success "Development scripts created"
}

# Main setup function
main() {
    print_status "Starting IBS Wellness Companion development setup..."
    
    # Check if we're in the right directory
    if [ ! -f "README.md" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Check system requirements
    check_requirements
    
    # Setup components
    setup_frontend
    setup_backend
    setup_ml_models
    setup_database
    setup_dev_services
    create_dev_scripts
    
    print_success "Development setup completed successfully!"
    print_status "Next steps:"
    echo "1. Update environment files (.env.local in frontend, .env in backend)"
    echo "2. Configure your database connection"
    echo "3. Set up OAuth providers (Google, GitHub)"
    echo "4. Configure SendGrid for email notifications"
    echo "5. Set up Firebase for push notifications"
    echo ""
    echo "To start development servers:"
    echo "  ./scripts/dev/start.sh"
    echo ""
    echo "To stop development servers:"
    echo "  ./scripts/dev/stop.sh"
    echo ""
    echo "For more information, see the README.md file."
}

# Run main function
main "$@"