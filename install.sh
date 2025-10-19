#!/bin/bash

# RAG Chatbot Installation Script
# This script sets up the project for development and deployment

set -e  # Exit on any error

echo "🚀 Setting up RAG Chatbot Codebase..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "backend" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check Python version
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_error "Python $required_version or higher is required. Found: $python_version"
    exit 1
fi
print_success "Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv .venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install the package in editable mode
print_status "Installing package in editable mode..."
pip install -e .

# Install development dependencies
print_status "Installing development dependencies..."
pip install -e ".[dev]"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_status "Creating .env file from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file and add your ANTHROPIC_API_KEY"
    else
        print_status "Creating .env file..."
        cat > .env << EOF
# Anthropic API Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
PLAN_MODE=false

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
EOF
        print_warning "Please edit .env file and add your ANTHROPIC_API_KEY"
    fi
else
    print_status ".env file already exists"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p docs
mkdir -p chroma_db
mkdir -p logs

# Test the installation
print_status "Testing installation..."
if python -c "import backend; print('Backend module imported successfully')" 2>/dev/null; then
    print_success "Backend module import test passed"
else
    print_error "Backend module import test failed"
    exit 1
fi

# Check if FastAPI is working
if python -c "from fastapi import FastAPI; print('FastAPI imported successfully')" 2>/dev/null; then
    print_success "FastAPI import test passed"
else
    print_error "FastAPI import test failed"
    exit 1
fi

print_success "Installation completed successfully!"
echo
echo "📋 Next steps:"
echo "1. Edit .env file and add your ANTHROPIC_API_KEY"
echo "2. Activate virtual environment: source .venv/bin/activate"
echo "3. Start the server: ./start_server.sh"
echo "   Or manually: cd backend && uvicorn app:app --reload --port 8000"
echo "4. Open your browser to: http://localhost:8000"
echo
echo "🔧 Development commands:"
echo "  - Run tests: pytest"
echo "  - Format code: black ."
echo "  - Sort imports: isort ."
echo "  - Lint code: flake8 ."
echo
echo "📚 For more information, see README.md"