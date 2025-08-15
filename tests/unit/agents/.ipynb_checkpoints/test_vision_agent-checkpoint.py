# tests/unit/agents/test_vision_agent.py
import pytest
from unittest.mock import MagicMock, patch
from agents.vision_agent.agent import VisionAgent
from common.mcp_protocol import MCPMessage, MCPHeader
from PIL import Image
import numpy as np
import io

@pytest.fixture
def vision_agent():
    agent = VisionAgent()
    agent.initialize = MagicMock()
    agent._load_models = MagicMock()
    return agent

def test_vision_agent_initialization(vision_agent):
    assert vision_agent.name == "VISION_AGENT"
    vision_agent.initialize.assert_called_once()

def test_process_valid_image(vision_agent):
    # Create a test image
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_data = img_byte_arr.getvalue()
    
    # Mock models
    vision_agent.clip_processor = MagicMock()
    vision_agent.clip_processor.describe_image.return_value = "Red square"
    vision_agent.object_detector = MagicMock()
    vision_agent.object_detector.detect_objects.return_value = [{"class": "object"}]
    
    # Create message
    message = MCPMessage(
        header=MCPHeader(
            source="TESTER",
            destination="VISION_AGENT",
            context_id="test-123"
        ),
        payload={"image_data": img_data}
    )
    
    response = vision_agent.process(message)
    assert "image_description" in response.payload
    assert "detected_objects" in response.payload
    assert response.payload["image_description"] == "Red square"

def test_process_missing_image(vision_agent):
    message = MCPMessage(
        header=MCPHeader(
            source="TESTER",
            destination="VISION_AGENT",
            context_id="test-123"
        ),
        payload={}
    )
    
    response = vision_agent.process(message)
    assert response.header.message_type == "error"
    assert "No image data" in response.payload["error"]