#!/usr/bin/env python3
"""
Test All GitHub Models API Catalog Models
Tests all 43 models from the catalog to identify which ones work
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

load_dotenv()
console = Console()

GITHUB_MODELS_API_BASE = "https://models.github.ai"
INFERENCE_ENDPOINT = f"{GITHUB_MODELS_API_BASE}/inference/chat/completions"
CATALOG_ENDPOINT = f"{GITHUB_MODELS_API_BASE}/catalog/models"


def get_github_token():
    """Get GITHUB_TOKEN from environment"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        console.print("[red]Error: GITHUB_TOKEN not found in environment[/red]")
        console.print("[yellow]Please set GITHUB_TOKEN in your .env file or environment[/yellow]")
        sys.exit(1)
    return token


def load_catalog() -> List[Dict]:
    """Load catalog from JSON file or query API"""
    catalog_file = "github_models_catalog.json"
    
    if os.path.exists(catalog_file):
        try:
            with open(catalog_file, "r") as f:
                catalog = json.load(f)
                console.print(f"[green]Loaded {len(catalog)} models from {catalog_file}[/green]")
                return catalog
        except Exception as e:
            console.print(f"[yellow]Error loading catalog file: {e}[/yellow]")
    
    # Query API if file doesn't exist
    token = get_github_token()
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    console.print("[cyan]Querying GitHub Models API catalog...[/cyan]")
    try:
        response = requests.get(CATALOG_ENDPOINT, headers=headers, timeout=30)
        response.raise_for_status()
        catalog = response.json()
        
        # Save to file
        with open(catalog_file, "w") as f:
            json.dump(catalog, f, indent=2)
        console.print(f"[green]Saved {len(catalog)} models to {catalog_file}[/green]")
        return catalog
    except Exception as e:
        console.print(f"[red]Error querying catalog: {e}[/red]")
        sys.exit(1)


def test_model(token: str, model_id: str, model_name: str) -> Tuple[bool, str, float, str]:
    """Test a single model with a minimal API call"""
    start_time = time.time()
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    
    # Try without max_tokens first (some models don't support it)
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "Say 'test'"}],
    }
    
    try:
        response = requests.post(
            INFERENCE_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0].get("message", {}).get("content", "")
                return True, f"Success: {content[:50]}", elapsed, "working"
            return False, "No choices in response", elapsed, "error"
        elif response.status_code == 400:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get("error", {}).get("message", response.text[:100])
            
            # Check if it's a max_tokens issue - try without it
            if "max_tokens" in error_msg.lower() or "unsupported parameter" in error_msg.lower():
                # Already tried without max_tokens, so this is a different issue
                return False, f"HTTP 400: {error_msg[:100]}", elapsed, "error"
            return False, f"HTTP 400: {error_msg[:100]}", elapsed, "error"
        elif response.status_code == 404:
            return False, "Model not found (404)", elapsed, "not_found"
        elif response.status_code == 401:
            return False, "Authentication failed (401)", elapsed, "auth_error"
        elif response.status_code == 403:
            return False, "Access forbidden (403)", elapsed, "auth_error"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}", elapsed, "error"
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        return False, "Request timeout", elapsed, "timeout"
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = str(e)[:100]
        return False, f"Error: {error_msg}", elapsed, "error"


def get_configured_models() -> set:
    """Get set of model IDs that are already configured"""
    import yaml
    
    config_file = "litellm_config.yaml"
    if not os.path.exists(config_file):
        return set()
    
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f) or {}
        
        configured = set()
        model_list = config.get("model_list", [])
        for model_config in model_list:
            model_name = model_config.get("model_name", "")
            if model_name.startswith("github/"):
                # Extract the model ID from litellm_params
                litellm_params = model_config.get("litellm_params", {})
                model_id = litellm_params.get("model", "")
                if model_id:
                    configured.add(model_id)
        
        return configured
    except Exception as e:
        console.print(f"[yellow]Error loading config: {e}[/yellow]")
        return set()


def main():
    """Main function"""
    console.print(Panel.fit(
        "[bold green]GitHub Models API - Complete Catalog Test[/bold green]\n"
        "Tests all 43 models from the catalog to identify working models",
        title="Catalog Model Testing",
        border_style="green"
    ))
    
    token = get_github_token()
    catalog = load_catalog()
    configured_models = get_configured_models()
    
    if not catalog:
        console.print("[red]No models found in catalog[/red]")
        return
    
    console.print(f"\n[cyan]Found {len(catalog)} models in catalog[/cyan]")
    console.print(f"[cyan]Already configured: {len(configured_models)} models[/cyan]\n")
    
    # Group results
    results = {
        "working": [],
        "error": [],
        "not_found": [],
        "auth_error": [],
        "timeout": [],
    }
    
    # Test each model
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Testing models...", total=len(catalog))
        
        for model in catalog:
            model_id = model.get("id", "")
            model_name = model.get("name", "")
            provider = model.get("provider", "unknown")
            
            is_configured = model_id in configured_models
            
            progress.update(task, description=f"Testing {model_id}...")
            
            # Skip embedding models (they use different endpoints)
            if "embedding" in model_id.lower() or "embedding" in model_name.lower():
                results["error"].append({
                    "id": model_id,
                    "name": model_name,
                    "provider": provider,
                    "configured": is_configured,
                    "message": "Embedding model - different endpoint",
                    "elapsed": 0.0
                })
                progress.advance(task)
                continue
            
            success, message, elapsed, status = test_model(token, model_id, model_name)
            
            result = {
                "id": model_id,
                "name": model_name,
                "provider": provider,
                "configured": is_configured,
                "message": message,
                "elapsed": elapsed
            }
            
            results[status].append(result)
            progress.advance(task)
    
    # Display results
    console.print("\n")
    
    # Summary table
    summary_table = Table(title="Test Results Summary", box=box.ROUNDED)
    summary_table.add_column("Status", style="cyan")
    summary_table.add_column("Count", justify="right")
    summary_table.add_column("Models", style="dim")
    
    summary_table.add_row(
        "[green]Working[/green]",
        str(len(results["working"])),
        f"{len([r for r in results['working'] if not r['configured']])} new"
    )
    summary_table.add_row(
        "[red]Error[/red]",
        str(len(results["error"])),
        "See details below"
    )
    summary_table.add_row(
        "[yellow]Not Found[/yellow]",
        str(len(results["not_found"])),
        "404 errors"
    )
    summary_table.add_row(
        "[red]Auth Error[/red]",
        str(len(results["auth_error"])),
        "401/403 errors"
    )
    summary_table.add_row(
        "[yellow]Timeout[/yellow]",
        str(len(results["timeout"])),
        "Request timeouts"
    )
    
    console.print(summary_table)
    
    # Working models table
    if results["working"]:
        console.print("\n[bold green]✓ Working Models:[/bold green]")
        working_table = Table(box=box.ROUNDED)
        working_table.add_column("Model ID", style="cyan")
        working_table.add_column("Name", style="white")
        working_table.add_column("Provider", style="yellow")
        working_table.add_column("Configured", justify="center")
        working_table.add_column("Response Time", justify="right")
        working_table.add_column("Status", style="green")
        
        for result in sorted(results["working"], key=lambda x: x["id"]):
            configured_status = "[green]✓[/green]" if result["configured"] else "[yellow]✗[/yellow]"
            working_table.add_row(
                result["id"],
                result["name"][:40],
                result["provider"],
                configured_status,
                f"{result['elapsed']:.2f}s",
                "Working"
            )
        
        console.print(working_table)
    
    # New working models (not yet configured)
    new_working = [r for r in results["working"] if not r["configured"]]
    if new_working:
        console.print(f"\n[bold cyan]Found {len(new_working)} new working models to add:[/bold cyan]")
        for result in sorted(new_working, key=lambda x: x["id"]):
            console.print(f"  [green]✓[/green] {result['id']} - {result['name']}")
    
    # Error models
    if results["error"]:
        console.print("\n[bold yellow]⚠ Models with Errors:[/bold yellow]")
        error_table = Table(box=box.ROUNDED)
        error_table.add_column("Model ID", style="cyan")
        error_table.add_column("Name", style="white")
        error_table.add_column("Provider", style="yellow")
        error_table.add_column("Error", style="red")
        
        for result in sorted(results["error"], key=lambda x: x["id"])[:10]:  # Show first 10
            error_table.add_row(
                result["id"],
                result["name"][:40],
                result["provider"],
                result["message"][:60]
            )
        
        console.print(error_table)
        if len(results["error"]) > 10:
            console.print(f"[dim]... and {len(results['error']) - 10} more errors[/dim]")
    
    # Save results to JSON
    output_file = "all_catalog_test_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    console.print(f"\n[green]Results saved to {output_file}[/green]")
    
    # Summary
    total_tested = len(catalog)
    total_working = len(results["working"])
    total_new = len(new_working)
    
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Total models tested: {total_tested}")
    console.print(f"  Working models: {total_working} ({total_working/total_tested*100:.1f}%)")
    console.print(f"  New working models: {total_new}")
    
    if new_working:
        console.print(f"\n[yellow]Next step: Add {total_new} new working models to configuration[/yellow]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Fatal error: {str(e)}[/bold red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
