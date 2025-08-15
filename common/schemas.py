from pydantic import BaseModel
from typing import Optional

class MultiModalInput(BaseModel):
    audio: Optional[dict] = None
    image: Optional[dict] = None
    text: Optional[dict] = None

class AudioProcessingResult(BaseModel):
    text: str
    language: str
    duration: float
    context_id: str

class ImageProcessingResult(BaseModel):
    text: str
    width: int
    height: int
    format: str
    context_id: str

class TextProcessingResult(BaseModel):
    text: str
    token_count: int
    context_id: str

class ProcessedOutput(BaseModel):
    status: str
    context_id: str
    message: str