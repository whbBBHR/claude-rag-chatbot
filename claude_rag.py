#!/usr/bin/env python3
"""
Claude RAG Chatbot CLI

Command-line interface for the RAG chatbot using Claude API.
Supports both interactive chat and single-query modes.
"""

import click
import os
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import print as rprint

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from rag_chatbot import initialize_rag_system, ClaudeRAGChatbot

console = Console()


def display_welcome():
    """Display welcome message."""
    welcome_text = """
# Claude RAG Chatbot 🤖

Welcome to the Claude-powered RAG (Retrieval-Augmented Generation) chatbot!

This chatbot has access to course materials on:
- Introduction to Machine Learning
- Deep Learning Fundamentals  
- Natural Language Processing
- Retrieval-Augmented Generation (RAG) Systems

**Commands:**
- Type your question and press Enter
- Type 'help' for more commands
- Type 'quit' or 'exit' to leave
- Type 'history' to see conversation history
- Type 'clear' to clear conversation history
- Type 'stats' to see system statistics

**Tips:**
- Ask specific questions about ML, DL, NLP, or RAG concepts
- Request examples, explanations, or comparisons
- Ask about implementation details or best practices
"""
    
    panel = Panel(
        Markdown(welcome_text),
        title="[bold blue]RAG Chatbot[/bold blue]",
        border_style="blue"
    )
    console.print(panel)


def display_answer(result: dict):
    """Display the chatbot's answer with sources."""
    # Display the main answer
    answer_panel = Panel(
        Markdown(result['answer']),
        title="[bold green]Answer[/bold green]",
        border_style="green"
    )
    console.print(answer_panel)
    
    # Display sources if available
    if result.get('sources') and len(result['sources']) > 0:
        console.print("\n[bold cyan]Sources:[/bold cyan]")
        
        sources_table = Table(show_header=True, header_style="bold cyan")
        sources_table.add_column("Source", style="cyan")
        sources_table.add_column("Relevance", style="yellow")
        sources_table.add_column("Preview", style="white", max_width=50)
        
        for i, source in enumerate(result['sources'][:3], 1):  # Show top 3 sources
            source_name = source.get('metadata', {}).get('source', 'Unknown')
            distance = source.get('distance', 0)
            relevance = f"{(1-distance)*100:.1f}%" if distance else "N/A"
            preview = source.get('content', '')[:100] + "..." if len(source.get('content', '')) > 100 else source.get('content', '')
            
            sources_table.add_row(source_name, relevance, preview)
        
        console.print(sources_table)
    
    # Display metadata
    metadata_info = f"Model: {result.get('model_used', 'N/A')} | "
    metadata_info += f"Chunks: {result.get('chunks_retrieved', 0)} | "
    metadata_info += f"Tokens: {result.get('token_count', 'N/A')}"
    
    console.print(f"\n[dim]{metadata_info}[/dim]")


def display_history(chatbot: ClaudeRAGChatbot):
    """Display conversation history."""
    history = chatbot.get_conversation_history()
    
    if not history:
        console.print("[yellow]No conversation history available.[/yellow]")
        return
    
    console.print(f"\n[bold cyan]Conversation History ({len(history)} entries):[/bold cyan]")
    
    for i, entry in enumerate(history, 1):
        console.print(f"\n[bold]{i}. Q:[/bold] {entry['query'][:100]}{'...' if len(entry['query']) > 100 else ''}")
        console.print(f"[bold]   A:[/bold] {entry['answer'][:200]}{'...' if len(entry['answer']) > 200 else ''}")
        console.print(f"[dim]   Time: {entry['timestamp']} | Sources: {len(entry.get('sources', [])))}[/dim]")


def display_stats(chatbot: ClaudeRAGChatbot):
    """Display system statistics."""
    collection_info = chatbot.vector_store.get_collection_info()
    history = chatbot.get_conversation_history()
    
    stats_table = Table(title="[bold cyan]System Statistics[/bold cyan]")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="white")
    
    stats_table.add_row("Documents in Vector Store", str(collection_info.get('document_count', 'N/A')))
    stats_table.add_row("Embedding Model", collection_info.get('embedding_model', 'N/A'))
    stats_table.add_row("Database Path", collection_info.get('db_path', 'N/A'))
    stats_table.add_row("Conversation Entries", str(len(history)))
    
    if history:
        total_tokens = sum(entry.get('token_count', 0) for entry in history)
        stats_table.add_row("Total Tokens Used", str(total_tokens))
    
    console.print(stats_table)


@click.group()
def cli():
    """Claude RAG Chatbot - Retrieval-Augmented Generation chatbot using Claude."""
    pass


@cli.command()
@click.option('--docs-path', default='./docs', help='Path to documents directory')
@click.option('--db-path', default='./chroma_db', help='Path to ChromaDB database')
@click.option('--model', default='claude-3-sonnet-20240229', help='Claude model to use')
@click.option('--max-chunks', default=5, help='Maximum number of chunks to retrieve')
def chat(docs_path: str, db_path: str, model: str, max_chunks: int):
    """Start an interactive chat session."""
    try:
        # Check for API key
        if not os.getenv('ANTHROPIC_API_KEY'):
            console.print("[red]Error: ANTHROPIC_API_KEY not found in environment variables.[/red]")
            console.print("[yellow]Please create a .env file with your Anthropic API key:[/yellow]")
            console.print("ANTHROPIC_API_KEY=your_api_key_here")
            sys.exit(1)
        
        # Initialize the RAG system
        console.print("[yellow]Initializing RAG system...[/yellow]")
        chatbot = initialize_rag_system(docs_path=docs_path, db_path=db_path)
        console.print("[green]✓ RAG system initialized successfully![/green]")
        
        # Display welcome message
        display_welcome()
        
        # Main chat loop
        while True:
            try:
                # Get user input
                query = Prompt.ask("\n[bold cyan]Your question[/bold cyan]", default="")
                
                if not query.strip():
                    continue
                
                # Handle special commands
                query_lower = query.lower().strip()
                
                if query_lower in ['quit', 'exit', 'q']:
                    console.print("[yellow]Goodbye! 👋[/yellow]")
                    break
                elif query_lower == 'help':
                    display_welcome()
                    continue
                elif query_lower == 'history':
                    display_history(chatbot)
                    continue
                elif query_lower == 'clear':
                    chatbot.clear_history()
                    console.print("[green]✓ Conversation history cleared.[/green]")
                    continue
                elif query_lower == 'stats':
                    display_stats(chatbot)
                    continue
                
                # Process the query
                console.print("[yellow]Thinking...[/yellow]")
                result = chatbot.chat(query, max_chunks=max_chunks, model=model)
                
                # Display the result
                display_answer(result)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                
    except Exception as e:
        console.print(f"[red]Failed to initialize RAG system: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('query', required=True)
@click.option('--docs-path', default='./docs', help='Path to documents directory')
@click.option('--db-path', default='./chroma_db', help='Path to ChromaDB database')
@click.option('--model', default='claude-3-sonnet-20240229', help='Claude model to use')
@click.option('--max-chunks', default=5, help='Maximum number of chunks to retrieve')
@click.option('--output', help='Output file path (optional)')
@click.option('--json', is_flag=True, help='Output in JSON format')
def query(query: str, docs_path: str, db_path: str, model: str, max_chunks: int, output: Optional[str], json: bool):
    """Ask a single question and get an answer."""
    try:
        # Check for API key
        if not os.getenv('ANTHROPIC_API_KEY'):
            console.print("[red]Error: ANTHROPIC_API_KEY not found in environment variables.[/red]")
            sys.exit(1)
        
        # Initialize the RAG system
        chatbot = initialize_rag_system(docs_path=docs_path, db_path=db_path)
        
        # Process the query
        result = chatbot.chat(query, max_chunks=max_chunks, model=model)
        
        if json:
            import json as json_lib
            output_data = {
                'query': query,
                'answer': result['answer'],
                'sources': [s.get('metadata', {}).get('source') for s in result.get('sources', [])],
                'chunks_retrieved': result.get('chunks_retrieved', 0),
                'model_used': result.get('model_used'),
                'timestamp': result.get('timestamp')
            }
            
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    json_lib.dump(output_data, f, indent=2, ensure_ascii=False)
                console.print(f"[green]✓ Results saved to {output}[/green]")
            else:
                console.print(json_lib.dumps(output_data, indent=2, ensure_ascii=False))
        else:
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(f"Query: {query}\n\n")
                    f.write(f"Answer: {result['answer']}\n\n")
                    f.write(f"Sources: {', '.join([s.get('metadata', {}).get('source', 'Unknown') for s in result.get('sources', [])])}\n")
                console.print(f"[green]✓ Results saved to {output}[/green]")
            else:
                display_answer(result)
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--docs-path', default='./docs', help='Path to documents directory')
@click.option('--db-path', default='./chroma_db', help='Path to ChromaDB database')
def build(docs_path: str, db_path: str):
    """Build/rebuild the vector database from documents."""
    try:
        console.print("[yellow]Building vector database...[/yellow]")
        
        # Remove existing database if it exists
        import shutil
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
            console.print(f"[yellow]Removed existing database at {db_path}[/yellow]")
        
        # Initialize and build the system
        chatbot = initialize_rag_system(docs_path=docs_path, db_path=db_path)
        
        # Display stats
        collection_info = chatbot.vector_store.get_collection_info()
        console.print(f"[green]✓ Successfully built vector database![/green]")
        console.print(f"[cyan]Documents processed: {collection_info.get('document_count', 'N/A')}[/cyan]")
        
    except Exception as e:
        console.print(f"[red]Error building database: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--docs-path', default='./docs', help='Path to documents directory')
@click.option('--db-path', default='./chroma_db', help='Path to ChromaDB database')
def info(docs_path: str, db_path: str):
    """Show information about the RAG system."""
    try:
        if not os.path.exists(db_path):
            console.print(f"[yellow]Vector database not found at {db_path}[/yellow]")
            console.print("[yellow]Run 'claude-rag build' to create the database.[/yellow]")
            return
        
        # Initialize system (without rebuilding)
        from rag_chatbot import VectorStore
        vector_store = VectorStore(db_path=db_path)
        collection_info = vector_store.get_collection_info()
        
        # Display information
        info_table = Table(title="[bold cyan]RAG System Information[/bold cyan]")
        info_table.add_column("Component", style="cyan")
        info_table.add_column("Details", style="white")
        
        info_table.add_row("Documents Directory", docs_path)
        info_table.add_row("Database Path", db_path)
        info_table.add_row("Document Count", str(collection_info.get('document_count', 'N/A')))
        info_table.add_row("Embedding Model", collection_info.get('embedding_model', 'N/A'))
        
        # Check for documents in docs directory
        if os.path.exists(docs_path):
            doc_files = list(Path(docs_path).glob("*.md"))
            info_table.add_row("Available Documents", f"{len(doc_files)} markdown files")
        else:
            info_table.add_row("Available Documents", "Documents directory not found")
        
        # Check API key
        api_key_status = "✓ Set" if os.getenv('ANTHROPIC_API_KEY') else "✗ Not set"
        info_table.add_row("Anthropic API Key", api_key_status)
        
        console.print(info_table)
        
        if not os.getenv('ANTHROPIC_API_KEY'):
            console.print("\n[yellow]⚠️  Set ANTHROPIC_API_KEY in .env file to use the chatbot.[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error getting system info: {e}[/red]")


if __name__ == '__main__':
    cli()