"""
RAG Chatbot Codebase

A retrieval-augmented generation (RAG) chatbot system for course materials.
"""

__version__ = "0.1.0"
__author__ = "RAG Chatbot Team"

# Package-level imports
try:
    from backend import RAGSystem, config
except ImportError:
    # Handle case where dependencies aren't installed yet
    pass