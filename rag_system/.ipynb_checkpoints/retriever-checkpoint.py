# rag_system/retriever.py
from typing import List, Dict, Any
from langchain_community.vectorstores import Neo4jVector
from langchain_community.graphs import Neo4jGraph
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from common.config import settings
from common.logger import get_logger
from memory.vector_indexing.embeddings import get_embedding_model
from .tools import MemoryRetriever, VisionTool, TemporalTool

logger = get_logger("retriever")

class GraphRetriever(BaseRetriever):
    def __init__(self, context: Dict[str, Any] = None):
        super().__init__()
        self.context = context or {}
        self.graph = Neo4jGraph(
            url=settings.neo4j_uri,
            username=settings.neo4j_user,
            password=settings.neo4j_password
        )
        self.embedding_model = get_embedding_model()
        self.memory_retriever = MemoryRetriever()
        self.vision_tool = VisionTool()
        self.temporal_tool = TemporalTool()
        
    def _get_relevant_documents(
        self, 
        query: str, 
        *,
        run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        # Enhance query with context
        enhanced_query = self._enhance_query(query)
        logger.info(f"Retrieving documents for query: {enhanced_query}")
        
        # Retrieve from vector store
        vector_store = Neo4jVector.from_existing_index(
            embedding=self.embedding_model,
            url=settings.neo4j_uri,
            username=settings.neo4j_user,
            password=settings.neo4j_password,
            index_name="memory_embeddings",
            node_label="Memory",
            text_node_property="content",
            embedding_node_property="embedding"
        )
        
        # Retrieve documents
        docs = vector_store.similarity_search(enhanced_query, k=5)
        
        # Add contextual metadata
        for doc in docs:
            doc.metadata["source"] = "graph_memory"
            doc.metadata["retrieval_strategy"] = "vector_similarity"
        
        return docs
    
    def _enhance_query(self, query: str) -> str:
        """Enhance the query with contextual information"""
        enhanced_query = query
        
        # Add vision context if available
        if "vision_context" in self.context:
            vision_context = self.context["vision_context"]
            enhanced_query = f"{vision_context}. {enhanced_query}"
            logger.debug(f"Added vision context: {vision_context}")
        
        # Add temporal context if available
        if "temporal_context" in self.context:
            temporal_context = self.context["temporal_context"]
            enhanced_query = f"Considering timeline: {temporal_context}. {enhanced_query}"
            logger.debug(f"Added temporal context: {temporal_context}")
        
        # Add user preferences if available
        if "user_preferences" in self.context:
            preferences = self.context["user_preferences"]
            enhanced_query = f"According to user preferences: {preferences}. {enhanced_query}"
            logger.debug(f"Added user preferences: {preferences}")
            
        return enhanced_query
    
    def retrieve_context(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve context from multiple sources"""
        if context:
            self.context = context
            
        # Get relevant documents
        documents = self._get_relevant_documents(query)
        
        # Retrieve additional context using tools
        context_data = []
        
        # Memory context
        memory_context = self.memory_retriever.retrieve(query)
        if memory_context:
            context_data.append({
                "source": "memory_retriever",
                "content": memory_context,
                "confidence": 0.85
            })
        
        # Vision context (if image data exists)
        if "image_data" in self.context:
            vision_context = self.vision_tool.analyze(self.context["image_data"])
            if vision_context:
                context_data.append({
                    "source": "vision_tool",
                    "content": vision_context,
                    "confidence": 0.90
                })
        
        # Temporal context
        temporal_context = self.temporal_tool.get_temporal_context(query)
        if temporal_context:
            context_data.append({
                "source": "temporal_tool",
                "content": temporal_context,
                "confidence": 0.75
            })
        
        # Convert documents to context format
        for doc in documents:
            context_data.append({
                "source": doc.metadata.get("source", "graph_memory"),
                "content": doc.page_content,
                "confidence": doc.metadata.get("similarity_score", 0.8),
                "metadata": {
                    "node_id": doc.metadata.get("id"),
                    "timestamp": doc.metadata.get("timestamp"),
                    "memory_type": doc.metadata.get("type")
                }
            })
        
        # Sort by confidence
        context_data.sort(key=lambda x: x["confidence"], reverse=True)
        
        return context_data