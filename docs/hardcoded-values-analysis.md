# Hard-coded Values Analysis

## Overview
This document provides a comprehensive analysis of all hard-coded values found in the IBS Wellness Companion codebase and recommendations for making them configurable.

## Categories of Hard-coded Values

### 1. URLs and Endpoints

#### Backend API URLs
- **Pattern**: `http://localhost:8000`, `https://api.github.com`, `https://www.googleapis.com`
- **Files**: Multiple frontend service files, test files
- **Impact**: High - affects deployment flexibility
- **Recommendation**: Use environment variables for all external URLs

#### Frontend Service URLs
- **Pattern**: `process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000'`
- **Files**: All frontend service files
- **Current Status**: Partially configurable but with hard-coded fallback
- **Recommendation**: Remove hard-coded fallbacks, use proper configuration

### 2. Port Numbers

#### Common Ports Found
- **3000**: Frontend development server
- **8000**: Backend API server
- **8001**: ChromaDB, alternative backend
- **5432**: PostgreSQL database
- **6379**: Redis server
- **5555**: Celery Flower monitoring
- **5000**: MLflow server

#### Files Affected
- Test scripts, deployment configurations, service files
- **Impact**: Medium - affects local development and deployment
- **Recommendation**: Centralize port configuration

### 3. Database and Connection Strings

#### Hard-coded Database URLs
```
postgresql://postgres:postgres@localhost:5432/ibs_wellness
postgresql+asyncpg://ayushagarwal:ayush1@localhost:5432/ibs_wellness
redis://localhost:6379/0
```

#### Files Affected
- `backend/app/core/config.py`
- `staging/config/.env.staging`
- Docker compose files
- **Impact**: High - security and deployment risk
- **Recommendation**: Use environment variables exclusively

### 4. Timeouts and Limits

#### Sleep/Timeout Values
- `time.sleep(1)`, `time.sleep(2)`, `time.sleep(5)` in test files
- `timeout=30`, `timeout=10` in HTTP requests
- `limit=5` in API calls
- `max_length=100`, `max_length=255` in Pydantic schemas

#### Files Affected
- Integration tests, API services, data models
- **Impact**: Medium - affects performance and user experience
- **Recommendation**: Make configurable based on environment

### 5. Security-related Values

#### API Keys and Secrets (Test/Staging)
- `SECRET_KEY="staging-secret-key-change-in-production"`
- `JWT_SECRET_KEY="staging-jwt-secret-change-in-production"`
- Hard-coded test passwords: `"TestPassword123!"`, `"testpassword123"`

#### Files Affected
- Staging configuration, test files
- **Impact**: Critical - security vulnerability
- **Recommendation**: Use secure environment variables and key management

### 6. ML Model Configuration

#### Hard-coded ML Parameters
- `OPENAI_MAX_TOKENS: int = 1000`
- `OPENAI_MODEL: str = "gpt-3.5-turbo"`
- Model file paths and training parameters

#### Files Affected
- `backend/app/core/config.py`, ML training scripts
- **Impact**: Medium - affects ML model performance
- **Recommendation**: Make ML parameters configurable

### 7. File Paths and Directories

#### Hard-coded Paths
- `ML_MODEL_PATH: str = "models/"`
- `UPLOAD_DIR: str = "uploads/"`
- `LOG_FILE: str = "logs/app.log"`

#### Files Affected
- Configuration files, service files
- **Impact**: Medium - affects deployment flexibility
- **Recommendation**: Use configurable paths with sensible defaults

### 8. Rate Limiting and Performance

#### Hard-coded Limits
- `RATE_LIMIT_PER_MINUTE: int = 60`
- `MAX_FILE_SIZE: int = 10485760` (10MB)
- `ACCESS_TOKEN_EXPIRE_MINUTES: int = 30`

#### Files Affected
- Configuration files, security modules
- **Impact**: Medium - affects scalability and security
- **Recommendation**: Environment-specific configuration

## Current Configuration Status

### Backend Configuration
- ✅ Uses Pydantic Settings with environment variable support
- ✅ Has fallback values for development
- ❌ Some values still hard-coded without environment variable options
- ❌ No validation for required production values

### Frontend Configuration
- ✅ Uses Next.js environment variables
- ❌ Hard-coded fallback URLs throughout the codebase
- ❌ No centralized configuration management
- ❌ Inconsistent environment variable usage

## Recommendations

### 1. Immediate Actions (High Priority)
1. **Remove hard-coded credentials** from staging configuration
2. **Centralize all URL configurations** in environment variables
3. **Create comprehensive .env.example files** for both frontend and backend
4. **Add validation** for required production environment variables

### 2. Medium Priority
1. **Make timeouts and limits configurable** based on environment
2. **Centralize port configuration** in environment variables
3. **Create environment-specific configuration files**
4. **Add configuration validation** at application startup

### 3. Long-term Improvements
1. **Implement configuration management service**
2. **Add runtime configuration updates** for non-security parameters
3. **Create configuration documentation** and validation schemas
4. **Implement configuration drift detection**

## Implementation Plan

### Phase 1: Security and Critical Values
- [ ] Remove hard-coded secrets and credentials
- [ ] Create secure environment variable management
- [ ] Add production configuration validation
- [ ] Update deployment scripts

### Phase 2: Service Configuration
- [ ] Centralize URL and port configuration
- [ ] Create environment-specific config files
- [ ] Update all service files to use centralized config
- [ ] Add configuration testing

### Phase 3: Performance and ML Configuration
- [ ] Make timeouts and limits configurable
- [ ] Create ML model configuration system
- [ ] Add runtime configuration management
- [ ] Implement configuration monitoring

## Files Requiring Updates

### Backend Files
- `backend/app/core/config.py` - Extend configuration options
- `backend/app/services/*.py` - Remove hard-coded values
- `backend/app/api/v1/*.py` - Use centralized configuration
- Test files - Use configuration for test parameters

### Frontend Files
- All service files in `frontend/src/services/`
- All API route files in `frontend/src/app/api/`
- Component files with API calls
- `frontend/next.config.js` - Centralize configuration

### Configuration Files
- Create comprehensive `.env.example` files
- Update Docker configuration files
- Update deployment scripts
- Create environment-specific configurations

## Risk Assessment

### High Risk
- Hard-coded credentials in staging configuration
- Database connection strings with credentials
- API keys and secrets in configuration files

### Medium Risk
- Hard-coded URLs affecting deployment flexibility
- Fixed timeouts that may not suit all environments
- Port numbers that may conflict in different environments

### Low Risk
- Default file paths and directories
- Non-sensitive configuration defaults
- Development-specific hard-coded values

## Success Metrics

1. **Zero hard-coded credentials** in any configuration file
2. **All URLs configurable** through environment variables
3. **Environment-specific configurations** for development, staging, and production
4. **Comprehensive configuration documentation**
5. **Automated configuration validation** in CI/CD pipeline