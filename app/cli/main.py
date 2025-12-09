"""
Main CLI Entry Point
Lumni Management CLI
"""

import typer
import uvicorn
import os
import sys
import json
import subprocess
import signal
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Optional, List
from prompt_toolkit.shortcuts import yes_no_dialog, message_dialog
from contextvars import ContextVar

from app.cli import usage, rates, providers, models, monitor, settings
from app.cli.utils import (
    console,
    print_success,
    print_error,
    print_warning,
    print_info,
    create_table,
    get_pid_file_path,
    save_server_pid,
    get_server_pid,
    is_server_running,
    kill_server_process,
    get_log_file_path,
    MenuContext,
    create_enhanced_menu,
    validate_port,
    validate_priority,
    validate_time_window,
    validate_threshold,
)
from app.cli.settings import (
    generate_unified_api_key,
    load_config_json,
    save_config_json,
    update_env_var,
)
from app.config import load_config
from app.models.categorization import MODEL_CATEGORIZATION, get_models_by_provider

# Global context for CLI options
class CLIContext:
    """Context object to hold global CLI options"""
    def __init__(self):
        self.verbose: bool = False
        self.quiet: bool = False
        self.json_output: bool = False

# Context variable for accessing CLI context
cli_context: ContextVar[CLIContext] = ContextVar('cli_context', default=CLIContext())

# Create main Typer app
app = typer.Typer(
    name="lumni",
    help="Lumni API Gateway Management CLI",
    add_completion=True,
)

# Add subcommands
app.add_typer(usage.app, name="usage")
app.add_typer(rates.app, name="rates")
app.add_typer(providers.app, name="providers")
app.add_typer(models.app, name="models")
app.add_typer(monitor.app, name="monitor")
app.add_typer(settings.app, name="settings")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version information and exit"),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-error output"),
    json: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """
    Lumni API Gateway Management CLI
    
    A unified API gateway for managing multiple AI providers with smart fallback
    and comprehensive monitoring capabilities.
    
    Examples:
        lumni --version                    # Show version
        lumni start                        # Start the server
        lumni providers list               # List all providers
        lumni usage show --hours 24        # Show usage statistics
    """
    # Handle --version flag
    if version:
        console.print("[bold green]Lumni API Gateway[/bold green]")
        console.print("[dim]Version 2.0.0[/dim]")
        raise typer.Exit(0)
    
    # Set up global context
    context = CLIContext()
    context.verbose = verbose
    context.quiet = quiet
    context.json_output = json
    cli_context.set(context)
    
    # If no command was provided, show help
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(0)


def mask_api_key(key: str, show_full: bool = False) -> str:
    """Mask API key for display"""
    if show_full or len(key) <= 12:
        return key
    return f"{key[:8]}...{key[-4:]}"


def display_unified_api_key(config, show_full: bool = False):
    """Display unified API key"""
    key = config.auth.unified_api_key
    masked = mask_api_key(key, show_full)
    console.print(f"[bold]Unified API Key:[/bold] [dim]{masked}[/dim]")


def select_providers_interactive(config) -> Optional[dict]:
    """Interactive provider selection menu"""
    try:
        config_dict = json.loads(Path("config.json").read_text())
        providers_config = config_dict.get("providers", {})
        
        if not providers_config:
            print_error("No providers found in configuration")
            return None
        
        # Show current status
        console.print("\n[bold]Current Provider Status:[/bold]")
        table = create_table("Providers", ["Provider", "Status"])
        for provider_name, provider_data in sorted(providers_config.items()):
            enabled = provider_data.get("enabled", False)
            status = "[green]Enabled[/green]" if enabled else "[red]Disabled[/red]"
            table.add_row(provider_name, status)
        console.print(table)
        console.print()
        
        # Ask if user wants to change provider settings
        first_dialog_result = yes_no_dialog(
            title="Provider Selection",
            text="Would you like to enable/disable providers before starting the server?"
        ).run()
        
        if not first_dialog_result:
            return providers_config
        
        # Allow toggling each provider
        updated = False
        
        for provider_name, provider_data in sorted(providers_config.items()):
            current_status = provider_data.get("enabled", False)
            
            # Ask user if they want to enable (if disabled) or disable (if enabled)
            if current_status:
                # Currently enabled - ask if they want to disable
                question_text = f"Provider '{provider_name}' is currently enabled.\n\nDisable this provider?"
                toggle_result = yes_no_dialog(
                    title=f"Provider: {provider_name}",
                    text=question_text
                ).run()
                
                # If user says yes, disable it (toggle_result=True means disable)
                if toggle_result is True:
                    providers_config[provider_name]["enabled"] = False
                    updated = True
            else:
                # Currently disabled - ask if they want to enable
                question_text = f"Provider '{provider_name}' is currently disabled.\n\nEnable this provider?"
                toggle_result = yes_no_dialog(
                    title=f"Provider: {provider_name}",
                    text=question_text
                ).run()
                
                # If user says yes, enable it (toggle_result=True means enable)
                if toggle_result is True:
                    providers_config[provider_name]["enabled"] = True
                    updated = True
        
        if updated:
            config_dict["providers"] = providers_config
            Path("config.json").write_text(json.dumps(config_dict, indent=2))
            print_success("Provider configuration updated")
        
        return providers_config
    except Exception as e:
        print_error(f"Failed to select providers: {e}")
        return None


def select_models_interactive(providers_config: dict) -> bool:
    """Optional model selection per provider"""
    try:
        # Get enabled providers
        enabled_providers = [p for p, cfg in providers_config.items() if cfg.get("enabled", False)]
        
        if not enabled_providers:
            return True
        
        # Ask if user wants to configure models
        if not yes_no_dialog(
            title="Model Selection",
            text="Would you like to configure default models for providers?\n(This is optional - auto-selection will be used if skipped)"
        ).run():
            return True
        
        # For each enabled provider, show available models
        for provider_name in enabled_providers:
            available_models_meta = get_models_by_provider(provider_name)
            if not available_models_meta:
                continue
            
            # Extract model names
            model_items = [(meta.model, f"{meta.model} ({meta.category})") for meta in available_models_meta]
            selected_model = create_enhanced_menu(
                title=f"Select Default Model for {provider_name}",
                items=model_items,
                help_text=f"Choose a default model for {provider_name} (optional)"
            )
            
            # Note: Model selection could be stored in config if needed
            # For now, we'll rely on the benchmark selector's auto-selection
        
        return True
    except Exception as e:
        print_warning(f"Model selection skipped: {e}")
        return True


def _start_server(
    host: Optional[str] = None,
    port: Optional[int] = None,
    reload: bool = False,
    foreground: bool = False,
    background: bool = True,
    show_key: bool = False,
    skip_selection: bool = False,
    check_running: bool = True,
):
    """Internal function to start the server"""
    try:
        # Check if server is already running
        if check_running and is_server_running():
            existing_pid = get_server_pid()
            print_warning(f"Server is already running (PID: {existing_pid})")
            if not yes_no_dialog(
                title="Server Already Running",
                text="Would you like to stop the existing server and start a new one?"
            ).run():
                console.print("[yellow]Start cancelled[/yellow]")
                return False
            kill_server_process()
        
        # Load configuration
        config = load_config()
        
        # Auto-generate API key if it's a placeholder
        key = config.auth.unified_api_key
        placeholder_keys = [
            "test-unified-api-key-12345",
            "your-unified-api-key-here",
            "unified-api-key",
            "api-key",
        ]
        is_placeholder = (
            not key or
            key.lower() in placeholder_keys or
            key.startswith("test-") or
            len(key) < 16
        )
        
        if is_placeholder:
            print_warning("API key is a placeholder. Generating a new secure key...")
            new_key = generate_unified_api_key()
            config_dict = load_config_json()
            config_dict["auth"]["unifiedApiKey"] = new_key
            save_config_json(config_dict)
            update_env_var("UNIFIED_API_KEY", new_key)
            print_success("New API key generated and saved!")
            # Reload config to get the new key
            config = load_config()
        
        # Use provided values or fall back to config
        server_host = host or config.server.host
        server_port = port or config.server.port
        
        # Display unified API key
        console.print()
        console.print(Panel.fit(
            f"[bold green]Lumni API Gateway[/bold green]\n\n"
            f"Host: [dim]{server_host}[/dim]\n"
            f"Port: [dim]{server_port}[/dim]\n",
            title="Server Configuration"
        ))
        display_unified_api_key(config, show_full=show_key)
        console.print()
        
        # Interactive provider selection
        if not skip_selection:
            providers_config = select_providers_interactive(config)
            
            if providers_config is None:
                console.print("[yellow]Start cancelled[/yellow]")
                return False
            
            # Optional model selection
            select_models_interactive(providers_config)
        
        # Reload config after provider selection
        config = load_config()
        
        # Determine if running in foreground or background
        run_foreground = foreground or (not background and not foreground)
        
        if run_foreground:
            # Run in foreground (blocking)
            from rich.progress import SpinnerColumn, TextColumn
            from rich.live import Live
            from rich.console import Group
            
            spinner = Group(
                SpinnerColumn(),
                TextColumn("[bold green]Starting Lumni API Gateway in foreground...[/bold green]"),
            )
            
            with Live(spinner, console=console, transient=True):
                import time
                time.sleep(0.5)  # Brief spinner display
            
            console.print("[bold green]Server started![/bold green]")
            console.print("[dim]Press Ctrl+C to stop[/dim]\n")
            
            uvicorn.run(
                "app.main:app",
                host=server_host,
                port=server_port,
                reload=reload,
            )
        else:
            # Run in background
            console.print(f"[bold green]Starting Lumni API Gateway in background...[/bold green]")
            
            # Prepare log file
            log_file = get_log_file_path()
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Build uvicorn command
            cmd = [
                sys.executable, "-m", "uvicorn",
                "app.main:app",
                "--host", server_host,
                "--port", str(server_port),
            ]
            
            if reload:
                cmd.append("--reload")
            
            # Start process in background
            try:
                with open(log_file, "a") as log_f:
                    process = subprocess.Popen(
                        cmd,
                        stdout=log_f,
                        stderr=subprocess.STDOUT,
                        cwd=Path.cwd(),
                        start_new_session=True,  # Detach from terminal
                    )
                
                # Save PID
                save_server_pid(process.pid)
                
                # Wait a moment to check if process started successfully
                import time
                time.sleep(0.5)
                
                if process.poll() is not None:
                    # Process exited immediately
                    print_error("Server failed to start. Check logs for details.")
                    print_info(f"Log file: {log_file}")
                    return False
                
                # Success
                console.print()
                console.print(Panel.fit(
                    f"[bold green]✓ Server started successfully![/bold green]\n\n"
                    f"PID: [dim]{process.pid}[/dim]\n"
                    f"URL: [dim]http://{server_host}:{server_port}[/dim]\n"
                    f"Logs: [dim]{log_file}[/dim]\n",
                    title="Server Status"
                ))
                display_unified_api_key(config, show_full=show_key)
                console.print()
                console.print("[dim]Use 'lumni stop' to stop the server[/dim]")
                console.print("[dim]Use 'lumni status' to check server status[/dim]")
                console.print("[dim]Use 'lumni show-key' to view the unified API key[/dim]")
                
                return True
                
            except Exception as e:
                print_error(f"Failed to start server: {e}")
                return False
                
    except FileNotFoundError as e:
        print_error(
            f"Configuration file not found: {e}",
            suggestion="Run 'lumni settings menu' to configure the gateway first"
        )
        return False
    except KeyboardInterrupt:
        console.print("\n[yellow]Start cancelled[/yellow]")
        return False
    except Exception as e:
        print_error(
            f"Error starting server: {e}",
            suggestion="Check logs with 'lumni logs' for more details"
        )
        return False


@app.command()
def start(
    host: Optional[str] = typer.Option(None, "--host", "-h", help="Host to bind to [default: from config]"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Port to bind to [default: from config]", callback=lambda ctx, param, value: value if value is None else validate_port(value)),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload (development mode)"),
    foreground: bool = typer.Option(False, "--foreground", "-f", help="Run in foreground (blocking mode)"),
    background: bool = typer.Option(True, "--background", "-b", help="Run in background (default)"),
    show_key: bool = typer.Option(False, "--show-key", help="Show full unified API key"),
    skip_selection: bool = typer.Option(False, "--skip-selection", help="Skip provider/model selection"),
):
    """Start the Lumni API Gateway server
    
    Examples:
        lumni start                          # Start server in background
        lumni start --foreground            # Start in foreground (see logs)
        lumni start --port 8080             # Start on custom port
        lumni start --reload                # Development mode with auto-reload
        lumni start --skip-selection        # Skip provider selection prompts
    """
    success = _start_server(
        host=host,
        port=port,
        reload=reload,
        foreground=foreground,
        background=background,
        show_key=show_key,
        skip_selection=skip_selection,
        check_running=True,
    )
    if not success:
        raise typer.Exit(1)


@app.command()
def stop(
    force: bool = typer.Option(False, "--force", "-f", help="Force kill the server"),
):
    """Stop the Lumni API Gateway server
    
    Examples:
        lumni stop              # Stop server gracefully
        lumni stop --force      # Force kill the server
    """
    pid = get_server_pid()
    
    if pid is None:
        print_warning("No server PID file found. Server may not be running.")
        raise typer.Exit(0)
    
    if not is_server_running(pid):
        print_warning(f"Server process (PID: {pid}) is not running. Cleaning up PID file.")
        pid_file = get_pid_file_path()
        if pid_file.exists():
            pid_file.unlink()
        raise typer.Exit(0)
    
    console.print(f"[yellow]Stopping server (PID: {pid})...[/yellow]")
    
    if kill_server_process(pid, force=force):
        print_success("Server stopped successfully")
    else:
        print_error("Failed to stop server")
        raise typer.Exit(1)


@app.command()
def status():
    """Show server status
    
    Examples:
        lumni status            # Show current server status
    """
    pid = get_server_pid()
    
    if pid is None:
        console.print("[yellow]Server is not running[/yellow]")
        console.print("[dim]No PID file found[/dim]")
        raise typer.Exit(0)
    
    if not is_server_running(pid):
        console.print("[yellow]Server is not running[/yellow]")
        console.print(f"[dim]PID file exists but process (PID: {pid}) is not running[/dim]")
        # Clean up stale PID file
        pid_file = get_pid_file_path()
        if pid_file.exists():
            pid_file.unlink()
        raise typer.Exit(0)
    
    # Server is running
    try:
        config = load_config()
        server_host = config.server.host
        server_port = config.server.port
        
        table = create_table("Server Status", ["Property", "Value"])
        table.add_row("Status", "[green]Running[/green]")
        table.add_row("PID", str(pid))
        table.add_row("Host", server_host)
        table.add_row("Port", str(server_port))
        table.add_row("URL", f"http://{server_host}:{server_port}")
        
        log_file = get_log_file_path()
        if log_file.exists():
            table.add_row("Log File", str(log_file))
        
        console.print(table)
    except Exception as e:
        print_error(f"Failed to get server details: {e}")
        console.print(f"[green]Server is running (PID: {pid})[/green]")


@app.command()
def restart(
    host: Optional[str] = typer.Option(None, "--host", "-h", help="Host to bind to [default: from config]"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Port to bind to [default: from config]", callback=lambda ctx, param, value: value if value is None else validate_port(value)),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload (development mode)"),
    show_key: bool = typer.Option(False, "--show-key", help="Show full unified API key"),
    skip_selection: bool = typer.Option(False, "--skip-selection", help="Skip provider/model selection"),
):
    """Restart the Lumni API Gateway server
    
    Examples:
        lumni restart                       # Restart server
        lumni restart --port 8080          # Restart on custom port
        lumni restart --reload             # Restart with auto-reload
    """
    console.print("[yellow]Stopping server...[/yellow]")
    
    # Stop existing server
    pid = get_server_pid()
    if pid and is_server_running(pid):
        kill_server_process(pid)
        import time
        time.sleep(0.5)  # Brief pause
    
    # Start new server
    console.print("[green]Starting server...[/green]")
    success = _start_server(
        host=host,
        port=port,
        reload=reload,
        foreground=False,
        background=True,
        show_key=show_key,
        skip_selection=skip_selection,
        check_running=False,  # Already checked and stopped
    )
    if not success:
        raise typer.Exit(1)


@app.command()
def show_key(
    copy: bool = typer.Option(False, "--copy", "-c", help="Copy key to clipboard"),
):
    """Show the unified API key (auto-generates if missing or placeholder)
    
    Examples:
        lumni show-key           # Show API key
        lumni show-key --copy   # Show and copy to clipboard
    """
    try:
        config = load_config()
        key = config.auth.unified_api_key
        
        # Check if key is a placeholder or needs to be generated
        placeholder_keys = [
            "test-unified-api-key-12345",
            "your-unified-api-key-here",
            "unified-api-key",
            "api-key",
        ]
        
        is_placeholder = (
            not key or
            key.lower() in placeholder_keys or
            key.startswith("test-") or
            len(key) < 16  # Too short to be a real key
        )
        
        if is_placeholder:
            print_warning("API key is a placeholder. Generating a new secure key...")
            
            # Generate new key
            new_key = generate_unified_api_key()
            
            # Update config.json
            config_dict = load_config_json()
            config_dict["auth"]["unifiedApiKey"] = new_key
            save_config_json(config_dict)
            
            # Update .env
            update_env_var("UNIFIED_API_KEY", new_key)
            
            key = new_key
            print_success("New API key generated and saved!")
            console.print()
        
        console.print()
        console.print(Panel.fit(
            f"[bold]Unified API Key[/bold]\n\n"
            f"[dim]{key}[/dim]",
            title="API Key"
        ))
        
        if copy:
            # Try to copy to clipboard
            try:
                import subprocess
                import platform
                
                system = platform.system()
                if system == "Darwin":  # macOS
                    subprocess.run(["pbcopy"], input=key, text=True, check=True)
                elif system == "Linux":
                    try:
                        subprocess.run(["xclip", "-selection", "clipboard"], input=key, text=True, check=True)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        try:
                            subprocess.run(["xsel", "--clipboard", "--input"], input=key, text=True, check=True)
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            print_warning("Clipboard not available on this system")
                elif system == "Windows":
                    subprocess.run(["clip"], input=key, text=True, check=True, shell=True)
                
                print_success("API key copied to clipboard")
            except Exception as e:
                print_warning(f"Failed to copy to clipboard: {e}")
        
        console.print()
    except FileNotFoundError as e:
        print_error(
            f"Configuration not found: {e}",
            suggestion="Run 'lumni settings menu' to configure the gateway first"
        )
        raise typer.Exit(1)
    except Exception as e:
        print_error(
            f"Failed to load API key: {e}",
            suggestion="Check that config.json exists and is valid JSON"
        )
        raise typer.Exit(1)


@app.command()
def logs(
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output (like tail -f)"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines to show"),
):
    """Show server logs
    
    Examples:
        lumni logs                # Show last 50 lines
        lumni logs --lines 100   # Show last 100 lines
        lumni logs --follow      # Follow logs in real-time
    """
    log_file = get_log_file_path()
    
    if not log_file.exists():
        print_warning(f"Log file not found: {log_file}")
        raise typer.Exit(0)
    
    if follow:
        # Follow logs (tail -f style)
        try:
            import time
            console.print(f"[dim]Following logs from {log_file}...[/dim]")
            console.print("[dim]Press Ctrl+C to stop[/dim]\n")
            
            # Simple tail -f implementation
            with open(log_file, "r") as f:
                # Go to end of file
                f.seek(0, 2)
                
                try:
                    while True:
                        line = f.readline()
                        if line:
                            console.print(line.rstrip())
                        else:
                            time.sleep(0.1)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Stopped following logs[/yellow]")
        except Exception as e:
            print_error(f"Failed to follow logs: {e}")
            raise typer.Exit(1)
    else:
        # Show last N lines
        try:
            with open(log_file, "r") as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                console.print("".join(last_lines))
        except Exception as e:
            print_error(f"Failed to read logs: {e}")
            raise typer.Exit(1)


@app.command()
def uninstall(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
    remove_path: bool = typer.Option(True, "--remove-path/--keep-path", help="Remove PATH modifications from shell config"),
):
    """Uninstall Lumni CLI and remove installation artifacts
    
    Examples:
        lumni uninstall           # Uninstall with confirmation
        lumni uninstall --yes    # Uninstall without confirmation
    """
    console.print("[bold yellow]Lumni Uninstall[/bold yellow]")
    console.print()
    
    # Find CLI wrapper
    local_bin_dir = Path.home() / ".local" / "bin"
    cli_wrapper = local_bin_dir / "lumni"
    
    items_to_remove = []
    
    # Check for CLI wrapper
    if cli_wrapper.exists():
        items_to_remove.append(("CLI wrapper", str(cli_wrapper)))
    
    # Check for PATH modifications
    if remove_path:
        shell_configs = []
        if os.getenv("ZSH_VERSION"):
            shell_configs.append(Path.home() / ".zshrc")
        elif os.getenv("BASH_VERSION"):
            shell_configs.append(Path.home() / ".bashrc")
        else:
            # Try both if shell not detected
            shell_configs.extend([
                Path.home() / ".zshrc",
                Path.home() / ".bashrc"
            ])
        
        for shell_config in shell_configs:
            if shell_config.exists():
                try:
                    content = shell_config.read_text()
                    # Check for Lumni PATH modifications
                    if "Lumni CLI" in content and "$HOME/.local/bin" in content:
                        items_to_remove.append(("PATH modification", str(shell_config)))
                except Exception:
                    pass
    
    if not items_to_remove:
        console.print("[green]No Lumni installation artifacts found. Nothing to remove.[/green]")
        raise typer.Exit(0)
    
    # Show what will be removed
    console.print("[bold]The following will be removed:[/bold]")
    for item_type, item_path in items_to_remove:
        console.print(f"  - {item_type}: [dim]{item_path}[/dim]")
    console.print()
    
    # Confirm unless --yes flag is used
    if not confirm:
        try:
            response = typer.prompt("Are you sure you want to continue? [y/N]", default="N")
            if response.lower() not in ["y", "yes"]:
                console.print("[yellow]Uninstall cancelled.[/yellow]")
                raise typer.Exit(0)
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Uninstall cancelled.[/yellow]")
            raise typer.Exit(0)
    
    # Perform uninstall
    removed_count = 0
    errors = []
    
    for item_type, item_path in items_to_remove:
        try:
            path = Path(item_path)
            if item_type == "CLI wrapper":
                # Remove CLI wrapper file
                if path.exists():
                    path.unlink()
                    console.print(f"[green]Removed CLI wrapper: {item_path}[/green]")
                    removed_count += 1
            elif item_type == "PATH modification":
                # Remove PATH lines from shell config
                try:
                    content = path.read_text()
                    lines = content.split("\n")
                    new_lines = []
                    in_lumni_section = False
                    
                    for i, line in enumerate(lines):
                        # Check if this is the start of Lumni section
                        if "# Lumni CLI" in line and "Added by setup script" in line:
                            in_lumni_section = True
                            continue  # Skip the comment line
                        
                        # Skip lines in Lumni section
                        if in_lumni_section:
                            # Skip the export PATH line if it's the Lumni one
                            if "export PATH" in line and "$HOME/.local/bin" in line:
                                # Check if this is followed by empty line or end of file
                                # This is the Lumni PATH line
                                continue
                            # If we hit an empty line after Lumni section, end the section
                            if line.strip() == "":
                                in_lumni_section = False
                                # Don't skip the empty line, keep it for formatting
                                new_lines.append(line)
                                continue
                            # If we hit a non-empty line that's not Lumni-related, end section
                            if line.strip() and not ("Lumni" in line or "$HOME/.local/bin" in line):
                                in_lumni_section = False
                                new_lines.append(line)
                                continue
                            # Skip any other Lumni-related lines
                            continue
                        
                        # Keep all other lines
                        new_lines.append(line)
                    
                    # Write back if changed
                    new_content = "\n".join(new_lines)
                    # Clean up multiple consecutive empty lines at the end
                    while new_content.endswith("\n\n"):
                        new_content = new_content.rstrip("\n") + "\n"
                    
                    if new_content != content:
                        path.write_text(new_content)
                        console.print(f"[green]Removed PATH modification from: {item_path}[/green]")
                        removed_count += 1
                    else:
                        console.print(f"[dim]No PATH modification found in: {item_path}[/dim]")
                except Exception as e:
                    errors.append(f"Failed to modify {item_path}: {str(e)}")
        except Exception as e:
            errors.append(f"Failed to remove {item_path}: {str(e)}")
    
    console.print()
    if removed_count > 0:
        console.print(f"[green]Successfully removed {removed_count} item(s).[/green]")
    if errors:
        console.print("[yellow]Some errors occurred:[/yellow]")
        for error in errors:
            console.print(f"  [red]{error}[/red]")
    
    console.print()
    console.print("[dim]Note: Project files and virtual environment are not removed.[/dim]")
    console.print("[dim]To completely remove Lumni, delete the project directory manually.[/dim]")


if __name__ == "__main__":
    app()

