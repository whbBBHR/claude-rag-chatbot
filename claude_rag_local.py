#!/usr/bin/env python3
"""
Local Claude RAG Chatbot

This is a simulation of a local Claude command for the RAG chatbot.
In a real scenario, this would use a locally hosted model like Ollama or similar.
For demonstration purposes, it uses a simplified approach.
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
import json

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from rag_chatbot import VectorStore, DocumentProcessor

console = Console()


class LocalRAGChatbot:
    """Local RAG chatbot that works without external API calls."""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.conversation_history = []
        
    def _create_local_response(self, query: str, search_results: list) -> str:
        """Create a response using retrieved context (simplified version)."""
        if not search_results:
            return "I don't have relevant information to answer this question. Please check if the documents are properly loaded."
        
        # Extract key information from the search results
        context_info = []
        for result in search_results[:3]:  # Use top 3 results
            source = result.get('metadata', {}).get('source', 'Unknown')
            content = result['content'][:500]  # Limit content length
            context_info.append(f"From {source}:\n{content}")
        
        # Simple template-based response
        response = f"""Based on the available course materials, here's what I found about your question: "{query}"

{chr(10).join(context_info)}

This information comes from the course materials in the vector database. For more detailed explanations, please refer to the full documents."""
        
        return response
    
    def chat(self, query: str, max_chunks: int = 5) -> dict:
        """Chat function for local mode."""
        try:
            # Search for relevant documents
            search_results = self.vector_store.search(query, n_results=max_chunks)
            
            # Generate local response
            answer = self._create_local_response(query, search_results)
            
            # Store in conversation history
            conversation_entry = {
                'timestamp': str(pd.Timestamp.now()),
                'query': query,
                'answer': answer,
                'sources': [r.get('metadata', {}).get('source', 'Unknown') for r in search_results],
                'chunks_used': len(search_results),
                'mode': 'local'
            }
            
            self.conversation_history.append(conversation_entry)
            
            return {
                'answer': answer,
                'sources': search_results,
                'chunks_retrieved': len(search_results),
                'mode': 'local',
                'query': query,
                'timestamp': conversation_entry['timestamp']
            }
            
        except Exception as e:
            return {
                'answer': f"Sorry, I encountered an error: {str(e)}",
                'sources': [],
                'chunks_retrieved': 0,
                'mode': 'local',
                'error': str(e)
            }
    
    def get_conversation_history(self):
        """Get conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


def display_local_welcome():
    """Display welcome message for local mode."""
    welcome_text = """
# Local RAG Chatbot 🏠

Welcome to the Local RAG chatbot! This version works entirely offline using your local documents.

**Features:**
- No API key required
- Works completely offline
- Uses the same vector database as the Claude version
- Simple template-based responses using retrieved context

**Commands:**
- Type your question and press Enter
- Type 'quit' or 'exit' to leave
- Type 'history' to see conversation history
- Type 'clear' to clear conversation history
- Type 'stats' to see system statistics

**Note:** This local version provides basic responses based on document retrieval.
For more sophisticated answers, use the Claude version with an API key.
"""
    
    panel = Panel(
        Markdown(welcome_text),
        title="[bold blue]Local RAG Chatbot[/bold blue]",
        border_style="blue"
    )
    console.print(panel)


def display_local_answer(result: dict):
    """Display the local chatbot's answer."""
    # Display the main answer
    answer_panel = Panel(
        result['answer'],
        title="[bold green]Answer (Local Mode)[/bold green]",
        border_style="green"
    )
    console.print(answer_panel)
    
    # Display sources if available
    if result.get('sources') and len(result['sources']) > 0:
        console.print(f"\n[bold cyan]Sources used ({len(result['sources'])}):[/bold cyan]")
        sources = set()  # Remove duplicates
        for source in result['sources']:
            source_name = source.get('metadata', {}).get('source', 'Unknown')
            sources.add(source_name)
        
        for source in sorted(sources):
            console.print(f"  • {source}")
    
    # Display metadata
    console.print(f"\n[dim]Mode: {result.get('mode', 'local')} | Chunks: {result.get('chunks_retrieved', 0)}[/dim]")


@click.group()
def cli():
    """Local Claude RAG Chatbot - Offline version of the RAG chatbot."""
    pass


@cli.command()
@click.option('--docs-path', default='./docs', help='Path to documents directory')
@click.option('--db-path', default='./chroma_db', help='Path to ChromaDB database')
@click.option('--max-chunks', default=5, help='Maximum number of chunks to retrieve')
def chat(docs_path: str, db_path: str, max_chunks: int):
    """Start an interactive local chat session."""
    try:
        # Check if vector database exists
        if not os.path.exists(db_path):
            console.print(f"[red]Vector database not found at {db_path}[/red]")
            console.print("[yellow]Please run 'claude-rag build' first to create the database.[/yellow]")
            sys.exit(1)
        
        # Initialize the local system
        console.print("[yellow]Initializing local RAG system...[/yellow]")
        vector_store = VectorStore(db_path=db_path)
        chatbot = LocalRAGChatbot(vector_store)
        console.print("[green]✓ Local RAG system initialized successfully![/green]")
        
        # Display welcome message
        display_local_welcome()
        
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
                elif query_lower == 'history':
                    history = chatbot.get_conversation_history()
                    if not history:
                        console.print("[yellow]No conversation history available.[/yellow]")
                    else:
                        console.print(f"\n[bold cyan]Conversation History ({len(history)} entries):[/bold cyan]")
                        for i, entry in enumerate(history, 1):
                            console.print(f"\n{i}. Q: {entry['query'][:100]}...")
                            console.print(f"   A: {entry['answer'][:200]}...")
                    continue
                elif query_lower == 'clear':
                    chatbot.clear_history()
                    console.print("[green]✓ Conversation history cleared.[/green]")
                    continue
                elif query_lower == 'stats':
                    collection_info = vector_store.get_collection_info()
                    console.print(f"\n[bold cyan]System Statistics:[/bold cyan]")
                    console.print(f"Documents: {collection_info.get('document_count', 'N/A')}")
                    console.print(f"Embedding Model: {collection_info.get('embedding_model', 'N/A')}")
                    console.print(f"Conversations: {len(chatbot.get_conversation_history())}")
                    continue
                
                # Process the query
                console.print("[yellow]Searching documents...[/yellow]")
                result = chatbot.chat(query, max_chunks=max_chunks)
                
                # Display the result
                display_local_answer(result)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                
    except Exception as e:
        console.print(f"[red]Failed to initialize local RAG system: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('query', required=True)
@click.option('--docs-path', default='./docs', help='Path to documents directory')
@click.option('--db-path', default='./chroma_db', help='Path to ChromaDB database')
@click.option('--max-chunks', default=5, help='Maximum number of chunks to retrieve')
@click.option('--output', help='Output file path (optional)')
def query(query: str, docs_path: str, db_path: str, max_chunks: int, output: Optional[str]):
    """Ask a single question using local mode."""
    try:
        # Check if vector database exists
        if not os.path.exists(db_path):
            console.print(f"[red]Vector database not found at {db_path}[/red]")
            sys.exit(1)
        
        # Initialize the local system
        vector_store = VectorStore(db_path=db_path)
        chatbot = LocalRAGChatbot(vector_store)
        
        # Process the query
        result = chatbot.chat(query, max_chunks=max_chunks)
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(f"Query: {query}\n\n")
                f.write(f"Answer (Local Mode): {result['answer']}\n\n")
                if result.get('sources'):
                    sources = set(s.get('metadata', {}).get('source', 'Unknown') for s in result['sources'])
                    f.write(f"Sources: {', '.join(sorted(sources))}\n")
            console.print(f"[green]✓ Results saved to {output}[/green]")
        else:
            display_local_answer(result)
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    # Need to import pandas for timestamp
    try:
        import pandas as pd
    except ImportError:
        # Fallback to datetime if pandas not available
        from datetime import datetime
        class pd:
            class Timestamp:
                @staticmethod
                def now():
                    return datetime.now()
    
    cli()