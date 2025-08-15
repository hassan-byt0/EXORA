# tests/integration/agent_tests/test_agent_communication.py
import pytest
import time
from agents.core.orchestrator import AgentOrchestrator
from agents.vision_agent.agent import VisionAgent
from common.mcp_protocol import MCPMessage, MCPHeader
from unittest.mock import MagicMock

@pytest.fixture
def orchestrator():
    orchestrator = AgentOrchestrator()
    vision_agent = VisionAgent()
    vision_agent.process = MagicMock(return_value={"status": "processed"})
    orchestrator.register_agent("VISION_AGENT", vision_agent.process)
    orchestrator.start()
    yield orchestrator
    orchestrator.stop()

def test_agent_communication(orchestrator):
    # Create test message
    message = MCPMessage(
        header=MCPHeader(
            source="TESTER",
            destination="VISION_AGENT",
            context_id="test-123"
        ),
        payload={"test": "data"}
    )
    
    # Route message
    orchestrator.route_message(message)
    
    # Wait for processing
    time.sleep(0.5)
    
    # Verify agent was called
    vision_agent = list(orchestrator.agents.values())[0]
    vision_agent.assert_called_once()
    
    # Verify response payload
    call_args = vision_agent.call_args[0][0]
    assert call_args.header.context_id == "test-123"
    assert call_args.payload["test"] == "data"