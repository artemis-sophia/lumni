"""
Usage Monitoring Commands
CLI commands for viewing usage statistics
"""

from datetime import datetime, timedelta
from typing import Optional
import typer
from rich.table import Table
from rich.console import Console
from rich.panel import Panel

from app.cli.utils import (
    get_db_session,
    format_number,
    create_table,
    print_error,
    parse_time_window,
    format_datetime,
    console,
    should_output_json,
    output_json,
    validate_time_window,
)
from app.storage.repositories import UsageMetricsRepository
from app.config.pricing import calculate_cost

app = typer.Typer(name="usage", help="Usage monitoring commands")


@app.command()
def show(
    hours: int = typer.Option(24, "--hours", "-h", help="Time window in hours", callback=validate_time_window),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Filter by provider"),
):
    """Show overall usage statistics
    
    Examples:
        lumni usage show                    # Show last 24 hours
        lumni usage show --hours 48        # Show last 48 hours
        lumni usage show --provider openai  # Filter by provider
        lumni usage show --json             # Output as JSON
    """
    try:
        db = get_db_session()
        since = datetime.now() - timedelta(hours=hours)
        
        if provider:
            metrics = UsageMetricsRepository.get_by_provider(db, provider, since)
            title = f"Usage Statistics for {provider} (Last {hours}h)"
        else:
            # Get all metrics
            all_metrics = []
            providers = ["groq", "deepseek", "github-copilot", "gemini", "mistral", "codestral", "openrouter"]
            for p in providers:
                metrics = UsageMetricsRepository.get_by_provider(db, p, since)
                all_metrics.extend(metrics)
            metrics = all_metrics
            title = f"Overall Usage Statistics (Last {hours}h)"
        
        if not metrics:
            if should_output_json():
                output_json({"time_window_hours": hours, "provider": provider, "summary": {}, "by_provider": {}})
            else:
                console.print(f"[yellow]No usage data found for the specified time window[/yellow]")
            db.close()
            return
        
        # Calculate totals
        total_requests = sum(m.requests for m in metrics)
        total_tokens = sum(m.tokens for m in metrics)
        total_errors = sum(m.errors for m in metrics)
        total_rate_limit_hits = sum(m.rate_limit_hits for m in metrics)
        
        # Group by provider
        provider_stats = {}
        for metric in metrics:
            if metric.provider not in provider_stats:
                provider_stats[metric.provider] = {
                    "requests": 0,
                    "tokens": 0,
                    "errors": 0,
                    "rate_limit_hits": 0,
                }
            provider_stats[metric.provider]["requests"] += metric.requests
            provider_stats[metric.provider]["tokens"] += metric.tokens
            provider_stats[metric.provider]["errors"] += metric.errors
            provider_stats[metric.provider]["rate_limit_hits"] += metric.rate_limit_hits
        
        # Build data structure for JSON
        error_rate = (total_errors / total_requests) * 100 if total_requests > 0 else 0.0
        usage_data = {
            "time_window_hours": hours,
            "provider": provider,
            "summary": {
                "total_requests": total_requests,
                "total_tokens": total_tokens,
                "total_errors": total_errors,
                "total_rate_limit_hits": total_rate_limit_hits,
                "error_rate_percent": round(error_rate, 2),
            },
            "by_provider": {k: v for k, v in sorted(provider_stats.items())},
        }
        
        # Output JSON if requested
        if should_output_json():
            output_json(usage_data)
            db.close()
            return
        
        # Otherwise output as tables
        summary_table = create_table("Summary", ["Metric", "Value"])
        summary_table.add_row("Total Requests", format_number(total_requests))
        summary_table.add_row("Total Tokens", format_number(total_tokens))
        summary_table.add_row("Total Errors", format_number(total_errors))
        summary_table.add_row("Rate Limit Hits", format_number(total_rate_limit_hits))
        if total_requests > 0:
            summary_table.add_row("Error Rate", f"{error_rate:.2f}%")
        
        console.print(summary_table)
        console.print()
        
        # Create provider breakdown table
        if len(provider_stats) > 1:
            provider_table = create_table("By Provider", ["Provider", "Requests", "Tokens", "Errors", "Rate Limit Hits"])
            for prov, stats in sorted(provider_stats.items()):
                provider_table.add_row(
                    prov,
                    format_number(stats["requests"]),
                    format_number(stats["tokens"]),
                    format_number(stats["errors"]),
                    format_number(stats["rate_limit_hits"])
                )
            console.print(provider_table)
        
        db.close()
    except Exception as e:
        print_error(f"Failed to retrieve usage statistics: {str(e)}")
        raise typer.Exit(1)


@app.command()
def provider(
    provider_name: str = typer.Argument(..., help="Provider name"),
    hours: int = typer.Option(24, "--hours", "-h", help="Time window in hours"),
):
    """Show usage statistics for a specific provider"""
    try:
        db = get_db_session()
        since = datetime.now() - timedelta(hours=hours)
        metrics = UsageMetricsRepository.get_by_provider(db, provider_name, since)
        
        if not metrics:
            console.print(f"[yellow]No usage data found for {provider_name}[/yellow]")
            db.close()
            return
        
        # Calculate totals
        total_requests = sum(m.requests for m in metrics)
        total_tokens = sum(m.tokens for m in metrics)
        total_errors = sum(m.errors for m in metrics)
        total_rate_limit_hits = sum(m.rate_limit_hits for m in metrics)
        
        # Group by model
        model_stats = {}
        for metric in metrics:
            model = metric.model or "default"
            if model not in model_stats:
                model_stats[model] = {
                    "requests": 0,
                    "tokens": 0,
                    "errors": 0,
                    "rate_limit_hits": 0,
                }
            model_stats[model]["requests"] += metric.requests
            model_stats[model]["tokens"] += metric.tokens
            model_stats[model]["errors"] += metric.errors
            model_stats[model]["rate_limit_hits"] += metric.rate_limit_hits
        
        # Create summary
        summary_table = create_table(f"Usage for {provider_name} (Last {hours}h)", ["Metric", "Value"])
        summary_table.add_row("Total Requests", format_number(total_requests))
        summary_table.add_row("Total Tokens", format_number(total_tokens))
        summary_table.add_row("Total Errors", format_number(total_errors))
        summary_table.add_row("Rate Limit Hits", format_number(total_rate_limit_hits))
        if total_requests > 0:
            error_rate = (total_errors / total_requests) * 100
            summary_table.add_row("Error Rate", f"{error_rate:.2f}%")
        
        console.print(summary_table)
        console.print()
        
        # Model breakdown
        if len(model_stats) > 1:
            model_table = create_table("By Model", ["Model", "Requests", "Tokens", "Errors"])
            for model, stats in sorted(model_stats.items()):
                model_table.add_row(
                    model,
                    format_number(stats["requests"]),
                    format_number(stats["tokens"]),
                    format_number(stats["errors"])
                )
            console.print(model_table)
        
        db.close()
    except Exception as e:
        print_error(f"Failed to retrieve usage statistics: {str(e)}")
        raise typer.Exit(1)


@app.command()
def model(
    provider_name: str = typer.Argument(..., help="Provider name"),
    model_name: str = typer.Argument(..., help="Model name"),
    hours: int = typer.Option(24, "--hours", "-h", help="Time window in hours"),
):
    """Show usage statistics for a specific model"""
    try:
        db = get_db_session()
        since = datetime.now() - timedelta(hours=hours)
        metrics = UsageMetricsRepository.get_by_model(db, provider_name, model_name, since)
        
        if not metrics:
            console.print(f"[yellow]No usage data found for {provider_name}/{model_name}[/yellow]")
            db.close()
            return
        
        # Calculate totals
        total_requests = sum(m.requests for m in metrics)
        total_tokens = sum(m.tokens for m in metrics)
        total_errors = sum(m.errors for m in metrics)
        total_rate_limit_hits = sum(m.rate_limit_hits for m in metrics)
        
        # Create table
        table = create_table(f"Usage for {provider_name}/{model_name} (Last {hours}h)", ["Metric", "Value"])
        table.add_row("Total Requests", format_number(total_requests))
        table.add_row("Total Tokens", format_number(total_tokens))
        table.add_row("Total Errors", format_number(total_errors))
        table.add_row("Rate Limit Hits", format_number(total_rate_limit_hits))
        if total_requests > 0:
            error_rate = (total_errors / total_requests) * 100
            avg_tokens = total_tokens / total_requests
            table.add_row("Error Rate", f"{error_rate:.2f}%")
            table.add_row("Avg Tokens/Request", format_number(avg_tokens))
        
        console.print(table)
        db.close()
    except Exception as e:
        print_error(f"Failed to retrieve usage statistics: {str(e)}")
        raise typer.Exit(1)


@app.command()
def cost(
    hours: int = typer.Option(24, "--hours", "-h", help="Time window in hours"),
):
    """Show cost breakdown"""
    try:
        db = get_db_session()
        since = datetime.now() - timedelta(hours=hours)
        
        # Get all metrics
        providers = ["groq", "deepseek", "github-copilot", "gemini", "mistral", "codestral", "openrouter"]
        all_metrics = []
        for p in providers:
            metrics = UsageMetricsRepository.get_by_provider(db, p, since)
            all_metrics.extend(metrics)
        
        if not all_metrics:
            console.print(f"[yellow]No usage data found for cost calculation[/yellow]")
            db.close()
            return
        
        # Calculate costs by provider/model
        cost_breakdown = {}
        total_cost = 0.0
        
        for metric in all_metrics:
            provider = metric.provider
            model = metric.model or "default"
            key = f"{provider}/{model}"
            
            if key not in cost_breakdown:
                cost_breakdown[key] = {
                    "provider": provider,
                    "model": model,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost": 0.0,
                }
            
            # Estimate input/output split (60/40)
            input_tokens = int(metric.tokens * 0.6)
            output_tokens = int(metric.tokens * 0.4)
            
            cost_breakdown[key]["input_tokens"] += input_tokens
            cost_breakdown[key]["output_tokens"] += output_tokens
            
            # Calculate cost
            cost = calculate_cost(provider, model, input_tokens, output_tokens)
            cost_breakdown[key]["cost"] += cost
            total_cost += cost
        
        # Create cost table
        table = create_table(f"Cost Breakdown (Last {hours}h)", ["Provider/Model", "Input Tokens", "Output Tokens", "Cost (USD)"])
        
        for key in sorted(cost_breakdown.keys()):
            data = cost_breakdown[key]
            table.add_row(
                f"{data['provider']}/{data['model']}",
                format_number(data["input_tokens"]),
                format_number(data["output_tokens"]),
                f"${data['cost']:.4f}"
            )
        
        table.add_row("", "", "[bold]Total[/bold]", f"[bold]${total_cost:.4f}[/bold]")
        console.print(table)
        
        db.close()
    except Exception as e:
        print_error(f"Failed to calculate costs: {str(e)}")
        raise typer.Exit(1)

