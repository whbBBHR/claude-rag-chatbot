"""
RAG Chatbot Backend Package

This package contains the backend components for the RAG-based chatbot system.
"""

__version__ = "0.1.0"
__author__ = "RAG Chatbot Team"

# Import main components for easier access
try:
    from .app import app
    from .rag_system import RAGSystem
    from .config import config
except ImportError:
    # Handle case where dependencies aren't installed yet
    pass

__all__ = ["app", "RAGSystem", "config"]