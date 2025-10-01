#!/bin/bash

# IBS Wellness Companion - ML Models Environment Activation Script
# This script activates the ML models virtual environment and sets up the development environment

echo "🧠 Activating IBS Wellness Companion ML Models Environment..."

# Check if we're in the correct directory
if [ ! -d "ml-models" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "ml-models/venv" ]; then
    echo "❌ Error: ML models virtual environment not found. Please run setup first."
    echo "   Run: cd ml-models && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate the virtual environment
cd ml-models
source venv/bin/activate

# Set environment variables for development
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export ENVIRONMENT="development"

# Display environment info
echo "✅ ML models environment activated!"
echo "📍 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"
echo "🔥 PyTorch version: $(python -c 'import torch; print(torch.__version__)' 2>/dev/null || echo 'Not installed')"
echo "🤗 Transformers version: $(python -c 'import transformers; print(transformers.__version__)' 2>/dev/null || echo 'Not installed')"
echo "📊 Scikit-learn version: $(python -c 'import sklearn; print(sklearn.__version__)' 2>/dev/null || echo 'Not installed')"
echo ""
echo "🔧 Available commands:"
echo "   jupyter notebook                                          # Start Jupyter for model development"
echo "   python src/training/train_model.py                       # Train models"
echo "   python src/inference/predict.py                          # Run predictions"
echo "   python -m pytest tests/                                  # Run ML tests"
echo ""
echo "💡 To deactivate: type 'deactivate'"

# Start a new shell with the environment activated
exec $SHELL