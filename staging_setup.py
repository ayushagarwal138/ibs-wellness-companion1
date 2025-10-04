#!/usr/bin/env python3
"""
Staging Environment Setup Script for IBS Wellness Companion

This script sets up a staging environment that mirrors production
for user acceptance testing and final validation.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('staging_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class StagingEnvironmentSetup:
    """Manages the setup of staging environment for UAT."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.staging_dir = self.project_root / "staging"
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
    def create_staging_directory(self):
        """Create staging directory structure."""
        logger.info("Creating staging directory structure...")
        
        # Create main staging directory
        self.staging_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        subdirs = [
            "config",
            "logs",
            "data",
            "backups",
            "scripts",
            "docs"
        ]
        
        for subdir in subdirs:
            (self.staging_dir / subdir).mkdir(exist_ok=True)
            
        logger.info("Staging directory structure created successfully")
        
    def create_staging_config(self):
        """Create staging-specific configuration files."""
        logger.info("Creating staging configuration files...")
        
        # Staging environment variables
        staging_env = {
            "ENVIRONMENT": "staging",
            "DEBUG": "false",
            "DATABASE_URL": (
                "postgresql://staging_user:staging_pass@localhost:5432/"
                "ibs_wellness_staging"
            ),
            "REDIS_URL": "redis://localhost:6379/1",
            "SECRET_KEY": "staging-secret-key-change-in-production",
            "JWT_SECRET_KEY": "staging-jwt-secret-change-in-production",
            "CORS_ORIGINS": "http://localhost:3000,http://localhost:3001",
            "ML_MODEL_PATH": "./ml_models/staging",
            "LOG_LEVEL": "INFO",
            "API_RATE_LIMIT": "100/minute",
            "ENABLE_METRICS": "true",
            "ENABLE_HEALTH_CHECKS": "true"
        }
        
        # Write staging .env file
        staging_env_file = self.staging_dir / "config" / ".env.staging"
        with open(staging_env_file, 'w') as f:
            for key, value in staging_env.items():
                f.write(f"{key}={value}\n")
                
        # Create staging database config
        db_config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "ibs_wellness_staging",
                "user": "staging_user",
                "password": "staging_pass",
                "pool_size": 10,
                "max_overflow": 20
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 1,
                "password": None
            },
            "ml_models": {
                "path": "./ml_models/staging",
                "auto_reload": True,
                "health_check_interval": 300
            }
        }
        
        db_config_file = self.staging_dir / "config" / "database.staging.json"
        with open(db_config_file, 'w') as f:
            json.dump(db_config, f, indent=2)
            
        logger.info("Staging configuration files created")
        
    def create_staging_scripts(self):
        """Create staging deployment and management scripts."""
        logger.info("Creating staging scripts...")
        
        # Start staging script
        start_script = """#!/bin/bash
set -e

echo "Starting IBS Wellness Companion - Staging Environment"
echo "=================================================="

# Load staging environment
export $(cat staging/config/.env.staging | xargs)

# Start backend
echo "Starting backend server..."
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001 \\
    --env-file ../staging/config/.env.staging &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Start frontend
echo "Starting frontend server..."
cd ../frontend
npm start -- --port 3001 &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

# Save PIDs for cleanup
echo $BACKEND_PID > ../staging/backend.pid
echo $FRONTEND_PID > ../staging/frontend.pid

echo "Staging environment started successfully!"
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3001"
echo "API Docs: http://localhost:8001/docs"

# Wait for services to be ready
sleep 5

# Run health checks
echo "Running health checks..."
curl -f http://localhost:8001/health || echo "Backend health check failed"
curl -f http://localhost:3001 || echo "Frontend health check failed"

echo "Staging environment is ready for testing!"
"""
        
        start_script_file = self.staging_dir / "scripts" / "start_staging.sh"
        with open(start_script_file, 'w') as f:
            f.write(start_script)
        os.chmod(start_script_file, 0o755)
        
        # Stop staging script
        stop_script = """#!/bin/bash
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
"""
        
        stop_script_file = self.staging_dir / "scripts" / "stop_staging.sh"
        with open(stop_script_file, 'w') as f:
            f.write(stop_script)
        os.chmod(stop_script_file, 0o755)
        
        # Health check script
        health_script = """#!/bin/bash
echo "IBS Wellness Companion - Staging Health Check"
echo "============================================="

# Check backend
echo "Checking backend health..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \\
    http://localhost:8001/health)
if [ "$BACKEND_STATUS" = "200" ]; then
    echo "✅ Backend: Healthy"
else
    echo "❌ Backend: Unhealthy (Status: $BACKEND_STATUS)"
fi

# Check frontend
echo "Checking frontend health..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \\
    http://localhost:3001)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend: Healthy"
else
    echo "❌ Frontend: Unhealthy (Status: $FRONTEND_STATUS)"
fi

# Check ML models
echo "Checking ML models..."
ML_STATUS=$(curl -s -H "Authorization: Bearer test-token" \\
    -o /dev/null -w "%{http_code}" \\
    http://localhost:8001/api/v1/ml/models/info)
if [ "$ML_STATUS" = "200" ] || [ "$ML_STATUS" = "401" ]; then
    echo "✅ ML Models: Available"
else
    echo "❌ ML Models: Unavailable (Status: $ML_STATUS)"
fi

echo "Health check completed!"
"""
        
        health_script_file = self.staging_dir / "scripts" / "health_check.sh"
        with open(health_script_file, 'w') as f:
            f.write(health_script)
        os.chmod(health_script_file, 0o755)
        
        logger.info("Staging scripts created successfully")
        
    def create_test_data(self):
        """Create test data for staging environment."""
        logger.info("Creating test data for staging...")
        
        # Test users
        test_users = [
            {
                "email": "staging.user1@example.com",
                "password": "StagingPass123!",
                "first_name": "Alice",
                "last_name": "Johnson",
                "profile": {
                    "age": 28,
                    "ibs_type": "IBS-D",
                    "dietary_restrictions": ["lactose_intolerant"],
                    "activity_level": "moderate"
                }
            },
            {
                "email": "staging.user2@example.com", 
                "password": "StagingPass123!",
                "first_name": "Bob",
                "last_name": "Smith",
                "profile": {
                    "age": 35,
                    "ibs_type": "IBS-C",
                    "dietary_restrictions": ["gluten_free"],
                    "activity_level": "high"
                }
            },
            {
                "email": "staging.user3@example.com",
                "password": "StagingPass123!",
                "first_name": "Carol",
                "last_name": "Davis",
                "profile": {
                    "age": 42,
                    "ibs_type": "IBS-M",
                    "dietary_restrictions": [],
                    "activity_level": "low"
                }
            }
        ]
        
        test_data_file = self.staging_dir / "data" / "test_users.json"
        with open(test_data_file, 'w') as f:
            json.dump(test_users, f, indent=2)
            
        # Sample symptoms data
        sample_symptoms = [
            {
                "user_email": "staging.user1@example.com",
                "symptoms": {
                    "abdominal_pain": 6.5,
                    "bloating": 7.0,
                    "gas": 5.5,
                    "diarrhea": 8.0,
                    "constipation": 2.0,
                    "urgency": 7.5,
                    "incomplete_evacuation": 4.0,
                    "nausea": 3.0,
                    "fatigue": 6.0,
                    "mood_score": 4.0,
                    "stress_level": 7.0,
                    "sleep_quality": 5.0
                },
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        symptoms_data_file = self.staging_dir / "data" / "sample_symptoms.json"
        with open(symptoms_data_file, 'w') as f:
            json.dump(sample_symptoms, f, indent=2)
            
        logger.info("Test data created successfully")
        
    def create_staging_documentation(self):
        """Create staging environment documentation."""
        logger.info("Creating staging documentation...")
        
        readme_content = """# IBS Wellness Companion - Staging Environment

## Overview
This staging environment provides a production-like setup for user acceptance 
testing (UAT) and final validation before deployment.

## Environment Details
- **Backend URL**: http://localhost:8001
- **Frontend URL**: http://localhost:3001
- **API Documentation**: http://localhost:8001/docs
- **Database**: PostgreSQL (staging database)
- **Cache**: Redis (database 1)

## Quick Start

### 1. Start Staging Environment
```bash
./staging/scripts/start_staging.sh
```

### 2. Run Health Checks
```bash
./staging/scripts/health_check.sh
```

### 3. Stop Staging Environment
```bash
./staging/scripts/stop_staging.sh
```

## Test Users
The following test users are available for UAT:

1. **Alice Johnson** (IBS-D)
   - Email: staging.user1@example.com
   - Password: StagingPass123!
   - Profile: 28 years old, lactose intolerant, moderate activity

2. **Bob Smith** (IBS-C)
   - Email: staging.user2@example.com
   - Password: StagingPass123!
   - Profile: 35 years old, gluten-free, high activity

3. **Carol Davis** (IBS-M)
   - Email: staging.user3@example.com
   - Password: StagingPass123!
   - Profile: 42 years old, no restrictions, low activity

## Testing Scenarios

### 1. User Registration & Authentication
- Test user registration with various profiles
- Verify login/logout functionality
- Test password reset flow

### 2. Symptom Tracking
- Log daily symptoms for different IBS types
- Test symptom severity tracking
- Verify data persistence

### 3. ML Predictions
- Test severity predictions with various symptom combinations
- Verify flareup risk assessments
- Test personalized recommendations

### 4. Dietary Management
- Test food diary functionality
- Verify trigger identification
- Test dietary recommendations

### 5. Lifestyle Tracking
- Test stress level monitoring
- Verify sleep quality tracking
- Test exercise impact analysis

## API Testing
Use the provided test data in `staging/data/` for API testing:
- `test_users.json`: Pre-configured test users
- `sample_symptoms.json`: Sample symptom data for testing

## Monitoring & Logs
- Application logs: `staging/logs/`
- Health check results: Run `./staging/scripts/health_check.sh`
- Performance metrics: Available at backend `/metrics` endpoint

## Configuration
- Environment variables: `staging/config/.env.staging`
- Database config: `staging/config/database.staging.json`

## Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure ports 8001 and 3001 are available
2. **Database connection**: Verify PostgreSQL is running
3. **ML models**: Check model files are present in `ml_models/staging/`

### Support
For issues during UAT, check:
1. Application logs in `staging/logs/`
2. Health check status
3. Database connectivity
4. ML model status via `/api/v1/ml/models/info`
"""
        
        readme_file = self.staging_dir / "docs" / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
            
        # UAT checklist
        uat_checklist = """# User Acceptance Testing (UAT) Checklist

## Pre-Testing Setup
- [ ] Staging environment started successfully
- [ ] All health checks pass
- [ ] Test users created and accessible
- [ ] Sample data loaded

## Authentication & User Management
- [ ] User registration works with valid data
- [ ] User registration rejects invalid data
- [ ] User login works with correct credentials
- [ ] User login rejects incorrect credentials
- [ ] Password reset functionality works
- [ ] User profile management works

## Core Functionality
- [ ] Symptom logging interface works
- [ ] Symptom data is saved correctly
- [ ] Historical symptom data displays properly
- [ ] Food diary functionality works
- [ ] Trigger identification works

## ML Features
- [ ] Severity prediction returns reasonable results
- [ ] Flareup risk assessment works
- [ ] Personalized recommendations are generated
- [ ] Medication effectiveness predictions work
- [ ] All ML endpoints handle errors gracefully

## User Experience
- [ ] Navigation is intuitive
- [ ] Forms are user-friendly
- [ ] Error messages are clear and helpful
- [ ] Loading states are appropriate
- [ ] Mobile responsiveness works

## Performance
- [ ] Page load times are acceptable (<3 seconds)
- [ ] API responses are fast (<1 second)
- [ ] ML predictions complete quickly (<2 seconds)
- [ ] No memory leaks or performance degradation

## Security
- [ ] Authentication tokens work correctly
- [ ] Unauthorized access is blocked
- [ ] Sensitive data is not exposed
- [ ] CORS settings are appropriate

## Error Handling
- [ ] Invalid inputs are handled gracefully
- [ ] Network errors are handled properly
- [ ] ML model errors don't crash the app
- [ ] Database errors are handled appropriately

## Final Validation
- [ ] All critical user journeys work end-to-end
- [ ] No blocking bugs identified
- [ ] Performance meets requirements
- [ ] Security requirements satisfied
- [ ] Ready for production deployment

## Sign-off
- [ ] Product Owner approval
- [ ] Technical Lead approval
- [ ] QA Team approval
- [ ] Security Team approval (if applicable)

**UAT Completed By**: ________________  
**Date**: ________________  
**Approved for Production**: [ ] Yes [ ] No  
**Comments**: ________________
"""
        
        checklist_file = self.staging_dir / "docs" / "UAT_Checklist.md"
        with open(checklist_file, 'w') as f:
            f.write(uat_checklist)
            
        logger.info("Staging documentation created successfully")
        
    def setup_ml_models_staging(self):
        """Set up ML models for staging environment."""
        logger.info("Setting up ML models for staging...")
        
        # Create staging ML models directory
        staging_ml_dir = self.project_root / "ml_models" / "staging"
        staging_ml_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy current models to staging
        source_ml_dir = self.project_root / "ml_models" / "checkpoints"
        if source_ml_dir.exists():
            for model_file in source_ml_dir.glob("*.pkl"):
                shutil.copy2(model_file, staging_ml_dir)
                logger.info(f"Copied {model_file.name} to staging")
                
            # Copy metadata if exists
            metadata_file = source_ml_dir / "model_metadata.json"
            if metadata_file.exists():
                shutil.copy2(metadata_file, staging_ml_dir)
                logger.info("Copied model metadata to staging")
        else:
            logger.warning("No ML models found to copy to staging")
            
        logger.info("ML models staging setup completed")
        
    def run_setup(self):
        """Run the complete staging environment setup."""
        logger.info("Starting staging environment setup...")
        
        try:
            self.create_staging_directory()
            self.create_staging_config()
            self.create_staging_scripts()
            self.create_test_data()
            self.create_staging_documentation()
            self.setup_ml_models_staging()
            
            logger.info("Staging environment setup completed successfully!")
            logger.info(f"Staging directory: {self.staging_dir}")
            logger.info("Next steps:")
            logger.info("1. Review configuration in staging/config/")
            logger.info(
                "2. Start staging environment: "
                "./staging/scripts/start_staging.sh"
            )
            logger.info(
                "3. Run health checks: "
                "./staging/scripts/health_check.sh"
            )
            logger.info(
                "4. Begin UAT using staging/docs/UAT_Checklist.md"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Staging setup failed: {e}")
            return False


if __name__ == "__main__":
    setup = StagingEnvironmentSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)