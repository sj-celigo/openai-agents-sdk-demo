"""Research Assistant Agent using OpenAI Agents SDK."""

import json
import logging
from typing import Any, Dict, List, Optional
from openai import OpenAI

from .models.data_models import ResearchQuery, ResearchResult, ResearchDepth
from .tools.web_search import WebSearchTool
from .tools.webpage_fetcher import WebpageFetcherTool
from .utils.config import Config
from .utils.citation import CitationManager, Citation

logger = logging.getLogger(__name__)


class ResearchAgent:
    """AI agent for conducting research using OpenAI."""
    
    SYSTEM_PROMPT = """You are a professional research assistant. Your role is to:

1. Search for information on topics using web search
2. Fetch and read webpage content from search results
3. Synthesize information from multiple sources
4. Provide well-cited, accurate summaries

When conducting research:
- Use web_search to find relevant sources
- Use fetch_webpage to read the full content of promising sources
- Cite your sources using [1], [2], etc. format
- Cross-reference information across multiple sources
- Present balanced viewpoints when sources disagree
- Organize findings logically

Always be thorough, accurate, and transparent about your sources."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the research agent.
        
        Args:
            config: Application configuration (uses default if not provided)
        """
        from .utils.config import get_config
        
        self.config = config or get_config()
        self.client = OpenAI(api_key=self.config.openai_api_key)
        self.citation_manager = CitationManager()
        
        # Initialize tools
        self.web_search_tool = WebSearchTool(self.config)
        self.webpage_fetcher_tool = WebpageFetcherTool(self.config)
        
        # Map tool names to execution methods
        self.tool_map = {
            "web_search": self.web_search_tool.execute,
            "fetch_webpage": self.webpage_fetcher_tool.execute,
        }
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """
        Get the tools schema for OpenAI function calling.
        
        Returns:
            List of tool schemas
        """
        return [
            self.web_search_tool.get_schema(),
            self.webpage_fetcher_tool.get_schema(),
        ]
    
    def research(
        self,
        query: str,
        research_depth: ResearchDepth = ResearchDepth.STANDARD,
        max_sources: int = 5,
    ) -> ResearchResult:
        """
        Conduct research on a given query.
        
        Args:
            query: Research question or topic
            research_depth: How deep to research
            max_sources: Maximum number of sources to consult
            
        Returns:
            Research results with summary and citations
        """
        research_query = ResearchQuery(
            query=query,
            research_depth=research_depth,
            max_sources=max_sources,
        )
        
        logger.info(f"Starting research on: {query}")
        self.citation_manager.clear()
        
        # Create messages
        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": self._create_research_prompt(research_query),
            },
        ]
        
        # Run agent loop with function calling
        sources_consulted = []
        max_iterations = 10
        
        for iteration in range(max_iterations):
            logger.info(f"Agent iteration {iteration + 1}/{max_iterations}")
            
            response = self.client.chat.completions.create(
                model=self.config.agent_model,
                messages=messages,
                tools=self.get_tools_schema(),
                temperature=self.config.agent_temperature,
            )
            
            message = response.choices[0].message
            messages.append(message.model_dump())
            
            # Check if agent wants to call tools
            if message.tool_calls:
                # Execute tool calls
                for tool_call in message.tool_calls:
                    result = self._execute_tool_call(tool_call)
                    
                    # Track sources
                    if tool_call.function.name == "fetch_webpage":
                        args = json.loads(tool_call.function.arguments)
                        if result.get("success"):
                            sources_consulted.append(args["url"])
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    })
            else:
                # Agent has finished, return final response
                summary = message.content or ""
                
                logger.info("Research complete")
                
                return ResearchResult(
                    query=query,
                    summary=summary + "\n\n" + self.citation_manager.format_bibliography(),
                    sources_consulted=sources_consulted,
                    research_depth=research_depth,
                )
        
        # Max iterations reached
        logger.warning("Max iterations reached")
        final_message = messages[-1].get("content", "Research incomplete due to iteration limit.")
        
        return ResearchResult(
            query=query,
            summary=final_message + "\n\n" + self.citation_manager.format_bibliography(),
            sources_consulted=sources_consulted,
            research_depth=research_depth,
        )
    
    def _create_research_prompt(self, query: ResearchQuery) -> str:
        """Create the research prompt for the agent."""
        depth_instructions = {
            ResearchDepth.QUICK: "Do a quick search and provide a brief summary from 2-3 sources.",
            ResearchDepth.STANDARD: "Search multiple sources and provide a comprehensive summary.",
            ResearchDepth.COMPREHENSIVE: "Conduct in-depth research across many sources and provide detailed analysis.",
        }
        
        return f"""Research the following topic: {query.query}

Research depth: {query.research_depth}
{depth_instructions.get(query.research_depth, "")}

Please:
1. Search for relevant information using web_search
2. Read the most relevant sources using fetch_webpage
3. Synthesize the information into a clear, well-organized summary
4. Cite all sources using [1], [2], etc. format
5. Provide a sources section at the end

Begin your research now."""
    
    def _execute_tool_call(self, tool_call: Any) -> Dict[str, Any]:
        """
        Execute a tool call from the agent.
        
        Args:
            tool_call: OpenAI tool call object
            
        Returns:
            Tool execution result
        """
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        logger.info(f"Executing tool: {function_name}")
        logger.debug(f"Arguments: {arguments}")
        
        if function_name not in self.tool_map:
            return {"error": f"Unknown tool: {function_name}"}
        
        try:
            result = self.tool_map[function_name](**arguments)
            
            # Track citations for fetched webpages
            if function_name == "fetch_webpage" and result.get("success"):
                citation = Citation(
                    url=result["url"],
                    title=result.get("title", "Untitled"),
                    snippet=result.get("content", "")[:200] if result.get("content") else None,
                    author=result.get("author"),
                    published_date=result.get("published_date"),
                )
                self.citation_manager.add_citation(citation)
            
            return result
            
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")
            return {"error": str(e)}

