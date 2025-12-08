"""
Model Management Commands
CLI commands for viewing and managing models
"""

from typing import Optional
import typer
from rich.table import Table
from rich.console import Console
from rich.panel import Panel

from app.cli.utils import (
    create_table,
    print_error,
    console
)
from app.models.categorization import (
    MODEL_CATEGORIZATION,
    get_models_by_provider,
    get_models_by_category
)

app = typer.Typer(name="models", help="Model management commands")


@app.command()
def list(
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Filter by provider"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category (fast/powerful)"),
    free_only: bool = typer.Option(False, "--free-only", help="Show only free models"),
):
    """List all available models"""
    try:
        # Create a copy of the list to avoid any mutation issues
        models = [m for m in MODEL_CATEGORIZATION.values()]
        
        # Apply filters
        if provider:
            models = [m for m in models if m.provider == provider]
        
        if category:
            models = [m for m in models if m.category == category]
        
        if free_only:
            # Filter to free providers (no credits required)
            free_providers = ["gemini", "github-copilot", "groq"]
            models = [m for m in models if m.provider in free_providers]
        
        if not models:
            console.print("[yellow]No models found matching criteria[/yellow]")
            return
        
        table = create_table("Available Models", ["Provider", "Model", "Category", "Benchmark Score"])
        
        for model_meta in sorted(models, key=lambda x: (x.provider, x.model)):
            benchmark = f"{model_meta.benchmark_score:.2f}" if model_meta.benchmark_score else "N/A"
            table.add_row(
                model_meta.provider,
                model_meta.model,
                model_meta.category,
                benchmark
            )
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(models)} models[/dim]")
    except Exception as e:
        print_error(f"Failed to list models: {str(e)}")
        raise typer.Exit(1)


@app.command()
def provider(
    provider_name: str = typer.Argument(..., help="Provider name"),
):
    """List models for a specific provider"""
    try:
        models = get_models_by_provider(provider_name)
        
        if not models:
            console.print(f"[yellow]No models found for provider '{provider_name}'[/yellow]")
            return
        
        table = create_table(f"Models for {provider_name}", ["Model", "Category", "Benchmark Score"])
        
        for model_meta in sorted(models, key=lambda x: x.model):
            benchmark = f"{model_meta.benchmark_score:.2f}" if model_meta.benchmark_score else "N/A"
            table.add_row(
                model_meta.model,
                model_meta.category,
                benchmark
            )
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(models)} models[/dim]")
    except Exception as e:
        print_error(f"Failed to list models: {str(e)}")
        raise typer.Exit(1)


@app.command()
def show(
    provider_name: str = typer.Argument(..., help="Provider name"),
    model_name: str = typer.Argument(..., help="Model name"),
):
    """Show detailed information for a specific model"""
    try:
        # Find model in categorization
        found = None
        for model_id, model_meta in MODEL_CATEGORIZATION.items():
            if model_meta.provider == provider_name and model_meta.model == model_name:
                found = model_meta
                break
        
        if not found:
            console.print(f"[yellow]Model '{provider_name}/{model_name}' not found[/yellow]")
            return
        
        table = create_table(f"Model Details: {provider_name}/{model_name}", ["Property", "Value"])
        table.add_row("Provider", found.provider)
        table.add_row("Model", found.model)
        table.add_row("Category", found.category)
        if found.benchmark_score:
            table.add_row("Benchmark Score", f"{found.benchmark_score:.2f}")
        
        console.print(table)
    except Exception as e:
        print_error(f"Failed to show model details: {str(e)}")
        raise typer.Exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
):
    """Search models by name"""
    try:
        query_lower = query.lower()
        matches = []
        
        for model_id, model_meta in MODEL_CATEGORIZATION.items():
            if (query_lower in model_meta.model.lower() or 
                query_lower in model_meta.provider.lower() or
                query_lower in model_id.lower()):
                matches.append(model_meta)
        
        if not matches:
            console.print(f"[yellow]No models found matching '{query}'[/yellow]")
            return
        
        table = create_table(f"Search Results for '{query}'", ["Provider", "Model", "Category"])
        
        for model_meta in sorted(matches, key=lambda x: (x.provider, x.model)):
            table.add_row(
                model_meta.provider,
                model_meta.model,
                model_meta.category
            )
        
        console.print(table)
        console.print(f"\n[dim]Found: {len(matches)} models[/dim]")
    except Exception as e:
        print_error(f"Failed to search models: {str(e)}")
        raise typer.Exit(1)


@app.command()
def categorize():
    """Show models organized by category"""
    try:
        fast_models = get_models_by_category("fast")
        powerful_models = get_models_by_category("powerful")
        
        # Fast models table
        if fast_models:
            table = create_table("Fast Models", ["Provider", "Model", "Benchmark Score"])
            for model_meta in sorted(fast_models, key=lambda x: (x.provider, x.model)):
                benchmark = f"{model_meta.benchmark_score:.2f}" if model_meta.benchmark_score else "N/A"
                table.add_row(model_meta.provider, model_meta.model, benchmark)
            console.print(table)
            console.print()
        
        # Powerful models table
        if powerful_models:
            table = create_table("Powerful Models", ["Provider", "Model", "Benchmark Score"])
            for model_meta in sorted(powerful_models, key=lambda x: (x.provider, x.model)):
                benchmark = f"{model_meta.benchmark_score:.2f}" if model_meta.benchmark_score else "N/A"
                table.add_row(model_meta.provider, model_meta.model, benchmark)
            console.print(table)
        
        console.print(f"\n[dim]Fast: {len(fast_models)} models, Powerful: {len(powerful_models)} models[/dim]")
    except Exception as e:
        print_error(f"Failed to categorize models: {str(e)}")
        raise typer.Exit(1)

