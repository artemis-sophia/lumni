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

# Install dependencies and package
echo "Installing dependencies..."
if command -v poetry &> /dev/null; then
    poetry install
    echo "Dependencies installed with Poetry"
    
    # Get Poetry's bin directory
    POETRY_BIN_DIR=$(poetry env info --path 2>/dev/null | head -1)
    if [ -z "$POETRY_BIN_DIR" ]; then
        POETRY_BIN_DIR="$HOME/.local/share/pypoetry/venv/bin"
    else
        POETRY_BIN_DIR="$POETRY_BIN_DIR/bin"
    fi
    
    # Create local bin directory if it doesn't exist
    LOCAL_BIN_DIR="$HOME/.local/bin"
    mkdir -p "$LOCAL_BIN_DIR"
    
    # Create lumni wrapper script
    cat > "$LOCAL_BIN_DIR/lumni" << 'LUMNI_EOF'
#!/bin/bash
# Lumni CLI wrapper script
# This script ensures lumni runs from the correct Poetry environment

# Try to find Poetry environment
if command -v poetry &> /dev/null; then
    # Get the project directory (where this script was installed from)
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Try to find project root by looking for pyproject.toml
    PROJECT_ROOT="$SCRIPT_DIR"
    while [ ! -f "$PROJECT_ROOT/pyproject.toml" ] && [ "$PROJECT_ROOT" != "/" ]; do
        PROJECT_ROOT="$(dirname "$PROJECT_ROOT")"
    done
    
    if [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
        cd "$PROJECT_ROOT" || exit 1
        exec poetry run lumni "$@"
    else
        # Fallback: try to run from current directory
        exec poetry run lumni "$@"
    fi
else
    echo "ERROR: Poetry not found. Please install Poetry or use 'poetry run lumni'"
    exit 1
fi
LUMNI_EOF
    
    chmod +x "$LOCAL_BIN_DIR/lumni"
    echo "Created lumni CLI wrapper at $LOCAL_BIN_DIR/lumni"
    
    # Add to PATH if not already there
    SHELL_RC=""
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"
    fi
    
    if [ -n "$SHELL_RC" ] && [ -f "$SHELL_RC" ]; then
        if ! grep -q "$LOCAL_BIN_DIR" "$SHELL_RC" 2>/dev/null; then
            echo "" >> "$SHELL_RC"
            echo "# Lumni CLI - Added by setup script" >> "$SHELL_RC"
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
            echo "Added $LOCAL_BIN_DIR to PATH in $SHELL_RC"
            echo "NOTE: Run 'source $SHELL_RC' or restart your terminal to use 'lumni' command"
        else
            echo "PATH already includes $LOCAL_BIN_DIR"
        fi
    fi
    
    # Also add to current session
    export PATH="$LOCAL_BIN_DIR:$PATH"
    
else
    pip install -r requirements.txt
    echo "Dependencies installed with pip"
    echo "NOTE: For pip installation, use 'python3 -m app.cli.main' instead of 'lumni'"
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

# Load existing .env values to check what's already set
if [ -f ".env" ]; then
    # Source .env file safely (ignore errors for missing vars)
    set -a
    source .env 2>/dev/null || true
    set +a
fi

# Function to check if an API key is set and valid
check_api_key() {
    local key_name=$1
    local key_value=$(eval echo \$$key_name)
    
    if [ -n "$key_value" ] && [ "$key_value" != "" ] && \
       [ "$key_value" != "your-${key_name,,}-key-here" ] && \
       [ "$key_value" != "your_${key_name,,}_key_here" ] && \
       [ "$key_value" != "your-${key_name,,}" ] && \
       [ "$key_value" != "your_${key_name,,}" ]; then
        return 0  # Key exists and is valid
    else
        return 1  # Key is missing or placeholder
    fi
}

# Check which providers already have API keys configured
AVAILABLE_PROVIDERS=()
PROVIDER_STATUS=()

if check_api_key "GROQ_API_KEY"; then
    AVAILABLE_PROVIDERS+=("groq")
    PROVIDER_STATUS+=("groq:configured")
    echo "Groq: API key already configured"
else
    PROVIDER_STATUS+=("groq:missing")
fi

if check_api_key "DEEPSEEK_API_KEY"; then
    AVAILABLE_PROVIDERS+=("deepseek")
    PROVIDER_STATUS+=("deepseek:configured")
    echo "DeepSeek: API key already configured"
else
    PROVIDER_STATUS+=("deepseek:missing")
fi

if check_api_key "GITHUB_TOKEN"; then
    AVAILABLE_PROVIDERS+=("github")
    PROVIDER_STATUS+=("github:configured")
    echo "GitHub Copilot: API key already configured"
else
    PROVIDER_STATUS+=("github:missing")
fi

if check_api_key "GEMINI_API_KEY"; then
    AVAILABLE_PROVIDERS+=("gemini")
    PROVIDER_STATUS+=("gemini:configured")
    echo "Google Gemini: API key already configured"
else
    PROVIDER_STATUS+=("gemini:missing")
fi

if check_api_key "MISTRAL_API_KEY"; then
    AVAILABLE_PROVIDERS+=("mistral")
    PROVIDER_STATUS+=("mistral:configured")
    echo "Mistral AI: API key already configured"
else
    PROVIDER_STATUS+=("mistral:missing")
fi

if check_api_key "OPENROUTER_API_KEY"; then
    AVAILABLE_PROVIDERS+=("openrouter")
    PROVIDER_STATUS+=("openrouter:configured")
    echo "OpenRouter: API key already configured"
else
    PROVIDER_STATUS+=("openrouter:missing")
fi

echo ""

# Provider selection menu - only show providers that need configuration
NEEDS_CONFIG=()
for status in "${PROVIDER_STATUS[@]}"; do
    provider=$(echo "$status" | cut -d':' -f1)
    state=$(echo "$status" | cut -d':' -f2)
    if [ "$state" = "missing" ]; then
        NEEDS_CONFIG+=("$provider")
    fi
done

if [ ${#NEEDS_CONFIG[@]} -eq 0 ]; then
    echo "All providers are already configured. Skipping provider setup."
    echo ""
else
    echo "=========================================="
    echo "Provider Configuration"
    echo "=========================================="
    echo ""
    echo "The following providers need API keys configured:"
    echo ""
    
    provider_num=1
    provider_map=()
    for provider in "${NEEDS_CONFIG[@]}"; do
        case $provider in
            groq)
                echo "$provider_num) Groq (Free tier: 600 RPM)"
                provider_map+=("groq")
                ;;
            deepseek)
                echo "$provider_num) DeepSeek (Pay-as-you-go API)"
                provider_map+=("deepseek")
                ;;
            github)
                echo "$provider_num) GitHub Copilot (Requires GitHub Pro/Education)"
                provider_map+=("github")
                ;;
            gemini)
                echo "$provider_num) Google Gemini (Free tier available)"
                provider_map+=("gemini")
                ;;
            mistral)
                echo "$provider_num) Mistral AI (Free tier or student plan)"
                provider_map+=("mistral")
                ;;
            openrouter)
                echo "$provider_num) OpenRouter (Free models require credits in balance)"
                provider_map+=("openrouter")
                ;;
        esac
        ((provider_num++))
    done
    echo ""
    echo "Enter provider numbers separated by spaces to configure (or press Enter to skip):"
    read -p "> " provider_choices
    
    # Process provider selections
    SELECTED_PROVIDERS=()
    if [ -n "$provider_choices" ]; then
        for choice in $provider_choices; do
            idx=$((choice - 1))
            if [ $idx -ge 0 ] && [ $idx -lt ${#provider_map[@]} ]; then
                SELECTED_PROVIDERS+=("${provider_map[$idx]}")
            fi
        done
    fi
    
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
                    read -p "Groq API Key: " api_key
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
                    read -p "DeepSeek API Key: " api_key
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
                    read -p "GitHub Token: " api_key
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
                    read -p "Google Gemini API Key: " api_key
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
                    read -p "Mistral API Key: " api_key
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
                    read -p "OpenRouter API Key: " api_key
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
fi

# Check and prompt for unified API key
echo "=========================================="
echo "Unified API Key Configuration"
echo "=========================================="
echo ""

# Reload .env to get updated values
if [ -f ".env" ]; then
    set -a
    source .env 2>/dev/null || true
    set +a
fi

current_unified_key="${UNIFIED_API_KEY:-}"

# Check if unified API key is already set and valid
if check_api_key "UNIFIED_API_KEY"; then
    echo "Unified API key is already configured: ${current_unified_key:0:10}..."
    read -p "Do you want to update it? (y/N): " update_choice
    if [ "$update_choice" != "y" ] && [ "$update_choice" != "Y" ]; then
        unified_key="$current_unified_key"
        echo "Keeping existing unified API key"
    else
        read -p "Unified API Key (for client authentication): " unified_key
    fi
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
echo "Configured providers:"
for status in "${PROVIDER_STATUS[@]}"; do
    provider=$(echo "$status" | cut -d':' -f1)
    state=$(echo "$status" | cut -d':' -f2)
    if [ "$state" = "configured" ]; then
        echo "  - $provider: configured"
    fi
done
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
