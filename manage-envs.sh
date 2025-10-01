#!/bin/bash

# IBS Wellness Companion - Environment Management Script
# This script provides utilities for managing virtual environments

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_VERSION="3.11.10"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  IBS Wellness Companion - Env Manager${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if pyenv is available
check_pyenv() {
    if ! command -v pyenv &> /dev/null; then
        print_error "pyenv is not installed. Please install pyenv first."
        echo "Install with: brew install pyenv"
        exit 1
    fi
}

# Check if Python 3.11 is available
check_python() {
    if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
        print_warning "Python $PYTHON_VERSION not found. Installing..."
        pyenv install $PYTHON_VERSION
    fi
}

# Create virtual environment
create_venv() {
    local component=$1
    local dir=$2
    
    print_info "Creating virtual environment for $component..."
    
    cd "$PROJECT_ROOT/$dir"
    
    # Remove existing venv if it exists
    if [ -d "venv" ]; then
        print_warning "Removing existing virtual environment..."
        rm -rf venv
    fi
    
    # Create new virtual environment with Python 3.11
    ~/.pyenv/versions/$PYTHON_VERSION/bin/python -m venv venv
    
    # Activate and upgrade pip
    source venv/bin/activate
    pip install --upgrade pip
    
    print_success "Virtual environment created for $component"
}

# Install dependencies
install_deps() {
    local component=$1
    local dir=$2
    
    print_info "Installing dependencies for $component..."
    
    cd "$PROJECT_ROOT/$dir"
    source venv/bin/activate
    
    if [ "$component" = "backend" ]; then
        pip install -r requirements.txt
    elif [ "$component" = "ml-models" ]; then
        # Install core packages first to avoid conflicts
        pip install numpy==1.24.4 pandas==2.1.4 torch==2.1.2
        pip install "scikit-learn>=1.0,<1.4"
        pip install torchvision==0.16.2 torchaudio==2.1.2 pytorch-lightning==2.1.2
        pip install matplotlib==3.8.2 seaborn==0.13.0 plotly==5.17.0
        pip install transformers==4.36.2 openai==1.6.1
        # Install remaining packages that don't conflict
        pip install joblib==1.3.2 httpx==0.25.2 python-dateutil==2.8.2
    fi
    
    print_success "Dependencies installed for $component"
}

# Check environment health
check_health() {
    local component=$1
    local dir=$2
    
    print_info "Checking health of $component environment..."
    
    cd "$PROJECT_ROOT/$dir"
    
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found for $component"
        return 1
    fi
    
    source venv/bin/activate
    
    if [ "$component" = "backend" ]; then
        python -c "import fastapi; print('FastAPI:', fastapi.__version__)" || return 1
        python -c "import uvicorn; print('Uvicorn: OK')" || return 1
        python -c "import sqlalchemy; print('SQLAlchemy: OK')" || return 1
    elif [ "$component" = "ml-models" ]; then
        python -c "import torch; print('PyTorch:', torch.__version__)" || return 1
        python -c "import sklearn; print('Scikit-learn:', sklearn.__version__)" || return 1
        python -c "import transformers; print('Transformers:', transformers.__version__)" || return 1
    fi
    
    print_success "$component environment is healthy"
}

# Show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup-all      Set up both backend and ML environments"
    echo "  setup-backend  Set up only backend environment"
    echo "  setup-ml       Set up only ML models environment"
    echo "  check-all      Check health of all environments"
    echo "  check-backend  Check health of backend environment"
    echo "  check-ml       Check health of ML models environment"
    echo "  clean-all      Remove all virtual environments"
    echo "  status         Show status of all environments"
    echo "  help           Show this help message"
}

# Show environment status
show_status() {
    print_header
    echo ""
    
    # Backend status
    echo -e "${BLUE}Backend Environment:${NC}"
    if [ -d "$PROJECT_ROOT/backend/venv" ]; then
        cd "$PROJECT_ROOT/backend"
        source venv/bin/activate
        echo "  Status: ✅ Active"
        echo "  Python: $(python --version)"
        echo "  Location: $PROJECT_ROOT/backend/venv"
        deactivate
    else
        echo "  Status: ❌ Not found"
    fi
    
    echo ""
    
    # ML models status
    echo -e "${BLUE}ML Models Environment:${NC}"
    if [ -d "$PROJECT_ROOT/ml-models/venv" ]; then
        cd "$PROJECT_ROOT/ml-models"
        source venv/bin/activate
        echo "  Status: ✅ Active"
        echo "  Python: $(python --version)"
        echo "  Location: $PROJECT_ROOT/ml-models/venv"
        deactivate
    else
        echo "  Status: ❌ Not found"
    fi
    
    echo ""
    echo -e "${BLUE}Quick Start:${NC}"
    echo "  Backend:    ./activate-backend.sh"
    echo "  ML Models:  ./activate-ml.sh"
}

# Main script logic
case "$1" in
    "setup-all")
        print_header
        check_pyenv
        check_python
        create_venv "backend" "backend"
        install_deps "backend" "backend"
        create_venv "ml-models" "ml-models"
        install_deps "ml-models" "ml-models"
        print_success "All environments set up successfully!"
        ;;
    "setup-backend")
        print_header
        check_pyenv
        check_python
        create_venv "backend" "backend"
        install_deps "backend" "backend"
        ;;
    "setup-ml")
        print_header
        check_pyenv
        check_python
        create_venv "ml-models" "ml-models"
        install_deps "ml-models" "ml-models"
        ;;
    "check-all")
        print_header
        check_health "backend" "backend"
        check_health "ml-models" "ml-models"
        ;;
    "check-backend")
        check_health "backend" "backend"
        ;;
    "check-ml")
        check_health "ml-models" "ml-models"
        ;;
    "clean-all")
        print_warning "Removing all virtual environments..."
        rm -rf "$PROJECT_ROOT/backend/venv"
        rm -rf "$PROJECT_ROOT/ml-models/venv"
        print_success "All virtual environments removed"
        ;;
    "status")
        show_status
        ;;
    "help"|"")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac