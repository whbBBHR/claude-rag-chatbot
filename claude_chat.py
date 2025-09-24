#!/usr/bin/env python3
"""
Claude CLI tool for interacting with Anthropic's Claude API.
Provides command-line access to Claude conversations.
"""

import sys
import requests
import json
import os
from pathlib import Path

def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def chat_with_claude(message):
    """Send a message to Claude and return the response"""
    load_env()  # Load .env file
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return "Error: ANTHROPIC_API_KEY environment variable not set. Please set it in your .env file."
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": message}]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['content'][0]['text']
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: claude 'your message here'")
        sys.exit(1)
    
    message = " ".join(sys.argv[1:])
    response = chat_with_claude(message)
    print(f"Claude: {response}")

if __name__ == "__main__":
    main()