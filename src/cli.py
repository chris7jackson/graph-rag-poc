"""
Command Line Interface for Graph RAG Pipeline

Provides commands for running different pipeline stages.
"""

import click
import logging
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler

from src.ingestion import WikipediaIngester
from src.extraction import CombinedExtractor
from src.graph import GraphBuilder

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

console = Console()


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Graph RAG Pipeline - Build knowledge graphs from Wikipedia."""
    pass

@cli.command()
@click.option('--topics', '-t', multiple=True, help='Topics to search for')
@click.option('--max-articles', '-m', default=10, help='Maximum articles to fetch')
@click.option('--search', '-s', help='Search query for finding topics')
def ingest(topics, max_articles, search):
    """Ingest Wikipedia articles."""
    console.print("[bold green]Starting Wikipedia ingestion...[/bold green]")
    
    ingester = WikipediaIngester()
    
    if search:
        # Search for topics
        search_results = ingester.search_articles(search, results=max_articles)
        topics = search_results
    elif not topics:
        # Default topics
        topics = [
            "Artificial Intelligence",
            "Machine Learning",
            "Natural Language Processing",
            "Deep Learning",
            "Computer Vision"
        ]
    
    # Fetch articles
    articles = ingester.fetch_articles(list(topics), max_articles=max_articles)
    
    console.print(f"[green]✓ Ingested {len(articles)} articles[/green]")
    console.print(f"[blue]Articles saved to: data/articles/[/blue]")

@cli.command()
@click.option('--input-dir', '-i', default='./data/articles', help='Input directory with articles')
def extract(input_dir):
    """Extract entities from articles."""
    console.print("[bold green]Starting entity extraction...[/bold green]")
    
    extractor = CombinedExtractor()
    results = extractor.process_articles(input_dir)
    
    if results:
        total_entities = sum(r['stats']['total_entities'] for r in results)
        console.print(f"[green]✓ Extracted {total_entities} entities from {len(results)} articles[/green]")
        console.print(f"[blue]Entities saved to: data/entities/[/blue]")
    else:
        console.print("[red]No articles found to process[/red]")


@cli.command()
@click.option('--input-dir', '-i', default='./data/entities', help='Input directory with entities')
@click.option('--output', '-o', default='knowledge_graph', help='Output filename')
@click.option('--visualize', '-v', is_flag=True, help='Create visualization')
def build(input_dir, output, visualize):
    """Build knowledge graph from entities."""
    console.print("[bold green]Building knowledge graph...[/bold green]")
    
    builder = GraphBuilder()
    
    # Load extraction results    extraction_dir = Path(input_dir)
    extraction_files = list(extraction_dir.glob('*_entities.json'))
    
    if not extraction_files:
        console.print("[red]No extraction files found. Run 'extract' command first.[/red]")
        return
    
    # Build graph
    graph = builder.build_from_extractions(extraction_files)
    
    # Save graph
    builder.save_graph(output)
    
    # Create visualization if requested
    if visualize:
        builder.visualize(f"{output}.html")
    
    console.print(f"[green]✓ Graph built with {len(graph.nodes)} nodes and {len(graph.edges)} edges[/green]")
    console.print(f"[blue]Graph saved to: data/graphs/{output}.pickle[/blue]")


@cli.command()
def validate():
    """Launch validation interface."""
    console.print("[bold green]Launching validation interface...[/bold green]")
    console.print("[yellow]Note: This will open in your browser[/yellow]")
    
    import subprocess
    import sys    
    # Check if Streamlit app exists
    app_path = Path('src/validation/app.py')
    if not app_path.exists():
        console.print("[red]Validation app not found. Creating placeholder...[/red]")
        # We'll create the app in the next step
        return
    
    # Launch Streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])


@cli.command()
@click.argument('question')
@click.option('--graph', '-g', default='./data/graphs/knowledge_graph.pickle', help='Graph file')
def query(question, graph):
    """Query the knowledge graph."""
    console.print(f"[bold green]Processing query: {question}[/bold green]")
    
    # Check if graph exists
    if not Path(graph).exists():
        console.print("[red]Graph file not found. Run 'build' command first.[/red]")
        return
    
    console.print("[yellow]Note: Query interface requires Ollama to be running[/yellow]")
    console.print("[yellow]Query functionality will be implemented with LLM integration[/yellow]")


@cli.command()
def pipeline():    """Run the complete pipeline end-to-end."""
    console.print("[bold green]Running complete Graph RAG pipeline...[/bold green]")
    
    # Step 1: Ingest
    console.print("\n[bold]Step 1: Ingesting Wikipedia articles[/bold]")
    ingester = WikipediaIngester()
    topics = ["Artificial Intelligence", "Machine Learning", "Deep Learning"]
    articles = ingester.fetch_articles(topics, max_articles=5)
    
    if not articles:
        console.print("[red]Failed to ingest articles. Exiting.[/red]")
        return
    
    # Step 2: Extract
    console.print("\n[bold]Step 2: Extracting entities[/bold]")
    extractor = CombinedExtractor()
    results = extractor.process_articles('./data/articles')
    
    # Step 3: Build Graph
    console.print("\n[bold]Step 3: Building knowledge graph[/bold]")
    builder = GraphBuilder()
    extraction_files = list(Path('./data/entities').glob('*_entities.json'))
    graph = builder.build_from_extractions(extraction_files)
    builder.save_graph()
    builder.visualize()
    
    console.print("\n[bold green]✓ Pipeline complete![/bold green]")
    console.print(f"[blue]Results:[/blue]")    console.print(f"  • Articles ingested: {len(articles)}")
    console.print(f"  • Entities extracted: {sum(r['stats']['total_entities'] for r in results)}")
    console.print(f"  • Graph nodes: {len(graph.nodes)}")
    console.print(f"  • Graph edges: {len(graph.edges)}")
    console.print(f"\n[blue]Outputs saved to:[/blue]")
    console.print(f"  • Articles: data/articles/")
    console.print(f"  • Entities: data/entities/")
    console.print(f"  • Graph: data/graphs/")
    console.print(f"  • Visualization: data/graphs/graph.html")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()