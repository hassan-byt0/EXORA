# agents/vision_agent/agent.py
import base64
import numpy as np
from io import BytesIO
from PIL import Image
from core.agent import BaseAgent
from core.mcp_protocol import MCPMessage
from .models.clip_processor import CLIPProcessor
from .models.object_detector import ObjectDetector

class VisionAgent(BaseAgent):
    def __init__(self):
        super().__init__("VISION_AGENT")
        self.clip_processor = None
        self.object_detector = None
        
    def _load_models(self):
        self.clip_processor = CLIPProcessor()
        self.object_detector = ObjectDetector()
        self.logger.info("Vision models loaded")
        
    def process(self, message: MCPMessage):
        if not self.initialized:
            self.initialize()
            
        self.logger.info("Processing vision request")
        
        # Extract image data from payload
        image_data = message.payload.get("image_data")
        if not image_data:
            return self._create_error_response(message, "No image data provided")
            
        try:
            # Decode base64 image
            image = self._decode_image(image_data)
            
            # Process with models
            clip_description = self.clip_processor.describe_image(image)
            objects = self.object_detector.detect_objects(image)
            
            # Prepare response
            response = {
                "image_description": clip_description,
                "detected_objects": objects,
                "analysis_time": time.time() - message.header.timestamp
            }
            
            return self.send_response(message, response)
            
        except Exception as e:
            return self._create_error_response(message, f"Vision processing failed: {str(e)}")
            
    def _decode_image(self, image_data: str) -> Image.Image:
        if isinstance(image_data, str) and image_data.startswith("data:image"):
            # Data URI format: data:image/jpeg;base64,...
            header, encoded = image_data.split(",", 1)
            image_bytes = base64.b64decode(encoded)
        else:
            # Assume raw bytes
            image_bytes = base64.b64decode(image_data)
            
        return Image.open(BytesIO(image_bytes))
    
    def _create_error_response(self, original_message: MCPMessage, error: str):
        return MCPMessage(
            header=MCPHeader(
                source=self.name,
                destination=original_message.header.source,
                context_id=original_message.header.context_id,
                message_type="error"
            ),
            payload={"error": error}
        )