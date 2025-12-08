# Installation Guide - Lumni CLI

This guide explains how to install Lumni and make the CLI command available in your PATH.

## Installation Methods

### Method 1: Poetry Installation (Recommended)

Poetry will automatically create the `lumni` command in the virtual environment.

#### Step 1: Install Dependencies

```bash
poetry install
```

#### Step 2: Add to PATH

After installation, add the Poetry virtual environment's bin directory to your PATH.

**Linux/macOS:**

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export PATH="$HOME/.local/share/pypoetry/venv/bin:$PATH"

# Or if using project-local venv:
export PATH="$(poetry env info --path)/bin:$PATH"
```

**Windows (PowerShell):**

```powershell
# Add to your PowerShell profile
$env:Path += ";$env:USERPROFILE\.local\share\pypoetry\venv\Scripts"
```

#### Step 3: Verify Installation

```bash
lumni --help
```

### Method 2: Direct Python Installation

If you prefer not to use Poetry:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install package
pip install -e .

# Add to PATH (Linux/macOS)
export PATH="$(pwd)/venv/bin:$PATH"

# Verify
lumni --help
```

### Method 3: Global Installation (Advanced)

For system-wide installation:

```bash
# Using Poetry
poetry build
pip install dist/lumni-*.whl

# Or using pip directly
pip install -e .
```

**Note:** Global installation may require `sudo` on Linux/macOS.

## Post-Installation Setup

After installation, run the setup script to configure your API keys:

```bash
./setup.sh
```

Or on Windows:

```cmd
setup.bat
```

## Verifying Installation

Check that the CLI is working:

```bash
lumni version
lumni --help
```

## Troubleshooting

### Command Not Found

If `lumni` command is not found:

1. **Check Poetry environment:**
   ```bash
   poetry env info --path
   ```

2. **Verify script exists:**
   ```bash
   ls $(poetry env info --path)/bin/lumni
   ```

3. **Add to PATH manually:**
   ```bash
   export PATH="$(poetry env info --path)/bin:$PATH"
   ```

### Using Poetry Run (Fallback)

If you can't add to PATH, you can always use:

```bash
poetry run lumni --help
```

## Uninstallation

To remove Lumni:

```bash
# If installed with Poetry
poetry env remove python3

# If installed globally
pip uninstall lumni
```

