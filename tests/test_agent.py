"""Tests for the research agent."""

import json
from unittest.mock import MagicMock, patch, Mock
import pytest

from src.agent import ResearchAgent
from src.models.data_models import ResearchDepth
from src.utils.citation import Citation


class TestResearchAgent:
    """Test ResearchAgent class."""
    
    def test_agent_initialization(self, mock_config):
        """Test agent initialization."""
        agent = ResearchAgent(mock_config)
        
        assert agent.config == mock_config
        assert agent.client is not None
        assert agent.web_search_tool is not None
        assert agent.webpage_fetcher_tool is not None
        assert len(agent.tool_map) == 2
    
    def test_get_tools_schema(self, mock_config):
        """Test getting tools schema."""
        agent = ResearchAgent(mock_config)
        schema = agent.get_tools_schema()
        
        assert len(schema) == 2
        assert all(s["type"] == "function" for s in schema)
        
        tool_names = [s["function"]["name"] for s in schema]
        assert "web_search" in tool_names
        assert "fetch_webpage" in tool_names
    
    @patch("src.agent.OpenAI")
    @patch("src.tools.web_search.TavilyClient")
    def test_research_simple_flow(
        self,
        mock_tavily_class,
        mock_openai_class,
        mock_config,
    ):
        """Test simple research flow without tool calls."""
        # Setup OpenAI mock
        mock_openai_client = MagicMock()
        mock_openai_class.return_value = mock_openai_client
        
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Research summary goes here"
        mock_message.tool_calls = None
        mock_message.model_dump.return_value = {
            "role": "assistant",
            "content": "Research summary goes here",
        }
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Create agent and run research
        agent = ResearchAgent(mock_config)
        result = agent.research(query="test query")
        
        assert result.query == "test query"
        assert "Research summary goes here" in result.summary
        assert result.research_depth == ResearchDepth.STANDARD
    
    @patch("src.agent.OpenAI")
    @patch("src.tools.web_search.TavilyClient")
    @patch("src.tools.webpage_fetcher.requests.Session.get")
    def test_research_with_tool_calls(
        self,
        mock_requests_get,
        mock_tavily_class,
        mock_openai_class,
        mock_config,
        sample_search_results,
    ):
        """Test research flow with tool calls."""
        # Setup Tavily mock
        mock_tavily_client = MagicMock()
        mock_tavily_client.search.return_value = {
            "results": [
                {
                    "url": r.url,
                    "title": r.title,
                    "content": r.snippet,
                    "score": r.score,
                }
                for r in sample_search_results[:1]  # Just one result
            ]
        }
        mock_tavily_class.return_value = mock_tavily_client
        
        # Setup requests mock
        mock_http_response = MagicMock()
        mock_http_response.status_code = 200
        mock_http_response.content = b"""
        <html>
        <head><title>Test Article</title></head>
        <body><article><p>Article content here</p></article></body>
        </html>
        """
        mock_requests_get.return_value = mock_http_response
        
        # Setup OpenAI mock - first response with tool calls, second without
        mock_openai_client = MagicMock()
        mock_openai_class.return_value = mock_openai_client
        
        # First response: agent wants to search
        tool_call_1 = MagicMock()
        tool_call_1.id = "call_1"
        tool_call_1.function.name = "web_search"
        tool_call_1.function.arguments = json.dumps({"query": "test query"})
        
        response_1 = MagicMock()
        choice_1 = MagicMock()
        message_1 = MagicMock()
        message_1.content = None
        message_1.tool_calls = [tool_call_1]
        message_1.model_dump.return_value = {
            "role": "assistant",
            "tool_calls": [{"id": "call_1", "function": {"name": "web_search"}}],
        }
        choice_1.message = message_1
        response_1.choices = [choice_1]
        
        # Second response: agent wants to fetch webpage
        tool_call_2 = MagicMock()
        tool_call_2.id = "call_2"
        tool_call_2.function.name = "fetch_webpage"
        tool_call_2.function.arguments = json.dumps({"url": "https://example.com/article1"})
        
        response_2 = MagicMock()
        choice_2 = MagicMock()
        message_2 = MagicMock()
        message_2.content = None
        message_2.tool_calls = [tool_call_2]
        message_2.model_dump.return_value = {
            "role": "assistant",
            "tool_calls": [{"id": "call_2", "function": {"name": "fetch_webpage"}}],
        }
        choice_2.message = message_2
        response_2.choices = [choice_2]
        
        # Third response: final answer
        response_3 = MagicMock()
        choice_3 = MagicMock()
        message_3 = MagicMock()
        message_3.content = "Final research summary"
        message_3.tool_calls = None
        message_3.model_dump.return_value = {
            "role": "assistant",
            "content": "Final research summary",
        }
        choice_3.message = message_3
        response_3.choices = [choice_3]
        
        mock_openai_client.chat.completions.create.side_effect = [
            response_1,
            response_2,
            response_3,
        ]
        
        # Create agent and run research
        agent = ResearchAgent(mock_config)
        result = agent.research(query="test query")
        
        assert result.query == "test query"
        assert "Final research summary" in result.summary
        assert len(result.sources_consulted) == 1
        assert result.sources_consulted[0] == "https://example.com/article1"
    
    @patch("src.agent.OpenAI")
    def test_execute_tool_call_unknown_tool(self, mock_openai_class, mock_config):
        """Test executing unknown tool call."""
        mock_openai_client = MagicMock()
        mock_openai_class.return_value = mock_openai_client
        
        agent = ResearchAgent(mock_config)
        
        tool_call = MagicMock()
        tool_call.function.name = "unknown_tool"
        tool_call.function.arguments = "{}"
        
        result = agent._execute_tool_call(tool_call)
        
        assert "error" in result
        assert "Unknown tool" in result["error"]
    
    @patch("src.agent.OpenAI")
    @patch("src.tools.web_search.TavilyClient")
    def test_execute_tool_call_search(
        self,
        mock_tavily_class,
        mock_openai_class,
        mock_config,
        sample_search_results,
    ):
        """Test executing web search tool call."""
        mock_tavily_client = MagicMock()
        mock_tavily_client.search.return_value = {
            "results": [
                {
                    "url": r.url,
                    "title": r.title,
                    "content": r.snippet,
                    "score": r.score,
                }
                for r in sample_search_results
            ]
        }
        mock_tavily_class.return_value = mock_tavily_client
        
        mock_openai_client = MagicMock()
        mock_openai_class.return_value = mock_openai_client
        
        agent = ResearchAgent(mock_config)
        
        tool_call = MagicMock()
        tool_call.function.name = "web_search"
        tool_call.function.arguments = json.dumps({"query": "test"})
        
        result = agent._execute_tool_call(tool_call)
        
        assert result["success"] is True
        assert len(result["results"]) == 3
    
    @patch("src.agent.OpenAI")
    @patch("src.tools.webpage_fetcher.requests.Session.get")
    def test_execute_tool_call_fetch_webpage(
        self,
        mock_requests_get,
        mock_openai_class,
        mock_config,
    ):
        """Test executing fetch webpage tool call."""
        mock_http_response = MagicMock()
        mock_http_response.status_code = 200
        mock_http_response.content = b"""
        <html>
        <head><title>Test</title></head>
        <body><p>Content</p></body>
        </html>
        """
        mock_requests_get.return_value = mock_http_response
        
        mock_openai_client = MagicMock()
        mock_openai_class.return_value = mock_openai_client
        
        agent = ResearchAgent(mock_config)
        
        tool_call = MagicMock()
        tool_call.function.name = "fetch_webpage"
        tool_call.function.arguments = json.dumps({"url": "https://example.com"})
        
        result = agent._execute_tool_call(tool_call)
        
        assert result["success"] is True
        assert result["url"] == "https://example.com"
        
        # Should add citation
        assert agent.citation_manager.count() == 1
    
    @patch("src.agent.OpenAI")
    def test_research_max_iterations(self, mock_openai_class, mock_config):
        """Test research stops at max iterations."""
        # Setup OpenAI to always return tool calls
        mock_openai_client = MagicMock()
        mock_openai_class.return_value = mock_openai_client
        
        tool_call = MagicMock()
        tool_call.id = "call_1"
        tool_call.function.name = "web_search"
        tool_call.function.arguments = json.dumps({"query": "test"})
        
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Searching..."
        mock_message.tool_calls = [tool_call]
        mock_message.model_dump.return_value = {
            "role": "assistant",
            "tool_calls": [{"id": "call_1"}],
        }
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        agent = ResearchAgent(mock_config)
        
        # This should hit max iterations and return
        result = agent.research(query="test")
        
        assert result is not None
        # Should have called API multiple times (max_iterations)
        assert mock_openai_client.chat.completions.create.call_count == 10
    
    def test_create_research_prompt_quick(self, mock_config):
        """Test creating research prompt for quick depth."""
        from src.models.data_models import ResearchQuery
        
        agent = ResearchAgent(mock_config)
        query = ResearchQuery(
            query="test topic",
            research_depth=ResearchDepth.QUICK,
        )
        
        prompt = agent._create_research_prompt(query)
        
        assert "test topic" in prompt
        assert "quick" in prompt.lower()
        assert "brief" in prompt.lower()
    
    def test_create_research_prompt_comprehensive(self, mock_config):
        """Test creating research prompt for comprehensive depth."""
        from src.models.data_models import ResearchQuery
        
        agent = ResearchAgent(mock_config)
        query = ResearchQuery(
            query="complex topic",
            research_depth=ResearchDepth.COMPREHENSIVE,
        )
        
        prompt = agent._create_research_prompt(query)
        
        assert "complex topic" in prompt
        assert "comprehensive" in prompt.lower()
        assert "in-depth" in prompt.lower()
    
    @patch("src.agent.OpenAI")
    def test_tool_execution_error_handling(self, mock_openai_class, mock_config):
        """Test error handling during tool execution."""
        mock_openai_client = MagicMock()
        mock_openai_class.return_value = mock_openai_client
        
        agent = ResearchAgent(mock_config)
        
        # Mock a tool that raises an exception
        agent.tool_map["web_search"] = Mock(side_effect=Exception("Tool error"))
        
        tool_call = MagicMock()
        tool_call.function.name = "web_search"
        tool_call.function.arguments = json.dumps({"query": "test"})
        
        result = agent._execute_tool_call(tool_call)
        
        assert "error" in result
        assert "Tool error" in result["error"]

