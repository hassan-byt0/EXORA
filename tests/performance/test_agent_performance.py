# tests/performance/test_agent_performance.py
import pytest
import time
from agents.core.orchestrator import AgentOrchestrator
from agents.vision_agent.agent import VisionAgent
from common.mcp_protocol import MCPMessage, MCPHeader
import numpy as np

class MockVisionAgent:
    def process(self, message):
        # Simulate processing time
        time.sleep(0.1)
        return {"status": "success"}

@pytest.fixture(scope="module")
def performance_orchestrator():
    orchestrator = AgentOrchestrator()
    orchestrator.register_agent("VISION_AGENT", MockVisionAgent().process)
    orchestrator.start()
    yield orchestrator
    orchestrator.stop()

def test_agent_throughput(performance_orchestrator):
    start_time = time.time()
    message_count = 100
    
    # Send messages
    for i in range(message_count):
        message = MCPMessage(
            header=MCPHeader(
                source="PERF_TEST",
                destination="VISION_AGENT",
                context_id=f"ctx-{i}"
            ),
            payload={"data": f"payload-{i}"}
        )
        performance_orchestrator.route_message(message)
    
    # Wait for processing
    time.sleep(2)
    
    # Calculate throughput
    duration = time.time() - start_time
    throughput = message_count / duration
    
    print(f"Processed {message_count} messages in {duration:.2f} seconds")
    print(f"Throughput: {throughput:.2f} msg/sec")
    
    # Assert minimum performance
    assert throughput > 50  # At least 50 messages per second