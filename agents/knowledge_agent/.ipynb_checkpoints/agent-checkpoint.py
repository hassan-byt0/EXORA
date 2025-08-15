# agents/knowledge_agent/agent.py
import time
from core.agent import BaseAgent
from core.mcp_protocol import MCPMessage
from .rag_system import KnowledgeRAGSystem
from common.config import settings
from common.logger import get_logger

class KnowledgeAgent(BaseAgent):
    def __init__(self):
        super().__init__("KNOWLEDGE_AGENT")
        self.rag_system = None
        
    def _load_models(self):
        self.rag_system = KnowledgeRAGSystem()
        self.logger.info("Knowledge RAG system initialized")
        
    def process(self, message: MCPMessage):
        if not self.initialized:
            self.initialize()
            
        self.logger.info("Processing knowledge request")
        
        query = message.payload.get("query")
        context = message.payload.get("context", {})
        
        if not query:
            return self._create_error_response(message, "No query provided")
            
        try:
            start_time = time.time()
            response = self.rag_system.query(query, context)
            processing_time = time.time() - start_time
            
            result = {
                "answer": response["answer"],
                "sources": response["sources"],
                "processing_time": processing_time
            }
            
            return self.send_response(message, result)
            
        except Exception as e:
            return self._create_error_response(message, f"Knowledge query failed: {str(e)}")
            
    def _create_error_response(self, original_message: MCPMessage, error: str):
        return MCPMessage(
            header=MCPHeader(
                source=self.name,
                destination=original_message.header.source,
                context_id=original_message.header.context_id,
                message_type="error"
            ),
            payload={"error": error}
        )