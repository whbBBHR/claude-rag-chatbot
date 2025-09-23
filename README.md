# Claude RAG Chatbot 🤖

A complete **Retrieval-Augmented Generation (RAG)** chatbot powered by **Claude AI** with comprehensive course materials on Machine Learning, Deep Learning, NLP, and RAG systems.

## ✅ Features Complete

- ✅ **Complete working RAG chatbot** with Claude integration
- ✅ **All 4 course materials** (35,000+ words of ML/AI content)
- ✅ **Both Claude commands** (external API + local simulation)
- ✅ **Pre-built vector database** with 528+ chunks
- ✅ **All fixes and improvements** with error handling
- ✅ **Full git history** with bundle creation option
- ✅ **Easy setup** - just add your API key!

## 📚 Course Materials Included

1. **Introduction to Machine Learning** (`01_introduction_to_ml.md`)
   - Types of ML (supervised, unsupervised, reinforcement)
   - The ML process and key concepts
   - Algorithms and applications
   - Ethical considerations

2. **Deep Learning Fundamentals** (`02_deep_learning.md`)
   - Neural networks and architectures
   - CNNs, RNNs, Transformers
   - Training techniques and optimization
   - Modern applications

3. **Natural Language Processing** (`03_nlp_fundamentals.md`)
   - Text processing and analysis
   - Traditional and modern NLP approaches
   - BERT, GPT, and transformer models
   - NLP applications and challenges

4. **Retrieval-Augmented Generation** (`04_rag_systems.md`)
   - RAG architecture and components
   - Vector databases and embeddings
   - Advanced RAG techniques
   - Implementation best practices

## 🚀 Quick Start

### 1. Clone or Download

```bash
# Option A: Clone from GitHub
git clone https://github.com/whbBBHR/claude-rag-chatbot.git
cd claude-rag-chatbot

# Option B: Clone from bundle (if provided)
git clone claude-rag-chatbot_YYYYMMDD_HHMMSS.bundle claude-rag-chatbot
cd claude-rag-chatbot
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set Up Your API Key

```bash
# Copy the environment template
cp .env.template .env

# Edit .env and add your Anthropic API key
# Get your key from: https://console.anthropic.com/
```

**Edit `.env` file:**
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 4. Build the Vector Database

```bash
# Build the pre-indexed vector database (528+ chunks)
python build_database.py --verify --samples
```

### 5. Start Chatting!

```bash
# Interactive chat with Claude (requires API key)
python claude_rag.py chat

# OR use local mode (no API key required)
python claude_rag_local.py chat
```

## 🛠️ Usage Guide

### Interactive Chat Mode

```bash
# Start interactive session with Claude
python claude_rag.py chat

# Start local mode (offline, no API required)
python claude_rag_local.py chat
```

**Chat Commands:**
- Type your question and press Enter
- `help` - Show help message
- `history` - View conversation history
- `clear` - Clear conversation history
- `stats` - Show system statistics
- `quit` / `exit` - Exit the chat

### Single Query Mode

```bash
# Ask a single question with Claude
python claude_rag.py query "What is machine learning?"

# Local mode single query
python claude_rag_local.py query "Explain neural networks"

# Save response to file
python claude_rag.py query "What is RAG?" --output response.txt

# JSON output format
python claude_rag.py query "What is deep learning?" --json
```

### Database Management

```bash
# Build/rebuild vector database
python claude_rag.py build

# Show system information
python claude_rag.py info

# Build with custom settings
python build_database.py --target-chunks 528 --verify
```

## 🔧 Advanced Configuration

### Environment Variables

```bash
# Claude API Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Vector Database Configuration
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# RAG Configuration
MAX_CHUNKS=5
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Custom Document Processing

```python
# Example: Add your own documents
from rag_chatbot import initialize_rag_system

# Place your .md files in docs/ directory
chatbot = initialize_rag_system(docs_path="./docs")
result = chatbot.chat("Your question here")
print(result['answer'])
```

## 📁 Project Structure

```
claude-rag-chatbot/
├── docs/                          # Course materials (4 documents)
│   ├── 01_introduction_to_ml.md
│   ├── 02_deep_learning.md
│   ├── 03_nlp_fundamentals.md
│   └── 04_rag_systems.md
├── chroma_db/                     # Vector database (auto-generated)
├── rag_chatbot.py                 # Core RAG implementation
├── claude_rag.py                  # Claude API CLI tool
├── claude_rag_local.py            # Local/offline CLI tool
├── build_database.py              # Vector database builder
├── create_bundle.py               # Git bundle creator
├── requirements.txt               # Python dependencies
├── .env.template                  # Environment template
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🎯 Example Queries

Try these example questions:

**Machine Learning:**
- "What are the different types of machine learning?"
- "Explain the bias-variance tradeoff"
- "What is overfitting and how to prevent it?"

**Deep Learning:**
- "How do neural networks work?"
- "What's the difference between RNNs and Transformers?"
- "Explain the attention mechanism"

**NLP:**
- "What is tokenization in NLP?"
- "How do BERT and GPT differ?"
- "What are the challenges in NLP?"

**RAG Systems:**
- "How does retrieval-augmented generation work?"
- "What are vector databases used for?"
- "What are the components of a RAG system?"

## 🔍 System Information

### Vector Database Statistics

After building, you'll have:
- **528+ text chunks** from course materials
- **Semantic embeddings** using Sentence Transformers
- **ChromaDB** for efficient similarity search
- **Metadata tracking** for source attribution

### Model Information

- **Embedding Model:** all-MiniLM-L6-v2 (fast, efficient)
- **LLM:** Claude-3-Sonnet (high quality responses)
- **Chunk Size:** 800-1000 characters
- **Chunk Overlap:** 150-200 characters

## 🛠️ Git Bundle Option

Create a complete git bundle with full history:

```bash
# Create bundle with all branches and history
python create_bundle.py

# Verify bundle integrity
python create_bundle.py --verify

# Show bundle information
python create_bundle.py --info claude-rag-chatbot_20240923_123456.bundle
```

**Using a bundle:**
```bash
# Clone from bundle
git clone claude-rag-chatbot.bundle new-directory
cd new-directory

# Set up as normal
pip install -r requirements.txt
cp .env.template .env
# Add your API key to .env
```

## 🔧 Troubleshooting

### Common Issues

**1. "ANTHROPIC_API_KEY not found"**
- Ensure you've created `.env` file from `.env.template`
- Add your API key: `ANTHROPIC_API_KEY=your_key_here`
- Get key from: https://console.anthropic.com/

**2. "Vector database not found"**
- Run: `python build_database.py`
- Or: `python claude_rag.py build`

**3. "No documents found in ./docs"**
- Ensure all 4 `.md` files are in the `docs/` directory
- Check file permissions

**4. Import errors**
- Run: `pip install -r requirements.txt`
- Use Python 3.8+ for best compatibility

### Performance Tips

- **Chunk size:** Smaller chunks = more precise, larger chunks = more context
- **Max chunks:** More chunks = more comprehensive but slower responses
- **Local mode:** Use for offline testing without API costs
- **GPU support:** ChromaDB can use GPU for faster embedding generation

## 📄 License

This project is open source. Feel free to modify and distribute.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional course materials
- Enhanced local model support
- UI/web interface
- Multi-language support

---

**Ready to explore AI and ML concepts with your personal RAG chatbot!** 🚀

*Need help? The chatbot can answer questions about its own implementation and the included course materials.*