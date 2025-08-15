# tests/unit/rag/test_generator.py
import pytest
from rag_system.generator import ResponseGenerator
from unittest.mock import MagicMock, patch

@pytest.fixture
def response_generator():
    generator = ResponseGenerator()
    generator.retriever = MagicMock()
    generator.llm = MagicMock()
    return generator

def test_generate_response(response_generator):
    # Mock retrieved context
    mock_context = [
        {"source": "memory", "content": "Context 1", "confidence": 0.9},
        {"source": "vision", "content": "Context 2", "confidence": 0.85}
    ]
    response_generator.retriever.retrieve_context.return_value = mock_context
    
    # Mock LLM response
    response_generator.llm.run.return_value = "Generated response"
    
    # Generate response
    response = response_generator.generate_response("test query")
    
    assert response["response_type"] == "answer"
    assert response["content"] == "Generated response"
    assert len(response["context_used"]) == 2

def test_clarification_request(response_generator):
    # Mock insufficient context
    response_generator.retriever.retrieve_context.return_value = [
        {"source": "memory", "content": "Weak context", "confidence": 0.4}
    ]
    
    # Generate response
    response = response_generator.generate_response("test query")
    
    assert response["response_type"] == "clarification"
    assert "missing_info" in response