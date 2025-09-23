#!/usr/bin/env python3
"""
Claude CLI tool for interacting with Anthropic's Claude API.
Provides command-line access to Claude conversations.
"""

import sys
import requests
import json

def chat_with_claude(message):
    """Send a message to Claude and return the response"""
    api_key = "YOUR_API_KEY_HERE"  # This will be replaced with actual key during setup
    
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