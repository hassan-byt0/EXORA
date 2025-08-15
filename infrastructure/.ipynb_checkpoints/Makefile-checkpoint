# AAHB Infrastructure Management

.PHONY: build start stop test clean

# Environment setup
init:
	@echo "Creating data directories..."
	@mkdir -p neo4j/data
	@mkdir -p rabbitmq/data
	@mkdir -p monitoring/data
	@echo "Initializing environment..."
	@cp .env.example .env
	@echo "Please update .env with your configuration"

# Build Docker images
build:
	@echo "Building Docker images..."
	docker build -t aahb-api-gateway -f ../api_gateway/Dockerfile ../api_gateway
	docker build -t aahb-agent-orchestrator -f ../agents/Dockerfile ../agents
	docker build -t aahb-neo4j-custom -f neo4j/Dockerfile neo4j

# Start the system
start:
	@echo "Starting AAHB infrastructure..."
	docker-compose up -d

# Stop the system
stop:
	@echo "Stopping AAHB infrastructure..."
	docker-compose down

# Test the system
test:
	@echo "Running infrastructure tests..."
	python scripts/test_mcp.py

# Clean up resources
clean:
	@echo "Cleaning up..."
	docker-compose down -v
	rm -rf neo4j/data/*
	rm -rf rabbitmq/data/*
	rm -rf monitoring/data/*

# Setup database
setup-db:
	@echo "Setting up database..."
	python scripts/setup_db.py

# Preload models
preload-models:
	@echo "Preloading ML models..."
	python scripts/load_models.py

# Deploy to Kubernetes
k8s-deploy:
	@echo "Deploying to Kubernetes..."
	kubectl apply -f kubernetes/namespace.yaml
	kubectl apply -f kubernetes/neo4j/
	kubectl apply -f kubernetes/rabbitmq/
	kubectl apply -f kubernetes/api-gateway/
	kubectl apply -f kubernetes/agents/
	kubectl apply -f kubernetes/monitoring/