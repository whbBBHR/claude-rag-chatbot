#!/usr/bin/env python3
"""
Command-line interface for the RAG Chatbot system
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="RAG Chatbot CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install the project")
    install_parser.add_argument("--dev", action="store_true", help="Install development dependencies")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start the server")
    server_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    server_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    server_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    
    # Format command
    format_parser = subparsers.add_parser("format", help="Format code")
    format_parser.add_argument("--check", action="store_true", help="Check formatting only")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    if args.command == "install":
        install_project(args.dev)
    elif args.command == "server":
        start_server(args.host, args.port, args.reload)
    elif args.command == "test":
        run_tests(args.coverage)
    elif args.command == "format":
        format_code(args.check)

def install_project(dev=False):
    """Install the project"""
    print("🚀 Installing RAG Chatbot project...")
    
    # Install main package
    cmd = [sys.executable, "-m", "pip", "install", "-e", "."]
    if dev:
        cmd.append("[dev]")
    
    subprocess.run(cmd, check=True)
    print("✅ Installation completed!")

def start_server(host="0.0.0.0", port=8000, reload=True):
    """Start the FastAPI server"""
    print(f"🚀 Starting server on {host}:{port}")
    
    # Ensure we're in the backend directory
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        sys.exit(1)
    
    os.chdir(backend_dir)
    
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app:app", 
        "--host", host, 
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def run_tests(coverage=False):
    """Run tests"""
    print("🧪 Running tests...")
    
    cmd = [sys.executable, "-m", "pytest"]
    if coverage:
        cmd.extend(["--cov=backend", "--cov-report=html"])
    
    subprocess.run(cmd)

def format_code(check=False):
    """Format code with black and isort"""
    print("🎨 Formatting code...")
    
    # Black
    black_cmd = [sys.executable, "-m", "black"]
    if check:
        black_cmd.append("--check")
    black_cmd.append(".")
    
    # isort
    isort_cmd = [sys.executable, "-m", "isort"]
    if check:
        isort_cmd.append("--check-only")
    isort_cmd.append(".")
    
    subprocess.run(black_cmd)
    subprocess.run(isort_cmd)
    
    if not check:
        print("✅ Code formatted!")

if __name__ == "__main__":
    main()