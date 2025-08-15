from fastapi import HTTPException, status
from common.logger import get_logger

logger = get_logger()

def validate_inputs(audio, image, text):
    # At least one input must be provided
    if not any([audio, image, text]):
        logger.warning("No input provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one input (audio, image, or text) is required"
        )
    
    # Validate audio file
    if audio:
        if not audio.content_type.startswith('audio/'):
            logger.warning(f"Invalid audio content type: {audio.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid audio file format"
            )
        if audio.size > 10 * 1024 * 1024:  # 10MB limit
            logger.warning(f"Audio file too large: {audio.size} bytes")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Audio file exceeds 10MB limit"
            )
    
    # Validate image file
    if image:
        if not image.content_type.startswith('image/'):
            logger.warning(f"Invalid image content type: {image.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file format"
            )
        if image.size > 5 * 1024 * 1024:  # 5MB limit
            logger.warning(f"Image file too large: {image.size} bytes")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image file exceeds 5MB limit"
            )
    
    # Validate text
    if text and len(text) > 10000:  # 10k characters limit
        logger.warning(f"Text input too long: {len(text)} characters")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Text input exceeds 10000 characters limit"
        )