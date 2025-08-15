# agents/start_agents.py
#!/usr/bin/env python3
import time
from common.config import settings
from common.logger import get_logger
from .core.orchestrator import AgentOrchestrator
from .vision_agent import VisionAgent
from .knowledge_agent import KnowledgeAgent
from .planning_agent import PlanningAgent
from .personality_agent import PersonalityAgent

logger = get_logger("agent_system")

def main():
    logger.info("Starting AAHB Agent System")
    
    # Create orchestrator
    orchestrator = AgentOrchestrator()
    
    # Create and register agents
    vision_agent = VisionAgent()
    knowledge_agent = KnowledgeAgent()
    planning_agent = PlanningAgent()
    personality_agent = PersonalityAgent()
    
    orchestrator.register_agent("VISION_AGENT", vision_agent.process)
    orchestrator.register_agent("KNOWLEDGE_AGENT", knowledge_agent.process)
    orchestrator.register_agent("PLANNING_AGENT", planning_agent.process)
    orchestrator.register_agent("PERSONALITY_AGENT", personality_agent.process)
    
    # Initialize agents
    vision_agent.initialize()
    knowledge_agent.initialize()
    planning_agent.initialize()
    personality_agent.initialize()
    
    # Start orchestrator
    orchestrator.start()
    
    logger.info("Agent system is running. Press Ctrl+C to exit.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down agent system")
        orchestrator.stop()

if __name__ == "__main__":
    main()