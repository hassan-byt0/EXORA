from pydantic import BaseModel
from typing import Dict, Any, Optional
import time
import uuid

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