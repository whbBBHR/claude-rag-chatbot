#!/usr/bin/env python3
"""
Git Bundle Creator for RAG Chatbot

Creates a complete git bundle of the RAG chatbot repository
including all history, branches, and tags.
"""

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import argparse
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

console = Console()


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=check
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode


def create_git_bundle(repo_path=".", bundle_name=None, include_all_refs=True):
    """Create a git bundle of the repository."""
    
    repo_path = Path(repo_path).resolve()
    
    if not (repo_path / ".git").exists():
        console.print(f"[red]No git repository found at {repo_path}[/red]")
        return False
    
    # Generate bundle name if not provided
    if not bundle_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_name = f"claude-rag-chatbot_{timestamp}.bundle"
    
    # Ensure bundle name ends with .bundle
    if not bundle_name.endswith('.bundle'):
        bundle_name += '.bundle'
    
    bundle_path = repo_path / bundle_name
    
    console.print("[bold blue]Creating Git Bundle[/bold blue]")
    console.print(f"Repository: {repo_path}")
    console.print(f"Bundle: {bundle_path}")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Get repository information
        task1 = progress.add_task("Gathering repository information...", total=None)
        
        # Get current branch
        current_branch, _, _ = run_command("git rev-parse --abbrev-ref HEAD", cwd=repo_path)
        
        # Get all branches
        branches_output, _, _ = run_command("git branch -a", cwd=repo_path)
        branches = [line.strip().replace('* ', '') for line in branches_output.split('\n') if line.strip()]
        
        # Get all tags
        tags_output, _, _ = run_command("git tag", cwd=repo_path)
        tags = [line.strip() for line in tags_output.split('\n') if line.strip()]
        
        # Get commit count
        commit_count, _, _ = run_command("git rev-list --count HEAD", cwd=repo_path)
        
        progress.update(task1, completed=True)
        
        # Create the bundle
        task2 = progress.add_task("Creating bundle...", total=None)
        
        if include_all_refs:
            # Include all branches and tags
            bundle_cmd = f"git bundle create {bundle_name} --all"
        else:
            # Include only current branch
            bundle_cmd = f"git bundle create {bundle_name} {current_branch}"
        
        stdout, stderr, returncode = run_command(bundle_cmd, cwd=repo_path)
        
        progress.update(task2, completed=True)
    
    if returncode == 0:
        # Get bundle size
        bundle_size = bundle_path.stat().st_size / (1024 * 1024)  # MB
        
        # Display success information
        success_info = f"""
**Bundle Created Successfully!**

📁 **File:** {bundle_name}
📏 **Size:** {bundle_size:.2f} MB
🌿 **Current Branch:** {current_branch}
📊 **Commits:** {commit_count}
🌲 **Branches:** {len(branches)}
🏷️  **Tags:** {len(tags)}

**How to use this bundle:**
```bash
# Clone from bundle
git clone {bundle_name} claude-rag-chatbot

# Or add as remote to existing repo
git remote add bundle {bundle_name}
git fetch bundle
```

**Bundle contains:**
- Complete git history
- All branches and commits
- All course materials (4 documents)
- RAG chatbot implementation
- Vector database setup
- CLI tools (external and local Claude)
- Documentation and setup instructions
"""
        
        panel = Panel(
            success_info,
            title="[bold green]Git Bundle Complete[/bold green]",
            border_style="green"
        )
        console.print(panel)
        
        return True
    else:
        console.print(f"[red]Failed to create bundle: {stderr}[/red]")
        return False


def verify_bundle(bundle_path):
    """Verify that the bundle is valid."""
    console.print("[bold cyan]Verifying Bundle[/bold cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("Verifying bundle integrity...", total=None)
        
        # Verify bundle
        stdout, stderr, returncode = run_command(f"git bundle verify {bundle_path}")
        
        progress.update(task, completed=True)
    
    if returncode == 0:
        console.print("[green]✅ Bundle verification successful![/green]")
        
        # Show bundle contents
        console.print("\n[bold cyan]Bundle Contents:[/bold cyan]")
        list_stdout, _, _ = run_command(f"git bundle list-heads {bundle_path}")
        if list_stdout:
            for line in list_stdout.split('\n'):
                if line.strip():
                    console.print(f"  • {line.strip()}")
        
        return True
    else:
        console.print(f"[red]❌ Bundle verification failed: {stderr}[/red]")
        return False


def show_bundle_info(bundle_path):
    """Show information about an existing bundle."""
    if not Path(bundle_path).exists():
        console.print(f"[red]Bundle not found: {bundle_path}[/red]")
        return
    
    console.print(f"[bold cyan]Bundle Information: {bundle_path}[/bold cyan]")
    
    # Get bundle size
    bundle_size = Path(bundle_path).stat().st_size / (1024 * 1024)  # MB
    console.print(f"Size: {bundle_size:.2f} MB")
    
    # List heads
    stdout, stderr, returncode = run_command(f"git bundle list-heads {bundle_path}")
    if returncode == 0 and stdout:
        console.print("\nRefs in bundle:")
        for line in stdout.split('\n'):
            if line.strip():
                console.print(f"  • {line.strip()}")
    
    # Verify bundle
    verify_bundle(bundle_path)


def main():
    parser = argparse.ArgumentParser(description="Create git bundle for RAG chatbot")
    parser.add_argument("--repo-path", default=".", help="Path to git repository")
    parser.add_argument("--bundle-name", help="Name for the bundle file")
    parser.add_argument("--current-branch-only", action="store_true", 
                       help="Include only current branch (not all refs)")
    parser.add_argument("--verify", action="store_true", 
                       help="Verify bundle after creation")
    parser.add_argument("--info", help="Show info about existing bundle")
    
    args = parser.parse_args()
    
    try:
        if args.info:
            show_bundle_info(args.info)
            return
        
        # Create bundle
        success = create_git_bundle(
            repo_path=args.repo_path,
            bundle_name=args.bundle_name,
            include_all_refs=not args.current_branch_only
        )
        
        if success and args.verify:
            bundle_name = args.bundle_name
            if not bundle_name:
                # Find the most recent bundle
                repo_path = Path(args.repo_path)
                bundles = list(repo_path.glob("*.bundle"))
                if bundles:
                    bundle_name = str(max(bundles, key=lambda p: p.stat().st_mtime))
            
            if bundle_name:
                console.print("\n")
                verify_bundle(bundle_name)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Bundle creation cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()