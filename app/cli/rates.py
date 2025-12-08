"""
Rate Limit Commands
CLI commands for viewing and managing rate limits
"""

from typing import Optional
import typer
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from datetime import datetime, timedelta

from app.cli.utils import (
    get_db_session,
    format_number,
    create_table,
    print_error,
    print_success,
    get_status_color,
    console
)
from app.config.rate_limits import (
    RATE_LIMIT_CONFIGS,
    get_provider_rate_limit,
    get_model_rate_limit,
    get_provider_rate_limits
)
from app.storage.repositories import UsageMetricsRepository

app = typer.Typer(name="rates", help="Rate limit management commands")


@app.command()
def list():
    """List all rate limit configurations"""
    try:
        table = create_table("Rate Limit Configurations", ["Provider", "Model", "RPM", "RPD", "TPM", "Notes"])
        
        for config in RATE_LIMIT_CONFIGS:
            model = config.model or "default"
            rpm = format_number(config.requests_per_minute) if config.requests_per_minute > 0 else "unlimited"
            rpd = format_number(config.requests_per_day) if config.requests_per_day > 0 else "unlimited"
            tpm = format_number(config.tokens_per_minute) if config.tokens_per_minute else "N/A"
            notes = config.notes or ""
            
            table.add_row(
                config.provider,
                model,
                rpm,
                rpd,
                tpm,
                notes
            )
        
        console.print(table)
    except Exception as e:
        print_error(f"Failed to list rate limits: {str(e)}")
        raise typer.Exit(1)


@app.command()
def provider(
    provider_name: str = typer.Argument(..., help="Provider name"),
):
    """Show rate limits for a specific provider"""
    try:
        configs = get_provider_rate_limits(provider_name)
        
        if not configs:
            console.print(f"[yellow]No rate limit configuration found for {provider_name}[/yellow]")
            return
        
        table = create_table(f"Rate Limits for {provider_name}", ["Model", "RPM", "RPD", "TPM", "Notes"])
        
        for config in configs:
            model = config.model or "default"
            rpm = format_number(config.requests_per_minute) if config.requests_per_minute > 0 else "unlimited"
            rpd = format_number(config.requests_per_day) if config.requests_per_day > 0 else "unlimited"
            tpm = format_number(config.tokens_per_minute) if config.tokens_per_minute else "N/A"
            notes = config.notes or ""
            
            table.add_row(model, rpm, rpd, tpm, notes)
        
        console.print(table)
    except Exception as e:
        print_error(f"Failed to retrieve rate limits: {str(e)}")
        raise typer.Exit(1)


@app.command()
def model(
    provider_name: str = typer.Argument(..., help="Provider name"),
    model_name: str = typer.Argument(..., help="Model name"),
):
    """Show rate limits for a specific model"""
    try:
        config = get_model_rate_limit(provider_name, model_name)
        
        if not config:
            console.print(f"[yellow]No rate limit configuration found for {provider_name}/{model_name}[/yellow]")
            return
        
        table = create_table(f"Rate Limits for {provider_name}/{model_name}", ["Setting", "Value"])
        table.add_row("Requests Per Minute", format_number(config.requests_per_minute) if config.requests_per_minute > 0 else "unlimited")
        table.add_row("Requests Per Day", format_number(config.requests_per_day) if config.requests_per_day > 0 else "unlimited")
        if config.tokens_per_minute:
            table.add_row("Tokens Per Minute", format_number(config.tokens_per_minute))
        if config.tokens_per_day:
            table.add_row("Tokens Per Day", format_number(config.tokens_per_day))
        if config.input_tokens_per_minute:
            table.add_row("Input Tokens Per Minute", format_number(config.input_tokens_per_minute))
        if config.output_tokens_per_minute:
            table.add_row("Output Tokens Per Minute", format_number(config.output_tokens_per_minute))
        if config.notes:
            table.add_row("Notes", config.notes)
        
        console.print(table)
    except Exception as e:
        print_error(f"Failed to retrieve rate limits: {str(e)}")
        raise typer.Exit(1)


@app.command()
def remaining(
    hours: int = typer.Option(1, "--hours", "-h", help="Time window in hours"),
):
    """Show remaining rate limits based on usage"""
    try:
        db = get_db_session()
        since = datetime.now() - timedelta(hours=hours)
        
        # Get rate limits and usage for each provider
        providers = set()
        for config in RATE_LIMIT_CONFIGS:
            providers.add(config.provider)
        
        table = create_table(f"Remaining Rate Limits (Last {hours}h)", ["Provider", "Model", "RPM Limit", "RPM Used", "RPM Remaining", "RPD Limit", "RPD Used", "RPD Remaining"])
        
        for provider in sorted(providers):
            # Get provider default config
            provider_config = get_provider_rate_limit(provider)
            if not provider_config:
                continue
            
            # Get usage for provider
            metrics = UsageMetricsRepository.get_by_provider(db, provider, since)
            total_requests = sum(m.requests for m in metrics)
            
            # Calculate per-minute usage (approximate)
            rpm_used = int(total_requests / (hours * 60)) if hours > 0 else 0
            rpm_limit = provider_config.requests_per_minute if provider_config.requests_per_minute > 0 else float('inf')
            rpm_remaining = rpm_limit - rpm_used if rpm_limit != float('inf') else "unlimited"
            
            # Calculate per-day usage
            rpd_used = total_requests
            rpd_limit = provider_config.requests_per_day if provider_config.requests_per_day > 0 else float('inf')
            rpd_remaining = rpd_limit - rpd_used if rpd_limit != float('inf') else "unlimited"
            
            # Color code remaining
            rpm_remaining_str = str(rpm_remaining) if isinstance(rpm_remaining, (int, float)) else rpm_remaining
            if isinstance(rpm_remaining, (int, float)) and rpm_limit != float('inf'):
                if rpm_remaining < rpm_limit * 0.1:
                    rpm_remaining_str = f"[red]{rpm_remaining_str}[/red]"
                elif rpm_remaining < rpm_limit * 0.3:
                    rpm_remaining_str = f"[yellow]{rpm_remaining_str}[/yellow]"
                else:
                    rpm_remaining_str = f"[green]{rpm_remaining_str}[/green]"
            
            table.add_row(
                provider,
                "default",
                format_number(rpm_limit) if rpm_limit != float('inf') else "unlimited",
                format_number(rpm_used),
                rpm_remaining_str,
                format_number(rpd_limit) if rpd_limit != float('inf') else "unlimited",
                format_number(rpd_used),
                str(rpd_remaining) if isinstance(rpd_remaining, (int, float)) else rpd_remaining
            )
        
        console.print(table)
        db.close()
    except Exception as e:
        print_error(f"Failed to calculate remaining rate limits: {str(e)}")
        raise typer.Exit(1)

