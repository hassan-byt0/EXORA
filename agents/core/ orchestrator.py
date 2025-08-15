# agents/core/orchestrator.py
import logging
import threading
import queue
import time
from typing import Dict, Callable
from common.logger import get_logger
from .mcp_protocol import MCPMessage
from common.config import settings

class AgentOrchestrator:
    def __init__(self):
        self.agents: Dict[str, Callable] = {}
        self.message_queue = queue.PriorityQueue()
        self.context_map = {}
        self.logger = get_logger("orchestrator")
        self.running = False
        self.thread = threading.Thread(target=self._process_messages)
        
    def register_agent(self, agent_id: str, agent_handler: Callable):
        self.agents[agent_id.lower()] = agent_handler
        self.logger.info(f"Registered agent: {agent_id}")
        
    def route_message(self, message: MCPMessage):
        priority = 1 if message.header.message_type == "request" else 2
        self.message_queue.put((priority, time.time(), message))
        
    def start(self):
        self.running = True
        self.thread.start()
        self.logger.info("Agent orchestrator started")
        
    def stop(self):
        self.running = False
        self.thread.join()
        self.logger.info("Agent orchestrator stopped")
        
    def _process_messages(self):
        while self.running:
            if not self.message_queue.empty():
                _, _, message = self.message_queue.get()
                self._handle_message(message)
            else:
                time.sleep(0.1)  # Prevent busy waiting
                
    def _handle_message(self, message: MCPMessage):
        target_agent = message.header.destination.lower()
        context_id = message.header.context_id
        
        self.logger.debug(f"Routing message to {target_agent} (Context: {context_id})")
        
        if target_agent not in self.agents:
            error_msg = f"Agent {target_agent} not found"
            self.logger.error(error_msg)
            # Create error response
            return
        
        try:
            # Update context state
            if context_id not in self.context_map:
                self.context_map[context_id] = {
                    "state": "ACTIVE",
                    "history": []
                }
            self.context_map[context_id]["history"].append(message)
            
            # Dispatch to agent
            response = self.agents[target_agent](message)
            
            # If agent returns a response message, route it
            if isinstance(response, MCPMessage):
                self.route_message(response)
                
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self.logger.exception(error_msg)
            # Create error response