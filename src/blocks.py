"""Block/Tool management system."""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from src.config import CONFIG_DIR


class BlockSchema(BaseModel):
    """Schema for a tool/block definition."""
    id: str
    name: str
    description: str
    category: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    capabilities: List[str]


class BlockManager:
    """Manages available blocks/tools for agent creation."""
    
    def __init__(self):
        self.blocks: List[BlockSchema] = []
        self._load_blocks()
    
    def _load_blocks(self):
        """Load block definitions from JSON file."""
        blocks_file = CONFIG_DIR / "blocks.json"
        with open(blocks_file, 'r') as f:
            data = json.load(f)
            self.blocks = [BlockSchema(**block) for block in data['blocks']]
    
    def get_all_blocks(self) -> List[BlockSchema]:
        """Get all available blocks."""
        return self.blocks
    
    def get_block_by_name(self, name: str) -> Optional[BlockSchema]:
        """Get a specific block by name."""
        for block in self.blocks:
            if block.name == name or block.id == name:
                return block
        return None
    
    def search_blocks(self, keywords: List[str]) -> List[BlockSchema]:
        """Search blocks by keywords in capabilities or description."""
        results = []
        keywords_lower = [k.lower() for k in keywords]
        
        for block in self.blocks:
            # Check capabilities
            caps_match = any(
                any(kw in cap.lower() for kw in keywords_lower)
                for cap in block.capabilities
            )
            # Check description
            desc_match = any(kw in block.description.lower() for kw in keywords_lower)
            
            if caps_match or desc_match:
                results.append(block)
        
        return results
    
    def get_blocks_summary(self) -> str:
        """Get a formatted summary of all blocks for LLM prompt."""
        summary_lines = ["Available Tools/Blocks:\n"]
        
        for block in self.blocks:
            summary_lines.append(f"- {block.name} ({block.category})")
            summary_lines.append(f"  Description: {block.description}")
            summary_lines.append(f"  Inputs: {', '.join(block.inputs.keys())}")
            summary_lines.append(f"  Outputs: {', '.join(block.outputs.keys())}")
            summary_lines.append(f"  Capabilities: {', '.join(block.capabilities)}\n")
        
        return "\n".join(summary_lines)

