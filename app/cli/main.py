"""
Main CLI Entry Point
Lumni Management CLI
"""

import typer
import uvicorn
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from typing import Optional

from app.cli import usage, rates, providers, models, monitor, settings
from app.config import load_config

# Create main Typer app
app = typer.Typer(
    name="lumni",
    help="Lumni API Gateway Management CLI",
    add_completion=False,
)

# Add subcommands
app.add_typer(usage.app, name="usage")
app.add_typer(rates.app, name="rates")
app.add_typer(providers.app, name="providers")
app.add_typer(models.app, name="models")
app.add_typer(monitor.app, name="monitor")
app.add_typer(settings.app, name="settings")

console = Console()


@app.callback()
def main():
    """Lumni API Gateway Management CLI"""
    pass


@app.command()
def version():
    """Show version information"""
    console.print("[bold green]Lumni API Gateway[/bold green]")
    console.print("[dim]Version 2.0.0[/dim]")


@app.command()
def start(
    host: Optional[str] = typer.Option(None, "--host", "-h", help="Host to bind to"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload (development mode)"),
):
    """Start the Lumni API Gateway server"""
    try:
        # Load configuration
        config = load_config()
        
        # Use provided values or fall back to config
        server_host = host or config.server.host
        server_port = port or config.server.port
        
        console.print(f"[bold green]Starting Lumni API Gateway...[/bold green]")
        console.print(f"[dim]Host: {server_host}[/dim]")
        console.print(f"[dim]Port: {server_port}[/dim]")
        if reload:
            console.print("[dim]Auto-reload: enabled (development mode)[/dim]")
        console.print()
        
        # Start uvicorn server
        uvicorn.run(
            "app.main:app",
            host=server_host,
            port=server_port,
            reload=reload,
        )
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("[yellow]Please run 'lumni settings menu' to configure the gateway first.[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error starting server:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def uninstall(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
    remove_path: bool = typer.Option(True, "--remove-path/--keep-path", help="Remove PATH modifications from shell config"),
):
    """Uninstall Lumni CLI and remove installation artifacts"""
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

