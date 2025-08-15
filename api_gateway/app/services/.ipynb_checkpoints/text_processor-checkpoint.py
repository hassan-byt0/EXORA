import uuid
import tiktoken
from common.logger import get_logger
from common.schemas import TextProcessingResult

logger = get_logger()

def process_text(text: str) -> TextProcessingResult:
    # Basic text cleaning
    cleaned_text = text.strip()
    
    # Token count estimation
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(cleaned_text)
    token_count = len(tokens)
    
    # Generate context ID
    context_id = f"ctx-{uuid.uuid4()}"
    
    return TextProcessingResult(
        text=cleaned_text,
        token_count=token_count,
        context_id=context_id
    )