# tests/integration/rag/test_rag_system.py
import pytest
from rag_system.generator import ResponseGenerator
from memory.graph_manager import GraphManager

@pytest.fixture
def rag_system():
    # Initialize with test database
    manager = GraphManager()
    manager.connect()
    manager.initialize_schema()
    
    # Add test data
    manager.store_memory(
        "The capital of France is Paris",
        "fact",
        entities=["France", "Paris", "capital"]
    )
    
    # Create generator
    generator = ResponseGenerator()
    return generator

def test_rag_query(rag_system):
    response = rag_system.generate_response("What is the capital of France?")
    assert "Paris" in response["content"]
    assert response["response_type"] == "answer"
    assert len(response["sources"]) > 0

def test_clarification_request(rag_system):
    response = rag_system.generate_response("What is the population?")
    assert response["response_type"] == "clarification"
    assert "missing_info" in response