# Lumni - Unified Student API Gateway

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A plug-and-play API gateway system optimized for teaching AI engineering, designed to maximize free API usage through smart fallback and limit monitoring.

## Features

- **Unified API Interface**: Single API key access to multiple student API providers
- **Smart Fallback**: Automatic provider switching when limits are hit or providers fail
- **Limit Monitoring**: Real-time tracking of API usage and remaining quotas
- **Persistent Operation**: Reliable state management and error recovery
- **Student-Optimized**: Pre-configured for free tier providers
- **Comprehensive CLI**: Full management interface with interactive settings
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Supported Providers

### Free Tier Providers (No Credits Required)
- **Google Gemini**: Multiple models via API key
- **GitHub Models API**: Access via GitHub Pro/Education
- **Groq**: 600 RPM free tier
- **DeepSeek**: Pay-as-you-go API (competitive pricing)
- **OpenRouter**: Free tier models (requires account credits)

### Student Credit Programs
- **Together AI**: $200-600 research credits for students
- **Fireworks AI**: $500 student credits available
- **Azure OpenAI**: $100/year via GitHub Student Pack
- **AWS Bedrock**: Access via AWS Educate program
- **Vertex AI**: GCP free trial for students
- **Mistral AI**: Student plan with special pricing

See [FREE_MODELS_CATALOGUE.md](./docs/FREE_MODELS_CATALOGUE.md) for a complete list of free models.

## Quick Start

### One-Command Setup

**Linux/Mac:**
```bash
./setup.sh
```

The setup script will:
- Install all dependencies
- Configure providers interactively
- Install the `lumni` CLI command to your PATH
- Set up the database

After setup, restart your terminal or run `source ~/.bashrc` (or `source ~/.zshrc`) to use the `lumni` command.

**Windows:**
```cmd
setup.bat
```

### Manual Setup

1. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install Package**
   ```bash
   # Install in editable mode (recommended - includes CLI command)
   pip install -e .
   
   # Or install dependencies only
   pip install -r requirements.txt
   ```

3. **Configure**
   ```bash
   cp config.example.json config.json
   cp .env.example .env
   ```
   Edit `.env` with your API keys and `config.json` with your unified API key.

4. **Initialize Database**
   ```bash
   alembic upgrade head
   ```

5. **Start the Gateway**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 3000
   ```

6. **Use the CLI** (after restarting terminal or running `source ~/.bashrc` / `source ~/.zshrc`)
   ```bash
   lumni --help
   lumni settings menu
   ```

For detailed instructions, see [QUICKSTART.md](./QUICKSTART.md).

## Usage

### API

The gateway exposes a unified REST API at `http://localhost:3000/api/v1`

```bash
curl -X POST http://localhost:3000/api/v1/chat \
  -H "Authorization: Bearer YOUR_UNIFIED_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### CLI Management

After installation, the `lumni` command is available in your PATH:

```bash
# Show usage statistics
lumni usage

# List providers
lumni providers list

# Monitor in real-time
lumni monitor watch

# Interactive settings
lumni settings menu

# Generate unified API key
lumni settings unified-key
```

See [docs/cli_demonstration.ipynb](./docs/cli_demonstration.ipynb) for a complete CLI guide.

## Architecture

- `app/main.py` - FastAPI application entry point
- `app/api/v1/` - API routes and schemas
- `app/core/` - Core integrations (LiteLLM, Portkey)
- `app/models/` - Task classification and model selection
- `app/monitoring/` - Usage tracking and metrics
- `app/storage/` - Database models and repositories
- `app/config/` - Configuration management
- `app/cli/` - Command-line interface for management

For detailed architecture information, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## Requirements

- Python 3.11+
- pip (Python package manager)
- SQLite (default) or PostgreSQL
- API keys for at least one provider

## Installation

### Recommended: Editable Install (includes CLI command)

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

This installs the package in editable mode and creates the `lumni` CLI command.

### Alternative: Install Dependencies Only

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Note: This method doesn't install the CLI command. Use `python -m app.cli.main` instead.

## Configuration

1. Copy `config.example.json` to `config.json`
2. Copy `.env.example` to `.env`
3. Add your provider API keys to `.env`
4. Set your unified API key in `config.json`

See [SETUP.md](./SETUP.md) for detailed configuration options.

## Documentation

- [QUICKSTART.md](./QUICKSTART.md) - Get started in 5 minutes
- [SETUP.md](./SETUP.md) - Detailed setup and configuration
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture overview
- [FREE_MODELS_CATALOGUE.md](./docs/FREE_MODELS_CATALOGUE.md) - Complete list of free models
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues and solutions

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"
# Or: pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black app/
ruff check app/
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on how to contribute.

- Read our [Code of Conduct](./CODE_OF_CONDUCT.md)
- Check out [existing issues](https://github.com/artemis-sophia/lumni/issues)
- Follow our [development workflow](./CONTRIBUTING.md#development-workflow)

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LiteLLM](https://github.com/BerriAI/litellm) - Unified LLM API
- [Portkey AI](https://portkey.ai/) - Observability and monitoring
