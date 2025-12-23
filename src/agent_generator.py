"""Core agent generation logic."""
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import jsonschema

from src.llm_client import LLMClient
from src.blocks import BlockManager
from src.templates import TemplateManager
from src.config import GENERATED_AGENTS_DIR


# JSON Schema for agent validation
AGENT_SCHEMA = {
    "type": "object",
    "required": ["name", "description", "systemPrompt", "tasks"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "description": {"type": "string", "minLength": 1},
        "systemPrompt": {"type": "string", "minLength": 1},
        "tasks": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["id", "name", "blockName", "inputs"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "blockName": {"type": "string"},
                    "inputs": {"type": "object"}
                }
            }
        },
        "memory": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "keys": {"type": "array", "items": {"type": "string"}}
            }
        }
    }
}


class AgentGenerator:
    """Main class for generating agents from natural language."""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.block_manager = BlockManager()
        self.template_manager = TemplateManager()
    
    def generate_from_description(self, description: str) -> Dict[str, Any]:
        """
        Generate an agent from natural language description.
        
        Args:
            description: Natural language description of desired agent
            
        Returns:
            Dict containing agent configuration and metadata
        """
        # Check if description matches a template
        matching_templates = self.template_manager.search_templates(description)
        
        # Get blocks summary for LLM
        blocks_summary = self.block_manager.get_blocks_summary()
        
        # Generate agent config using LLM
        raw_response = self.llm_client.generate_agent(description, blocks_summary)
        
        # Parse and validate
        agent_config = self._parse_and_validate(raw_response)
        
        # Add metadata
        result = {
            "agent": agent_config,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "description": description,
                "suggested_templates": [t.id for t in matching_templates[:3]],
                "provider": self.llm_client.provider
            }
        }
        
        return result
    
    def generate_from_template(self, template_id: str, custom_params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate an agent from a template.
        
        Args:
            template_id: ID of the template to use
            custom_params: Optional parameters to customize the template
            
        Returns:
            Dict containing agent configuration
        """
        template = self.template_manager.get_template_by_id(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        agent_config = template.agent_config.copy()
        
        # Apply custom parameters if provided
        if custom_params:
            agent_config.update(custom_params)
        
        return {
            "agent": agent_config,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "template_id": template_id,
                "template_name": template.name
            }
        }
    
    def refine_agent(self, agent_config: Dict[str, Any], refinement: str) -> Dict[str, Any]:
        """
        Refine an existing agent based on user feedback.
        
        Args:
            agent_config: Current agent configuration
            refinement: Description of desired changes
            
        Returns:
            Updated agent configuration
        """
        current_json = json.dumps(agent_config, indent=2)
        raw_response = self.llm_client.refine_agent(current_json, refinement)
        
        refined_config = self._parse_and_validate(raw_response)
        
        return {
            "agent": refined_config,
            "metadata": {
                "refined_at": datetime.now().isoformat(),
                "refinement_request": refinement
            }
        }
    
    def _parse_and_validate(self, raw_json: str) -> Dict[str, Any]:
        """Parse and validate agent JSON."""
        # Clean up response (remove markdown code blocks if present)
        cleaned = raw_json.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1])
        
        # Parse JSON
        try:
            agent_config = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse agent JSON: {e}")
        
        # Validate against schema
        try:
            jsonschema.validate(instance=agent_config, schema=AGENT_SCHEMA)
        except jsonschema.ValidationError as e:
            raise ValueError(f"Agent validation failed: {e.message}")
        
        # Validate blocks exist
        for task in agent_config.get("tasks", []):
            block_name = task.get("blockName")
            if not self.block_manager.get_block_by_name(block_name):
                raise ValueError(f"Unknown block: {block_name}")
        
        return agent_config
    
    def save_agent(self, agent_data: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """Save generated agent to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            agent_name = agent_data.get("agent", {}).get("name", "agent")
            safe_name = "".join(c for c in agent_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_').lower()
            filename = f"{safe_name}_{timestamp}.json"
        
        filepath = GENERATED_AGENTS_DIR / filename
        with open(filepath, 'w') as f:
            json.dump(agent_data, f, indent=2)
        
        return filepath
    
    def validate_agent(self, agent_config: Dict[str, Any]) -> List[str]:
        """
        Validate an agent configuration and return list of issues.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        issues = []
        
        try:
            jsonschema.validate(instance=agent_config, schema=AGENT_SCHEMA)
        except jsonschema.ValidationError as e:
            issues.append(f"Schema validation: {e.message}")
        
        # Check blocks
        for i, task in enumerate(agent_config.get("tasks", [])):
            block_name = task.get("blockName")
            block = self.block_manager.get_block_by_name(block_name)
            
            if not block:
                issues.append(f"Task {i+1}: Unknown block '{block_name}'")
                continue
            
            # Check required inputs
            task_inputs = task.get("inputs", {})
            for input_name, input_spec in block.inputs.items():
                if input_spec.get("required") and input_name not in task_inputs:
                    issues.append(f"Task {i+1}: Missing required input '{input_name}'")
        
        return issues

