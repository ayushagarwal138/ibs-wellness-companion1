#!/bin/bash

echo "🔧 Fixing pyenv configuration..."

# Source the updated .zshrc to apply pyenv configuration
source ~/.zshrc

# Verify pyenv is working
if command -v pyenv &> /dev/null; then
    echo "✅ pyenv is now properly configured"
    echo "🐍 Available Python versions:"
    pyenv versions
    echo ""
    echo "📍 Current Python version: $(python --version)"
else
    echo "❌ pyenv configuration failed"
    exit 1
fi

echo ""
echo "🎉 Configuration complete!"
echo "💡 The pyenv error should no longer appear in new terminals"
echo "💡 To apply changes to current terminal, run: source ~/.zshrc"