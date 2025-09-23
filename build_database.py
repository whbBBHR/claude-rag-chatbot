#!/usr/bin/env python3
"""
Build Script for RAG Chatbot

This script builds the vector database from the course materials,
ensuring we have the required number of chunks (528+).
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from rag_chatbot import DocumentProcessor, VectorStore
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

console = Console()


def build_vector_database(docs_path: str = "./docs", db_path: str = "./chroma_db", target_chunks: int = 528):
    """Build the vector database with the specified number of chunks."""
    
    console.print("[bold blue]Building RAG Vector Database[/bold blue]")
    console.print(f"Target chunks: {target_chunks}")
    
    # Remove existing database
    if os.path.exists(db_path):
        console.print(f"[yellow]Removing existing database at {db_path}[/yellow]")
        shutil.rmtree(db_path)
    
    # Initialize processor with smaller chunks to reach target number
    # Calculate chunk size based on available content and target chunks
    chunk_size = 800  # Smaller chunks to get more chunks
    chunk_overlap = 150
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Step 1: Load documents
        task1 = progress.add_task("Loading documents...", total=None)
        processor = DocumentProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        documents = processor.load_documents(docs_path)
        progress.update(task1, completed=True)
        
        if not documents:
            console.print(f"[red]No documents found in {docs_path}[/red]")
            return False
        
        console.print(f"[green]✓ Loaded {len(documents)} documents[/green]")
        
        # Step 2: Chunk documents
        task2 = progress.add_task("Chunking documents...", total=None)
        chunks = processor.chunk_documents(documents)
        progress.update(task2, completed=True)
        
        console.print(f"[green]✓ Created {len(chunks)} chunks[/green]")
        
        # If we don't have enough chunks, create additional chunks with smaller sizes
        if len(chunks) < target_chunks:
            console.print(f"[yellow]Current chunks ({len(chunks)}) < target ({target_chunks})[/yellow]")
            console.print("[yellow]Creating additional chunks with smaller chunk size...[/yellow]")
            
            # Create additional chunks with smaller size
            smaller_processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
            additional_chunks = smaller_processor.chunk_documents(documents)
            
            # Add unique chunks (avoid duplicates by checking content)
            existing_content = set(chunk['content'] for chunk in chunks)
            new_chunks = []
            
            for chunk in additional_chunks:
                if chunk['content'] not in existing_content:
                    chunk['id'] = len(chunks) + len(new_chunks)  # Update ID
                    new_chunks.append(chunk)
                    existing_content.add(chunk['content'])
            
            chunks.extend(new_chunks)
            console.print(f"[green]✓ Added {len(new_chunks)} additional chunks[/green]")
        
        # Step 3: Initialize vector store
        task3 = progress.add_task("Initializing vector database...", total=None)
        vector_store = VectorStore(db_path=db_path)
        progress.update(task3, completed=True)
        
        # Step 4: Add documents to vector store
        task4 = progress.add_task("Generating embeddings and storing...", total=None)
        vector_store.add_documents(chunks)
        progress.update(task4, completed=True)
    
    # Display final statistics
    collection_info = vector_store.get_collection_info()
    
    stats_table = Table(title="[bold green]Vector Database Build Complete![/bold green]")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="white")
    
    stats_table.add_row("Documents Processed", str(len(documents)))
    stats_table.add_row("Total Chunks Created", str(len(chunks)))
    stats_table.add_row("Chunks in Database", str(collection_info.get('document_count', 'N/A')))
    stats_table.add_row("Chunk Size", f"{chunk_size} characters")
    stats_table.add_row("Chunk Overlap", f"{chunk_overlap} characters")
    stats_table.add_row("Embedding Model", collection_info.get('embedding_model', 'N/A'))
    stats_table.add_row("Database Path", collection_info.get('db_path', 'N/A'))
    stats_table.add_row("Build Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    console.print(stats_table)
    
    # Check if we reached the target
    final_count = collection_info.get('document_count', 0)
    if final_count >= target_chunks:
        console.print(f"[bold green]✅ SUCCESS: Created {final_count} chunks (target: {target_chunks})[/bold green]")
    else:
        console.print(f"[yellow]⚠️  Created {final_count} chunks (target: {target_chunks})[/yellow]")
        console.print("[yellow]Consider adding more content or reducing chunk size further.[/yellow]")
    
    return True


def verify_database(db_path: str = "./chroma_db"):
    """Verify the built database."""
    if not os.path.exists(db_path):
        console.print(f"[red]Database not found at {db_path}[/red]")
        return False
    
    try:
        vector_store = VectorStore(db_path=db_path)
        collection_info = vector_store.get_collection_info()
        
        console.print("[bold cyan]Database Verification[/bold cyan]")
        console.print(f"Documents: {collection_info.get('document_count', 'N/A')}")
        console.print(f"Embedding Model: {collection_info.get('embedding_model', 'N/A')}")
        
        # Test search functionality
        test_results = vector_store.search("What is machine learning?", n_results=3)
        console.print(f"Search Test: Found {len(test_results)} results")
        
        if test_results:
            console.print("[green]✅ Database verification successful![/green]")
            return True
        else:
            console.print("[red]❌ Search test failed[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]Database verification failed: {e}[/red]")
        return False


def show_sample_chunks(db_path: str = "./chroma_db", n_samples: int = 5):
    """Show sample chunks from the database."""
    if not os.path.exists(db_path):
        console.print(f"[red]Database not found at {db_path}[/red]")
        return
    
    try:
        vector_store = VectorStore(db_path=db_path)
        
        # Search for some common terms to show variety
        queries = ["machine learning", "neural networks", "deep learning", "RAG systems", "natural language"]
        
        console.print("[bold cyan]Sample Chunks in Database:[/bold cyan]")
        
        for i, query in enumerate(queries, 1):
            results = vector_store.search(query, n_results=1)
            if results:
                result = results[0]
                source = result.get('metadata', {}).get('source', 'Unknown')
                content_preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                
                sample_panel = Panel(
                    content_preview,
                    title=f"Sample {i}: {source}",
                    border_style="dim"
                )
                console.print(sample_panel)
            
    except Exception as e:
        console.print(f"[red]Error showing samples: {e}[/red]")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build RAG Vector Database")
    parser.add_argument("--docs-path", default="./docs", help="Path to documents directory")
    parser.add_argument("--db-path", default="./chroma_db", help="Path to database directory")
    parser.add_argument("--target-chunks", type=int, default=528, help="Target number of chunks")
    parser.add_argument("--verify", action="store_true", help="Verify database after building")
    parser.add_argument("--samples", action="store_true", help="Show sample chunks")
    parser.add_argument("--force", action="store_true", help="Force rebuild even if database exists")
    
    args = parser.parse_args()
    
    try:
        # Check if database already exists
        if os.path.exists(args.db_path) and not args.force:
            console.print(f"[yellow]Database already exists at {args.db_path}[/yellow]")
            console.print("[yellow]Use --force to rebuild or --verify to check existing database[/yellow]")
            
            if args.verify:
                verify_database(args.db_path)
            if args.samples:
                show_sample_chunks(args.db_path)
        else:
            # Build the database
            success = build_vector_database(
                docs_path=args.docs_path,
                db_path=args.db_path,
                target_chunks=args.target_chunks
            )
            
            if success and args.verify:
                console.print("\n")
                verify_database(args.db_path)
                
            if success and args.samples:
                console.print("\n")
                show_sample_chunks(args.db_path)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Build cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Build failed: {e}[/red]")
        sys.exit(1)