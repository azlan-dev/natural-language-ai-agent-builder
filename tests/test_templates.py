"""Tests for template management."""
import pytest
from src.templates import TemplateManager


def test_template_manager_initialization():
    """Test that TemplateManager initializes and loads templates."""
    manager = TemplateManager()
    assert len(manager.templates) > 0


def test_get_all_templates():
    """Test getting all templates."""
    manager = TemplateManager()
    templates = manager.get_all_templates()
    assert isinstance(templates, list)
    assert len(templates) > 0


def test_search_templates():
    """Test searching templates."""
    manager = TemplateManager()
    results = manager.search_templates("sales")
    assert len(results) > 0


def test_get_template_by_id():
    """Test getting specific template by ID."""
    manager = TemplateManager()
    template = manager.get_template_by_id("sales_outreach")
    assert template is not None
    assert template.name == "Sales Outreach Agent"

