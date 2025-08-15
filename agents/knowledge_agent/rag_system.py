# agents/knowledge_agent/rag_system.py
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Neo4jVector
from langchain_community.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from common.config import settings
from common.logger import get_logger

# Gemini fallback: use a placeholder if not installed
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

logger = get_logger("rag_system")

class KnowledgeRAGSystem:
    def __init__(self):
        logger.info("Initializing Knowledge RAG System")
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key
        )
        
        # Connect to Neo4j vector store
        self.vector_store = Neo4jVector.from_existing_index(
            embedding=self.embeddings,
            url=settings.neo4j_uri,
            username=settings.neo4j_user,
            password=settings.neo4j_password,
            index_name="memory_embeddings",
            node_label="Memory",
            text_node_property="content",
            embedding_node_property="embedding"
        )
        
        # LLM selection logic
        if settings.llm_provider == "gemini" and settings.enable_gemini and ChatGoogleGenerativeAI:
            self.llm = ChatGoogleGenerativeAI(
                google_api_key=settings.gemini_api_key,
                model=settings.gemini_model
            )
        elif settings.llm_provider == "gemini" and not ChatGoogleGenerativeAI:
            raise ImportError("Gemini LLM selected but langchain_google_genai is not installed.")
        else:
            self.llm = OpenAI(
                temperature=0,
                openai_api_key=settings.openai_api_key
            )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(),
            return_source_documents=True
        )
        
        logger.info("Knowledge RAG System initialized")
    
    def query(self, query: str, context: dict = None) -> dict:
        logger.info(f"Processing query: {query}")
        
        # Enhance query with context
        enhanced_query = self._enhance_query(query, context)
        
        # Execute query
        result = self.qa_chain({"query": enhanced_query})
        
        # Format response
        sources = [doc.metadata["source"] for doc in result["source_documents"]]
        
        return {
            "answer": result["result"],
            "sources": sources,
            "context_used": context
        }
    
    def _enhance_query(self, query: str, context: dict) -> str:
        """Enhance query with contextual information"""
        if not context:
            return query
            
        # Add vision context if available
        if "vision" in context:
            return f"Based on this visual context: {context['vision']}. {query}"
            
        # Add temporal context if available
        if "temporal" in context:
            return f"Considering this timeline: {context['temporal']}. {query}"
            
        return query