import anthropic
from typing import List, Optional, Dict, Any

class AIGenerator:
    """Handles interactions with Anthropic's Claude API for generating responses"""
    
    # Static system prompt to avoid rebuilding on each call
    SYSTEM_PROMPT = """ You are an AI assistant specialized in course materials and educational content with access to a comprehensive search tool for course information.

Search Tool Usage:
- Use the search tool **only** for questions about specific course content or detailed educational materials
- **One search per query maximum**
- Synthesize search results into accurate, fact-based responses
- If search yields no results, state this clearly without offering alternatives

Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without searching
- **Course-specific questions**: Search first, then answer
- **No meta-commentary**:
 - Provide direct answers only — no reasoning process, search explanations, or question-type analysis
 - Do not mention "based on the search results"


All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
"""
    
    def __init__(self, api_key: str, model: str, plan_mode: bool = False):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.plan_mode = plan_mode
        
        # Pre-build base API parameters
        self.base_params = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 800
        }
    
    def generate_response(self, query: str,
                         conversation_history: Optional[str] = None,
                         tools: Optional[List] = None,
                         tool_manager=None,
                         use_planning: Optional[bool] = None) -> str:
        """
        Generate AI response with optional tool usage and conversation context.
        
        Args:
            query: The user's question or request
            conversation_history: Previous messages for context
            tools: Available tools the AI can use
            tool_manager: Manager to execute tools
            
        Returns:
            Generated response as string
        """
        
        # Determine if planning should be used
        planning_enabled = use_planning if use_planning is not None else self.plan_mode
        
        # Build system content
        system_content = self.SYSTEM_PROMPT
        if conversation_history:
            system_content = f"{system_content}\n\nPrevious conversation:\n{conversation_history}"
        
        # Prepare API call parameters efficiently
        api_params = {
            **self.base_params,
            "messages": [{"role": "user", "content": query}],
            "system": system_content
        }
        
        # Add tools if available
        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = {"type": "auto"}
        
        # Enable enhanced reasoning for planning mode
        if planning_enabled:
            # Increase temperature slightly for more creative reasoning
            api_params["temperature"] = 0.3
            api_params["max_tokens"] = 1500  # Allow more tokens for detailed reasoning
            
            # For newer Claude models, we can request step-by-step reasoning
            enhanced_query = f"""Think through this step-by-step before answering:

{query}

Please show your reasoning process including:
1. What the question is asking
2. What information you need to find
3. Your approach to finding it
4. Your analysis of the results
5. Your final answer"""
            
            api_params["messages"] = [{"role": "user", "content": enhanced_query}]
        
        try:
            # Get response from Claude
            response = self.client.messages.create(**api_params)
        except anthropic.AuthenticationError:
            # Fallback for invalid API key - return mock response
            return f"⚠️ **Demo Mode**: API key is invalid. Here's what I would search for: '{query}'\n\nPlease set a valid ANTHROPIC_API_KEY in your .env file to get real AI responses about the course materials.\n\n**Available courses:**\n- Advanced Retrieval for AI with Chroma\n- Prompt Compression and Query Optimization\n- Building Towards Computer Use with Anthropic\n- MCP: Build Rich-Context AI Apps with Anthropic"
        except Exception as e:
            # Handle other API errors
            return f"❌ **Error**: {str(e)}\n\nPlease check your API key and network connection."
        
        # Handle tool execution if needed
        if response.stop_reason == "tool_use" and tool_manager:
            return self._handle_tool_execution(response, api_params, tool_manager)
        
        # Return direct response
        return response.content[0].text
    
    def _handle_tool_execution(self, initial_response, base_params: Dict[str, Any], tool_manager):
        """
        Handle execution of tool calls and get follow-up response.
        
        Args:
            initial_response: The response containing tool use requests
            base_params: Base API parameters
            tool_manager: Manager to execute tools
            
        Returns:
            Final response text after tool execution
        """
        # Start with existing messages
        messages = base_params["messages"].copy()
        
        # Add AI's tool use response
        messages.append({"role": "assistant", "content": initial_response.content})
        
        # Execute all tool calls and collect results
        tool_results = []
        for content_block in initial_response.content:
            if content_block.type == "tool_use":
                tool_result = tool_manager.execute_tool(
                    content_block.name, 
                    **content_block.input
                )
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": content_block.id,
                    "content": tool_result
                })
        
        # Add tool results as single message
        if tool_results:
            messages.append({"role": "user", "content": tool_results})
        
        # Prepare final API call without tools
        final_params = {
            **self.base_params,
            "messages": messages,
            "system": base_params["system"]
        }
        
        # Get final response
        final_response = self.client.messages.create(**final_params)
        return final_response.content[0].text