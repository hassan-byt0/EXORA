# EXORA: Multimodal AI Agent System

## Overviewā
EXORA is a modular, multimodal AI agent platform designed for advanced knowledge retrieval, reasoning, and AR integration. It leverages LLMs (OpenAI, Gemini), Neo4j for graph storage, RabbitMQ for messaging, and supports audio, image, and text processing. The system is built for extensibility, research, and real-world AR applications.

## Features
- **API Gateway**: FastAPI-based, handles multimodal requests (audio, image, text).
- **Agents**: Modular agents for knowledge, personality, planning, and vision.
- **RAG System**: Retrieval-Augmented Generation using LLMs and Neo4j vector store.
- **AR Interface**: Unity-based AR client for real-time interaction.
- **Messaging**: RabbitMQ for agent orchestration and communication.
- **LLM Support**: Easily switch between OpenAI and Gemini (Google AI Studio) via `.env`.

## Quick Start

### 1. Clone and Setup
```sh
# Clone the repo
cd /path/to/your/workspace
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
- Copy `env.txt` to `.env` and fill in your API keys (OpenAI, Gemini, Neo4j, RabbitMQ, etc).
- For Gemini (Google AI Studio), only `GEMINI_API_KEY` and `GEMINI_MODEL` are required.

### 3. Start Services
```sh
cd infrastructure
cp ../env.txt .env  # Ensure .env is present for Docker Compose
# Start Neo4j and RabbitMQ
docker compose up -d neo4j rabbitmq
```

### 4. Initialize Database and Models
```sh
make setup-db
make preload-models
```

### 5. Run API Gateway and Agents
```sh
cd api_gateway
uvicorn app.main:app --reload
cd ../agents
python start_agents.py
```

### 6. Run Tests
```sh
pytest
```

### 7. AR Interface
- Open `ar_interface` in Unity (2022.x or 2023.x recommended).
- Build and run on device for full AR experience.

## Folder Structure
- `agents/` - All agent logic (knowledge, personality, planning, vision)
- `api_gateway/` - FastAPI app and routers
- `ar_interface/` - Unity AR client
- `common/` - Shared config, schemas, utilities
- `infrastructure/` - Docker, Kubernetes, setup scripts
- `memory/` - Graph manager, temporal processor, vector indexing
- `rag_system/` - RAG generator, retriever, tools
- `tests/` - Unit, integration, performance tests

## Environment Variables
See `.env` for all required settings. Key variables:
- `OPENAI_API_KEY`, `GEMINI_API_KEY`, `NEO4J_URI`, `RABBITMQ_HOST`, etc.
- `LLM_PROVIDER=openai` or `gemini`

## Troubleshooting
- Ensure all services (Neo4j, RabbitMQ) are running before starting agents/API.
- Use Python 3.10 or 3.11 for best compatibility.
- For Gemini, use Google AI Studio API key (not Vertex AI).
- Check logs for errors and missing dependencies.

## License
MIT

## Contact
For questions or contributions, open an issue or contact the maintainer.
