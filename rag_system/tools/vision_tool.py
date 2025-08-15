# rag_system/tools/vision_tool.py
import base64
import numpy as np
from PIL import Image
from io import BytesIO
from transformers import pipeline
from common.config import settings
from common.logger import get_logger

logger = get_logger("vision_tool")

class VisionTool:
    def __init__(self):
        self.image_analyzer = pipeline(
            "image-to-text",
            model="Salesforce/blip-image-captioning-base",
            device=0 if settings.gpu_enabled else -1
        )
        logger.info("Vision tool initialized")
    
    def analyze(self, image_data: str) -> str:
        """Analyze image and generate description"""
        try:
            # Decode image
            image = self._decode_image(image_data)
            
            # Generate caption
            result = self.image_analyzer(image)
            caption = result[0]["generated_text"]
            
            logger.info(f"Image caption: {caption}")
            return caption
            
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            return ""
    
    def _decode_image(self, image_data: str) -> Image.Image:
        if isinstance(image_data, str) and image_data.startswith("data:image"):
            # Data URI format: data:image/jpeg;base64,...
            header, encoded = image_data.split(",", 1)
            image_bytes = base64.b64decode(encoded)
        else:
            # Assume raw bytes
            image_bytes = base64.b64decode(image_data)
            
        return Image.open(BytesIO(image_bytes))