"""Template management for common agent patterns."""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from src.config import CONFIG_DIR


class AgentTemplate(BaseModel):
    """Schema for an agent template."""
    id: str
    name: str
    description: str
    keywords: List[str]
    agent_config: Dict[str, Any]


class TemplateManager:
    """Manages agent templates."""
    
    def __init__(self):
        self.templates: List[AgentTemplate] = []
        self._load_templates()
    
    def _load_templates(self):
        """Load templates from JSON file."""
        templates_file = CONFIG_DIR / "templates.json"
        with open(templates_file, 'r') as f:
            data = json.load(f)
            self.templates = [AgentTemplate(**tmpl) for tmpl in data['templates']]
    
    def get_all_templates(self) -> List[AgentTemplate]:
        """Get all available templates."""
        return self.templates
    
    def search_templates(self, query: str) -> List[AgentTemplate]:
        """Search templates by query matching keywords or description."""
        query_lower = query.lower()
        results = []
        
        for template in self.templates:
            # Check keywords
            keyword_match = any(kw.lower() in query_lower for kw in template.keywords)
            # Check description
            desc_match = query_lower in template.description.lower()
            # Check name
            name_match = query_lower in template.name.lower()
            
            if keyword_match or desc_match or name_match:
                results.append(template)
        
        return results
    
    def get_template_by_id(self, template_id: str) -> Optional[AgentTemplate]:
        """Get a specific template by ID."""
        for template in self.templates:
            if template.id == template_id:
                return template
        return None

