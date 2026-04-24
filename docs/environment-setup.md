# IBS Wellness Companion - Environment Setup Guide

This guide provides comprehensive instructions for setting up and managing the development environments for the IBS Wellness Companion project.

## 🚀 Quick Start

### Prerequisites
- macOS with Homebrew installed
- pyenv for Python version management
- Python 3.11.10 (automatically installed if not present)

### One-Command Setup
```bash
# Set up all environments at once
./manage-envs.sh setup-all
```

### Individual Environment Setup
```bash
# Backend only
./manage-envs.sh setup-backend

# ML Models only
./manage-envs.sh setup-ml
```

## 📁 Project Structure

```
ibs-wellness-companion/
├── backend/                 # FastAPI backend service
│   ├── venv/               # Backend virtual environment
│   └── requirements.txt    # Backend dependencies
├── ml-models/              # Machine learning models
│   ├── venv/               # ML virtual environment
│   └── requirements.txt    # ML dependencies
├── activate-backend.sh     # Backend environment activation
├── activate-ml.sh          # ML environment activation
└── manage-envs.sh          # Environment management utility
```

## 🔧 Environment Management

### Status Check
```bash
# Check status of all environments
./manage-envs.sh status

# Health check for all environments
./manage-envs.sh check-all
```

### Environment Activation

#### Backend Environment
```bash
# Activate backend environment
./activate-backend.sh

# Available commands in backend environment:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000  # Start dev server
python -m pytest tests/                                   # Run tests
alembic upgrade head                                       # Run migrations
```

#### ML Models Environment
```bash
# Activate ML environment
./activate-ml.sh

# Available commands in ML environment:
jupyter notebook                          # Start Jupyter
python src/training/train_model.py       # Train models
python src/inference/predict.py          # Run predictions
python -m pytest tests/                  # Run ML tests
```

## 📦 Dependencies

### Backend Dependencies
- **FastAPI 0.104.1** - Modern web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation
- **Alembic** - Database migrations

### ML Models Dependencies
- **PyTorch 2.1.2** - Deep learning framework
- **Scikit-learn 1.3.2** - Machine learning library
- **Transformers 4.36.2** - Hugging Face transformers
- **NumPy 1.26.4** - Numerical computing
- **Pandas 2.1.4** - Data manipulation
- **Matplotlib/Seaborn/Plotly** - Data visualization

## 🛠️ Troubleshooting

### Common Issues

#### Python Version Conflicts
If you encounter Python version issues:
```bash
# Clean all environments and recreate
./manage-envs.sh clean-all
./manage-envs.sh setup-all
```

#### Dependency Conflicts
The ML environment uses carefully selected package versions to avoid conflicts:
- Scikit-learn is pinned to <1.4 for compatibility with sktime
- PyTorch ecosystem packages are version-matched
- Core packages (numpy, pandas) are installed first

#### Permission Issues
Make sure scripts are executable:
```bash
chmod +x activate-backend.sh activate-ml.sh manage-envs.sh
```

### Environment Health Check
```bash
# Check if environments are working correctly
./manage-envs.sh check-backend
./manage-envs.sh check-ml
```

## 🔄 Development Workflow

### Starting Development
1. Check environment status: `./manage-envs.sh status`
2. Activate appropriate environment:
   - Backend: `./activate-backend.sh`
   - ML: `./activate-ml.sh`
3. Start development servers or run scripts

### Switching Between Environments
- Each activation script starts a new shell with the environment active
- Use `deactivate` to exit the virtual environment
- Use `exit` to return to the previous shell

### Updating Dependencies
```bash
# Backend
cd backend && source venv/bin/activate
pip install new-package
pip freeze > requirements.txt

# ML Models
cd ml-models && source venv/bin/activate
pip install new-package
# Note: Update requirements.txt manually for ML to maintain compatibility
```

## 📋 Management Commands

| Command | Description |
|---------|-------------|
| `./manage-envs.sh status` | Show environment status |
| `./manage-envs.sh check-all` | Health check all environments |
| `./manage-envs.sh setup-all` | Set up all environments |
| `./manage-envs.sh clean-all` | Remove all environments |
| `./activate-backend.sh` | Activate backend environment |
| `./activate-ml.sh` | Activate ML environment |

## 🎯 Best Practices

1. **Always use the activation scripts** for consistent environment setup
2. **Check environment health** before starting development
3. **Use the management script** for environment maintenance
4. **Keep dependencies updated** but test thoroughly
5. **Document any new dependencies** and their purpose

## 🆘 Getting Help

If you encounter issues:
1. Check the environment status: `./manage-envs.sh status`
2. Run health checks: `./manage-envs.sh check-all`
3. Review the troubleshooting section above
4. Clean and recreate environments if needed

For additional support, refer to the main project documentation or contact the development team.