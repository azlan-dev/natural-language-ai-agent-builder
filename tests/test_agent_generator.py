"""Tests for agent generation (requires API keys)."""
import pytest
import json
from src.agent_generator import AgentGenerator, AGENT_SCHEMA


def test_agent_schema_validation():
    """Test that agent schema validates correct configurations."""
    valid_agent = {
        "name": "Test Agent",
        "description": "A test agent",
        "systemPrompt": "You are a helpful assistant",
        "tasks": [
            {
                "id": "task1",
                "name": "Test Task",
                "blockName": "WebSearchBlock",
                "inputs": {"query": "test"}
            }
        ]
    }
    
    import jsonschema
    # Should not raise exception
    jsonschema.validate(instance=valid_agent, schema=AGENT_SCHEMA)


def test_agent_validation_missing_fields():
    """Test that validation catches missing fields."""
    invalid_agent = {
        "name": "Test Agent"
        # Missing required fields
    }
    
    import jsonschema
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_agent, schema=AGENT_SCHEMA)


@pytest.mark.skipif(True, reason="Requires API key and makes external calls")
def test_generate_from_template():
    """Test generating agent from template."""
    generator = AgentGenerator()
    result = generator.generate_from_template("sales_outreach")
    
    assert "agent" in result
    assert "metadata" in result
    assert result["agent"]["name"] == "Sales Outreach Assistant"


def test_validate_agent_with_issues():
    """Test agent validation with issues."""
    generator = AgentGenerator()
    
    invalid_agent = {
        "name": "Test",
        "description": "Test",
        "systemPrompt": "Test",
        "tasks": [
            {
                "id": "task1",
                "name": "Test",
                "blockName": "NonExistentBlock",
                "inputs": {}
            }
        ]
    }
    
    issues = generator.validate_agent(invalid_agent)
    assert len(issues) > 0
    assert any("NonExistentBlock" in issue for issue in issues)

