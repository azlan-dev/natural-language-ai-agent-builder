"""Tests for block management."""
import pytest
from src.blocks import BlockManager


def test_block_manager_initialization():
    """Test that BlockManager initializes and loads blocks."""
    manager = BlockManager()
    assert len(manager.blocks) > 0


def test_get_all_blocks():
    """Test getting all blocks."""
    manager = BlockManager()
    blocks = manager.get_all_blocks()
    assert isinstance(blocks, list)
    assert len(blocks) > 0


def test_get_block_by_name():
    """Test getting a specific block by name."""
    manager = BlockManager()
    block = manager.get_block_by_name("WebSearchBlock")
    assert block is not None
    assert block.name == "WebSearchBlock"


def test_search_blocks():
    """Test searching blocks by keywords."""
    manager = BlockManager()
    results = manager.search_blocks(["email", "writing"])
    assert len(results) > 0
    assert any("email" in block.description.lower() for block in results)


def test_get_blocks_summary():
    """Test getting blocks summary for LLM."""
    manager = BlockManager()
    summary = manager.get_blocks_summary()
    assert "Available Tools/Blocks" in summary
    assert len(summary) > 100

