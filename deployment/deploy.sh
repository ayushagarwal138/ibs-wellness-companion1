#!/bin/bash

# IBS Wellness Companion - Deployment Script
# Usage: ./deploy.sh [environment] [options]
# Environments: development, staging, production
# Options: --build, --no-cache, --logs, --stop, --restart

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-development}
BUILD_FLAG=""
CACHE_FLAG=""
LOGS_FLAG=""
ACTION="start"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD_FLAG="--build"
            shift
            ;;
        --no-cache)
            CACHE_FLAG="--no-cache"
            shift
            ;;
        --logs)
            LOGS_FLAG="--follow"
            ACTION="logs"
            shift
            ;;
        --stop)
            ACTION="stop"
            shift
            ;;
        --restart)
            ACTION="restart"
            shift
            ;;
        development|staging|production)
            ENVIRONMENT=$1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if required files exist
check_requirements() {
    local required_files=(
        "deployment/docker/docker-compose.yml"
        "deployment/docker/Dockerfile.backend"
        "deployment/docker/Dockerfile.frontend"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "Required file not found: $file"
            exit 1
        fi
    done
}

# Function to create environment file if it doesn't exist
create_env_file() {
    local env_file=".env.${ENVIRONMENT}"
    
    if [[ ! -f "$env_file" ]]; then
        print_warning "Environment file $env_file not found. Creating default..."
        
        case $ENVIRONMENT in
            development)
                cat > "$env_file" << EOF
# Development Environment
POSTGRES_PASSWORD=postgres
DEBUG=true
ENVIRONMENT=development
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_AUTH_PROVIDER=firebase
EOF
                ;;
            staging)
                cat > "$env_file" << EOF
# Staging Environment
POSTGRES_PASSWORD=staging_secure_password
DEBUG=false
ENVIRONMENT=staging
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_WS_URL=ws://localhost:8001
NEXT_PUBLIC_AUTH_PROVIDER=firebase
EOF
                ;;
            production)
                cat > "$env_file" << EOF
# Production Environment
POSTGRES_PASSWORD=production_secure_password
DEBUG=false
ENVIRONMENT=production
NEXT_PUBLIC_API_URL=https://your-domain.com
NEXT_PUBLIC_WS_URL=wss://your-domain.com
NEXT_PUBLIC_AUTH_PROVIDER=firebase
EOF
                ;;
        esac
        
        print_success "Created $env_file with default values"
        print_warning "Please review and update the environment variables in $env_file"
    fi
}

# Function to start services
start_services() {
    print_status "Starting $ENVIRONMENT environment..."
    
    local compose_file="deployment/docker/docker-compose.yml"
    local env_file=".env.${ENVIRONMENT}"
    
    # Build command
    local cmd="docker-compose -f $compose_file --env-file $env_file"
    
    # Add profile for production
    if [[ "$ENVIRONMENT" == "production" ]]; then
        cmd="$cmd --profile production"
    fi
    
    # Execute command
    if [[ "$BUILD_FLAG" == "--build" ]]; then
        print_status "Building and starting services..."
        $cmd up -d $BUILD_FLAG $CACHE_FLAG
    else
        print_status "Starting services..."
        $cmd up -d
    fi
    
    print_success "$ENVIRONMENT environment started successfully!"
    
    # Show service status
    print_status "Service status:"
    $cmd ps
    
    # Show access URLs
    echo ""
    print_status "Access URLs:"
    case $ENVIRONMENT in
        development)
            echo "  Frontend: http://localhost:3000"
            echo "  Backend API: http://localhost:8000"
            echo "  API Docs: http://localhost:8000/docs"
            echo "  Flower (Celery): http://localhost:5555"
            echo "  MLflow: http://localhost:5000"
            echo "  ChromaDB: http://localhost:8001"
            ;;
        staging)
            echo "  Frontend: http://localhost:3001"
            echo "  Backend API: http://localhost:8001"
            echo "  API Docs: http://localhost:8001/docs"
            ;;
        production)
            echo "  Application: https://your-domain.com"
            echo "  API: https://your-domain.com/api"
            ;;
    esac
}

# Function to stop services
stop_services() {
    print_status "Stopping $ENVIRONMENT environment..."
    
    local compose_file="deployment/docker/docker-compose.yml"
    local env_file=".env.${ENVIRONMENT}"
    
    local cmd="docker-compose -f $compose_file --env-file $env_file"
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        cmd="$cmd --profile production"
    fi
    
    $cmd down
    
    print_success "$ENVIRONMENT environment stopped successfully!"
}

# Function to restart services
restart_services() {
    print_status "Restarting $ENVIRONMENT environment..."
    stop_services
    start_services
}

# Function to show logs
show_logs() {
    print_status "Showing logs for $ENVIRONMENT environment..."
    
    local compose_file="deployment/docker/docker-compose.yml"
    local env_file=".env.${ENVIRONMENT}"
    
    local cmd="docker-compose -f $compose_file --env-file $env_file"
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        cmd="$cmd --profile production"
    fi
    
    if [[ "$LOGS_FLAG" == "--follow" ]]; then
        $cmd logs -f
    else
        $cmd logs
    fi
}

# Function to run health checks
health_check() {
    print_status "Running health checks for $ENVIRONMENT environment..."
    
    local backend_port
    case $ENVIRONMENT in
        development) backend_port=8000 ;;
        staging) backend_port=8001 ;;
        production) backend_port=80 ;;
    esac
    
    # Wait for services to be ready
    sleep 10
    
    # Check backend health
    if curl -f "http://localhost:${backend_port}/health" > /dev/null 2>&1; then
        print_success "Backend is healthy"
    else
        print_error "Backend health check failed"
    fi
    
    # Check database connection
    if docker-compose -f deployment/docker/docker-compose.yml --env-file ".env.${ENVIRONMENT}" exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
        print_success "Database is healthy"
    else
        print_error "Database health check failed"
    fi
    
    # Check Redis
    if docker-compose -f deployment/docker/docker-compose.yml --env-file ".env.${ENVIRONMENT}" exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is healthy"
    else
        print_error "Redis health check failed"
    fi
}

# Main execution
main() {
    print_status "IBS Wellness Companion Deployment Script"
    print_status "Environment: $ENVIRONMENT"
    print_status "Action: $ACTION"
    
    # Check prerequisites
    check_docker
    check_requirements
    
    # Create environment file if needed
    create_env_file
    
    # Execute action
    case $ACTION in
        start)
            start_services
            health_check
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            health_check
            ;;
        logs)
            show_logs
            ;;
        *)
            print_error "Unknown action: $ACTION"
            exit 1
            ;;
    esac
}

# Show usage if no arguments
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 [environment] [options]"
    echo ""
    echo "Environments:"
    echo "  development  - Local development environment (default)"
    echo "  staging      - Staging environment for testing"
    echo "  production   - Production environment"
    echo ""
    echo "Options:"
    echo "  --build      - Build images before starting"
    echo "  --no-cache   - Build without using cache"
    echo "  --logs       - Show and follow logs"
    echo "  --stop       - Stop the environment"
    echo "  --restart    - Restart the environment"
    echo ""
    echo "Examples:"
    echo "  $0 development --build"
    echo "  $0 staging --restart"
    echo "  $0 production --logs"
    echo "  $0 development --stop"
    exit 0
fi

# Run main function
main