# agents/core/mcp_protocol.py
import time
import uuid
from pydantic import BaseModel
from typing import Dict, Any

class MCPHeader(BaseModel):
    protocol: str = "MCP/1.0"
    source: str
    destination: str
    context_id: str
    timestamp: float = time.time()
    message_id: str = str(uuid.uuid4())
    message_type: str = "request"  # request/response/error

class MCPMessage(BaseModel):
    header: MCPHeader
    payload: Dict[str, Any]
    
    def serialize(self) -> str:
        return self.json()
    
    @classmethod
    def deserialize(cls, data: str):
        return cls.parse_raw(data)