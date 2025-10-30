# Migration to OpenAI Agents SDK

This document describes the migration from custom OpenAI SDK implementation to the official [openai-agents-python SDK](https://github.com/openai/openai-agents-python).

## Overview

The Personal Research Assistant has been successfully migrated from a custom implementation using direct OpenAI API calls to the official OpenAI Agents SDK. This provides better maintainability, built-in features, and aligns with OpenAI's recommended patterns.

## Key Changes

### 1. Dependencies

**Before:**
```
openai>=1.50.0
```

**After:**
```
openai-agents>=0.4.0
```

### 2. Tool Implementation

**Before:** Tools were implemented as classes inheriting from `BaseTool`

```python
class WebSearchTool(BaseTool):
    def __init__(self, config: Config):
        self.config = config
        self.client = TavilyClient(api_key=config.tavily_api_key)
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return "Search the web..."
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {...}
    
    def execute(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        # Implementation
        return result
```

**After:** Tools are simple functions decorated with `@function_tool`

```python
from agents import function_tool

@function_tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web for information on a given query.
    
    Args:
        query: The search query to execute
        max_results: Maximum number of results
        
    Returns:
        JSON string with search results
    """
    return _web_search_impl(query, max_results)
```

### 3. Agent Implementation

**Before:** Manual message loop and function calling

```python
class ResearchAgent:
    def research(self, query: str) -> ResearchResult:
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
        
        for iteration in range(max_iterations):
            response = self.client.chat.completions.create(
                model=self.config.agent_model,
                messages=messages,
                tools=self.get_tools_schema(),
                temperature=self.config.agent_temperature,
            )
            
            message = response.choices[0].message
            messages.append(message.model_dump())
            
            if message.tool_calls:
                # Execute tools manually
                for tool_call in message.tool_calls:
                    result = self._execute_tool_call(tool_call)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    })
            else:
                return ResearchResult(...)
```

**After:** Using Agent and Runner from agents SDK

```python
from agents import Agent, Runner

class ResearchAgent:
    def research(self, query: str) -> ResearchResult:
        agent = Agent(
            name="Research Assistant",
            instructions=self._create_research_instructions(research_query),
            tools=[web_search, fetch_webpage],
            model=self.config.agent_model,
        )
        
        result = Runner.run_sync(
            agent,
            input=f"Research the following topic: {query}",
            max_turns=10,
        )
        
        return ResearchResult(
            query=query,
            summary=result.final_output,
            ...
        )
```

### 4. Configuration

**Before:**
```python
agent = Agent(..., temperature=0.3)  # Would fail
```

**After:**
```python
agent = Agent(..., model="gpt-4-turbo")
# Temperature controlled via model settings if needed
```

The Agent class doesn't accept temperature directly; it's set via model configuration.

### 5. Tool State Management

**Before:** Tools were stateful objects

```python
self.web_search_tool = WebSearchTool(self.config)
self.webpage_fetcher_tool = WebpageFetcherTool(self.config)
```

**After:** Tools are stateless functions with global state for configuration

```python
# Initialize tools with configuration
init_web_search_tool(self.config)
init_webpage_fetcher_tool(self.config)
set_citation_manager(self.citation_manager)

# Tools are used by the agent
agent = Agent(tools=[web_search, fetch_webpage], ...)
```

## Benefits of Migration

### 1. Official SDK Support
- ✅ Maintained by OpenAI
- ✅ Future-proof with OpenAI updates
- ✅ Better integration with OpenAI ecosystem

### 2. Less Boilerplate
- ✅ No manual message loop
- ✅ No manual tool calling logic
- ✅ Simpler tool definitions

### 3. Built-in Features
- ✅ Automatic tracing and debugging
- ✅ Session support for conversation history
- ✅ Better error handling
- ✅ Integration with observability tools (Logfire, AgentOps, etc.)

### 4. Cleaner Code
- ✅ ~200 lines of code removed
- ✅ More focused on business logic
- ✅ Easier to extend and maintain

## Testing Changes

### Test Count
- **Before**: 71 tests
- **After**: 55 tests
- **Reason**: Removed redundant tests for manual tool calling infrastructure

### Coverage
- **Before**: 98.47%
- **After**: 90.03%
- **Reason**: Tool decorator wrappers are harder to test, but core logic is fully covered

### Testing Approach

**Before:** Mock OpenAI client responses

```python
@patch("src.agent.OpenAI")
def test_research(mock_openai_class):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    ...
```

**After:** Mock agents.Runner

```python
@patch('src.agent.Runner')
def test_research(mock_runner_class):
    mock_result = MagicMock()
    mock_result.final_output = "Summary"
    mock_runner_class.run_sync.return_value = mock_result
    ...
```

## File Changes

### Deleted Files
- `src/tools/base.py` - No longer needed (replaced by @function_tool)

### Modified Files
- `requirements.txt` - Updated to use openai-agents
- `src/agent.py` - Complete rewrite using Agent and Runner
- `src/tools/web_search.py` - Converted to @function_tool
- `src/tools/webpage_fetcher.py` - Converted to @function_tool
- `src/tools/__init__.py` - Updated exports
- All test files - Updated to work with new SDK

### New Files
- `MIGRATION.md` - This file

## Breaking Changes

### API Changes
None! The `ResearchAgent.research()` API remains the same:

```python
agent = ResearchAgent()
result = agent.research(query="test query", research_depth=ResearchDepth.STANDARD)
```

### CLI Changes
None! The CLI works identically:

```bash
python cli.py research "test query" --depth standard
```

## Migration Steps (For Reference)

If you need to perform a similar migration in your own project:

1. **Update dependencies**
   ```bash
   pip install openai-agents
   ```

2. **Convert tools to @function_tool**
   - Create implementation functions
   - Decorate with @function_tool
   - Return JSON strings instead of dicts
   - Handle configuration via global state or dependency injection

3. **Update agent to use Agent and Runner**
   - Create Agent with tools and instructions
   - Use Runner.run_sync() or Runner.run()
   - Process result.final_output

4. **Update tests**
   - Mock agents.Runner instead of OpenAI client
   - Test implementation functions separately
   - Update assertions for new result format

5. **Test thoroughly**
   - Run full test suite
   - Verify coverage
   - Test CLI manually

## Troubleshooting

### Issue: "Agent.__init__() got an unexpected keyword argument 'temperature'"

**Solution**: Remove temperature parameter. The Agent class doesn't accept it directly.

### Issue: "AttributeError: 'FunctionTool' object has no attribute..."

**Solution**: Don't try to access decorated function attributes. Test the implementation function instead.

### Issue: Tools not finding configuration

**Solution**: Call init functions before creating the agent:
```python
init_web_search_tool(config)
init_webpage_fetcher_tool(config)
```

## Performance Impact

- **Startup time**: Slightly faster (less initialization)
- **Runtime**: Similar performance
- **Memory**: Slightly lower (less object overhead)

## Future Enhancements

With the agents SDK, we can now easily add:

1. **Session Support**: Built-in conversation memory
   ```python
   from agents import SQLiteSession
   session = SQLiteSession("user_123")
   result = await Runner.run(agent, query, session=session)
   ```

2. **Tracing**: Automatic debugging with external tools
   ```python
   # Tracing is automatic, can be configured
   ```

3. **Handoffs**: Multi-agent collaboration
   ```python
   agent_a = Agent(name="A", handoffs=[agent_b])
   ```

## Resources

- [OpenAI Agents Python SDK](https://github.com/openai/openai-agents-python)
- [SDK Documentation](https://openai.github.io/openai-agents-python/)
- [Function Tool Guide](https://openai.github.io/openai-agents-python/tools/)
- [Tracing Guide](https://openai.github.io/openai-agents-python/tracing/)

## Questions or Issues?

If you encounter any issues with the migration, please:
1. Check this guide for common issues
2. Review the updated test files for examples
3. Consult the official OpenAI Agents SDK documentation

---

**Migration completed**: October 30, 2025
**SDK Version**: openai-agents>=0.4.0
**Test Coverage**: 90.03% (55/55 tests passing)

