import logging
from fastapi import APIRouter, UploadFile, Form, HTTPException, status
from app.services import audio_processor, image_processor, text_processor
from app.utils.validation import validate_inputs
from common.schemas import MultiModalInput, ProcessedOutput
from common.mcp_protocol import MCPMessage, MCPHeader
from common.utils import send_mcp_message
from common.config import settings
from common.logger import get_logger

router = APIRouter()
logger = get_logger()

@router.post("/process", response_model=ProcessedOutput)
async def process_input(
    audio: UploadFile = None,
    image: UploadFile = None,
    text: str = Form(None)
):
    try:
        # Validate inputs
        validate_inputs(audio, image, text)
        
        # Process inputs
        processed = {}
        context_id = None
        
        if audio:
            audio_result = await audio_processor.process_audio(audio)
            processed["audio"] = audio_result
            context_id = audio_result.get("context_id")
        
        if image:
            image_result = await image_processor.process_image(image)
            processed["image"] = image_result
            context_id = context_id or image_result.get("context_id")
        
        if text:
            text_result = text_processor.process_text(text)
            processed["text"] = text_result
            context_id = context_id or text_result.get("context_id")
        
        # Create MCP message
        mcp_message = MCPMessage(
            header=MCPHeader(
                source="API_GATEWAY",
                destination="ORCHESTRATOR",
                context_id=context_id,
                message_type="request"
            ),
            payload=processed
        )
        
        # Send to RabbitMQ
        await send_mcp_message(mcp_message, settings.rabbitmq_host)
        
        return {
            "status": "success",
            "context_id": context_id,
            "message": "Input processed and routed to orchestrator"
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception(f"Processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during processing"
        )