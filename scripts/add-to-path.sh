#!/bin/bash

# Script to add Lumni CLI to PATH
# This script helps you add the lumni command to your PATH

set -e

echo "Lumni CLI - Add to PATH"
echo "======================="
echo ""

# Detect shell
SHELL_NAME=$(basename "$SHELL")
SHELL_RC=""

if [ "$SHELL_NAME" = "bash" ]; then
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        SHELL_RC="$HOME/.bash_profile"
    fi
elif [ "$SHELL_NAME" = "zsh" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ "$SHELL_NAME" = "fish" ]; then
    SHELL_RC="$HOME/.config/fish/config.fish"
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "ERROR: Poetry is not installed. Please install Poetry first."
    exit 1
fi

# Get Poetry environment path
POETRY_ENV=$(poetry env info --path 2>/dev/null || echo "")

if [ -z "$POETRY_ENV" ]; then
    echo "ERROR: Poetry environment not found. Run 'poetry install' first."
    exit 1
fi

BIN_PATH="$POETRY_ENV/bin"
EXPORT_LINE="export PATH=\"$BIN_PATH:\$PATH\""

echo "Poetry environment found: $POETRY_ENV"
echo "Binary path: $BIN_PATH"
echo ""

# Check if already in PATH
if echo "$PATH" | grep -q "$BIN_PATH"; then
    echo "Lumni CLI is already in your PATH!"
    echo ""
    echo "Verify with: lumni --help"
    exit 0
fi

# Add to PATH
if [ -n "$SHELL_RC" ]; then
    echo "Detected shell: $SHELL_NAME"
    echo "Config file: $SHELL_RC"
    echo ""
    
    # Check if already added
    if grep -q "$BIN_PATH" "$SHELL_RC" 2>/dev/null; then
        echo "PATH entry already exists in $SHELL_RC"
    else
        echo "Adding to $SHELL_RC..."
        echo "" >> "$SHELL_RC"
        echo "# Lumni CLI" >> "$SHELL_RC"
        echo "$EXPORT_LINE" >> "$SHELL_RC"
        echo "Added to $SHELL_RC"
    fi
    
    echo ""
    echo "To use immediately, run:"
    echo "  source $SHELL_RC"
    echo ""
    echo "Or open a new terminal."
    echo ""
    echo "Then verify with: lumni --help"
else
    echo "Could not detect shell configuration file."
    echo ""
    echo "Please add this line to your shell configuration file:"
    echo "  $EXPORT_LINE"
    echo ""
    echo "Common locations:"
    echo "  - Bash: ~/.bashrc or ~/.bash_profile"
    echo "  - Zsh: ~/.zshrc"
    echo "  - Fish: ~/.config/fish/config.fish"
fi

