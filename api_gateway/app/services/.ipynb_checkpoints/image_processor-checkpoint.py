import logging
import pytesseract
import uuid
from PIL import Image
from io import BytesIO
from fastapi import UploadFile, HTTPException, status
from common.logger import get_logger
from common.schemas import ImageProcessingResult

logger = get_logger()

async def process_image(image_file: UploadFile) -> ImageProcessingResult:
    try:
        # Read image file
        contents = await image_file.read()
        image = Image.open(BytesIO(contents))
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        # Get image metadata
        width, height = image.size
        format = image.format
        
        # Generate context ID
        context_id = f"ctx-{uuid.uuid4()}"
        
        return ImageProcessingResult(
            text=text.strip(),
            width=width,
            height=height,
            format=format,
            context_id=context_id
        )
    
    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image processing error"
        )