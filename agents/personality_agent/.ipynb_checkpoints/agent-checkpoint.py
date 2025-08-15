# agents/personality_agent/agent.py
from core.agent import BaseAgent
from core.mcp_protocol import MCPMessage
from common.config import settings
from common.logger import get_logger
import openai

class PersonalityAgent(BaseAgent):
    def __init__(self):
        super().__init__("PERSONALITY_AGENT")
        self.persona = "helpful, witty, and slightly sarcastic AI assistant"
        self.openai_api_key = settings.openai_api_key
        
    def _load_models(self):
        # Personality agent doesn't need heavy models
        self.logger.info("Personality agent initialized")
        
    def process(self, message: MCPMessage):
        if not self.initialized:
            self.initialize()
            
        self.logger.info("Processing personality request")
        
        raw_response = message.payload.get("raw_response")
        context = message.payload.get("context", {})
        
        if not raw_response:
            return self._create_error_response(message, "No response content provided")
            
        try:
            # Add personality to the raw response
            personalized = self._apply_personality(raw_response, context)
            
            # Format response
            response = {
                "final_response": personalized,
                "persona": self.persona
            }
            
            return self.send_response(message, response)
            
        except Exception as e:
            return self._create_error_response(message, f"Personality application failed: {str(e)}")
            
    def _apply_personality(self, content: str, context: dict) -> str:
        """Apply personality traits to the raw response"""
        # Use LLM to rewrite with personality
        prompt = f"""
        Rewrite the following response in the style of a {self.persona}. 
        Keep the core information but make it more engaging and personality-driven.
        
        Context: {context.get('user_context', 'No additional context')}
        
        Original response:
        {content}
        
        Rewritten response:
        """
        
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=500,
            temperature=0.7,
            api_key=self.openai_api_key
        )
        
        return response.choices[0].text.strip()
    
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