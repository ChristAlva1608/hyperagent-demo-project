"""Central registry for all tools available to bots."""

from dataclasses import dataclass
from typing import Callable, List, Dict, Any, Optional
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    """Definition of a tool that can be used by bots."""
    
    id: str
    name: str
    description: str
    factory: Callable  # Function that creates the tool instance


class ToolRegistry:
    """Central registry for managing and accessing tools."""
    
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()
    
    def register_tool(self, tool_def: ToolDefinition):
        """Register a new tool."""
        self._tools[tool_def.id] = tool_def
        logger.debug(f"Registered tool: {tool_def.id}")
    
    def get_tool(self, tool_id: str):
        """Get a single tool by ID."""
        if tool_id not in self._tools:
            raise ValueError(f"Tool not found: {tool_id}")
        return self._tools[tool_id].factory()
    
    def get_tools_by_ids(self, tool_ids: List[str]) -> List[Any]:
        """Get multiple tools by their IDs."""
        tools = []
        for tool_id in tool_ids:
            try:
                tools.append(self.get_tool(tool_id))
            except ValueError as e:
                logger.warning(f"Skipping tool {tool_id}: {e}")
        return tools
    
    def list_tools(self) -> List[str]:
        """List all registered tool IDs."""
        return list(self._tools.keys())
    
    def _register_default_tools(self):
        """Register all default tools."""
        
        # Generate Prior Auth tool
        def create_generate_prior_auth_tool():
            try:
                from tools.generate_prior_auth import generate_prior_auth_tool
            except ImportError:
                from app.tools.generate_prior_auth import generate_prior_auth_tool
            
            @tool
            def generate_prior_auth(
                uploaded_file_path: Optional[str] = None,
                content: Optional[str] = None,
                api_key: Optional[str] = None
            ) -> str:
                """Generate a Prior Authorization form from a patient note.
                
                Parameters:
                - uploaded_file_path: Optional path to uploaded patient note (.docx or .pdf)
                - content: Optional raw text content of patient note (alternative to file)
                - api_key: Optional OpenAI API key
                """
                return generate_prior_auth_tool(uploaded_file_path, content, api_key)
            return generate_prior_auth

        # Register tools
        self.register_tool(ToolDefinition(
            id="generate_prior_auth",
            name="Generate Prior Authorization",
            description="Generate a Prior Authorization form from patient notes",
            factory=create_generate_prior_auth_tool
        ))


# Global singleton instance
_tool_registry = None

def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry