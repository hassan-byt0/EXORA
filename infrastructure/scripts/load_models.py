import os
import torch
from common.config import settings
from common.logger import get_logger

logger = get_logger("model_loader")

MODELS = {
    "whisper": {
        "sizes": ["tiny", "base", "small", "medium"],
        "repo": "openai/whisper"
    },
    "clip": {
        "sizes": ["base", "large"],
        "repo": "openai/clip-vit-base-patch32"
    },
    "yolo": {
        "sizes": ["n", "s", "m", "l", "x"],
        "repo": "ultralytics/yolov8"
    }
}

def download_model(model_type, size):
    logger.info(f"Downloading {model_type} model ({size})")
    try:
        if model_type == "whisper":
            import whisper
            whisper.load_model(size)
        elif model_type == "clip":
            from transformers import CLIPModel
            CLIPModel.from_pretrained(f"openai/clip-vit-{size}-patch32")
        elif model_type == "yolo":
            from ultralytics import YOLO
            YOLO(f"yolov8{size}.pt")
        logger.info(f"Model downloaded: {model_type}-{size}")
    except Exception as e:
        logger.error(f"Failed to download model: {str(e)}")

def main():
    logger.info("Starting model preloading")
    
    # Create model cache directory
    os.makedirs("/root/.cache", exist_ok=True)
    
    # Download specified models
    for model_type, config in MODELS.items():
        for size in config["sizes"]:
            if size in settings.preload_models.get(model_type, []):
                download_model(model_type, size)
    
    # Clean up to save space
    torch.cuda.empty_cache()
    logger.info("Model preloading completed")

if __name__ == "__main__":
    main()