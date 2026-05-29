import logging
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from models.llm import get_llm
from prompts.templates import get_chat_prompt

logger = logging.getLogger(__name__)

from typing import Optional, List, Dict, Any

class ConversationalAgentChain:
    """A conversational agent chain that handles routing and execution of tools."""
    
    def __init__(self, prompt: Any, llm: Any, tools: List[Any]):
        self.prompt = prompt
        self.llm = llm
        self.tools = {t.name: t for t in tools}
        logger.info(f"Initialized ConversationalAgentChain with registered tools: {list(self.tools.keys())}")

    def invoke(self, inputs: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> str:
        user_input = inputs.get("input") or ""
        logger.info(f"Agent Chain invoked. User input: {user_input[:100]}...")
        
        # 1. Format the initial prompt to get the starting messages
        formatted_prompt = self.prompt.format_prompt(
            input=inputs.get("input", ""),
            history=inputs.get("history", [])
        )
        messages = formatted_prompt.to_messages()
        logger.info(f"Initial message history count: {len(messages)}")

        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Agent loop iteration {iteration}/{max_iterations}")
            
            # Invoke the LLM
            logger.info(f"Invoking LLM to generate response or tool calls...")
            try:
                response = self.llm.invoke(messages, config=config)
            except Exception as e:
                logger.error(f"Error during LLM invocation: {str(e)}", exc_info=True)
                raise e
            
            # Check for tool calls
            if hasattr(response, "tool_calls") and response.tool_calls:
                logger.info(f"LLM response contains tool calls: {response.tool_calls}")
                
                # Append the LLM's response to keep messages history correct
                messages.append(response)
                
                # Execute tool calls
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    tool_id = tool_call["id"]
                    
                    logger.info(f"Executing tool '{tool_name}' with arguments: {tool_args}")
                    if tool_name in self.tools:
                        try:
                            # Invoke tool
                            tool_result = self.tools[tool_name].invoke(tool_args)
                            logger.info(f"Tool '{tool_name}' execution succeeded. Result length: {len(str(tool_result))}")
                        except Exception as e:
                            logger.error(f"Tool '{tool_name}' execution failed with error: {str(e)}", exc_info=True)
                            tool_result = f"Error executing tool '{tool_name}': {str(e)}"
                    else:
                        logger.warning(f"Requested tool '{tool_name}' is not registered in the chain tools.")
                        tool_result = f"Error: Tool '{tool_name}' is not available."
                    
                    # Create ToolMessage and append to messages history
                    tool_message = ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_id,
                        name=tool_name
                    )
                    messages.append(tool_message)
                    logger.info(f"Appended ToolMessage for '{tool_name}' (ID: {tool_id}) to message history.")
                
                # Loop back to let the LLM consume the tool results
                continue
            else:
                logger.info("LLM generated final text response. Loop finished.")
                return response.content

        logger.warning("Reached maximum iterations without a final response.")
        return "The request is taking too long to complete. Please try again."

def get_conversational_chain(
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    api_key: Optional[str] = None,
    streaming: bool = False,
    callbacks: Optional[List[Any]] = None
):
    """Factory to build a conversational LLM chain with prompt and optional callbacks."""
    prompt = get_chat_prompt()
    
    from config import DEFAULT_MODEL
    
    llm = get_llm(
        model_name=model_name or DEFAULT_MODEL,
        temperature=temperature,
        api_key=api_key,
        streaming=streaming,
        callbacks=callbacks
    )

    from tools.tool_registry import get_tool_registry

    registry = get_tool_registry()
    tool_ids = registry.list_tools()
    tools = registry.get_tools_by_ids(tool_ids)
    
    if tools:
        llm = llm.bind_tools(tools)
    
    # Custom conversational agent chain handling tools
    chain = ConversationalAgentChain(prompt, llm, tools)
    
    return chain
