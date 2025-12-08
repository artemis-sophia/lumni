#!/bin/bash

# Lumni - One-Command Setup Script (Linux/Mac)
# This script sets up the entire project in one go

set -e

echo "🎓 Lumni API Gateway - Quick Setup"
echo "==================================="
echo ""

# Check Python version
echo "🔍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ required. Please install Python."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python version: $PYTHON_VERSION"
echo ""

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "⚠️  Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    echo "✅ Poetry installed"
    echo ""
fi

# Create virtual environment if using pip
if [ ! -d "venv" ] && ! command -v poetry &> /dev/null; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created"
    echo ""
fi

# Install dependencies
echo "📦 Installing dependencies..."
if command -v poetry &> /dev/null; then
    poetry install
    echo "✅ Dependencies installed with Poetry"
else
    pip install -r requirements.txt
    echo "✅ Dependencies installed with pip"
fi
echo ""

# Copy configuration files
echo "📝 Setting up configuration..."
if [ ! -f "config.json" ]; then
    cp config.example.json config.json
    echo "✅ Created config.json from example"
else
    echo "✅ config.json already exists"
fi

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env from example"
    else
        echo "⚠️  .env.example not found, skipping .env creation"
    fi
else
    echo "✅ .env already exists"
fi
echo ""

# Create directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
echo "✅ Directories created"
echo ""

# Initialize database
echo "🗄️  Initializing database..."
if command -v poetry &> /dev/null; then
    poetry run alembic upgrade head
else
    python3 -m alembic upgrade head
fi
echo "✅ Database initialized"
echo ""

echo "✨ Setup complete!"
echo ""
echo "⚠️  IMPORTANT: Before starting the gateway:"
echo "   1. Edit config.json and add your API keys"
echo "   2. Edit .env and set your unified API key"
echo ""
echo "🚀 To start the gateway:"
if command -v poetry &> /dev/null; then
    echo "   poetry run uvicorn app.main:app --host 0.0.0.0 --port 3000"
else
    echo "   source venv/bin/activate"
    echo "   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 3000"
fi
echo ""
echo "📖 For detailed instructions, see QUICKSTART.md or SETUP.md"
echo ""

