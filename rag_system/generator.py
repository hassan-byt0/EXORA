# rag_system/generator.py
import json
from typing import Dict, Any
from langchain.chains import LLMChain
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate
from common.config import settings
from common.logger import get_logger
from .retriever import GraphRetriever

logger = get_logger("generator")

class ResponseGenerator:
    def __init__(self):
        self.llm = OpenAI(
            temperature=0.7,
            max_tokens=500,
            openai_api_key=settings.openai_api_key
        )
        self.retriever = GraphRetriever()
        
        # Define prompt templates
        self.response_template = PromptTemplate(
            input_variables=["query", "context", "persona"],
            template="""
            You are AAHB, an advanced AI assistant. Your personality: {persona}
            
            Contextual information:
            {context}
            
            User query: {query}
            
            Instructions:
            1. Provide a comprehensive, accurate response
            2. Cite sources when possible
            3. Maintain a {persona} tone
            4. If information is insufficient, ask clarifying questions
            
            Response:
            """
        )
        
        self.clarification_template = PromptTemplate(
            input_variables=["query", "missing_info"],
            template="""
            The user asked: {query}
            
            Additional information needed:
            {missing_info}
            
            Politely ask for the missing information in a helpful tone.
            """
        )
    
    def generate_response(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        # Retrieve relevant context
        retrieved_context = self.retriever.retrieve_context(query, context)
        logger.info(f"Retrieved {len(retrieved_context)} context items")
        
        # Format context for LLM
        context_str = self._format_context(retrieved_context)
        
        # Check if context is sufficient
        if not self._is_context_sufficient(retrieved_context, query):
            missing_info = self._identify_missing_info(query, retrieved_context)
            clarification = self._request_clarification(query, missing_info)
            return {
                "response_type": "clarification",
                "content": clarification,
                "context_used": [],
                "missing_info": missing_info
            }
        
        # Generate response
        persona = context.get("persona", "helpful and professional") if context else "helpful and professional"
        chain = LLMChain(llm=self.llm, prompt=self.response_template)
        response = chain.run(query=query, context=context_str, persona=persona)
        
        return {
            "response_type": "answer",
            "content": response,
            "context_used": retrieved_context,
            "sources": [ctx["source"] for ctx in retrieved_context]
        }
    
    def _format_context(self, context_data: List[Dict[str, Any]]) -> str:
        """Format context data for LLM consumption"""
        context_str = ""
        for i, ctx in enumerate(context_data):
            context_str += f"Context source {i+1} ({ctx['source']}, confidence: {ctx['confidence']:.2f}):\n"
            context_str += f"{ctx['content']}\n\n"
        return context_str.strip()
    
    def _is_context_sufficient(self, context_data: List[Dict[str, Any]], query: str) -> bool:
        """Determine if context is sufficient to answer the query"""
        if not context_data:
            return False
            
        # Check confidence levels
        top_confidence = context_data[0]["confidence"]
        if top_confidence < 0.6:
            logger.warning(f"Low confidence context: {top_confidence}")
            return False
            
        # Check for specific missing information patterns
        missing_keywords = ["who is", "what is", "explain", "define"]
        if any(kw in query.lower() for kw in missing_keywords) and top_confidence < 0.75:
            return False
            
        return True
    
    def _identify_missing_info(self, query: str, context_data: List[Dict[str, Any]]) -> str:
        """Identify what information is missing"""
        # Simple heuristic - in production we'd use more sophisticated methods
        if "when" in query.lower() and not any(ctx["source"] == "temporal_tool" for ctx in context_data):
            return "temporal information"
            
        if ("show" in query.lower() or "look" in query.lower()) and not any(ctx["source"] == "vision_tool" for ctx in context_data):
            return "visual context"
            
        return "relevant information"
    
    def _request_clarification(self, query: str, missing_info: str) -> str:
        """Generate a clarification request"""
        chain = LLMChain(llm=self.llm, prompt=self.clarification_template)
        return chain.run(query=query, missing_info=missing_info)