"""
CLI Utilities
Shared utilities for CLI commands
"""

import os
import signal
import subprocess
import json
from typing import Optional, Any, Dict, List
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from contextvars import ContextVar

from app.storage.database import get_db, init_db
from app.config import load_config

console = Console()

# Import CLI context from main (will be set by main callback)
try:
    from app.cli.main import cli_context
except ImportError:
    # Fallback if context not available
    cli_context: ContextVar = None


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


def print_error(message: str, suggestion: Optional[str] = None):
    """Print error message with optional suggestion"""
    console.print(f"[red]ERROR[/red] {message}")
    if suggestion:
        console.print(f"[dim]💡 {suggestion}[/dim]")


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


# Enhanced menu navigation utilities
from typing import List, Tuple, Callable, Any
from prompt_toolkit.shortcuts import radiolist_dialog, message_dialog
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings


class MenuContext:
    """Context for hierarchical menu navigation"""
    def __init__(self):
        self.breadcrumbs: List[str] = []
        self.history: List[Tuple[str, Any]] = []
    
    def push(self, title: str, data: Any = None):
        """Push a menu level onto the stack"""
        self.breadcrumbs.append(title)
        if data:
            self.history.append((title, data))
    
    def pop(self):
        """Pop a menu level from the stack"""
        if self.breadcrumbs:
            self.breadcrumbs.pop()
        if self.history:
            self.history.pop()
    
    def get_breadcrumb(self) -> str:
        """Get breadcrumb string"""
        return " > ".join(self.breadcrumbs) if self.breadcrumbs else "Main Menu"


def create_enhanced_menu(
    title: str,
    items: List[Tuple[str, str]],
    context: Optional[MenuContext] = None,
    help_text: Optional[str] = None,
    searchable: bool = False
) -> Optional[str]:
    """Create an enhanced menu with navigation features"""
    if context is None:
        context = MenuContext()
    
    context.push(title)
    breadcrumb = context.get_breadcrumb()
    
    # Build menu text with breadcrumbs and shortcuts
    menu_text = f"[bold]{breadcrumb}[/bold]\n\n"
    if help_text:
        menu_text += f"{help_text}\n\n"
    menu_text += "Use ↑↓ arrow keys to navigate, Space to select, Enter to confirm\n"
    menu_text += "[dim]Press 'q' to quit, 'b' to go back, '/' to search[/dim]"
    
    # Add search functionality if enabled
    if searchable and len(items) > 5:
        # For now, use standard radiolist - search can be added with prompt_toolkit's search
        pass
    
    try:
        result = radiolist_dialog(
            title=title,
            text=menu_text,
            values=items,
        ).run()
        
        if result is None:
            context.pop()
            return None
        
        return result
    except KeyboardInterrupt:
        context.pop()
        return None


def create_hierarchical_menu(
    title: str,
    items: List[Tuple[str, str, Optional[Callable]]],
    context: Optional[MenuContext] = None
) -> Optional[str]:
    """Create a hierarchical menu with sub-menus"""
    if context is None:
        context = MenuContext()
    
    # Format items for display
    menu_items = [(item[0], item[1]) for item in items]
    
    result = create_enhanced_menu(title, menu_items, context)
    
    if result:
        # Find the selected item and execute its callback if available
        for item_id, item_label, callback in items:
            if item_id == result and callback:
                try:
                    callback()
                except Exception as e:
                    print_error(f"Error executing menu item: {e}")
                break
    
    context.pop()
    return result


def show_breadcrumb(context: MenuContext):
    """Display breadcrumb navigation"""
    if context.breadcrumbs:
        breadcrumb = " > ".join(context.breadcrumbs)
        console.print(f"[dim]📍 {breadcrumb}[/dim]\n")


# PID file management utilities
def get_pid_file_path() -> Path:
    """Get path to PID file (prefer project-local, fallback to home directory)"""
    # Try project-local first
    project_pid = Path(".lumni") / "server.pid"
    if Path.cwd().name != "lumni" or not Path("config.json").exists():
        # If not in project root, use home directory
        home_pid = Path.home() / ".lumni" / "server.pid"
        home_pid.parent.mkdir(parents=True, exist_ok=True)
        return home_pid
    
    # Create .lumni directory if it doesn't exist
    project_pid.parent.mkdir(parents=True, exist_ok=True)
    return project_pid


def save_server_pid(pid: int):
    """Save server PID to file"""
    pid_file = get_pid_file_path()
    try:
        pid_file.write_text(str(pid))
    except Exception as e:
        print_error(f"Failed to save PID file: {e}")


def get_server_pid() -> Optional[int]:
    """Read server PID from file"""
    pid_file = get_pid_file_path()
    if not pid_file.exists():
        return None
    
    try:
        pid_str = pid_file.read_text().strip()
        return int(pid_str)
    except (ValueError, FileNotFoundError):
        return None


def is_server_running(pid: Optional[int] = None) -> bool:
    """Check if server process is running"""
    if pid is None:
        pid = get_server_pid()
    
    if pid is None:
        return False
    
    try:
        # Send signal 0 (no-op) to check if process exists
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        # Process doesn't exist
        return False


def kill_server_process(pid: Optional[int] = None, force: bool = False) -> bool:
    """Stop server process gracefully (or forcefully)"""
    if pid is None:
        pid = get_server_pid()
    
    if pid is None:
        return False
    
    if not is_server_running(pid):
        # Clean up stale PID file
        pid_file = get_pid_file_path()
        if pid_file.exists():
            pid_file.unlink()
        return False
    
    try:
        if force:
            # Force kill
            os.kill(pid, signal.SIGKILL)
        else:
            # Graceful shutdown
            os.kill(pid, signal.SIGTERM)
        
        # Wait a bit for process to terminate
        import time
        for _ in range(10):  # Wait up to 1 second
            time.sleep(0.1)
            if not is_server_running(pid):
                break
        
        # If still running and force wasn't used, try force kill
        if is_server_running(pid) and not force:
            os.kill(pid, signal.SIGKILL)
        
        # Clean up PID file
        pid_file = get_pid_file_path()
        if pid_file.exists():
            pid_file.unlink()
        
        return True
    except (OSError, ProcessLookupError) as e:
        print_error(f"Failed to stop server: {e}")
        return False


# Progress Indicators

def create_progress_bar(total: int = 100, description: str = "Processing"):
    """Create a progress bar using Rich"""
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    )
    return progress


def create_spinner(message: str = "Processing..."):
    """Create a spinner for indeterminate operations"""
    from rich.progress import SpinnerColumn, TextColumn
    from rich.console import Group
    
    return Group(
        SpinnerColumn(),
        TextColumn(message),
    )


# Input Validation

def validate_port(port: int) -> int:
    """Validate port number (1-65535)"""
    if not (1 <= port <= 65535):
        raise typer.BadParameter(f"Port must be between 1 and 65535, got {port}")
    return port


def validate_priority(priority: int) -> int:
    """Validate priority value (must be positive integer)"""
    if priority < 0:
        raise typer.BadParameter(f"Priority must be a positive integer, got {priority}")
    return priority


def validate_time_window(hours: int) -> int:
    """Validate time window (must be positive)"""
    if hours <= 0:
        raise typer.BadParameter(f"Time window must be positive, got {hours}")
    return hours


def validate_threshold(threshold: float) -> float:
    """Validate threshold value (0.0-1.0)"""
    if not (0.0 <= threshold <= 1.0):
        raise typer.BadParameter(f"Threshold must be between 0.0 and 1.0, got {threshold}")
    return threshold


def get_log_file_path() -> Path:
    """Get path to server log file"""
    # Use project logs directory if in project, otherwise home directory
    if Path("logs").exists():
        return Path("logs") / "server.log"
    else:
        log_dir = Path.home() / ".lumni" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir / "server.log"


# JSON Output Utilities

def should_output_json() -> bool:
    """Check if JSON output is requested"""
    if cli_context is None:
        return False
    try:
        context = cli_context.get()
        return getattr(context, 'json_output', False)
    except LookupError:
        return False


def is_quiet_mode() -> bool:
    """Check if quiet mode is enabled"""
    if cli_context is None:
        return False
    try:
        context = cli_context.get()
        return getattr(context, 'quiet', False)
    except LookupError:
        return False


def is_verbose_mode() -> bool:
    """Check if verbose mode is enabled"""
    if cli_context is None:
        return False
    try:
        context = cli_context.get()
        return getattr(context, 'verbose', False)
    except LookupError:
        return False


def output_json(data: Any, indent: int = 2):
    """Output data as JSON"""
    try:
        json_str = json.dumps(data, indent=indent, default=_json_serializer)
        console.print(json_str)
    except (TypeError, ValueError) as e:
        print_error(f"Failed to serialize output as JSON: {e}")
        raise typer.Exit(1)


def _json_serializer(obj: Any) -> Any:
    """Custom JSON serializer for datetime and other types"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, timedelta):
        return obj.total_seconds()
    elif isinstance(obj, Path):
        return str(obj)
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def table_to_dict(table: Table) -> Dict[str, Any]:
    """Convert a Rich table to a dictionary for JSON output"""
    # This is a simplified version - Rich tables don't expose their data easily
    # In practice, commands should build data structures directly
    return {"note": "Use structured data instead of Rich tables for JSON output"}


def format_for_json(value: Any) -> Any:
    """Format a value for JSON output, removing Rich markup"""
    if isinstance(value, str):
        # Remove Rich markup tags like [green], [bold], etc.
        import re
        return re.sub(r'\[/?[^\]]+\]', '', value)
    return value

