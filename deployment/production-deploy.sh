#!/bin/bash

# IBS Wellness Companion - Production Deployment Script
# This script handles production deployments with enhanced security and monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="./deployment/logs/production-deploy-$(date +%Y%m%d_%H%M%S).log"
HEALTH_CHECK_TIMEOUT=300
ROLLBACK_ENABLED=true

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to create log directory
setup_logging() {
    mkdir -p "$(dirname "$LOG_FILE")"
    print_status "Logging to: $LOG_FILE"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if running as root (not recommended for production)
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root is not recommended for production deployments"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check Docker
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running"
        exit 1
    fi
    
    # Check Docker Compose
    if ! docker-compose --version > /dev/null 2>&1; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check available disk space (minimum 5GB)
    available_space=$(df . | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 5242880 ]]; then
        print_warning "Low disk space detected. Available: $(($available_space / 1024 / 1024))GB"
    fi
    
    # Check if production environment file exists
    if [[ ! -f ".env.production" ]]; then
        print_error "Production environment file (.env.production) not found"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to validate environment configuration
validate_environment() {
    print_status "Validating production environment configuration..."
    
    # Check required environment variables
    local required_vars=(
        "POSTGRES_PASSWORD"
        "SECRET_KEY"
        "NEXT_PUBLIC_API_URL"
        "NEXT_PUBLIC_FIREBASE_API_KEY"
    )
    
    source .env.production
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            print_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Check for default/weak passwords
    if [[ "$POSTGRES_PASSWORD" == "postgres" ]] || [[ "$POSTGRES_PASSWORD" == "password" ]]; then
        print_error "Weak database password detected. Please use a strong password."
        exit 1
    fi
    
    # Validate URLs
    if [[ "$NEXT_PUBLIC_API_URL" == *"localhost"* ]]; then
        print_warning "API URL contains localhost. This may not work in production."
    fi
    
    print_success "Environment configuration validated"
}

# Function to create backup
create_backup() {
    if [[ "$ROLLBACK_ENABLED" == "true" ]]; then
        print_status "Creating backup..."
        
        mkdir -p "$BACKUP_DIR"
        
        # Backup database
        if docker-compose -f deployment/docker/docker-compose.yml --env-file .env.production ps postgres | grep -q "Up"; then
            print_status "Backing up database..."
            docker-compose -f deployment/docker/docker-compose.yml --env-file .env.production exec -T postgres pg_dump -U postgres ibs_wellness > "$BACKUP_DIR/database.sql"
        fi
        
        # Backup volumes
        print_status "Backing up volumes..."
        docker run --rm -v ibs-wellness-companion_postgres_data:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
        docker run --rm -v ibs-wellness-companion_backend_uploads:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine tar czf /backup/backend_uploads.tar.gz -C /data .
        
        print_success "Backup created at: $BACKUP_DIR"
    fi
}

# Function to build and deploy
deploy() {
    print_status "Starting production deployment..."
    
    # Pull latest images
    print_status "Pulling latest base images..."
    docker-compose -f deployment/docker/docker-compose.yml --env-file .env.production --profile production pull
    
    # Build application images
    print_status "Building application images..."
    docker-compose -f deployment/docker/docker-compose.yml --env-file .env.production --profile production build --no-cache
    
    # Start services with zero-downtime deployment
    print_status "Deploying services..."
    docker-compose -f deployment/docker/docker-compose.yml --env-file .env.production --profile production up -d --remove-orphans
    
    print_success "Deployment completed"
}

# Function to run comprehensive health checks
health_check() {
    print_status "Running comprehensive health checks..."
    
    local start_time=$(date +%s)
    local timeout=$HEALTH_CHECK_TIMEOUT
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 30
    
    # Check backend health
    local backend_healthy=false
    local attempts=0
    local max_attempts=10
    
    while [[ $attempts -lt $max_attempts ]]; do
        if curl -f -s "http://localhost/health" > /dev/null 2>&1; then
            backend_healthy=true
            break
        fi
        
        attempts=$((attempts + 1))
        print_status "Backend health check attempt $attempts/$max_attempts..."
        sleep 10
    done
    
    if [[ "$backend_healthy" == "true" ]]; then
        print_success "Backend is healthy"
    else
        print_error "Backend health check failed after $max_attempts attempts"
        return 1
    fi
    
    # Check database connectivity
    if docker-compose -f deployment/docker/docker-compose.yml --env-file .env.production exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
        print_success "Database is healthy"
    else
        print_error "Database health check failed"
        return 1
    fi
    
    # Check Redis
    if docker-compose -f deployment/docker/docker-compose.yml --env-file .env.production exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is healthy"
    else
        print_error "Redis health check failed"
        return 1
    fi
    
    # Check ML models endpoint
    if curl -f -s "http://localhost/api/v1/ml/models/info" > /dev/null 2>&1; then
        print_success "ML models endpoint is accessible"
    else
        print_warning "ML models endpoint check failed (may require authentication)"
    fi
    
    # Performance checks
    print_status "Running performance checks..."
    
    # Check response time
    local response_time=$(curl -o /dev/null -s -w '%{time_total}' "http://localhost/health")
    if (( $(echo "$response_time < 2.0" | bc -l) )); then
        print_success "Response time is good: ${response_time}s"
    else
        print_warning "Response time is slow: ${response_time}s"
    fi
    
    # Check memory usage
    local memory_usage=$(docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}" | grep -E "(backend|frontend|postgres)" | head -3)
    print_status "Memory usage:"
    echo "$memory_usage" | tee -a "$LOG_FILE"
    
    print_success "Health checks completed"
}

# Function to setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring and alerting..."
    
    # Create monitoring directory
    mkdir -p ./monitoring
    
    # Create basic monitoring script
    cat > ./monitoring/health-monitor.sh << 'EOF'
#!/bin/bash
# Simple health monitoring script

ALERT_EMAIL=${ALERT_EMAIL:-admin@example.com}
LOG_FILE="./monitoring/health-$(date +%Y%m%d).log"

check_service() {
    local service_name=$1
    local url=$2
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo "$(date): $service_name - OK" >> "$LOG_FILE"
        return 0
    else
        echo "$(date): $service_name - FAILED" >> "$LOG_FILE"
        echo "ALERT: $service_name is down!" | mail -s "Service Alert" "$ALERT_EMAIL" 2>/dev/null || true
        return 1
    fi
}

# Check main services
check_service "Backend" "http://localhost/health"
check_service "Frontend" "http://localhost/"

# Check resource usage
df -h / | tail -1 | awk '{print "Disk usage: " $5}' >> "$LOG_FILE"
free -m | awk 'NR==2{printf "Memory usage: %.2f%%\n", $3*100/$2}' >> "$LOG_FILE"
EOF
    
    chmod +x ./monitoring/health-monitor.sh
    
    # Create log rotation script
    cat > ./monitoring/rotate-logs.sh << 'EOF'
#!/bin/bash
# Log rotation script

find ./deployment/logs -name "*.log" -mtime +30 -delete
find ./monitoring -name "health-*.log" -mtime +7 -delete
docker system prune -f --volumes --filter "until=168h"
EOF
    
    chmod +x ./monitoring/rotate-logs.sh
    
    print_success "Monitoring setup completed"
    print_status "Consider setting up cron jobs for:"
    print_status "  - Health monitoring: */5 * * * * /path/to/monitoring/health-monitor.sh"
    print_status "  - Log rotation: 0 2 * * 0 /path/to/monitoring/rotate-logs.sh"
}

# Function to rollback deployment
rollback() {
    if [[ "$ROLLBACK_ENABLED" == "true" ]] && [[ -d "$BACKUP_DIR" ]]; then
        print_warning "Rolling back deployment..."
        
        # Stop current services
        docker-compose -f deployment/docker/docker-compose.yml --env-file .env.production --profile production down
        
        # Restore database
        if [[ -f "$BACKUP_DIR/database.sql" ]]; then
            print_status "Restoring database..."
            docker-compose -f deployment/docker/docker-compose.yml --env-file .env.production up -d postgres
            sleep 10
            docker-compose -f deployment/docker/docker-compose.yml --env-file .env.production exec -T postgres psql -U postgres -d ibs_wellness < "$BACKUP_DIR/database.sql"
        fi
        
        # Restore volumes
        if [[ -f "$BACKUP_DIR/postgres_data.tar.gz" ]]; then
            print_status "Restoring volumes..."
            docker run --rm -v ibs-wellness-companion_postgres_data:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine tar xzf /backup/postgres_data.tar.gz -C /data
        fi
        
        print_success "Rollback completed"
    else
        print_error "Rollback not available"
    fi
}

# Function to cleanup old resources
cleanup() {
    print_status "Cleaning up old resources..."
    
    # Remove old images
    docker image prune -f --filter "until=168h"
    
    # Remove old volumes
    docker volume prune -f
    
    # Remove old backups (keep last 5)
    find ./backups -maxdepth 1 -type d -name "20*" | sort -r | tail -n +6 | xargs rm -rf
    
    print_success "Cleanup completed"
}

# Main deployment function
main() {
    print_status "IBS Wellness Companion - Production Deployment"
    print_status "Started at: $(date)"
    
    # Setup logging
    setup_logging
    
    # Check prerequisites
    check_prerequisites
    
    # Validate environment
    validate_environment
    
    # Create backup
    create_backup
    
    # Deploy
    if deploy; then
        print_success "Deployment successful"
        
        # Run health checks
        if health_check; then
            print_success "All health checks passed"
            
            # Setup monitoring
            setup_monitoring
            
            # Cleanup
            cleanup
            
            print_success "Production deployment completed successfully!"
            print_status "Application is available at: $(grep NEXT_PUBLIC_API_URL .env.production | cut -d'=' -f2)"
        else
            print_error "Health checks failed"
            read -p "Do you want to rollback? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rollback
            fi
            exit 1
        fi
    else
        print_error "Deployment failed"
        rollback
        exit 1
    fi
}

# Handle script arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    rollback)
        rollback
        ;;
    health-check)
        health_check
        ;;
    cleanup)
        cleanup
        ;;
    *)
        echo "Usage: $0 [deploy|rollback|health-check|cleanup]"
        echo ""
        echo "Commands:"
        echo "  deploy       - Full production deployment (default)"
        echo "  rollback     - Rollback to previous version"
        echo "  health-check - Run health checks only"
        echo "  cleanup      - Clean up old resources"
        exit 1
        ;;
esac