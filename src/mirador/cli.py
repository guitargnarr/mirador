"""
Mirador CLI - Command-line interface for AI orchestration
"""

import typer
from rich.console import Console
from rich.table import Table
import requests
from typing import List, Optional
from pathlib import Path

from .orchestrator import Orchestrator

app = typer.Typer(help="Mirador: Local AI Orchestration Framework")
console = Console()
orchestrator = Orchestrator()


@app.command()
def ask(
    model: str = typer.Argument(..., help="Model name to query"),
    prompt: str = typer.Argument(..., help="Prompt to send"),
    temperature: float = typer.Option(0.7, help="Temperature (0.0-1.0)")
):
    """
    Query a single Ollama model

    Example: mirador ask llama3.2 "Explain multi-agent systems"
    """
    console.print(f"[yellow]Querying {model}...[/yellow]")

    try:
        response = orchestrator.query_single(model, prompt, temperature)
        console.print(f"\n[cyan]Response:[/cyan]\n{response}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def chain(
    description: str = typer.Argument(..., help="Description of the task"),
    models: List[str] = typer.Argument(..., help="Models to chain")
):
    """
    Execute a chain of models in sequence

    Example: mirador chain "Review code" code-reviewer creative-entrepreneur
    """
    console.print(f"[bold]Starting chain:[/bold] {description}")
    console.print(f"[yellow]Models:[/yellow] {' → '.join(models)}")

    try:
        results = orchestrator.run_chain(description, models)

        console.print(f"\n[green]✓ Chain complete![/green]")
        console.print(f"Output saved to: {results['output_dir']}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def models():
    """List all available Ollama models"""

    try:
        response = requests.get("http://localhost:11434/api/tags")
        data = response.json()

        table = Table(title="Available Ollama Models")
        table.add_column("Name", style="cyan")
        table.add_column("Size", style="yellow")
        table.add_column("Modified", style="green")

        for model in data.get("models", []):
            name = model.get("name", "Unknown")
            size = f"{model.get('size', 0) / 1e9:.1f} GB"
            modified = model.get("modified_at", "")[:10]
            table.add_row(name, size, modified)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error connecting to Ollama: {e}[/red]")
        console.print("Make sure Ollama is running: ollama serve")
        raise typer.Exit(1)


@app.command()
def health():
    """Check system health"""

    console.print("[bold]Mirador System Health Check[/bold]\n")

    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        model_count = len(response.json().get("models", []))
        console.print(f"✓ Ollama: [green]Running[/green] ({model_count} models)")
    except:
        console.print("✗ Ollama: [red]Not running[/red]")

    # Check output directory
    output_dir = Path.home() / "mirador_outputs"
    if output_dir.exists():
        console.print(f"✓ Output directory: [green]{output_dir}[/green]")
    else:
        console.print(f"  Output directory: [yellow]Will be created[/yellow]")

    # Check agents
    agent_count = len(list((Path(__file__).parent.parent.parent / "models" / "domain").glob("*.modelfile")))
    console.print(f"✓ Agents available: [green]{agent_count}[/green]")

    console.print("\n[green]System ready![/green]")


@app.command()
def web():
    """Launch Streamlit web UI"""

    import subprocess

    web_app = Path(__file__).parent / "web" / "app.py"

    if not web_app.exists():
        console.print("[red]Web UI not found[/red]")
        raise typer.Exit(1)

    console.print("[yellow]Launching Streamlit web UI...[/yellow]")
    subprocess.run(["streamlit", "run", str(web_app)])


def main():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()
