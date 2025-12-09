"""
Provider Management Commands
CLI commands for managing providers
"""

from typing import Optional
import typer
import json
from pathlib import Path
from rich.table import Table
from rich.console import Console
from rich.panel import Panel

from app.cli.utils import (
    create_table,
    print_error,
    print_success,
    print_warning,
    get_status_color,
    console,
    should_output_json,
    output_json,
    validate_priority,
)
from app.config import load_config

app = typer.Typer(name="providers", help="Provider management commands")


def get_config_path() -> Path:
    """Get path to config.json"""
    return Path("config.json")


@app.command("list", "ls")
def list():
    """List all providers with their status
    
    Examples:
        lumni providers list              # List all providers
        lumni providers list --json      # Output as JSON
    """
    try:
        config = load_config()
        
        # Build data structure
        providers_data = []
        for provider_name, provider_config in config.providers.items():
            providers_data.append({
                "provider": provider_name,
                "enabled": provider_config.enabled,
                "priority": provider_config.priority,
                "base_url": provider_config.base_url or None,
            })
        
        # Output JSON if requested
        if should_output_json():
            output_json({"providers": providers_data})
            return
        
        # Otherwise output as table
        table = create_table("Providers", ["Provider", "Enabled", "Priority", "Base URL"])
        
        for provider_data in providers_data:
            enabled = "YES" if provider_data["enabled"] else "NO"
            enabled_markup = f"[green]{enabled}[/green]" if provider_data["enabled"] else f"[red]{enabled}[/red]"
            table.add_row(
                provider_data["provider"],
                enabled_markup,
                str(provider_data["priority"]),
                provider_data["base_url"] or "N/A"
            )
        
        console.print(table)
    except Exception as e:
        print_error(f"Failed to list providers: {str(e)}")
        raise typer.Exit(1)


@app.command("status", "info")
def status(
    provider_name: str = typer.Argument(..., help="Provider name"),
):
    """Show detailed status for a provider
    
    Examples:
        lumni providers status openai     # Show status for OpenAI
        lumni providers status openai --json  # Output as JSON
    """
    try:
        config = load_config()
        
        if provider_name not in config.providers:
            print_error(
                f"Provider '{provider_name}' not found",
                suggestion="Use 'lumni providers list' to see available providers"
            )
            raise typer.Exit(1)
        
        provider_config = config.providers[provider_name]
        
        # Build data structure
        status_data = {
            "provider": provider_name,
            "enabled": provider_config.enabled,
            "priority": provider_config.priority,
            "base_url": provider_config.base_url or None,
        }
        
        if provider_config.rate_limit:
            status_data["rate_limits"] = {
                "requests_per_minute": provider_config.rate_limit.requests_per_minute,
                "requests_per_day": provider_config.rate_limit.requests_per_day,
            }
        
        # Output JSON if requested
        if should_output_json():
            output_json(status_data)
            return
        
        # Otherwise output as table
        table = create_table(f"Status for {provider_name}", ["Setting", "Value"])
        table.add_row("Enabled", "Yes" if provider_config.enabled else "No")
        table.add_row("Priority", str(provider_config.priority))
        table.add_row("Base URL", provider_config.base_url or "N/A")
        
        if provider_config.rate_limit:
            table.add_row("RPM Limit", str(provider_config.rate_limit.requests_per_minute))
            table.add_row("RPD Limit", str(provider_config.rate_limit.requests_per_day))
        
        console.print(table)
    except Exception as e:
        print_error(f"Failed to get provider status: {str(e)}")
        raise typer.Exit(1)


@app.command()
def enable(
    provider_name: str = typer.Argument(..., help="Provider name"),
):
    """Enable a provider"""
    try:
        config_path = get_config_path()
        
        if not config_path.exists():
            print_error(
                "config.json not found",
                suggestion="Run 'lumni settings menu' to create configuration"
            )
            raise typer.Exit(1)
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if provider_name not in config.get("providers", {}):
            print_error(f"Provider '{provider_name}' not found")
            raise typer.Exit(1)
        
        config["providers"][provider_name]["enabled"] = True
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print_success(f"Provider '{provider_name}' enabled")
    except Exception as e:
        print_error(f"Failed to enable provider: {str(e)}")
        raise typer.Exit(1)


@app.command()
def disable(
    provider_name: str = typer.Argument(..., help="Provider name"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done without making changes"),
):
    """Disable a provider
    
    Examples:
        lumni providers disable openai        # Disable OpenAI provider
        lumni providers disable openai --dry-run  # Preview changes without applying
    """
    try:
        config_path = get_config_path()
        
        if not config_path.exists():
            print_error(
                "config.json not found",
                suggestion="Run 'lumni settings menu' to create configuration"
            )
            raise typer.Exit(1)
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if provider_name not in config.get("providers", {}):
            print_error(f"Provider '{provider_name}' not found")
            raise typer.Exit(1)
        
        current_status = config["providers"][provider_name].get("enabled", False)
        
        if dry_run:
            console.print(f"[yellow]DRY RUN:[/yellow] Would disable provider '{provider_name}'")
            console.print(f"  Current status: {'Enabled' if current_status else 'Disabled'}")
            console.print(f"  New status: Disabled")
            return
        
        if not current_status:
            print_warning(f"Provider '{provider_name}' is already disabled")
            return
        
        config["providers"][provider_name]["enabled"] = False
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print_success(f"Provider '{provider_name}' disabled")
    except Exception as e:
        print_error(f"Failed to disable provider: {str(e)}")
        raise typer.Exit(1)


@app.command()
def priority(
    provider_name: str = typer.Argument(..., help="Provider name"),
    priority: int = typer.Argument(..., help="Priority (lower = higher priority)", callback=validate_priority),
):
    """Set provider priority"""
    try:
        config_path = get_config_path()
        
        if not config_path.exists():
            print_error(
                "config.json not found",
                suggestion="Run 'lumni settings menu' to create configuration"
            )
            raise typer.Exit(1)
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if provider_name not in config.get("providers", {}):
            print_error(f"Provider '{provider_name}' not found")
            raise typer.Exit(1)
        
        config["providers"][provider_name]["priority"] = priority
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print_success(f"Provider '{provider_name}' priority set to {priority}")
    except Exception as e:
        print_error(f"Failed to set provider priority: {str(e)}")
        raise typer.Exit(1)


@app.command()
def health():
    """Run health checks on all providers"""
    try:
        config = load_config()
        table = create_table("Provider Health", ["Provider", "Status", "Enabled"])
        
        # This would integrate with actual health check logic
        # For now, just show enabled status
        for provider_name, provider_config in config.providers.items():
            enabled = provider_config.enabled
            status = "healthy" if enabled else "disabled"
            status_color = "[green]healthy[/green]" if enabled else "[red]disabled[/red]"
            
            table.add_row(
                provider_name,
                status_color,
                "YES" if enabled else "NO"
            )
        
        console.print(table)
        print_warning("Full health checks require running server. Use API endpoint for detailed health status.")
    except Exception as e:
        print_error(f"Failed to check provider health: {str(e)}")
        raise typer.Exit(1)

