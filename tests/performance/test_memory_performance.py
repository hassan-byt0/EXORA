# tests/performance/test_memory_performance.py
import pytest
import time
import numpy as np
from memory.graph_manager import GraphManager
from memory.vector_indexing.embeddings import EmbeddingModel

@pytest.fixture(scope="module")
def performance_manager():
    manager = GraphManager()
    manager.connect()
    manager.initialize_schema()
    return manager

def test_memory_storage_performance(performance_manager):
    start_time = time.time()
    count = 100
    
    for i in range(count):
        content = f"Test memory content {i}"
        performance_manager.store_memory(content, "test")
    
    duration = time.time() - start_time
    print(f"Stored {count} memories in {duration:.2f} seconds")
    print(f"Rate: {count/duration:.2f} memories/sec")
    
    assert duration < 5  # Should take less than 5 seconds

def test_memory_retrieval_performance(performance_manager):
    start_time = time.time()
    query = "test content"
    results = performance_manager.retrieve_context(query, top_k=10)
    duration = time.time() - start_time
    
    print(f"Retrieved {len(results)} memories in {duration:.4f} seconds")
    assert duration < 0.5  # Should be very fast