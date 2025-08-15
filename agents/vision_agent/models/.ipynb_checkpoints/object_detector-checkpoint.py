# agents/vision_agent/models/object_detector.py
import cv2
import numpy as np
from PIL import Image
from common.logger import get_logger
from ultralytics import YOLO

logger = get_logger("object_detector")

class ObjectDetector:
    def __init__(self, model_name: str = "yolov8n.pt"):
        logger.info(f"Loading object detection model: {model_name}")
        self.model = YOLO(model_name)
        logger.info("Object detection model loaded")
        
    def detect_objects(self, image: Image.Image) -> list:
        # Convert PIL image to OpenCV format
        cv_image = np.array(image)
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
        
        # Run detection
        results = self.model(cv_image)
        
        # Parse results
        detections = []
        for result in results:
            for box in result.boxes:
                obj = {
                    "class": result.names[box.cls[0].item()],
                    "confidence": box.conf[0].item(),
                    "bbox": box.xyxy[0].tolist()
                }
                detections.append(obj)
                
        return detections