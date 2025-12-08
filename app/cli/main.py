"""
Main CLI Entry Point
Lumni Management CLI
"""

import typer
from rich.console import Console
from rich.panel import Panel

from app.cli import usage, rates, providers, models, monitor, settings

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


if __name__ == "__main__":
    app()

