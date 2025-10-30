# Personal Research Assistant

An AI-powered research assistant built with the OpenAI Agents SDK that autonomously searches for information, fetches web content, and synthesizes findings into well-cited summaries.

## 🎯 Project Overview

This project demonstrates key agentic workflow concepts including:
- **Tool Use**: Web search and webpage fetching tools
- **Autonomous Decision Making**: Agent decides which sources to consult
- **Iterative Refinement**: Multi-step research with adaptive strategies
- **Citation Management**: Automatic source tracking and formatting
- **Error Handling**: Robust handling of API failures and edge cases

## 📋 Features

- 🔍 **Web Search**: Searches across the internet using Tavily API
- 📄 **Content Extraction**: Fetches and parses webpage content
- 📚 **Citation Tracking**: Automatically tracks and formats sources
- 🎨 **Rich CLI**: Beautiful command-line interface with progress indicators
- ⚡ **Fast & Efficient**: Optimized for quick research
- 🧪 **95%+ Test Coverage**: Comprehensive unit tests

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Tavily API key (for web search)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd openai-agents-sdk-demo
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required environment variables:
```
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### Getting API Keys

- **OpenAI API Key**: Get it from [platform.openai.com](https://platform.openai.com/api-keys)
- **Tavily API Key**: Get it from [tavily.com](https://tavily.com)

## 💻 Usage

### Command Line Interface

**Basic research**:
```bash
python cli.py research "vector databases for RAG applications"
```

**Research with options**:
```bash
python cli.py research "climate change impacts" --depth comprehensive --max-sources 10
```

**Save results to file**:
```bash
python cli.py research "quantum computing" --output results.md
```

**Interactive mode**:
```bash
python cli.py interactive
```

### Programmatic Usage

```python
from src.agent import ResearchAgent
from src.models.data_models import ResearchDepth

# Initialize agent
agent = ResearchAgent()

# Conduct research
result = agent.research(
    query="How do transformers work in deep learning?",
    research_depth=ResearchDepth.STANDARD,
    max_sources=5,
)

# Access results
print(result.summary)
print(f"Sources consulted: {len(result.sources_consulted)}")
```

### Jupyter Notebook

```python
from src.agent import ResearchAgent
from src.models.data_models import ResearchDepth
from IPython.display import Markdown, display

agent = ResearchAgent()

result = agent.research(
    query="latest developments in AI coding assistants",
    research_depth=ResearchDepth.COMPREHENSIVE,
)

display(Markdown(result.summary))
```

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         CLI Interface                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Research Agent (GPT-4)          │
│  - Query understanding               │
│  - Tool orchestration                │
│  - Synthesis & reasoning             │
└──────────────┬──────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌──────────┐     ┌──────────┐
│   Web    │     │ Webpage  │
│  Search  │     │ Fetcher  │
│  Tool    │     │  Tool    │
└──────────┘     └──────────┘
      │                 │
      ▼                 ▼
┌──────────┐     ┌──────────┐
│  Tavily  │     │ Requests │
│   API    │     │    +     │
│          │     │   BS4    │
└──────────┘     └──────────┘
```

## 📁 Project Structure

```
openai-agents-sdk-demo/
├── src/
│   ├── __init__.py
│   ├── agent.py              # Main agent implementation
│   ├── models/
│   │   ├── __init__.py
│   │   └── data_models.py    # Pydantic models
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py           # Base tool class
│   │   ├── web_search.py     # Web search tool
│   │   └── webpage_fetcher.py # Webpage fetching tool
│   └── utils/
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       └── citation.py       # Citation tracking
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_agent.py
│   ├── test_citation.py
│   ├── test_config.py
│   ├── test_data_models.py
│   ├── test_web_search.py
│   └── test_webpage_fetcher.py
├── cli.py                    # Command-line interface
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
└── README.md
```

## 🧪 Testing

Run all tests:
```bash
pytest
```

Run with coverage report:
```bash
pytest --cov=src --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_agent.py -v
```

The project maintains **95%+ code coverage** with comprehensive unit tests covering:
- Agent orchestration and tool calling
- Web search functionality
- Webpage fetching and parsing
- Citation management
- Configuration handling
- Error scenarios and edge cases

## 🔧 Configuration

Configure the agent via environment variables:

```bash
# Required
OPENAI_API_KEY=your_key
TAVILY_API_KEY=your_key

# Optional
AGENT_MODEL=gpt-4-turbo          # OpenAI model to use
AGENT_TEMPERATURE=0.3            # Temperature for responses
MAX_SEARCH_RESULTS=5             # Default search results
REQUEST_TIMEOUT=30               # HTTP request timeout (seconds)
```

## 📖 Key Concepts Demonstrated

### 1. Tool Use
The agent can call external tools (functions) to interact with the world:
- `web_search`: Searches the internet for information
- `fetch_webpage`: Retrieves and parses webpage content

### 2. Autonomous Decision Making
The agent autonomously:
- Determines which sources to search
- Decides which webpages to fetch
- Synthesizes information from multiple sources
- Knows when to stop researching

### 3. Function Calling (OpenAI Agents SDK)
Uses OpenAI's function calling to enable the agent to:
- Understand when tools are needed
- Generate proper tool arguments
- Process tool results
- Chain multiple tool calls together

### 4. State Management
- Tracks conversation history across tool calls
- Manages citations and sources
- Handles multi-turn interactions

### 5. Error Handling
- Gracefully handles API failures
- Retries with fallbacks
- Provides meaningful error messages
- Continues research when individual sources fail

## 🎓 Learning Path

This project is designed as Phase 1 (MVP) of the Personal Research Assistant PRD. To continue learning:

1. **Phase 2**: Add academic paper search, source credibility scoring, iterative refinement
2. **Phase 3**: Add export functionality, research history, advanced features

See `personal-research-assistant-prd.md` for the full roadmap.

## 📝 Example Interaction

```bash
$ python cli.py research "vector databases for RAG applications"

╭─────────────────────────────────────────────────────────╮
│ Research Query: vector databases for RAG applications   │
│ Depth: standard                                         │
│ Max Sources: 5                                          │
╰─────────────────────────────────────────────────────────╯

⠋ Researching...

# Vector Databases for RAG Applications

## Summary
Vector databases are specialized databases designed to store and query
high-dimensional vectors efficiently, making them essential for Retrieval
Augmented Generation (RAG) applications...

## Key Points
- Popular options include Pinecone, Weaviate, and Qdrant [1]
- Support for hybrid search (vector + keyword) [2]
- Performance considerations for production use [3]

## Sources
[1] Introduction to Vector Databases - https://example.com/... (Accessed: 2025-10-30)
[2] RAG Architecture Guide - https://example.com/... (Accessed: 2025-10-30)
[3] Vector DB Benchmarks - https://example.com/... (Accessed: 2025-10-30)
```

## 🤝 Contributing

This is an educational project. Feel free to:
- Add new tools (e.g., academic paper search)
- Improve synthesis quality
- Add new features from Phase 2/3
- Enhance error handling
- Improve test coverage

## 📄 License

MIT License - feel free to use this project for learning and development.

## 🙏 Acknowledgments

- Built with [OpenAI Agents SDK](https://platform.openai.com/docs/)
- Web search powered by [Tavily](https://tavily.com)
- CLI interface using [Rich](https://rich.readthedocs.io/)

## 📚 Additional Resources

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Agentic Workflows](https://www.anthropic.com/research/building-effective-agents)
- [RAG Systems](https://python.langchain.com/docs/use_cases/question_answering/)

---

**Built as a learning project for understanding agentic workflows with the OpenAI Agents SDK.**

