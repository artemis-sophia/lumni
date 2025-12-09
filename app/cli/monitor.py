"""
Monitoring Commands
CLI commands for real-time monitoring
"""

from typing import Optional
import typer
import time
from datetime import datetime, timedelta
from rich.table import Table
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout

from app.cli.utils import (
    get_db_session,
    format_number,
    create_table,
    print_error,
    format_relative_time,
    console,
    should_output_json,
    output_json,
)
from app.storage.repositories import UsageMetricsRepository

app = typer.Typer(name="monitor", help="Monitoring commands")


@app.command()
def live(
    interval: int = typer.Option(5, "--interval", "-i", help="Update interval in seconds"),
):
    """Real-time monitoring dashboard"""
    try:
        console.print("[bold green]Starting live monitoring...[/bold green]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        
        def generate_dashboard():
            db = get_db_session()
            try:
                # Get recent metrics (last hour)
                since = datetime.now() - timedelta(hours=1)
                
                # Get all providers
                providers = ["groq", "deepseek", "github-copilot", "gemini", "mistral", "codestral", "openrouter"]
                
                # Create summary table
                summary_table = create_table("Usage Summary (Last Hour)", ["Provider", "Requests", "Tokens", "Errors", "Rate Limit Hits"])
                
                total_requests = 0
                total_tokens = 0
                total_errors = 0
                total_rate_limit_hits = 0
                
                for provider in providers:
                    metrics = UsageMetricsRepository.get_by_provider(db, provider, since)
                    if metrics:
                        requests = sum(m.requests for m in metrics)
                        tokens = sum(m.tokens for m in metrics)
                        errors = sum(m.errors for m in metrics)
                        rate_limit_hits = sum(m.rate_limit_hits for m in metrics)
                        
                        total_requests += requests
                        total_tokens += tokens
                        total_errors += errors
                        total_rate_limit_hits += rate_limit_hits
                        
                        error_indicator = "[red]" if errors > 0 else "[green]"
                        summary_table.add_row(
                            provider,
                            format_number(requests),
                            format_number(tokens),
                            f"{error_indicator}{errors}[/{error_indicator}]",
                            format_number(rate_limit_hits)
                        )
                
                # Add totals row
                summary_table.add_row(
                    "[bold]Total[/bold]",
                    f"[bold]{format_number(total_requests)}[/bold]",
                    f"[bold]{format_number(total_tokens)}[/bold]",
                    f"[bold]{total_errors}[/bold]",
                    f"[bold]{format_number(total_rate_limit_hits)}[/bold]"
                )
                
                # Create layout
                layout = Layout()
                layout.split_column(
                    Layout(Panel(summary_table, title="Live Dashboard", border_style="green")),
                    Layout(Panel(f"[dim]Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]", border_style="dim"))
                )
                
                return layout
            finally:
                db.close()
        
        with Live(generate_dashboard(), refresh_per_second=1/interval, screen=True) as live:
            try:
                while True:
                    live.update(generate_dashboard())
                    time.sleep(interval)
            except KeyboardInterrupt:
                console.print("\n[yellow]Monitoring stopped[/yellow]")
    
    except Exception as e:
        print_error(f"Failed to start monitoring: {str(e)}")
        raise typer.Exit(1)


@app.command()
def errors(
    hours: int = typer.Option(24, "--hours", "-h", help="Time window in hours"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of errors to show"),
):
    """Show recent errors"""
    try:
        db = get_db_session()
        since = datetime.now() - timedelta(hours=hours)
        
        # Get all metrics with errors
        providers = ["groq", "deepseek", "github-copilot", "gemini", "mistral", "codestral", "openrouter"]
        error_metrics = []
        
        for provider in providers:
            metrics = UsageMetricsRepository.get_by_provider(db, provider, since)
            for metric in metrics:
                if metric.errors > 0:
                    error_metrics.append(metric)
        
        # Sort by timestamp (most recent first)
        error_metrics.sort(key=lambda x: x.timestamp, reverse=True)
        error_metrics = error_metrics[:limit]
        
        if not error_metrics:
            console.print(f"[green]No errors found in the last {hours} hours[/green]")
            db.close()
            return
        
        table = create_table(f"Recent Errors (Last {hours}h)", ["Time", "Provider", "Model", "Errors"])
        
        for metric in error_metrics:
            time_str = format_relative_time(metric.timestamp) if hasattr(metric.timestamp, 'strftime') else "N/A"
            table.add_row(
                time_str,
                metric.provider,
                metric.model or "default",
                str(metric.errors)
            )
        
        console.print(table)
        db.close()
    except Exception as e:
        print_error(f"Failed to retrieve errors: {str(e)}")
        raise typer.Exit(1)


@app.command()
def performance(
    hours: int = typer.Option(24, "--hours", "-h", help="Time window in hours"),
):
    """Show performance metrics
    
    Examples:
        lumni monitor performance            # Show performance metrics
        lumni monitor performance --json    # Output as JSON
    """
    try:
        db = get_db_session()
        since = datetime.now() - timedelta(hours=hours)
        
        # Get metrics for all providers
        providers = ["groq", "deepseek", "github-copilot", "gemini", "mistral", "codestral", "openrouter"]
        
        # Build data structure
        performance_data = []
        for provider in providers:
            metrics = UsageMetricsRepository.get_by_provider(db, provider, since)
            if metrics:
                total_requests = sum(m.requests for m in metrics)
                total_tokens = sum(m.tokens for m in metrics)
                total_errors = sum(m.errors for m in metrics)
                total_rate_limit_hits = sum(m.rate_limit_hits for m in metrics)
                
                avg_tokens = total_tokens / total_requests if total_requests > 0 else 0
                error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
                
                performance_data.append({
                    "provider": provider,
                    "requests": total_requests,
                    "avg_tokens_per_request": round(avg_tokens, 1),
                    "error_rate_percent": round(error_rate, 2),
                    "rate_limit_hits": total_rate_limit_hits,
                })
        
        # Output JSON if requested
        if should_output_json():
            output_json({"time_window_hours": hours, "performance": performance_data})
            db.close()
            return
        
        # Otherwise output as table
        table = create_table(f"Performance Metrics (Last {hours}h)", ["Provider", "Requests", "Avg Tokens/Req", "Error Rate", "Rate Limit Hits"])
        
        for perf in performance_data:
            error_rate = perf["error_rate_percent"]
            error_color = "[red]" if error_rate > 5 else "[yellow]" if error_rate > 1 else "[green]"
            
            table.add_row(
                perf["provider"],
                format_number(perf["requests"]),
                format_number(perf["avg_tokens_per_request"], 1),
                f"{error_color}{error_rate:.2f}%[/{error_color}]",
                format_number(perf["rate_limit_hits"])
            )
        
        console.print(table)
        db.close()
    except Exception as e:
        print_error(f"Failed to retrieve performance metrics: {str(e)}")
        raise typer.Exit(1)


@app.command()
def alerts():
    """Show active alerts"""
    try:
        db = get_db_session()
        since = datetime.now() - timedelta(hours=1)
        
        # Check for high error rates
        providers = ["groq", "deepseek", "github-copilot", "gemini", "mistral", "codestral", "openrouter"]
        alerts = []
        
        for provider in providers:
            metrics = UsageMetricsRepository.get_by_provider(db, provider, since)
            if metrics:
                total_requests = sum(m.requests for m in metrics)
                total_errors = sum(m.errors for m in metrics)
                total_rate_limit_hits = sum(m.rate_limit_hits for m in metrics)
                
                if total_requests > 0:
                    error_rate = (total_errors / total_requests) * 100
                    if error_rate > 10:
                        alerts.append({
                            "type": "High Error Rate",
                            "provider": provider,
                            "value": f"{error_rate:.1f}%",
                            "severity": "high"
                        })
                    
                    if total_rate_limit_hits > total_requests * 0.5:
                        alerts.append({
                            "type": "Rate Limit Issues",
                            "provider": provider,
                            "value": f"{total_rate_limit_hits} hits",
                            "severity": "medium"
                        })
        
        if not alerts:
            console.print("[green]No active alerts[/green]")
            db.close()
            return
        
        table = create_table("Active Alerts", ["Type", "Provider", "Value", "Severity"])
        
        for alert in alerts:
            severity_color = "[red]" if alert["severity"] == "high" else "[yellow]"
            table.add_row(
                alert["type"],
                alert["provider"],
                alert["value"],
                f"{severity_color}{alert['severity']}[/{severity_color}]"
            )
        
        console.print(table)
        db.close()
    except Exception as e:
        print_error(f"Failed to retrieve alerts: {str(e)}")
        raise typer.Exit(1)


@app.command()
def watch(
    interval: int = typer.Option(5, "--interval", "-i", help="Refresh interval in seconds"),
):
    """Watch mode with auto-refresh"""
    console.print("[bold]Watch mode - auto-refreshing every {interval} seconds[/bold]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")
    
    try:
        while True:
            # Show current stats
            console.print("\n" * 2)  # Add spacing instead of clearing
            console.print(f"[bold]Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/bold]\n")
            
            # Show summary
            db = get_db_session()
            try:
                since = datetime.now() - timedelta(hours=1)
                providers = ["groq", "deepseek", "github-copilot", "gemini", "mistral", "codestral", "openrouter"]
                
                table = create_table("Current Status (Last Hour)", ["Provider", "Requests", "Tokens", "Errors"])
                
                for provider in providers:
                    metrics = UsageMetricsRepository.get_by_provider(db, provider, since)
                    if metrics:
                        requests = sum(m.requests for m in metrics)
                        tokens = sum(m.tokens for m in metrics)
                        errors = sum(m.errors for m in metrics)
                        
                        table.add_row(
                            provider,
                            format_number(requests),
                            format_number(tokens),
                            str(errors)
                        )
                
                console.print(table)
            finally:
                db.close()
            
            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[yellow]Watch mode stopped[/yellow]")

