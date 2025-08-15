# rag_system/tools/memory_retriever.py
from typing import Dict, List
from langchain_community.graphs import Neo4jGraph
from common.config import settings
from common.logger import get_logger

logger = get_logger("memory_retriever")

class MemoryRetriever:
    def __init__(self):
        self.graph = Neo4jGraph(
            url=settings.neo4j_uri,
            username=settings.neo4j_user,
            password=settings.neo4j_password
        )
    
    def retrieve(self, query: str, top_k: int = 3) -> str:
        """Retrieve relevant memories using Cypher query"""
        logger.info(f"Retrieving memories for: {query}")
        
        # Cypher query to find related memories
        cypher_query = """
        MATCH (m:Memory)
        WHERE m.content CONTAINS $query
        OPTIONAL MATCH (m)-[:RELATED_TO]->(related:Memory)
        RETURN m.content AS main_content,
               COLLECT(related.content) AS related_contents
        ORDER BY m.timestamp DESC
        LIMIT $top_k
        """
        
        try:
            results = self.graph.query(
                cypher_query, 
                params={"query": query, "top_k": top_k}
            )
            
            if not results:
                return ""
                
            # Format results
            memory_context = ""
            for i, result in enumerate(results):
                memory_context += f"Memory {i+1}:\n{result['main_content']}\n"
                if result["related_contents"]:
                    memory_context += "Related memories:\n"
                    for j, content in enumerate(result["related_contents"]):
                        memory_context += f"  - {content}\n"
                memory_context += "\n"
                
            return memory_context.strip()
            
        except Exception as e:
            logger.error(f"Memory retrieval failed: {str(e)}")
            return ""