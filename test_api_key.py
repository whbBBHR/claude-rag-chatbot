#!/usr/bin/env python3
"""API Key validation script"""

import anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')

print(f'Testing API key: {api_key[:15]}...' if api_key else 'No API key found')
print(f'Key length: {len(api_key)} characters' if api_key else 'API key is empty')

if not api_key:
    print('❌ No API key found in environment')
    exit(1)

try:
    client = anthropic.Anthropic(api_key=api_key)
    
    # Make a simple test request
    print('🔄 Testing API connection...')
    response = client.messages.create(
        model='claude-3-5-sonnet-20241022',
        max_tokens=20,
        messages=[{'role': 'user', 'content': 'Say hello'}]
    )
    
    print('✅ API key is VALID!')
    print(f'✅ Response: {response.content[0].text}')
    
except anthropic.AuthenticationError as e:
    print('❌ API key is INVALID')
    print(f'Authentication error: {e}')
    
except anthropic.RateLimitError as e:
    print('⚠️ API key is valid but rate limited')
    print(f'Rate limit error: {e}')
    
except anthropic.APIError as e:
    print('⚠️ API key might be valid but there was an API error')
    print(f'API error: {e}')
    
except Exception as e:
    print(f'❌ Unexpected error: {e}')