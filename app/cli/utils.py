"""
CLI Utilities
Shared utilities for CLI commands
"""

from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from app.storage.database import get_db, init_db
from app.config import load_config

console = Console()


def get_db_session() -> Session:
    """Get database session for CLI"""
    init_db()
    db_gen = get_db()
    return next(db_gen)


def format_number(num: float, precision: int = 2) -> str:
    """Format number with appropriate units"""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.{precision}f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.{precision}f}K"
    else:
        return f"{num:.{precision}f}"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.1f}m"
    else:
        return f"{seconds / 3600:.1f}h"


def get_status_color(status: str) -> str:
    """Get color for status"""
    status_lower = status.lower()
    if status_lower in ["healthy", "enabled", "active", "success"]:
        return "green"
    elif status_lower in ["unhealthy", "disabled", "inactive", "error"]:
        return "red"
    elif status_lower in ["warning", "degraded"]:
        return "yellow"
    else:
        return "blue"


def create_table(title: str, columns: list[str]) -> Table:
    """Create a rich table with title"""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    for col in columns:
        table.add_column(col)
    return table


def print_success(message: str):
    """Print success message"""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str):
    """Print error message"""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str):
    """Print warning message"""
    console.print(f"[yellow]WARNING[/yellow] {message}")


def print_info(message: str):
    """Print info message"""
    console.print(f"[blue]ℹ[/blue] {message}")


def parse_time_window(window: str) -> timedelta:
    """Parse time window string (e.g., '1h', '24h', '7d')"""
    window = window.lower().strip()
    
    if window.endswith('h'):
        hours = int(window[:-1])
        return timedelta(hours=hours)
    elif window.endswith('d'):
        days = int(window[:-1])
        return timedelta(days=days)
    elif window.endswith('m'):
        minutes = int(window[:-1])
        return timedelta(minutes=minutes)
    else:
        # Default to hours if no unit
        try:
            hours = int(window)
            return timedelta(hours=hours)
        except ValueError:
            raise ValueError(f"Invalid time window format: {window}")


def format_datetime(dt: datetime) -> str:
    """Format datetime for display"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_relative_time(dt: datetime) -> str:
    """Format datetime as relative time"""
    delta = datetime.now() - dt
    if delta.total_seconds() < 60:
        return f"{int(delta.total_seconds())}s ago"
    elif delta.total_seconds() < 3600:
        return f"{int(delta.total_seconds() / 60)}m ago"
    elif delta.total_seconds() < 86400:
        return f"{int(delta.total_seconds() / 3600)}h ago"
    else:
        return f"{int(delta.total_seconds() / 86400)}d ago"

