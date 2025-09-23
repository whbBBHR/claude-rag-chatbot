#!/usr/bin/env python3
"""
Local Claude command that queries the RAG system with course materials.
This gives you access to the course content that's loaded in your vector database.
"""

import sys
import requests
import json

def query_local_rag(question):
    """Query the local RAG system running on port 8000"""
    try:
        response = requests.post(
            "http://localhost:8000/api/query",
            json={"query": question},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("answer", "No response received")
        else:
            return f"Error: Server returned status code {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to RAG server. Is it running on port 8000?"
    except requests.exceptions.Timeout:
        return "Error: Request timed out"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: claude-local 'your question here'")
        print("This queries your local RAG system with course materials.")
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    print(f"Querying local RAG system: {question}")
    print("-" * 60)
    
    response = query_local_rag(question)
    print(response)

if __name__ == "__main__":
    main()