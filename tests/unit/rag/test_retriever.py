# tests/unit/rag/test_retriever.py
import pytest
from rag_system.retriever import GraphRetriever
from memory.graph_manager import GraphManager
from unittest.mock import MagicMock

@pytest.fixture
def graph_retriever():
    retriever = GraphRetriever()
    retriever.graph_manager = MagicMock()
    return retriever

def test_retrieve_context(graph_retriever):
    # Mock context retrieval
    graph_retriever.graph_manager.retrieve_context.return_value = [
        {"content": "Test context 1", "score": 0.9},
        {"content": "Test context 2", "score": 0.85}
    ]
    
    context_data = graph_retriever.retrieve_context("test query")
    assert len(context_data) == 2
    assert context_data[0]["source"] == "graph_memory"
    assert context_data[0]["confidence"] == 0.9

def test_enhance_query(graph_retriever):
    # Without context
    enhanced = graph_retriever._enhance_query("test query")
    assert enhanced == "test query"
    
    # With vision context
    graph_retriever.context = {"vision_context": "image description"}
    enhanced = graph_retriever._enhance_query("test query")
    assert "image description" in enhanced
    
    # With temporal context
    graph_retriever.context = {"temporal_context": "timeline info"}
    enhanced = graph_retriever._enhance_query("test query")
    assert "timeline" in enhanced