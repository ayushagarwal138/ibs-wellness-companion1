# IBS Wellness Companion

A comprehensive web application for IBS patients featuring AI-powered predictions, progress tracking, personalized recommendations, and intelligent chatbot support.

## 🏗️ Architecture Overview

```
ibs-wellness-companion/
├── frontend/                 # Next.js React application
├── backend/                  # FastAPI Python backend
├── ml-models/               # Machine learning models and training
├── database/                # Database schemas and migrations
├── shared/                  # Shared types and utilities
├── deployment/              # Deployment configurations
├── docs/                    # Documentation
└── scripts/                 # Development and deployment scripts
```

## 🚀 Tech Stack

### Frontend
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **TailwindCSS** for styling
- **Framer Motion** for animations
- **Chart.js/Recharts** for data visualization
- **React Hook Form** for form handling
- **Zustand** for state management

### Backend
- **FastAPI** with async/await
- **PostgreSQL** with TimescaleDB extension
- **Celery + Redis** for background tasks
- **OAuth2 + JWT** for authentication
- **Pydantic** for data validation

### ML & AI
- **scikit-learn** (Random Forest, XGBoost)
- **PyTorch** (LSTM/GRU for time-series)
- **Prophet** for forecasting
- **LangChain + ChromaDB** for RAG chatbot
- **Sentence Transformers** for embeddings

### Infrastructure
- **Docker** for containerization
- **Vercel** for frontend deployment
- **Render/Heroku** for backend deployment
- **Supabase** for PostgreSQL hosting

## 🔧 Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ibs-wellness-companion
   ```

2. **Setup Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Setup**
   - Copy `.env.example` files in both frontend and backend
   - Configure your database, API keys, and other settings

5. **Run Development Servers**
   ```bash
   # Backend (Terminal 1)
   cd backend && uvicorn main:app --reload

   # Frontend (Terminal 2)
   cd frontend && npm run dev
   ```

## 📋 Features

- ✅ **Flare-up Prediction**: ML-powered risk assessment
- ✅ **Progress Tracking**: Time-series visualization and forecasting
- ✅ **Diet Recommendations**: Personalized nutrition guidance
- ✅ **AI Chatbot**: RAG-powered Q&A system
- ✅ **Smart Notifications**: Email and push reminders
- ✅ **Secure Authentication**: OAuth2 + JWT implementation
- ✅ **Real-time Dashboard**: Interactive charts and analytics

## 🔒 Security

- OAuth 2.0 authentication
- JWT token-based authorization
- HTTPS/TLS encryption
- Database encryption at rest
- Input validation and sanitization

## 📊 ML Models

1. **Flare-up Prediction**: Random Forest classifier
2. **Progress Forecasting**: Prophet + LSTM hybrid
3. **Diet Recommendations**: Collaborative + content-based filtering
4. **Symptom Analysis**: Time-series clustering

## 🤖 AI Chatbot

- **RAG Pipeline**: LangChain + ChromaDB
- **Embeddings**: Sentence Transformers (MiniLM)
- **LLM**: Llama 3 (local deployment)
- **Knowledge Base**: IBS medical literature and guidelines

## 📱 Deployment

- **Frontend**: Vercel (automatic deployments)
- **Backend**: Render/Heroku with Docker
- **Database**: Supabase PostgreSQL
- **ML Models**: FastAPI model serving endpoints

## 🧪 Testing

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test
```

## 📚 Documentation

### Setup & Environment
- [Environment Setup Guide](./docs/environment-setup.md) - Comprehensive environment setup instructions
- [Setup Guide](./docs/setup-guide.md) - Quick setup reference

### Technical Documentation
- [Technical Summary](./docs/technical-summary.md) - Debugging sessions and technical fixes
- [ML Integration Fixes](./docs/ml-integration-fixes.md) - ML integration troubleshooting

### API & Architecture
- [API Documentation](./docs/api.md)
- [Database Schema](./docs/database.md)
- [ML Models](./docs/ml-models.md)
- [Deployment Guide](./docs/deployment.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.