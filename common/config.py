import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Environment configuration
    ENV: str = os.getenv("ENV", "development")
    VERSION: str = "0.1.0"
    
    # API Gateway settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Model configurations
    whisper_model: str = os.getenv("WHISPER_MODEL", "base")
    
    # Storage configurations
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")
    
    # Messaging configuration
    rabbitmq_host: str = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_user: str = os.getenv("RABBITMQ_USER", "guest")
    rabbitmq_password: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    
    # Testing flags
    TEST_AUDIO_ENABLED: bool = os.getenv("TEST_AUDIO_ENABLED", "false").lower() == "true"
    TEST_IMAGE_ENABLED: bool = os.getenv("TEST_IMAGE_ENABLED", "false").lower() == "true"

    # LLM configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # 'openai' or 'gemini'
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_project_id: str = os.getenv("GEMINI_PROJECT_ID", "")
    gemini_location: str = os.getenv("GEMINI_LOCATION", "us-central1")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    enable_openai: bool = os.getenv("ENABLE_OPENAI", "true").lower() == "true"
    enable_gemini: bool = os.getenv("ENABLE_GEMINI", "false").lower() == "true"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()