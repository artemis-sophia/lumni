#!/bin/bash

# Lumni - Initialization Script
# This script helps set up the gateway for first-time use

set -e

echo "🎓 Lumni API Gateway - Initialization"
echo "======================================"
echo ""

# Check if config.json exists
if [ ! -f "config.json" ]; then
    echo "📝 Creating config.json from example..."
    cp config.example.json config.json
    echo "✅ Created config.json"
    echo ""
    echo "⚠️  Please edit config.json and add your API keys!"
    echo ""
else
    echo "✅ config.json already exists"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env from example..."
        cp .env.example .env
        echo "✅ Created .env"
        echo ""
        echo "⚠️  Please edit .env and add your API keys!"
        echo ""
    else
        echo "⚠️  .env.example not found, creating basic .env file..."
        cat > .env << 'ENVEOF'
# Unified API Key
UNIFIED_API_KEY=your-unified-api-key-here

# Provider API Keys
GROQ_API_KEY=your_groq_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here

# Logging
LOG_LEVEL=info
CONFIG_PATH=./config.json
ENVEOF
        echo "✅ Created basic .env file"
        echo "⚠️  Please edit .env and add your API keys!"
        echo ""
    fi
else
    echo "✅ .env already exists"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
echo "✅ Directories created"

# Check Python version
echo ""
echo "🔍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ required. Please install Python."
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python version: $(python3 --version)"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo ""
    echo "⚠️  Poetry not found. Installing dependencies with pip..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "❌ requirements.txt not found"
        exit 1
    fi
else
    echo ""
    echo "📦 Installing dependencies with Poetry..."
    poetry install
    echo "✅ Dependencies installed"
fi

# Initialize database
echo ""
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
echo "Next steps:"
echo "1. Edit config.json and add your API keys"
echo "2. Edit .env and set your unified API key"
echo "3. Run 'poetry run uvicorn app.main:app --host 0.0.0.0 --port 3000' to start the gateway"
echo ""
echo "For detailed setup instructions, see SETUP.md"

