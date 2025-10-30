#!/usr/bin/env python3
"""Command-line interface for the Research Assistant."""

import sys
import logging
from typing import Optional

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.agent import ResearchAgent
from src.models.data_models import ResearchDepth
from src.utils.config import get_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

console = Console()


@click.group()
def cli():
    """Personal Research Assistant - AI-powered research tool."""
    pass


@cli.command()
@click.argument("query", nargs=-1, required=True)
@click.option(
    "--depth",
    type=click.Choice(["quick", "standard", "comprehensive"], case_sensitive=False),
    default="standard",
    help="Research depth level",
)
@click.option(
    "--max-sources",
    type=int,
    default=5,
    help="Maximum number of sources to consult",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Save results to a file",
)
def research(
    query: tuple,
    depth: str,
    max_sources: int,
    output: Optional[str],
):
    """
    Conduct research on a topic.
    
    Example: research "vector databases for RAG applications"
    """
    query_str = " ".join(query)
    
    console.print(Panel.fit(
        f"[bold cyan]Research Query:[/bold cyan] {query_str}\n"
        f"[bold cyan]Depth:[/bold cyan] {depth}\n"
        f"[bold cyan]Max Sources:[/bold cyan] {max_sources}",
        title="Research Assistant",
        border_style="cyan",
    ))
    
    try:
        # Initialize config and agent
        config = get_config()
        agent = ResearchAgent(config)
        
        # Conduct research with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Researching...", total=None)
            
            result = agent.research(
                query=query_str,
                research_depth=ResearchDepth(depth),
                max_sources=max_sources,
            )
            
            progress.update(task, completed=True)
        
        # Display results
        console.print("\n")
        console.print(Markdown(result.summary))
        
        # Save to file if requested
        if output:
            with open(output, "w") as f:
                f.write(f"# Research Results\n\n")
                f.write(f"**Query:** {query_str}\n\n")
                f.write(f"**Depth:** {depth}\n\n")
                f.write(f"**Timestamp:** {result.timestamp.isoformat()}\n\n")
                f.write("---\n\n")
                f.write(result.summary)
            
            console.print(f"\n✓ Results saved to: {output}", style="green")
        
    except ValueError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {str(e)}")
        console.print("\nPlease ensure you have set up your .env file with required API keys.")
        console.print("See .env.example for reference.")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Research failed")
        sys.exit(1)


@cli.command()
def interactive():
    """Start an interactive research session."""
    console.print(Panel.fit(
        "[bold cyan]Interactive Research Assistant[/bold cyan]\n"
        "Type your research queries and I'll help you find information.\n"
        "Type 'quit' or 'exit' to end the session.",
        border_style="cyan",
    ))
    
    try:
        config = get_config()
        agent = ResearchAgent(config)
        
        while True:
            console.print("\n")
            query = console.input("[bold green]Research query:[/bold green] ").strip()
            
            if query.lower() in ["quit", "exit", "q"]:
                console.print("Goodbye!", style="cyan")
                break
            
            if not query:
                continue
            
            # Get optional depth
            depth_input = console.input(
                "[dim]Research depth (quick/standard/comprehensive) [standard]:[/dim] "
            ).strip().lower()
            
            depth = depth_input if depth_input in ["quick", "comprehensive"] else "standard"
            
            # Conduct research
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Researching...", total=None)
                
                result = agent.research(
                    query=query,
                    research_depth=ResearchDepth(depth),
                )
                
                progress.update(task, completed=True)
            
            # Display results
            console.print("\n")
            console.print(Markdown(result.summary))
            
    except ValueError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {str(e)}")
        console.print("\nPlease ensure you have set up your .env file with required API keys.")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n\nGoodbye!", style="cyan")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logger.exception("Interactive session failed")
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    from src import __version__
    console.print(f"Research Assistant v{__version__}")


if __name__ == "__main__":
    cli()

