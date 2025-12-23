"""LLM client for agent generation."""
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage

from src.config import (
    LLM_PROVIDER, OPENAI_API_KEY, GOOGLE_API_KEY,
    OPENAI_MODEL, GOOGLE_MODEL
)


class LLMClient:
    """Client for interacting with LLM providers."""
    
    def __init__(self, provider: Optional[str] = None):
        """Initialize LLM client with specified provider."""
        self.provider = provider or LLM_PROVIDER
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the appropriate LLM based on provider."""
        if self.provider == "openai":
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set")
            return ChatOpenAI(
                model=OPENAI_MODEL,
                api_key=OPENAI_API_KEY,
                temperature=0.7
            )
        elif self.provider == "google":
            if not GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not set")
            return ChatGoogleGenerativeAI(
                model=GOOGLE_MODEL,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.7
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate_agent(self, user_description: str, blocks_summary: str) -> str:
        """Generate agent configuration from natural language description."""
        
        system_prompt = f"""You are an expert AutoGPT agent architect. Your task is to generate a complete agent configuration in JSON format based on user descriptions.

{blocks_summary}

Guidelines:
1. Use ONLY the tools/blocks listed above
2. Break down the user's goal into logical subtasks
3. Map each subtask to the appropriate block
4. Create meaningful variable connections between tasks using {{{{task_id.output_field}}}} syntax
5. Design a clear system prompt that defines the agent's personality and approach
6. Enable memory for agents that need to track state

Output Format (JSON):
{{
  "name": "Agent Name",
  "description": "Clear description of what the agent does",
  "systemPrompt": "Detailed system prompt defining agent behavior",
  "tasks": [
    {{
      "id": "task_id",
      "name": "Human-readable task name",
      "blockName": "ExactBlockName",
      "inputs": {{
        "input_field": "value or {{{{reference}}}}"
      }}
    }}
  ],
  "memory": {{
    "enabled": true,
    "keys": ["key1", "key2"]
  }}
}}

Important:
- Respond ONLY with valid JSON, no additional text
- Ensure blockName exactly matches available blocks
- Make inputs connect logically between tasks
- Keep the agent focused and practical"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Create an agent for: {user_description}")
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def refine_agent(self, current_config: str, refinement_request: str) -> str:
        """Refine an existing agent configuration based on feedback."""
        
        system_prompt = """You are refining an existing agent configuration. 
        Modify the JSON configuration based on the user's feedback while maintaining the same structure.
        Respond ONLY with the updated JSON configuration."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Current configuration:\n{current_config}\n\nRefinement request: {refinement_request}")
        ]
        
        response = self.llm.invoke(messages)
        return response.content

