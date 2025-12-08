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
- **DeepSeek**: Free tier available
- **OpenRouter**: Free tier models (requires account credits)

### Student Credit Programs
- Together AI ($200-600 research credits)
- Fireworks AI ($500 student credits)
- Azure OpenAI ($100/year via GitHub Student Pack)
- AWS Bedrock (via AWS Educate)
- Vertex AI (GCP free trial)
- Mistral AI (student plan)

See [FREE_MODELS_CATALOGUE.md](./docs/FREE_MODELS_CATALOGUE.md) for a complete list of free models.

## Quick Start

### One-Command Setup

**Linux/Mac:**
```bash
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

### Manual Setup

1. **Install Dependencies**
   ```bash
   # Using Poetry (recommended)
   poetry install
   
   # Or using pip
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure**
   ```bash
   cp config.example.json config.json
   cp .env.example .env
   ```
   Edit `.env` with your API keys and `config.json` with your unified API key.

3. **Initialize Database**
   ```bash
   poetry run alembic upgrade head
   # Or: python3 -m alembic upgrade head
   ```

4. **Start the Gateway**
   ```bash
   poetry run uvicorn app.main:app --host 0.0.0.0 --port 3000
   # Or: python3 -m uvicorn app.main:app --host 0.0.0.0 --port 3000
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

```bash
# Show usage statistics
poetry run lumni usage

# List providers
poetry run lumni providers list

# Monitor in real-time
poetry run lumni monitor watch

# Interactive settings
poetry run lumni settings menu
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
- Poetry (recommended) or pip
- SQLite (default) or PostgreSQL
- API keys for at least one provider

## Installation

### Using Poetry (Recommended)

```bash
poetry install
```

### Using pip

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

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
poetry install --with dev

# Run tests
poetry run pytest

# Format code
poetry run black app/
poetry run ruff check app/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LiteLLM](https://github.com/BerriAI/litellm) - Unified LLM API
- [Portkey AI](https://portkey.ai/) - Observability and monitoring
- [Poetry](https://python-poetry.org/) - Dependency management
