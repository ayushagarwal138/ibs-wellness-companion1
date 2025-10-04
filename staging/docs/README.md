# IBS Wellness Companion - Staging Environment

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
