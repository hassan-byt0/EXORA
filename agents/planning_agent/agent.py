# agents/planning_agent/agent.py
from core.agent import BaseAgent
from core.mcp_protocol import MCPMessage
from common.config import settings
from common.logger import get_logger
import json

class PlanningAgent(BaseAgent):
    def __init__(self):
        super().__init__("PLANNING_AGENT")
        self.planning_model = None
        
    def _load_models(self):
        # In a real system, we'd load a planning model here
        self.logger.info("Planning models loaded (simulated)")
        
    def process(self, message: MCPMessage):
        if not self.initialized:
            self.initialize()
            
        self.logger.info("Processing planning request")
        
        goal = message.payload.get("goal")
        constraints = message.payload.get("constraints", {})
        
        if not goal:
            return self._create_error_response(message, "No goal provided")
            
        try:
            # Generate plan
            plan = self._generate_plan(goal, constraints)
            
            # Format response
            response = {
                "plan": plan,
                "steps": len(plan),
                "estimated_duration": sum(step.get("duration", 0) for step in plan)
            }
            
            return self.send_response(message, response)
            
        except Exception as e:
            return self._create_error_response(message, f"Planning failed: {str(e)}")
            
    def _generate_plan(self, goal: str, constraints: dict) -> list:
        """Generate a plan to achieve the given goal"""
        # Simulated planning logic
        # In a real system, we'd use an LLM or planning algorithm
        
        return [
            {"step": 1, "action": "Analyze goal", "duration": 5},
            {"step": 2, "action": "Gather resources", "duration": 10},
            {"step": 3, "action": "Execute primary task", "duration": 30},
            {"step": 4, "action": "Verify results", "duration": 10},
            {"step": 5, "action": "Report completion", "duration": 5}
        ]
    
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