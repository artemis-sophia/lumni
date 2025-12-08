#!/usr/bin/env python3
"""
Create Jupyter Notebook Demonstration
Generates a comprehensive .ipynb file demonstrating all CLI features
"""

import nbformat as nbf
from pathlib import Path

# Project root path (update this to your project path)
PROJECT_ROOT = Path(__file__).parent.parent.absolute()


def cli_command(cmd: str) -> str:
    """Wrap CLI command with directory change"""
    # Use shell cd command that works with ! commands
    project_root_str = str(PROJECT_ROOT)
    return f'!cd "{project_root_str}" && {cmd}'


def create_demo_notebook():
    """Create comprehensive CLI demonstration notebook"""
    
    # Create new notebook
    nb = nbf.v4.new_notebook()
    
    # Title and Introduction
    nb.cells.append(nbf.v4.new_markdown_cell("""# Lumni CLI - Complete Demonstration

This notebook demonstrates all features and use cases of the Lumni Management CLI.

## Overview

The Lumni CLI provides comprehensive management tools for:
- **Usage Monitoring**: Track API usage, costs, and statistics
- **Rate Limits**: View and manage rate limit configurations
- **Provider Management**: Enable/disable providers, set priorities
- **Model Management**: Browse and search available models
- **Monitoring**: Real-time monitoring and alerting

## Prerequisites

Make sure you have:
1. Installed dependencies: `poetry install`
2. Configured API keys in `.env`
3. Initialized database: `alembic upgrade head`
"""))
    
    # Setup cell - Change to project directory and set Python path
    nb.cells.append(nbf.v4.new_markdown_cell("""## Setup

The following cell sets up the environment to run CLI commands from the project root directory.
"""))
    
    nb.cells.append(nbf.v4.new_code_cell("""import os
import sys
from pathlib import Path

# Get the project root directory (where this notebook is located)
project_root = Path().resolve()
if 'docs' in str(project_root):
    project_root = project_root.parent

# Change to project root directory
os.chdir(project_root)

# Add project root to Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"Working directory: {os.getcwd()}")
print(f"Project root: {project_root}")
print(f"Python path includes project root: {str(project_root) in sys.path}")
"""))
    
    # Section 1: Usage Monitoring
    nb.cells.append(nbf.v4.new_markdown_cell("""## 1. Usage Monitoring

Track API usage, costs, and statistics across all providers and models.
"""))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 1.1 Overall Usage Statistics

View overall usage across all providers for the last 24 hours:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main usage show --hours 24')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 1.2 Provider-Specific Usage

View usage for a specific provider (e.g., Groq):
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main usage provider groq --hours 24')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 1.3 Model-Specific Usage

View usage for a specific model:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main usage model groq llama-3.1-8b-instant --hours 24')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 1.4 Cost Breakdown

View cost breakdown across all providers:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main usage cost --hours 24')))
    
    # Section 2: Rate Limits
    nb.cells.append(nbf.v4.new_markdown_cell("""## 2. Rate Limit Management

View and understand rate limit configurations for all providers and models.
"""))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 2.1 List All Rate Limits

View all rate limit configurations:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main rates list')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 2.2 Provider Rate Limits

View rate limits for a specific provider:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main rates provider groq')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 2.3 Model Rate Limits

View rate limits for a specific model:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main rates model groq llama-3.1-8b-instant')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 2.4 Remaining Rate Limits

View remaining rate limits based on current usage:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main rates remaining --hours 1')))
    
    # Section 3: Provider Management
    nb.cells.append(nbf.v4.new_markdown_cell("""## 3. Provider Management

Manage provider configurations, enable/disable providers, and set priorities.
"""))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 3.1 List All Providers

View all providers with their status:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main providers list')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 3.2 Provider Status

View detailed status for a specific provider:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main providers status groq')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 3.3 Enable/Disable Providers

Enable a provider:
```bash
poetry run python -m app.cli.main providers enable groq
```

Disable a provider:
```bash
poetry run python -m app.cli.main providers disable mistral
```
"""))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 3.4 Set Provider Priority

Set provider priority (lower number = higher priority):
```bash
poetry run python -m app.cli.main providers priority groq 1
```
"""))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 3.5 Health Checks

Run health checks on all providers:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main providers health')))
    
    # Section 4: Model Management
    nb.cells.append(nbf.v4.new_markdown_cell("""## 4. Model Management

Browse, search, and explore available models across all providers.
"""))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 4.1 List All Models

View all available models:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main models list')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 4.2 List Free Models Only

View only free models (no credits required):
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main models list --free-only')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 4.3 Filter by Provider

List models for a specific provider:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main models provider groq')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 4.4 Filter by Category

List models by category (fast or powerful):
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main models list --category fast')))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main models list --category powerful')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 4.5 Model Details

View detailed information for a specific model:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main models show groq llama-3.1-8b-instant')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 4.6 Search Models

Search for models by name:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main models search llama')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 4.7 Models by Category

View models organized by category (fast vs powerful):
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main models categorize')))
    
    # Section 5: Monitoring
    nb.cells.append(nbf.v4.new_markdown_cell("""## 5. Monitoring

Real-time monitoring, error tracking, and performance metrics.
"""))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 5.1 Recent Errors

View recent errors across all providers:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main monitor errors --hours 24')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 5.2 Performance Metrics

View performance metrics for all providers:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main monitor performance --hours 24')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 5.3 Active Alerts

View active alerts and warnings:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main monitor alerts')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 5.4 Live Monitoring

Start live monitoring dashboard (runs continuously):
```bash
poetry run python -m app.cli.main monitor live --interval 5
```

Note: This command runs continuously and updates every 5 seconds. Press Ctrl+C to stop.
"""))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 5.5 Watch Mode

Watch mode with auto-refresh:
```bash
poetry run python -m app.cli.main monitor watch --interval 5
```

Note: This command runs continuously and refreshes every 5 seconds. Press Ctrl+C to stop.
"""))
    
    # Section 6: Common Use Cases
    nb.cells.append(nbf.v4.new_markdown_cell("""## 6. Common Use Cases

Practical workflows and examples.
"""))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 6.1 Quick Health Check

Check the status of all providers and view recent usage:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main providers list && echo "---" && poetry run python -m app.cli.main usage show --hours 1')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 6.2 Find Free Models

Find all free models available:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main models list --free-only')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 6.3 Check Rate Limits

Check current rate limits and remaining capacity:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main rates remaining --hours 1')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 6.4 Cost Analysis

Analyze costs for the last 24 hours:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main usage cost --hours 24')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 6.5 Provider Comparison

Compare usage across multiple providers:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main usage provider groq --hours 24 && echo "---" && poetry run python -m app.cli.main usage provider deepseek --hours 24')))
    
    # Section 7: Advanced Usage
    nb.cells.append(nbf.v4.new_markdown_cell("""## 7. Advanced Usage

Advanced workflows and tips.
"""))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 7.1 Combining Filters

Combine multiple filters to find specific models:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main models list --provider groq --category fast')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 7.2 Time Window Analysis

Analyze usage over different time windows:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main usage show --hours 1 && echo "---Last Hour---" && poetry run python -m app.cli.main usage show --hours 24 && echo "---Last 24 Hours---"')))
    
    nb.cells.append(nbf.v4.new_markdown_cell("""### 7.3 Model Discovery

Discover models by searching for capabilities:
"""))
    
    nb.cells.append(nbf.v4.new_code_cell(cli_command('poetry run python -m app.cli.main models search gemini && echo "---" && poetry run python -m app.cli.main models search claude')))
    
    # Section 8: Tips and Best Practices
    nb.cells.append(nbf.v4.new_markdown_cell("""## 8. Tips and Best Practices

### Getting Help

All commands support `--help` flag:
```bash
poetry run python -m app.cli.main --help
poetry run python -m app.cli.main usage --help
poetry run python -m app.cli.main models --help
```

### Command Shortcuts

Many commands support short flags:
- `-h` for `--hours`
- `-p` for `--provider`
- `-c` for `--category`
- `-i` for `--interval`
- `-l` for `--limit`

### Output Formatting

The CLI uses Rich library for beautiful terminal output:
- Color-coded status indicators
- Formatted tables
- Progress indicators
- Markdown-style formatting

### Performance Tips

1. **Use time windows wisely**: Smaller time windows (1-6 hours) are faster
2. **Filter early**: Use provider/model filters to reduce data
3. **Monitor in background**: Use `monitor live` for continuous monitoring
4. **Cache results**: Some commands cache results for faster subsequent runs

### Integration with Scripts

You can use the CLI in shell scripts:
```bash
#!/bin/bash
# Check if any providers are disabled
DISABLED=$(poetry run python -m app.cli.main providers list | grep "✗" | wc -l)
if [ $DISABLED -gt 0 ]; then
    echo "Warning: $DISABLED providers are disabled"
fi
```

### Error Handling

The CLI provides clear error messages:
- Missing configuration files
- Invalid provider/model names
- Database connection issues
- API key problems

All errors include suggestions for resolution.
"""))
    
    # Metadata
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11"
        }
    }
    
    # Save notebook
    output_path = Path("docs/cli_demonstration.ipynb")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    
    print(f"✅ Created demonstration notebook: {output_path}")
    print(f"   Total cells: {len(nb.cells)}")
    print(f"   - Markdown cells: {sum(1 for c in nb.cells if c.cell_type == 'markdown')}")
    print(f"   - Code cells: {sum(1 for c in nb.cells if c.cell_type == 'code')}")


if __name__ == "__main__":
    create_demo_notebook()

