# Quick Start Guide

Get Lumni up and running in 5 minutes!

## One-Command Setup (Recommended)

### Linux/Mac

```bash
./setup.sh
```

### Windows

```cmd
setup.bat
```

This will automatically:
- Check Python version
- Install dependencies (Poetry or pip)
- Create configuration files
- Initialize database
- Set up directories

**After setup completes**, edit `config.json` and `.env` with your API keys, then start the gateway.

## Manual Setup

### Step 1: Install Dependencies

**Linux/Mac:**
```bash
# Using Poetry (recommended)
poetry install

# Or using pip
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```cmd
REM Using Poetry (recommended)
poetry install

REM Or using pip
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure

**Linux/Mac:**
```bash
cp config.example.json config.json
cp .env.example .env
```

**Windows:**
```cmd
copy config.example.json config.json
copy .env.example .env
```

Then edit both files:
- **`.env`**: Add your provider API keys (GROQ_API_KEY, DEEPSEEK_API_KEY, etc.)
- **`config.json`**: Set your `unifiedApiKey` in the `auth` section

### Step 3: Initialize Database

**Linux/Mac:**
```bash
# With Poetry
poetry run alembic upgrade head

# With pip/venv
python3 -m alembic upgrade head
```

**Windows:**
```cmd
REM With Poetry
poetry run alembic upgrade head

REM With pip/venv
python -m alembic upgrade head
```

### Step 4: Start the Gateway

**Linux/Mac:**
```bash
# With Poetry
poetry run uvicorn app.main:app --host 0.0.0.0 --port 3000

# With pip/venv
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 3000
```

**Windows:**
```cmd
REM With Poetry
poetry run uvicorn app.main:app --host 0.0.0.0 --port 3000

REM With pip/venv
python -m uvicorn app.main:app --host 0.0.0.0 --port 3000
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:3000
```

## Test It

```bash
# Health check
curl http://localhost:3000/health

# Make a request (replace YOUR_KEY with your unified API key)
curl -X POST http://localhost:3000/api/v1/chat \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

**Windows PowerShell:**
```powershell
# Health check
Invoke-WebRequest -Uri http://localhost:3000/health

# Make a request
$headers = @{
    "Authorization" = "Bearer YOUR_KEY"
    "Content-Type" = "application/json"
}
$body = @{
    messages = @(@{role="user"; content="Hello!"})
} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:3000/api/v1/chat -Method POST -Headers $headers -Body $body
```

## That's It! 🎉

Your gateway is now running. The system will automatically:
- Try providers in priority order
- Fall back to backup providers if one fails
- Track usage and rate limits
- Monitor provider health

## Next Steps

- Add more providers for better redundancy
- Set up monitoring alerts
- Read `SETUP.md` for advanced configuration
- Use the CLI: `poetry run lumni --help` (or `python -m app.cli.main --help`)

## Troubleshooting

**Port already in use?**
- Change port in `config.json`: `"port": 3001`

**Providers failing?**
- Check API keys in `.env`
- Verify provider is enabled in `config.json`
- Check logs in `logs/combined.log`

**Python not found?**
- Ensure Python 3.11+ is installed
- On Windows, add Python to PATH during installation

**Poetry not found?**
- Install from https://python-poetry.org/docs/#installation
- Or use pip/venv method instead

**Need help?**
- See `SETUP.md` for detailed instructions
- Check `ARCHITECTURE.md` for system overview
- Check `TROUBLESHOOTING.md` for common issues
