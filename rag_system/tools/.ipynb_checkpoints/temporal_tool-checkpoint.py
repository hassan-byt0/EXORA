# rag_system/tools/temporal_tool.py
from typing import Dict, List
from langchain_community.graphs import Neo4jGraph
from common.config import settings
from common.logger import get_logger
from datetime import datetime, timedelta

logger = get_logger("temporal_tool")

class TemporalTool:
    def __init__(self):
        self.graph = Neo4jGraph(
            url=settings.neo4j_uri,
            username=settings.neo4j_user,
            password=settings.neo4j_password
        )
    
    def get_temporal_context(self, query: str) -> str:
        """Extract temporal context from query and retrieve related events"""
        time_refs = self._extract_time_references(query)
        
        if not time_refs:
            return ""
            
        # Query for related events
        cypher_query = """
        MATCH (m:Memory)
        WHERE ANY(ref in $time_refs WHERE m.content CONTAINS ref)
        OR m.timestamp >= datetime($start_date) AND m.timestamp <= datetime($end_date)
        RETURN m.content AS content, m.timestamp AS timestamp
        ORDER BY timestamp DESC
        LIMIT 5
        """
        
        try:
            # Calculate date range
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
            
            results = self.graph.query(
                cypher_query,
                params={
                    "time_refs": time_refs,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )
            
            if not results:
                return ""
                
            # Format results
            timeline = "Recent related events:\n"
            for i, result in enumerate(results):
                timestamp = result["timestamp"].strftime("%Y-%m-%d %H:%M")
                timeline += f"{i+1}. [{timestamp}] {result['content']}\n"
                
            return timeline
            
        except Exception as e:
            logger.error(f"Temporal context retrieval failed: {str(e)}")
            return ""
    
    def _extract_time_references(self, query: str) -> List[str]:
        """Extract time references from query"""
        time_keywords = [
            "today", "yesterday", "tomorrow", "now", "recent", "last week",
            "next week", "month", "year", "ago", "before", "after"
        ]
        
        # Simple extraction - in production use NLP library
        refs = []
        for keyword in time_keywords:
            if keyword in query.lower():
                refs.append(keyword)
                
        # Add date references
        if "monday" in query.lower(): refs.append("monday")
        if "tuesday" in query.lower(): refs.append("tuesday")
        # ... add other days
        
        return refs