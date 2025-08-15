# agents/core/agent.py
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict
from common.config import settings
from common.logger import get_logger
from .mcp_protocol import MCPMessage

class BaseAgent(ABC):
    def __init__(self, agent_name: str):
        self.name = agent_name
        self.logger = get_logger(f"agent.{agent_name}")
        self.context = None
        self.initialized = False
        
    def initialize(self):
        """Initialize agent resources"""
        self.logger.info(f"Initializing {self.name} agent")
        self._load_models()
        self.initialized = True
        self.logger.info(f"{self.name} agent initialized successfully")
    
    @abstractmethod
    def _load_models(self):
        """Load required models for the agent"""
        pass
    
    @abstractmethod
    def process(self, message: MCPMessage) -> Dict[str, Any]:
        """Main processing method for agents"""
        pass
    
    def send_response(self, original_message: MCPMessage, response: Dict[str, Any]):
        """Send response using MCP protocol"""
        response_msg = MCPMessage(
            header=MCPHeader(
                source=self.name,
                destination=original_message.header.source,
                context_id=original_message.header.context_id,
                message_type="response"
            ),
            payload=response
        )
        self.logger.debug(f"Sending response to {original_message.header.source}")
        # This would connect to RabbitMQ in production
        return response_msg