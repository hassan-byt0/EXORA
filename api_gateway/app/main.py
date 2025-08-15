from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import multimodal, health
from .utils.logging import setup_logging
from common.config import settings

# Setup logging
logger = setup_logging()

app = FastAPI(
    title="AAHB API Gateway",
    description="Multi-modal API Gateway for AAHB System",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(multimodal.router, prefix="/api/v1")
app.include_router(health.router, prefix="/health")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting AAHB API Gateway")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Neo4j URI: {settings.neo4j_uri}")
    logger.info(f"RabbitMQ Host: {settings.rabbitmq_host}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AAHB API Gateway")