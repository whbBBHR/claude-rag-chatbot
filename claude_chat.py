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

def process_file_references(message):
    """Process @file/ or @directory/ references in the message"""
    import re
    import glob
    
    # Find all @path references in the message
    file_refs = re.findall(r'@([^\s]+)', message)
    
    processed_message = message
    for ref in file_refs:
        try:
            # Handle directory references
            if ref.endswith('/'):
                # Get all files in directory
                pattern = f"{ref}*"
                files = glob.glob(pattern)
                if files:
                    file_contents = []
                    for file_path in sorted(files):
                        if os.path.isfile(file_path):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    file_contents.append(f"=== {file_path} ===\n{content}\n")
                            except Exception as e:
                                file_contents.append(f"=== {file_path} ===\nError reading file: {e}\n")
                    
                    file_context = "\n".join(file_contents)
                    processed_message = processed_message.replace(f'@{ref}', f'\n\nHere are the contents of {ref}:\n{file_context}\n')
                else:
                    processed_message = processed_message.replace(f'@{ref}', f'(Directory {ref} not found or empty)')
            
            # Handle single file references
            elif os.path.isfile(ref):
                try:
                    with open(ref, 'r', encoding='utf-8') as f:
                        content = f.read()
                        processed_message = processed_message.replace(f'@{ref}', f'\n\nContents of {ref}:\n{content}\n')
                except Exception as e:
                    processed_message = processed_message.replace(f'@{ref}', f'(Error reading {ref}: {e})')
            else:
                processed_message = processed_message.replace(f'@{ref}', f'(File {ref} not found)')
                
        except Exception as e:
            processed_message = processed_message.replace(f'@{ref}', f'(Error processing {ref}: {e})')
    
    return processed_message

def main():
    if len(sys.argv) < 2:
        print("Usage: claude [--plan] 'your message here'")
        print("You can reference files with @filename or directories with @dirname/")
        print("Use --plan for step-by-step reasoning mode")
        sys.exit(1)
    
    # Check for plan mode flag
    plan_mode = False
    args = sys.argv[1:]
    
    if '--plan' in args:
        plan_mode = True
        args.remove('--plan')
    
    if not args:
        print("Error: No message provided after flags")
        sys.exit(1)
    
    message = " ".join(args)
    processed_message = process_file_references(message)
    
    # Add planning prompt if plan mode is enabled
    if plan_mode:
        processed_message = f"""Please approach this request using step-by-step reasoning. Before providing your final answer, show your thinking process by:
1. Understanding what is being asked
2. Identifying what information you need
3. Planning your approach
4. Working through the steps
5. Providing your final answer

Request: {processed_message}"""
    
    response = chat_with_claude(processed_message)
    
    if plan_mode:
        print(f"Claude (Plan Mode): {response}")
    else:
        print(f"Claude: {response}")

if __name__ == "__main__":
    main()