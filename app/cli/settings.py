"""
Settings Management Commands
CLI commands for managing configuration settings
"""

from typing import Optional
import typer
import json
import os
import secrets
import subprocess
import sys
from pathlib import Path
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit.shortcuts import (
    radiolist_dialog,
    yes_no_dialog,
    input_dialog,
    message_dialog,
)

from app.cli.utils import (
    create_table,
    print_error,
    print_success,
    print_warning,
    print_info,
    console
)
from app.config import load_config

app = typer.Typer(name="settings", help="Configuration settings management")


def get_config_path() -> Path:
    """Get path to config.json"""
    return Path("config.json")


def load_config_json() -> dict:
    """Load config.json as dict"""
    config_path = get_config_path()
    if not config_path.exists():
        raise FileNotFoundError("config.json not found")
    with open(config_path, 'r') as f:
        return json.load(f)


def save_config_json(config: dict):
    """Save config.json"""
    config_path = get_config_path()
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def get_env_path() -> Path:
    """Get path to .env file"""
    return Path(".env")


def load_env_file() -> dict:
    """Load .env file as dictionary"""
    env_path = get_env_path()
    env_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def save_env_file(env_vars: dict):
    """Save .env file from dictionary"""
    env_path = get_env_path()
    
    # Read existing file to preserve comments and order
    lines = []
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    
    # Update or add variables
    updated_keys = set()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and '=' in stripped:
            key = stripped.split('=', 1)[0].strip()
            if key in env_vars:
                new_lines.append(f"{key}={env_vars[key]}\n")
                updated_keys.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add new variables that weren't in the file
    for key, value in env_vars.items():
        if key not in updated_keys:
            new_lines.append(f"{key}={value}\n")
    
    with open(env_path, 'w') as f:
        f.writelines(new_lines)


def update_env_var(key: str, value: str):
    """Update a single environment variable in .env file"""
    env_vars = load_env_file()
    env_vars[key] = value
    save_env_file(env_vars)


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard. Returns True if successful."""
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["pbcopy"], input=text, text=True, check=True)
            return True
        elif sys.platform == "linux":  # Linux
            # Try xclip first, then xsel
            try:
                subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    subprocess.run(["xsel", "--clipboard", "--input"], input=text, text=True, check=True)
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    return False
        elif sys.platform == "win32":  # Windows
            subprocess.run(["clip"], input=text, text=True, check=True, shell=True)
            return True
        return False
    except Exception:
        return False


def generate_unified_api_key() -> str:
    """Generate a secure random API key"""
    # Generate 32 bytes of random data and encode as hex (64 characters)
    return secrets.token_urlsafe(32)


def show_settings():
    """Show current configuration settings (internal function)"""
    try:
        config = load_config()
        
        # Server settings
        server_table = create_table("Server Settings", ["Setting", "Value"])
        server_table.add_row("Host", config.server.host)
        server_table.add_row("Port", str(config.server.port))
        console.print(server_table)
        console.print()
        
        # Auth settings
        auth_table = create_table("Authentication Settings", ["Setting", "Value"])
        auth_table.add_row("Unified API Key", config.auth.unified_api_key[:20] + "..." if len(config.auth.unified_api_key) > 20 else config.auth.unified_api_key)
        auth_table.add_row("Key Rotation", "Enabled" if config.auth.key_rotation_enabled else "Disabled")
        console.print(auth_table)
        console.print()
        
        # Provider settings summary
        provider_table = create_table("Provider Settings", ["Provider", "Enabled", "Priority", "Base URL"])
        for provider_name, provider_config in sorted(config.providers.items()):
            enabled_markup = f"[green]YES[/green]" if provider_config.enabled else f"[red]NO[/red]"
            provider_table.add_row(
                provider_name,
                enabled_markup,
                str(provider_config.priority),
                provider_config.base_url or "N/A"
            )
        console.print(provider_table)
        console.print()
        
        # Fallback settings
        fallback_table = create_table("Fallback Settings", ["Setting", "Value"])
        fallback_table.add_row("Enabled", "Yes" if config.fallback.enabled else "No")
        fallback_table.add_row("Strategy", config.fallback.strategy)
        fallback_table.add_row("Health Check Interval", f"{config.fallback.health_check_interval}ms")
        fallback_table.add_row("Retry Attempts", str(config.fallback.retry_attempts))
        fallback_table.add_row("Retry Delay", f"{config.fallback.retry_delay}ms")
        console.print(fallback_table)
        console.print()
        
        # Monitoring settings
        monitoring_table = create_table("Monitoring Settings", ["Setting", "Value"])
        monitoring_table.add_row("Enabled", "Yes" if config.monitoring.enabled else "No")
        monitoring_table.add_row("Track Usage", "Yes" if config.monitoring.track_usage else "No")
        monitoring_table.add_row("Alert Threshold", f"{config.monitoring.alert_threshold * 100}%")
        monitoring_table.add_row("Persist Metrics", "Yes" if config.monitoring.persist_metrics else "No")
        console.print(monitoring_table)
        console.print()
        
        # Storage settings
        storage_table = create_table("Storage Settings", ["Setting", "Value"])
        storage_table.add_row("Type", config.storage.type)
        storage_table.add_row("Path", config.storage.path)
        if config.storage.connection_string:
            storage_table.add_row("Connection String", config.storage.connection_string[:30] + "..." if len(config.storage.connection_string) > 30 else config.storage.connection_string)
        console.print(storage_table)
        
    except Exception as e:
        print_error(f"Failed to show settings: {str(e)}")
        raise


@app.command()
def menu():
    """Interactive settings menu with arrow key navigation"""
    try:
        while True:
            # Main menu
            result = radiolist_dialog(
                title="Settings Menu",
                text="Use ↑↓ arrow keys to navigate, Space to select, Enter to confirm:",
                values=[
                    ("show", "Show All Settings"),
                    ("provider", "Configure Provider"),
                    ("unified-key", "Generate Unified API Key"),
                    ("fallback", "Configure Fallback"),
                    ("monitoring", "Configure Monitoring"),
                    ("export", "Export Configuration"),
                    ("import", "Import Configuration"),
                    ("reset", "Reset Configuration"),
                    ("exit", "Exit"),
                ],
            ).run()
            
            if result is None or result == "exit":
                break
            
            if result == "show":
                console.clear()
                show_settings()
                input("\nPress Enter to continue...")
            
            elif result == "provider":
                configure_provider_interactive()
            
            elif result == "unified-key":
                generate_unified_key_interactive()
            
            elif result == "fallback":
                configure_fallback_interactive()
            
            elif result == "monitoring":
                configure_monitoring_interactive()
            
            elif result == "export":
                export_interactive()
            
            elif result == "import":
                import_interactive()
            
            elif result == "reset":
                reset_interactive()
        
        message_dialog(title="Settings", text="Settings menu closed").run()
        
    except KeyboardInterrupt:
        message_dialog(title="Settings", text="Settings menu cancelled").run()
    except Exception as e:
        print_error(f"Error in settings menu: {str(e)}")
        raise typer.Exit(1)


def configure_provider_interactive():
    """Interactive provider configuration"""
    try:
        config = load_config_json()
        providers = list(config.get("providers", {}).keys())
        
        if not providers:
            message_dialog(title="Error", text="No providers found in configuration").run()
            return
        
        # Select provider
        provider_name = radiolist_dialog(
            title="Select Provider",
            text="Use arrow keys to select a provider:",
            values=[(p, p) for p in sorted(providers)],
        ).run()
        
        if not provider_name:
            return
        
        provider_config = config["providers"][provider_name]
        
        # Configure provider
        while True:
            action = radiolist_dialog(
                title=f"Configure {provider_name}",
                text="Select an action:",
                values=[
                    ("toggle", f"Toggle Enabled (Currently: {'Enabled' if provider_config['enabled'] else 'Disabled'})"),
                    ("priority", f"Set Priority (Currently: {provider_config['priority']})"),
                    ("api-key", "Set API Key"),
                    ("back", "Back to Main Menu"),
                ],
            ).run()
            
            if action == "back":
                break
            
            elif action == "toggle":
                provider_config["enabled"] = not provider_config["enabled"]
                save_config_json(config)
                status = "enabled" if provider_config["enabled"] else "disabled"
                message_dialog(title="Success", text=f"Provider {provider_name} {status}").run()
            
            elif action == "priority":
                priority_str = input_dialog(
                    title="Set Priority",
                    text=f"Enter priority for {provider_name} (lower = higher priority):",
                    default=str(provider_config["priority"]),
                ).run()
                
                if priority_str:
                    try:
                        priority = int(priority_str)
                        provider_config["priority"] = priority
                        save_config_json(config)
                        message_dialog(title="Success", text=f"Priority set to {priority}").run()
                    except ValueError:
                        message_dialog(title="Error", text="Invalid priority. Must be a number.").run()
            
            elif action == "api-key":
                # Map provider names to environment variable names
                env_var_map = {
                    "groq": "GROQ_API_KEY",
                    "deepseek": "DEEPSEEK_API_KEY",
                    "github-copilot": "GITHUB_TOKEN",
                    "gemini": "GEMINI_API_KEY",
                    "mistral": "MISTRAL_API_KEY",
                    "openrouter": "OPENROUTER_API_KEY",
                }
                
                env_var = env_var_map.get(provider_name)
                if not env_var:
                    message_dialog(
                        title="Error",
                        text=f"API key configuration not available for provider: {provider_name}"
                    ).run()
                    continue
                
                # Get current API key if exists
                env_vars = load_env_file()
                current_key = env_vars.get(env_var, "")
                
                api_key = input_dialog(
                    title=f"Set API Key for {provider_name}",
                    text=f"Enter API key for {provider_name}:\n(Leave empty to keep current)",
                    default=current_key if current_key else "",
                ).run()
                
                if api_key is not None:
                    if api_key:
                        update_env_var(env_var, api_key)
                        message_dialog(
                            title="Success",
                            text=f"API key for {provider_name} saved successfully"
                        ).run()
                    elif current_key:
                        message_dialog(
                            title="Info",
                            text="API key unchanged"
                        ).run()
        
    except Exception as e:
        message_dialog(title="Error", text=f"Failed to configure provider: {str(e)}").run()


def configure_fallback_interactive():
    """Interactive fallback configuration"""
    try:
        config = load_config_json()
        
        if "fallback" not in config:
            message_dialog(title="Error", text="Fallback configuration not found").run()
            return
        
        fallback_config = config["fallback"]
        
        while True:
            action = radiolist_dialog(
                title="Configure Fallback",
                text="Select an action:",
                values=[
                    ("toggle", f"Toggle Enabled (Currently: {'Enabled' if fallback_config['enabled'] else 'Disabled'})"),
                    ("strategy", f"Set Strategy (Currently: {fallback_config['strategy']})"),
                    ("back", "Back to Main Menu"),
                ],
            ).run()
            
            if action == "back":
                break
            
            elif action == "toggle":
                fallback_config["enabled"] = not fallback_config["enabled"]
                save_config_json(config)
                status = "enabled" if fallback_config["enabled"] else "disabled"
                message_dialog(title="Success", text=f"Fallback {status}").run()
            
            elif action == "strategy":
                strategy = radiolist_dialog(
                    title="Select Strategy",
                    text="Choose fallback strategy:",
                    values=[
                        ("priority", "Priority (use providers in priority order)"),
                        ("round-robin", "Round-Robin (distribute requests evenly)"),
                        ("least-used", "Least-Used (use least busy provider)"),
                    ],
                ).run()
                
                if strategy:
                    fallback_config["strategy"] = strategy
                    save_config_json(config)
                    message_dialog(title="Success", text=f"Strategy set to {strategy}").run()
        
    except Exception as e:
        message_dialog(title="Error", text=f"Failed to configure fallback: {str(e)}").run()


def configure_monitoring_interactive():
    """Interactive monitoring configuration"""
    try:
        config = load_config_json()
        
        if "monitoring" not in config:
            message_dialog(title="Error", text="Monitoring configuration not found").run()
            return
        
        monitoring_config = config["monitoring"]
        
        while True:
            action = radiolist_dialog(
                title="Configure Monitoring",
                text="Select an action:",
                values=[
                    ("toggle", f"Toggle Enabled (Currently: {'Enabled' if monitoring_config['enabled'] else 'Disabled'})"),
                    ("track_usage", f"Track Usage (Currently: {'Enabled' if monitoring_config.get('trackUsage', True) else 'Disabled'})"),
                    ("threshold", f"Alert Threshold (Currently: {monitoring_config.get('alertThreshold', 0.8) * 100}%)"),
                    ("back", "Back to Main Menu"),
                ],
            ).run()
            
            if action == "back":
                break
            
            elif action == "toggle":
                monitoring_config["enabled"] = not monitoring_config["enabled"]
                save_config_json(config)
                status = "enabled" if monitoring_config["enabled"] else "disabled"
                message_dialog(title="Success", text=f"Monitoring {status}").run()
            
            elif action == "track_usage":
                monitoring_config["trackUsage"] = not monitoring_config.get("trackUsage", True)
                save_config_json(config)
                status = "enabled" if monitoring_config["trackUsage"] else "disabled"
                message_dialog(title="Success", text=f"Track usage {status}").run()
            
            elif action == "threshold":
                threshold_str = input_dialog(
                    title="Set Alert Threshold",
                    text="Enter alert threshold (0.0-1.0, e.g., 0.8 for 80%):",
                    default=str(monitoring_config.get("alertThreshold", 0.8)),
                ).run()
                
                if threshold_str:
                    try:
                        threshold = float(threshold_str)
                        if 0.0 <= threshold <= 1.0:
                            monitoring_config["alertThreshold"] = threshold
                            save_config_json(config)
                            message_dialog(title="Success", text=f"Alert threshold set to {threshold * 100}%").run()
                        else:
                            message_dialog(title="Error", text="Threshold must be between 0.0 and 1.0").run()
                    except ValueError:
                        message_dialog(title="Error", text="Invalid threshold. Must be a number.").run()
        
    except Exception as e:
        message_dialog(title="Error", text=f"Failed to configure monitoring: {str(e)}").run()


def export_interactive():
    """Interactive configuration export"""
    try:
        output_file = input_dialog(
            title="Export Configuration",
            text="Enter output file path:",
            default="config_backup.json",
        ).run()
        
        if output_file:
            config = load_config_json()
            output_path = Path(output_file)
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
            message_dialog(title="Success", text=f"Configuration exported to {output_file}").run()
        
    except Exception as e:
        message_dialog(title="Error", text=f"Failed to export configuration: {str(e)}").run()


def import_interactive():
    """Interactive configuration import"""
    try:
        input_file = input_dialog(
            title="Import Configuration",
            text="Enter input file path:",
        ).run()
        
        if not input_file:
            return
        
        input_path = Path(input_file)
        if not input_path.exists():
            message_dialog(title="Error", text=f"File not found: {input_file}").run()
            return
        
        # Confirm import
        if yes_no_dialog(
            title="Confirm Import",
            text=f"Import configuration from {input_file}? This will overwrite current settings.",
        ).run():
            config_path = get_config_path()
            
            # Backup current config
            if config_path.exists():
                backup_path = Path(f"{config_path}.backup")
                with open(config_path, 'r') as f:
                    backup_data = json.load(f)
                with open(backup_path, 'w') as f:
                    json.dump(backup_data, f, indent=2)
            
            # Import new config
            with open(input_path, 'r') as f:
                new_config = json.load(f)
            
            with open(config_path, 'w') as f:
                json.dump(new_config, f, indent=2)
            
            message_dialog(title="Success", text=f"Configuration imported from {input_file}").run()
        
    except Exception as e:
        message_dialog(title="Error", text=f"Failed to import configuration: {str(e)}").run()


def reset_interactive():
    """Interactive configuration reset"""
    try:
        section = radiolist_dialog(
            title="Reset Configuration",
            text="Select section to reset:",
            values=[
                ("providers", "Reset all providers to enabled"),
                ("fallback", "Reset fallback to defaults"),
                ("monitoring", "Reset monitoring to defaults"),
            ],
        ).run()
        
        if not section:
            return
        
        if yes_no_dialog(
            title="Confirm Reset",
            text=f"Reset {section} configuration to defaults?",
        ).run():
            config = load_config_json()
            
            if section == "providers":
                for provider_name in config.get("providers", {}):
                    config["providers"][provider_name]["enabled"] = True
                message_dialog(title="Success", text="All providers reset to enabled").run()
            
            elif section == "fallback":
                config["fallback"] = {
                    "enabled": True,
                    "strategy": "priority",
                    "healthCheckInterval": 30000,
                    "retryAttempts": 3,
                    "retryDelay": 1000
                }
                message_dialog(title="Success", text="Fallback settings reset to defaults").run()
            
            elif section == "monitoring":
                config["monitoring"] = {
                    "enabled": True,
                    "trackUsage": True,
                    "alertThreshold": 0.8,
                    "persistMetrics": True
                }
                message_dialog(title="Success", text="Monitoring settings reset to defaults").run()
            
            save_config_json(config)
        
    except Exception as e:
        message_dialog(title="Error", text=f"Failed to reset configuration: {str(e)}").run()


@app.command()
def show():
    """Show current configuration settings"""
    try:
        show_settings()
    except Exception as e:
        print_error(f"Failed to show settings: {str(e)}")
        raise typer.Exit(1)


@app.command()
def provider(
    provider_name: str = typer.Argument(..., help="Provider name"),
    enabled: Optional[bool] = typer.Option(None, "--enabled/--disabled", help="Enable or disable provider"),
    priority: Optional[int] = typer.Option(None, "--priority", "-p", help="Set provider priority"),
):
    """Configure provider settings"""
    try:
        config_path = get_config_path()
        
        if not config_path.exists():
            print_error("config.json not found")
            raise typer.Exit(1)
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if provider_name not in config.get("providers", {}):
            print_error(f"Provider '{provider_name}' not found")
            raise typer.Exit(1)
        
        provider_config = config["providers"][provider_name]
        changes = []
        
        if enabled is not None:
            provider_config["enabled"] = enabled
            changes.append(f"enabled={enabled}")
        
        if priority is not None:
            provider_config["priority"] = priority
            changes.append(f"priority={priority}")
        
        if not changes:
            print_warning("No changes specified. Use --enabled/--disabled or --priority")
            return
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print_success(f"Updated {provider_name}: {', '.join(changes)}")
        
    except Exception as e:
        print_error(f"Failed to update provider settings: {str(e)}")
        raise typer.Exit(1)


@app.command()
def fallback(
    enabled: Optional[bool] = typer.Option(None, "--enabled/--disabled", help="Enable or disable fallback"),
    strategy: Optional[str] = typer.Option(None, "--strategy", "-s", help="Fallback strategy (priority, round-robin, least-used)"),
):
    """Configure fallback settings"""
    try:
        config_path = get_config_path()
        
        if not config_path.exists():
            print_error("config.json not found")
            raise typer.Exit(1)
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "fallback" not in config:
            print_error("Fallback configuration not found")
            raise typer.Exit(1)
        
        fallback_config = config["fallback"]
        changes = []
        
        if enabled is not None:
            fallback_config["enabled"] = enabled
            changes.append(f"enabled={enabled}")
        
        if strategy is not None:
            if strategy not in ["priority", "round-robin", "least-used"]:
                print_error(f"Invalid strategy: {strategy}. Must be one of: priority, round-robin, least-used")
                raise typer.Exit(1)
            fallback_config["strategy"] = strategy
            changes.append(f"strategy={strategy}")
        
        if not changes:
            print_warning("No changes specified. Use --enabled/--disabled or --strategy")
            return
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print_success(f"Updated fallback settings: {', '.join(changes)}")
        
    except Exception as e:
        print_error(f"Failed to update fallback settings: {str(e)}")
        raise typer.Exit(1)


@app.command()
def monitoring(
    enabled: Optional[bool] = typer.Option(None, "--enabled/--disabled", help="Enable or disable monitoring"),
    track_usage: Optional[bool] = typer.Option(None, "--track-usage/--no-track-usage", help="Track usage metrics"),
    alert_threshold: Optional[float] = typer.Option(None, "--alert-threshold", "-t", help="Alert threshold (0.0-1.0)"),
):
    """Configure monitoring settings"""
    try:
        config_path = get_config_path()
        
        if not config_path.exists():
            print_error("config.json not found")
            raise typer.Exit(1)
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "monitoring" not in config:
            print_error("Monitoring configuration not found")
            raise typer.Exit(1)
        
        monitoring_config = config["monitoring"]
        changes = []
        
        if enabled is not None:
            monitoring_config["enabled"] = enabled
            changes.append(f"enabled={enabled}")
        
        if track_usage is not None:
            monitoring_config["trackUsage"] = track_usage
            changes.append(f"track_usage={track_usage}")
        
        if alert_threshold is not None:
            if not 0.0 <= alert_threshold <= 1.0:
                print_error("Alert threshold must be between 0.0 and 1.0")
                raise typer.Exit(1)
            monitoring_config["alertThreshold"] = alert_threshold
            changes.append(f"alert_threshold={alert_threshold}")
        
        if not changes:
            print_warning("No changes specified. Use --enabled/--disabled, --track-usage, or --alert-threshold")
            return
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print_success(f"Updated monitoring settings: {', '.join(changes)}")
        
    except Exception as e:
        print_error(f"Failed to update monitoring settings: {str(e)}")
        raise typer.Exit(1)


@app.command()
def export(
    output: str = typer.Option("config_backup.json", "--output", "-o", help="Output file path"),
):
    """Export current configuration to a file"""
    try:
        config_path = get_config_path()
        
        if not config_path.exists():
            print_error("config.json not found")
            raise typer.Exit(1)
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        output_path = Path(output)
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print_success(f"Configuration exported to {output_path}")
        
    except Exception as e:
        print_error(f"Failed to export configuration: {str(e)}")
        raise typer.Exit(1)


@app.command("import")
def import_config(
    input_file: str = typer.Argument(..., help="Input file path"),
    backup: bool = typer.Option(True, "--backup/--no-backup", help="Create backup of current config"),
):
    """Import configuration from a file"""
    try:
        config_path = get_config_path()
        input_path = Path(input_file)
        
        if not input_path.exists():
            print_error(f"Input file not found: {input_file}")
            raise typer.Exit(1)
        
        # Backup current config
        if backup and config_path.exists():
            backup_path = Path(f"{config_path}.backup")
            with open(config_path, 'r') as f:
                backup_data = json.load(f)
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            print_info(f"Backup created: {backup_path}")
        
        # Import new config
        with open(input_path, 'r') as f:
            new_config = json.load(f)
        
        with open(config_path, 'w') as f:
            json.dump(new_config, f, indent=2)
        
        print_success(f"Configuration imported from {input_file}")
        
    except Exception as e:
        print_error(f"Failed to import configuration: {str(e)}")
        raise typer.Exit(1)


@app.command()
def reset(
    section: Optional[str] = typer.Option(None, "--section", "-s", help="Reset specific section (providers, fallback, monitoring)"),
    confirm: bool = typer.Option(False, "--confirm", help="Confirm reset without prompt"),
):
    """Reset configuration to defaults"""
    try:
        if not confirm:
            print_warning("This will reset configuration. Use --confirm to proceed.")
            return
        
        config_path = get_config_path()
        
        if not config_path.exists():
            print_error("config.json not found")
            raise typer.Exit(1)
        
        # Load current config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if section == "providers":
            # Reset all providers to enabled with default priorities
            for provider_name in config.get("providers", {}):
                config["providers"][provider_name]["enabled"] = True
            print_success("Reset all providers to enabled")
        elif section == "fallback":
            # Reset fallback to defaults
            config["fallback"] = {
                "enabled": True,
                "strategy": "priority",
                "healthCheckInterval": 30000,
                "retryAttempts": 3,
                "retryDelay": 1000
            }
            print_success("Reset fallback settings to defaults")
        elif section == "monitoring":
            # Reset monitoring to defaults
            config["monitoring"] = {
                "enabled": True,
                "trackUsage": True,
                "alertThreshold": 0.8,
                "persistMetrics": True
            }
            print_success("Reset monitoring settings to defaults")
        else:
            print_error(f"Unknown section: {section}. Use: providers, fallback, or monitoring")
            raise typer.Exit(1)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
    except Exception as e:
        print_error(f"Failed to reset configuration: {str(e)}")
        raise typer.Exit(1)
