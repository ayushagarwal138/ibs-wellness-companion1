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