import logging
import whisper
import numpy as np
import time
import uuid
from io import BytesIO
from pydub import AudioSegment
from fastapi import UploadFile, HTTPException, status
from common.logger import get_logger
from common.config import settings
from common.schemas import AudioProcessingResult

logger = get_logger()

# Load model at startup
model = None

def load_model():
    global model
    if model is None:
        logger.info(f"Loading Whisper model: {settings.whisper_model}")
        start_time = time.time()
        model = whisper.load_model(settings.whisper_model)
        load_time = time.time() - start_time
        logger.info(f"Whisper model loaded in {load_time:.2f} seconds")

async def process_audio(audio_file: UploadFile) -> AudioProcessingResult:
    try:
        # Ensure model is loaded
        if model is None:
            load_model()
        
        # Read audio file
        contents = await audio_file.read()
        audio_buffer = BytesIO(contents)
        
        # Convert to WAV if needed
        if audio_file.filename.endswith('.mp3'):
            audio = AudioSegment.from_mp3(audio_buffer)
            audio = audio.set_frame_rate(16000)
            audio = audio.set_channels(1)
            buffer_wav = BytesIO()
            audio.export(buffer_wav, format="wav")
            audio_data = buffer_wav.getvalue()
        else:
            audio_data = contents
        
        # Convert to numpy array
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Transcribe
        result = model.transcribe(audio_np, fp16=False)  # fp16=False for CPU compatibility
        
        # Generate context ID
        context_id = f"ctx-{uuid.uuid4()}"
        
        return AudioProcessingResult(
            text=result["text"],
            language=result.get("language", "en"),
            duration=result.get("duration", 0),
            context_id=context_id
        )
    
    except Exception as e:
        logger.error(f"Audio processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio processing error"
        )