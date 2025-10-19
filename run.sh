#!/bin/bash

# RAG Chatbot Server Runner
# This script starts the FastAPI server for the RAG chatbot

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "backend" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Create necessary directories
mkdir -p docs 
mkdir -p chroma_db
mkdir -p logs

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "Error: backend directory not found"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_warning "Virtual environment not found. Run ./install.sh first."
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Check if package is installed
if ! python -c "import backend" 2>/dev/null; then
    print_warning "Backend package not installed. Installing in editable mode..."
    pip install -e .
fi

print_status "Starting Course Materials RAG System..."

# Check for API key
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating from template..."
    cp .env.example .env 2>/dev/null || echo "ANTHROPIC_API_KEY=your-key-here" > .env
fi

print_warning "Make sure you have set your ANTHROPIC_API_KEY in .env"

# Set default values
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}

print_status "Server will start on http://${HOST}:${PORT}"

# Change to backend directory and start the server
cd backend

# Check if uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    print_status "Using python -m uvicorn..."
    python -m uvicorn app:app --reload --host $HOST --port $PORT
else
    print_status "Using uvicorn directly..."
    uvicorn app:app --reload --host $HOST --port $PORT
fi