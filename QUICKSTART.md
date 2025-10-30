# Quick Start Guide

Get the Personal Research Assistant (built with **OpenAI Agents Python SDK**) running in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get it here](https://platform.openai.com/api-keys))
- Tavily API key ([Get it here](https://tavily.com))

> **Note**: This project uses the official [OpenAI Agents Python SDK](https://github.com/openai/openai-agents-python) for agent orchestration.

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here
```

### 3. Run Your First Research Query

```bash
python cli.py research "What are vector databases?"
```

That's it! 🎉

## Example Usage

### Quick Research
```bash
python cli.py research "machine learning basics" --depth quick
```

### Comprehensive Research
```bash
python cli.py research "climate change solutions" --depth comprehensive --max-sources 10
```

### Save Results to File
```bash
python cli.py research "quantum computing" --output results.md
```

### Interactive Mode
```bash
python cli.py interactive
```

## Programmatic Usage

```python
from src.agent import ResearchAgent

# Create agent
agent = ResearchAgent()

# Research a topic
result = agent.research("How does CRISPR work?")

# Print results
print(result.summary)
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'tavily'"
**Solution**: Run `pip install -r requirements.txt`

### "OPENAI_API_KEY environment variable is required"
**Solution**: Make sure you created the `.env` file with your API keys

### "Rate limit exceeded"
**Solution**: Wait a few seconds and try again. Consider using `--depth quick` for faster queries.

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Check out [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) to understand the architecture
3. Review the [PRD](personal-research-assistant-prd.md) for future enhancements

## Support

- **Issues**: Check existing issues or create a new one
- **Documentation**: See README.md
- **Examples**: Check the `examples/` directory (coming in Phase 2)

Happy researching! 🔍

