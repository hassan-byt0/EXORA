# agents/vision_agent/models/clip_processor.py
import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from common.config import settings
from common.logger import get_logger

logger = get_logger("clip_processor")

class CLIPProcessor:
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading CLIP model: {model_name} on {self.device}")
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        logger.info("CLIP model loaded")
        
    def describe_image(self, image: Image.Image) -> str:
        inputs = self.processor(
            text=["a photo of"], 
            images=image, 
            return_tensors="pt", 
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Get image-text similarity score
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1).cpu().numpy()
        
        # For simplicity, return top 3 descriptions
        # In a real system, we'd use more sophisticated captioning
        return f"An image with visual features matching probabilities: {probs[0]}"
        
    def image_to_vector(self, image: Image.Image) -> np.ndarray:
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            features = self.model.get_image_features(**inputs)
        return features.cpu().numpy().flatten()