#!/bin/bash

# Kaggle Environment Setup Script for IBS Wellness Companion ML Models
# This script helps you set up Kaggle API credentials

echo "🔑 Kaggle API Credentials Setup"
echo "================================"

# Check if credentials are already set
if [ -n "$KAGGLE_USERNAME" ] && [ -n "$KAGGLE_KEY" ]; then
    echo "✅ Kaggle credentials are already set in environment"
    echo "KAGGLE_USERNAME: $KAGGLE_USERNAME"
    echo "KAGGLE_KEY: [HIDDEN FOR SECURITY]"
    exit 0
fi

# Check if kaggle.json exists
if [ -f ~/.kaggle/kaggle.json ]; then
    echo "✅ Found existing ~/.kaggle/kaggle.json file"
    echo "Your Kaggle credentials are configured via JSON file"
    exit 0
fi

echo "❌ No Kaggle credentials found"
echo ""
echo "To set up Kaggle API credentials, choose one of these methods:"
echo ""
echo "Method 1: Environment Variables (Recommended for development)"
echo "-----------------------------------------------------------"
echo "1. Get your API credentials from https://kaggle.com/account"
echo "2. Run these commands with your actual credentials:"
echo ""
echo "   export KAGGLE_USERNAME=your-kaggle-username"
echo "   export KAGGLE_KEY=your-kaggle-api-key"
echo ""
echo "3. To make it permanent, add to ~/.zshrc:"
echo "   echo 'export KAGGLE_USERNAME=your-kaggle-username' >> ~/.zshrc"
echo "   echo 'export KAGGLE_KEY=your-kaggle-api-key' >> ~/.zshrc"
echo "   source ~/.zshrc"
echo ""
echo "Method 2: Kaggle JSON File (Standard method)"
echo "--------------------------------------------"
echo "1. Download kaggle.json from https://kaggle.com/account"
echo "2. Run these commands:"
echo "   mkdir -p ~/.kaggle"
echo "   cp /path/to/downloaded/kaggle.json ~/.kaggle/"
echo "   chmod 600 ~/.kaggle/kaggle.json"
echo ""
echo "Method 3: Interactive Setup"
echo "---------------------------"
read -p "Would you like to set up credentials interactively? (y/n): " setup_interactive

if [ "$setup_interactive" = "y" ] || [ "$setup_interactive" = "Y" ]; then
    echo ""
    echo "Please enter your Kaggle credentials:"
    read -p "Kaggle Username: " kaggle_username
    read -s -p "Kaggle API Key: " kaggle_key
    echo ""
    
    if [ -n "$kaggle_username" ] && [ -n "$kaggle_key" ]; then
        # Create kaggle.json file
        mkdir -p ~/.kaggle
        cat > ~/.kaggle/kaggle.json << EOF
{
    "username": "$kaggle_username",
    "key": "$kaggle_key"
}
EOF
        chmod 600 ~/.kaggle/kaggle.json
        echo "✅ Kaggle credentials saved to ~/.kaggle/kaggle.json"
        echo "🔒 File permissions set to 600 for security"
    else
        echo "❌ Invalid credentials provided"
        exit 1
    fi
fi

echo ""
echo "🧪 Testing Kaggle API connection..."
python -c "
try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    print('✅ Kaggle API authentication successful!')
except Exception as e:
    print(f'❌ Kaggle API authentication failed: {e}')
    print('Please check your credentials and try again.')
"