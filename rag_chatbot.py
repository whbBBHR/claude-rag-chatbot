"""
RAG Chatbot Core Module

This module implements the core functionality for the RAG (Retrieval-Augmented Generation) chatbot,
including document processing, vector storage, and chat interactions.
"""

import os
import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleTextSplitter:
    """Simple text splitter for chunking documents."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at paragraph boundary
            if end < len(text):
                # Look for paragraph breaks within the next 200 characters
                search_end = min(end + 200, len(text))
                paragraph_break = text.rfind('\n\n', end, search_end)
                if paragraph_break > start:
                    end = paragraph_break
                else:
                    # Look for sentence breaks
                    sentence_break = text.rfind('. ', start, end)
                    if sentence_break > start:
                        end = sentence_break + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = max(start + self.chunk_size - self.chunk_overlap, end)
            
            if start >= len(text):
                break
                
        return chunks


class DocumentProcessor:
    """Handles document loading, chunking, and preprocessing."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = SimpleTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        
    def load_documents(self, docs_path: str) -> List[Dict[str, Any]]:
        """Load documents from a directory."""
        docs_path = Path(docs_path)
        documents = []
        
        for file_path in docs_path.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                documents.append({
                    'content': content,
                    'source': str(file_path.name),
                    'path': str(file_path)
                })
                logger.info(f"Loaded document: {file_path.name}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                
        return documents
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split documents into chunks."""
        chunks = []
        chunk_id = 0
        
        for doc in documents:
            text_chunks = self.text_splitter.split_text(doc['content'])
            
            for i, chunk in enumerate(text_chunks):
                chunks.append({
                    'id': chunk_id,
                    'content': chunk,
                    'source': doc['source'],
                    'chunk_index': i,
                    'metadata': {
                        'source': doc['source'],
                        'chunk_index': i,
                        'total_chunks': len(text_chunks),
                        'path': doc.get('path', ''),
                        'created_at': datetime.now().isoformat()
                    }
                })
                chunk_id += 1
                
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks


class VectorStore:
    """Manages vector embeddings and similarity search using ChromaDB."""
    
    def __init__(self, db_path: str = "./chroma_db", embedding_model: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.embedding_model_name = embedding_model
        self.embedding_model = SentenceTransformer(embedding_model)
        self.client = None
        self.collection = None
        self._initialize_db()
        
    def _initialize_db(self):
        """Initialize ChromaDB client and collection."""
        try:
            self.client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.client.get_or_create_collection(
                name="rag_documents",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Initialized ChromaDB at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
            
    def add_documents(self, chunks: List[Dict[str, Any]]):
        """Add document chunks to the vector store."""
        if not chunks:
            logger.warning("No chunks provided to add")
            return
            
        try:
            # Extract text content for embedding
            texts = [chunk['content'] for chunk in chunks]
            
            # Generate embeddings
            logger.info("Generating embeddings...")
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
            
            # Prepare data for ChromaDB
            ids = [str(chunk['id']) for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(chunks)} chunks to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
            
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                        'id': results['ids'][0][i] if results['ids'] else str(i)
                    })
            
            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
            
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            count = self.collection.count()
            return {
                'document_count': count,
                'embedding_model': self.embedding_model_name,
                'db_path': self.db_path
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}


class ClaudeRAGChatbot:
    """Main RAG chatbot class using Claude for generation."""
    
    def __init__(self, vector_store: VectorStore, api_key: Optional[str] = None):
        self.vector_store = vector_store
        self.client = Anthropic(api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))
        self.conversation_history = []
        
    def _count_tokens(self, text: str) -> int:
        """Rough token count estimation."""
        # Rough approximation: 4 characters per token
        return len(text) // 4
            
    def _format_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Format search results into context for the prompt."""
        if not search_results:
            return "No relevant context found."
            
        context_parts = []
        for i, result in enumerate(search_results, 1):
            source = result.get('metadata', {}).get('source', 'Unknown')
            content = result['content']
            
            context_parts.append(f"Source {i} ({source}):\n{content}\n")
            
        return "\n---\n".join(context_parts)
        
    def _create_prompt(self, query: str, context: str) -> str:
        """Create the full prompt for Claude."""
        return f"""You are a helpful AI assistant specializing in machine learning, deep learning, NLP, and RAG systems. You have access to relevant course materials and documentation to answer questions accurately.

Based on the provided context, please answer the user's question. Follow these guidelines:

1. Use the provided context to inform your response
2. If the context doesn't contain relevant information, say so clearly
3. Cite sources when possible (mention the document name)
4. Be accurate and don't make up information not in the context
5. Provide helpful, detailed explanations when appropriate
6. If you're unsure about something, acknowledge the uncertainty

Context:
{context}

Question: {query}

Answer:"""

    def chat(self, query: str, max_chunks: int = 5, model: str = "claude-3-sonnet-20240229") -> Dict[str, Any]:
        """Main chat function that retrieves relevant documents and generates response."""
        try:
            # Search for relevant documents
            search_results = self.vector_store.search(query, n_results=max_chunks)
            
            # Format context
            context = self._format_context(search_results)
            
            # Create prompt
            prompt = self._create_prompt(query, context)
            
            # Count tokens (approximate)
            token_count = self._count_tokens(prompt)
            
            # Generate response using Claude
            response = self.client.messages.create(
                model=model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            answer = response.content[0].text
            
            # Store in conversation history
            conversation_entry = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'answer': answer,
                'sources': [r.get('metadata', {}).get('source', 'Unknown') for r in search_results],
                'chunks_used': len(search_results),
                'model': model,
                'token_count': token_count
            }
            
            self.conversation_history.append(conversation_entry)
            
            # Return detailed response
            return {
                'answer': answer,
                'sources': search_results,
                'chunks_retrieved': len(search_results),
                'model_used': model,
                'token_count': token_count,
                'query': query,
                'timestamp': conversation_entry['timestamp']
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                'answer': f"Sorry, I encountered an error: {str(e)}",
                'sources': [],
                'chunks_retrieved': 0,
                'model_used': model,
                'error': str(e)
            }
            
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history
        
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")
        
    def save_history(self, filepath: str):
        """Save conversation history to file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
            logger.info(f"Conversation history saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving history: {e}")


def initialize_rag_system(docs_path: str = "./docs", db_path: str = "./chroma_db") -> ClaudeRAGChatbot:
    """Initialize the complete RAG system."""
    logger.info("Initializing RAG system...")
    
    # Check if API key is available
    if not os.getenv('ANTHROPIC_API_KEY'):
        logger.warning("No ANTHROPIC_API_KEY found. Please set your API key in the .env file.")
    
    # Initialize components
    processor = DocumentProcessor()
    vector_store = VectorStore(db_path=db_path)
    
    # Check if vector store already has documents
    collection_info = vector_store.get_collection_info()
    
    if collection_info.get('document_count', 0) == 0:
        logger.info("Vector store is empty, processing documents...")
        
        # Load and process documents
        documents = processor.load_documents(docs_path)
        if not documents:
            raise ValueError(f"No documents found in {docs_path}")
            
        chunks = processor.chunk_documents(documents)
        vector_store.add_documents(chunks)
        
        logger.info(f"Processed {len(documents)} documents into {len(chunks)} chunks")
    else:
        logger.info(f"Vector store already contains {collection_info['document_count']} documents")
    
    # Initialize chatbot
    chatbot = ClaudeRAGChatbot(vector_store)
    
    logger.info("RAG system initialized successfully!")
    return chatbot


if __name__ == "__main__":
    # Example usage
    try:
        chatbot = initialize_rag_system()
        
        # Test query
        result = chatbot.chat("What is machine learning?")
        print(f"Answer: {result['answer']}")
        print(f"Sources used: {len(result['sources'])}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")