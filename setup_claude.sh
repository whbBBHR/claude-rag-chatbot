#!/bin/bash
# Setup script for Claude commands

echo "Setting up Claude commands..."

# Add ~/.local/bin to PATH for current session
export PATH="$HOME/.local/bin:$PATH"

# Try to add to .zshrc if possible
if [ -w ~/.zshrc ]; then
    # Check if already added
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.zshrc; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        echo "✅ Added ~/.local/bin to PATH in ~/.zshrc"
    else
        echo "✅ PATH already configured in ~/.zshrc"
    fi
else
    echo "⚠️  Cannot write to ~/.zshrc (permission denied)"
    echo "   Please add this line manually to your ~/.zshrc:"
    echo '   export PATH="$HOME/.local/bin:$PATH"'
fi

echo ""
echo "🎉 Claude commands are now available:"
echo "   claude        - External Anthropic API (general questions)"
echo "   claude-local  - Local RAG system (course-specific questions)"
echo ""
echo "Test them:"
echo '   claude "What is machine learning?"'
echo '   claude-local "What is the MCP course about?"'