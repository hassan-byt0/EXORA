# tests/unit/memory/test_graph_manager.py
import pytest
from memory.graph_manager import GraphManager
from common.config import settings
from datetime import datetime

@pytest.fixture
def graph_manager():
    manager = GraphManager()
    manager.connect()
    manager.initialize_schema()
    return manager

def test_store_memory(graph_manager):
    memory_id = graph_manager.store_memory(
        content="Test memory content",
        memory_type="test",
        entities=["test_entity"]
    )
    assert memory_id is not None
    assert isinstance(memory_id, str)

def test_retrieve_context(graph_manager):
    # Store a memory
    content = "Important information for retrieval"
    graph_manager.store_memory(content, "test")
    
    # Retrieve context
    context = graph_manager.retrieve_context("important information")
    assert len(context) > 0
    assert content in context[0]["content"]

def test_temporal_relationships(graph_manager):
    # Create two memories
    mem1 = graph_manager.store_memory("Event A", "event")
    mem2 = graph_manager.store_memory("Event B", "event")
    
    # Create temporal relationship
    success = graph_manager.create_temporal_relationship(mem1, mem2, "BEFORE")
    assert success is True
    
    # Find relationships
    relationships = graph_manager.find_temporal_relationships(mem1)
    assert len(relationships) > 0
    assert relationships[0]["from_id"] == mem1
    assert relationships[0]["to_id"] == mem2