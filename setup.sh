#!/bin/bash

# ===================================
# Delhi Metro Route Finder - Setup Script
# ===================================
# This script automates the setup process
# Run with: bash setup.sh

echo "🚇 Delhi Metro Route Finder - Setup"
echo "===================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed!"
    echo "Please install Python 3.10 or higher from python.org"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "  → Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "  ✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "  ✓ All dependencies installed"

# Create .env file if it doesn't exist
echo ""
if [ -f ".env" ]; then
    echo "✓ .env file already exists"
else
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "  ✓ .env file created"
fi

# Run tests to verify installation
echo ""
echo "🧪 Running tests to verify installation..."
python -m pytest tests/ --quiet
TEST_EXIT_CODE=$?

echo ""
echo "===================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ Setup completed successfully!"
    echo ""
    echo "To run the application:"
    echo "  1. Activate the virtual environment:"
    echo "     source venv/bin/activate"
    echo ""
    echo "  2. Start the server:"
    echo "     python app.py"
    echo ""
    echo "  3. Open your browser:"
    echo "     http://localhost:5000"
else
    echo "⚠️  Setup completed but some tests failed."
    echo "The app should still work, but check the test output above."
fi
echo "===================================="
