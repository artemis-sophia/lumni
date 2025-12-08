#!/bin/bash

# Lumni - One-Command Setup Script (Linux/Mac)
# This script sets up the entire project in one go

set -e

echo "Lumni API Gateway - Quick Setup"
echo "================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3.11+ required. Please install Python."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Python version: $PYTHON_VERSION"
echo ""

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "WARNING: Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    echo "Poetry installed"
    echo ""
fi

# Create virtual environment if using pip
if [ ! -d "venv" ] && ! command -v poetry &> /dev/null; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment created"
    echo ""
fi

# Install dependencies
echo "Installing dependencies..."
if command -v poetry &> /dev/null; then
    poetry install
    echo "Dependencies installed with Poetry"
else
    pip install -r requirements.txt
    echo "Dependencies installed with pip"
fi
echo ""

# Copy configuration files
echo "Setting up configuration..."
if [ ! -f "config.json" ]; then
    cp config.example.json config.json
    echo "Created config.json from example"
else
    echo "config.json already exists"
fi

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Created .env from example"
    else
        echo "WARNING: .env.example not found, creating basic .env file..."
        cat > .env << 'ENVEOF'
# Unified API Key
UNIFIED_API_KEY=your-unified-api-key-here

# Provider API Keys
GROQ_API_KEY=
DEEPSEEK_API_KEY=
GITHUB_TOKEN=
GEMINI_API_KEY=
MISTRAL_API_KEY=
OPENROUTER_API_KEY=

# Logging
LOG_LEVEL=info
CONFIG_PATH=./config.json
ENVEOF
        echo "Created basic .env file"
    fi
else
    echo ".env already exists"
fi
echo ""

# Provider selection menu
echo "=========================================="
echo "Provider Configuration"
echo "=========================================="
echo ""
echo "Select which providers you want to configure (enter numbers separated by spaces, or press Enter to skip):"
echo ""
echo "1) Groq (Free tier: 600 RPM)"
echo "2) DeepSeek (Pay-as-you-go API)"
echo "3) GitHub Copilot (Requires GitHub Pro/Education)"
echo "4) Google Gemini (Free tier available)"
echo "5) Mistral AI (Free tier or student plan)"
echo "6) OpenRouter (Free models require credits in balance)"
echo ""

read -p "Enter provider numbers (e.g., 1 3 4): " provider_choices

# Load existing .env values
if [ -f ".env" ]; then
    source .env 2>/dev/null || true
fi

# Process provider selections
SELECTED_PROVIDERS=()
for choice in $provider_choices; do
    case $choice in
        1) SELECTED_PROVIDERS+=("groq") ;;
        2) SELECTED_PROVIDERS+=("deepseek") ;;
        3) SELECTED_PROVIDERS+=("github") ;;
        4) SELECTED_PROVIDERS+=("gemini") ;;
        5) SELECTED_PROVIDERS+=("mistral") ;;
        6) SELECTED_PROVIDERS+=("openrouter") ;;
    esac
done

# Prompt for API keys for selected providers
if [ ${#SELECTED_PROVIDERS[@]} -gt 0 ]; then
    echo ""
    echo "=========================================="
    echo "API Key Configuration"
    echo "=========================================="
    echo ""
    
    for provider in "${SELECTED_PROVIDERS[@]}"; do
        case $provider in
            groq)
                current_key="${GROQ_API_KEY:-}"
                if [ -n "$current_key" ] && [ "$current_key" != "" ] && [ "$current_key" != "your_groq_key_here" ]; then
                    read -p "Groq API Key [press Enter to keep current: ${current_key:0:10}...]: " api_key
                    [ -z "$api_key" ] && api_key="$current_key"
                else
                    read -p "Groq API Key: " api_key
                fi
                if [ -n "$api_key" ]; then
                    if grep -q "^GROQ_API_KEY=" .env 2>/dev/null; then
                        sed -i.bak "s|^GROQ_API_KEY=.*|GROQ_API_KEY=$api_key|" .env && rm -f .env.bak
                    else
                        echo "GROQ_API_KEY=$api_key" >> .env
                    fi
                    echo "Groq API key saved"
                fi
                ;;
            deepseek)
                current_key="${DEEPSEEK_API_KEY:-}"
                if [ -n "$current_key" ] && [ "$current_key" != "" ] && [ "$current_key" != "your_deepseek_key_here" ]; then
                    read -p "DeepSeek API Key [press Enter to keep current: ${current_key:0:10}...]: " api_key
                    [ -z "$api_key" ] && api_key="$current_key"
                else
                    read -p "DeepSeek API Key: " api_key
                fi
                if [ -n "$api_key" ]; then
                    if grep -q "^DEEPSEEK_API_KEY=" .env 2>/dev/null; then
                        sed -i.bak "s|^DEEPSEEK_API_KEY=.*|DEEPSEEK_API_KEY=$api_key|" .env && rm -f .env.bak
                    else
                        echo "DEEPSEEK_API_KEY=$api_key" >> .env
                    fi
                    echo "DeepSeek API key saved"
                fi
                ;;
            github)
                current_key="${GITHUB_TOKEN:-}"
                if [ -n "$current_key" ] && [ "$current_key" != "" ] && [ "$current_key" != "your_github_token_here" ]; then
                    read -p "GitHub Token [press Enter to keep current: ${current_key:0:10}...]: " api_key
                    [ -z "$api_key" ] && api_key="$current_key"
                else
                    read -p "GitHub Token: " api_key
                fi
                if [ -n "$api_key" ]; then
                    if grep -q "^GITHUB_TOKEN=" .env 2>/dev/null; then
                        sed -i.bak "s|^GITHUB_TOKEN=.*|GITHUB_TOKEN=$api_key|" .env && rm -f .env.bak
                    else
                        echo "GITHUB_TOKEN=$api_key" >> .env
                    fi
                    echo "GitHub token saved"
                fi
                ;;
            gemini)
                current_key="${GEMINI_API_KEY:-}"
                if [ -n "$current_key" ] && [ "$current_key" != "" ] && [ "$current_key" != "your_gemini_key_here" ]; then
                    read -p "Google Gemini API Key [press Enter to keep current: ${current_key:0:10}...]: " api_key
                    [ -z "$api_key" ] && api_key="$current_key"
                else
                    read -p "Google Gemini API Key: " api_key
                fi
                if [ -n "$api_key" ]; then
                    if grep -q "^GEMINI_API_KEY=" .env 2>/dev/null; then
                        sed -i.bak "s|^GEMINI_API_KEY=.*|GEMINI_API_KEY=$api_key|" .env && rm -f .env.bak
                    else
                        echo "GEMINI_API_KEY=$api_key" >> .env
                    fi
                    echo "Gemini API key saved"
                fi
                ;;
            mistral)
                current_key="${MISTRAL_API_KEY:-}"
                if [ -n "$current_key" ] && [ "$current_key" != "" ] && [ "$current_key" != "your_mistral_key_here" ]; then
                    read -p "Mistral API Key [press Enter to keep current: ${current_key:0:10}...]: " api_key
                    [ -z "$api_key" ] && api_key="$current_key"
                else
                    read -p "Mistral API Key: " api_key
                fi
                if [ -n "$api_key" ]; then
                    if grep -q "^MISTRAL_API_KEY=" .env 2>/dev/null; then
                        sed -i.bak "s|^MISTRAL_API_KEY=.*|MISTRAL_API_KEY=$api_key|" .env && rm -f .env.bak
                    else
                        echo "MISTRAL_API_KEY=$api_key" >> .env
                    fi
                    echo "Mistral API key saved"
                fi
                ;;
            openrouter)
                current_key="${OPENROUTER_API_KEY:-}"
                if [ -n "$current_key" ] && [ "$current_key" != "" ] && [ "$current_key" != "your_openrouter_key_here" ]; then
                    read -p "OpenRouter API Key [press Enter to keep current: ${current_key:0:10}...]: " api_key
                    [ -z "$api_key" ] && api_key="$current_key"
                else
                    read -p "OpenRouter API Key: " api_key
                fi
                if [ -n "$api_key" ]; then
                    if grep -q "^OPENROUTER_API_KEY=" .env 2>/dev/null; then
                        sed -i.bak "s|^OPENROUTER_API_KEY=.*|OPENROUTER_API_KEY=$api_key|" .env && rm -f .env.bak
                    else
                        echo "OPENROUTER_API_KEY=$api_key" >> .env
                    fi
                    echo "OpenRouter API key saved"
                fi
                ;;
        esac
    done
    echo ""
fi

# Prompt for unified API key
echo "=========================================="
echo "Unified API Key Configuration"
echo "=========================================="
echo ""
current_unified_key="${UNIFIED_API_KEY:-}"
if [ -n "$current_unified_key" ] && [ "$current_unified_key" != "your-unified-api-key-here" ]; then
    read -p "Unified API Key [press Enter to keep current: ${current_unified_key:0:10}...]: " unified_key
    [ -z "$unified_key" ] && unified_key="$current_unified_key"
else
    read -p "Unified API Key (for client authentication): " unified_key
fi

if [ -n "$unified_key" ]; then
    # Update config.json
    if command -v python3 &> /dev/null; then
        python3 << EOF
import json
import sys

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    config['auth']['unifiedApiKey'] = '$unified_key'
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("Unified API key saved to config.json")
except Exception as e:
    print(f"Error updating config.json: {e}", file=sys.stderr)
    sys.exit(1)
EOF
    fi
    
    # Update .env
    if grep -q "^UNIFIED_API_KEY=" .env 2>/dev/null; then
        sed -i.bak "s|^UNIFIED_API_KEY=.*|UNIFIED_API_KEY=$unified_key|" .env && rm -f .env.bak
    else
        echo "UNIFIED_API_KEY=$unified_key" >> .env
    fi
    echo "Unified API key saved"
fi
echo ""

# Create directories
echo "Creating directories..."
mkdir -p logs
mkdir -p data
echo "Directories created"
echo ""

# Initialize database
echo "Initializing database..."
if command -v poetry &> /dev/null; then
    poetry run alembic upgrade head
else
    python3 -m alembic upgrade head
fi
echo "Database initialized"
echo ""

echo "Setup complete!"
echo ""
echo "IMPORTANT: Review your configuration:"
echo "  - config.json: Check provider settings and unified API key"
echo "  - .env: Verify all API keys are set correctly"
echo ""
echo "To start the gateway:"
if command -v poetry &> /dev/null; then
    echo "  poetry run uvicorn app.main:app --host 0.0.0.0 --port 3000"
else
    echo "  source venv/bin/activate"
    echo "  python3 -m uvicorn app.main:app --host 0.0.0.0 --port 3000"
fi
echo ""
echo "For detailed instructions, see QUICKSTART.md or SETUP.md"
echo ""
