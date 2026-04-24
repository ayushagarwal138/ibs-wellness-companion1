# IBS Wellness Companion - Setup Guide

## Database Configuration

This project now uses **PostgreSQL exclusively** for all environments (development, testing, and production). SQLite has been removed to ensure consistency and better production readiness.

### Prerequisites

1. **PostgreSQL 15+** with TimescaleDB extension
2. **Redis** for caching and background tasks
3. **Python 3.11+**
4. **Node.js 18+**

### Database Setup

#### Option 1: Using Docker (Recommended)
```bash
cd deployment/docker
docker-compose up -d postgres redis
```

#### Option 2: Local PostgreSQL Installation
1. Install PostgreSQL with TimescaleDB
2. Create database:
```sql
CREATE DATABASE ibs_wellness;
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

### Environment Configuration

#### Backend (.env)
```bash
cp backend/.env.example backend/.env
```

Key configurations:
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ibs_wellness`
- Update other credentials as needed

#### Frontend (.env.local)
```bash
cp frontend/.env.example frontend/.env.local
```

### Dependency Management

This project uses a **shared dependencies approach** to ensure version consistency:

- `shared-requirements.txt` - Common dependencies (ML, AI, data processing)
- `backend/requirements.txt` - Backend-specific dependencies + shared deps
- `ml-models/requirements.txt` - ML-specific dependencies + shared deps

### Installation

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

#### ML Models
```bash
cd ml-models
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Migrations

Run Alembic migrations:
```bash
cd backend
alembic upgrade head
```

### Development Servers

#### Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run dev
```

## Architecture Improvements Made

### ✅ Resolved Conflicts

1. **Migration Consolidation**: Removed duplicate migration directories, using only Alembic
2. **Database Standardization**: PostgreSQL-only configuration across all environments
3. **Dependency Management**: Shared requirements file prevents version conflicts
4. **Clean Repository**: Removed database files from version control

### 🔧 Benefits

- **Consistency**: Same database engine across all environments
- **Scalability**: PostgreSQL with TimescaleDB for time-series health data
- **Maintainability**: Centralized dependency management
- **Production Ready**: No SQLite limitations in production

### 📋 Next Steps

1. Set up CI/CD pipelines with PostgreSQL
2. Configure monitoring and logging
3. Implement proper backup strategies
4. Add comprehensive testing with test database