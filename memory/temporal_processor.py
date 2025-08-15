# memory/temporal_processor.py
from datetime import datetime, timedelta
from typing import Dict, List, Any
from neo4j import GraphDatabase
from common.config import settings
from common.logger import get_logger
from .graph_manager import GraphManager

logger = get_logger("temporal_processor")

class TemporalProcessor:
    def __init__(self):
        self.graph_manager = GraphManager()
        self.graph_manager.connect()
    
    def create_temporal_relationship(
        self, 
        from_memory_id: str, 
        to_memory_id: str, 
        relationship_type: str = "BEFORE",
        properties: Optional[Dict] = None
    ) -> bool:
        """Create a temporal relationship between two memories"""
        if not properties:
            properties = {}
            
        # Add temporal metadata
        properties["created_at"] = datetime.utcnow().isoformat()
        properties["relationship_type"] = relationship_type
        
        query = """
        MATCH (from:Memory {id: $from_id})
        MATCH (to:Memory {id: $to_id})
        MERGE (from)-[r:TEMPORAL {
            type: $relationship_type
        }]->(to)
        SET r += $properties
        RETURN r IS NOT NULL AS success
        """
        
        try:
            with self.graph_manager.driver.session() as session:
                result = session.run(query, {
                    "from_id": from_memory_id,
                    "to_id": to_memory_id,
                    "relationship_type": relationship_type,
                    "properties": properties
                })
                return result.single()["success"]
        except Exception as e:
            logger.error(f"Failed to create temporal relationship: {str(e)}")
            return False
    
    def get_timeline(
        self, 
        memory_id: str, 
        depth: int = 3, 
        relationship_types: List[str] = ["BEFORE", "AFTER"]
    ) -> List[Dict[str, Any]]:
        """Get a timeline of related memories"""
        # Convert relationship types to Neo4j pattern
        rel_pattern = "|".join(relationship_types)
        
        query = f"""
        MATCH (start:Memory {{id: $memory_id}})
        CALL apoc.path.expandConfig(start, {{
            relationshipFilter: "TEMPORAL>|<{rel_pattern}",
            minLevel: 1,
            maxLevel: $depth,
            uniqueness: "NODE_GLOBAL"
        }})
        YIELD path
        WITH nodes(path) AS nodes
        UNWIND nodes AS node
        WITH DISTINCT node
        RETURN node
        ORDER BY node.timestamp
        """
        
        try:
            with self.graph_manager.driver.session() as session:
                result = session.run(query, {
                    "memory_id": memory_id,
                    "depth": depth
                })
                return [record["node"] for record in result]
        except Exception as e:
            logger.error(f"Failed to retrieve timeline: {str(e)}")
            return []
    
    def find_related_events(
        self,
        start_time: datetime,
        end_time: datetime,
        event_types: Optional[List[str]] = None,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find events within a time range"""
        query = """
        MATCH (m:Memory)
        WHERE m.timestamp >= datetime($start_time) 
        AND m.timestamp <= datetime($end_time)
        AND ($event_types IS NULL OR m.type IN $event_types)
        AND m.confidence >= $min_confidence
        RETURN m
        ORDER BY m.timestamp
        """
        
        try:
            with self.graph_manager.driver.session() as session:
                result = session.run(query, {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "event_types": event_types or None,
                    "min_confidence": min_confidence
                })
                return [record["m"] for record in result]
        except Exception as e:
            logger.error(f"Failed to find events: {str(e)}")
            return []
    
    def detect_patterns(
        self,
        pattern_type: str = "sequence",
        min_occurrences: int = 3,
        time_window: timedelta = timedelta(days=7)
    ) -> List[Dict[str, Any]]:
        """Detect temporal patterns in memories"""
        # This is a simplified version - real implementation would use APOC or GDS
        query = """
        MATCH (m:Memory)
        WITH m, date.truncate('day', m.timestamp) AS day
        WITH day, COLLECT(m) AS memories
        WHERE SIZE(memories) >= $min_occurrences
        RETURN day, [mem IN memories | mem.id] AS memory_ids
        ORDER BY day
        """
        
        try:
            with self.graph_manager.driver.session() as session:
                result = session.run(query, {
                    "min_occurrences": min_occurrences
                })
                return [{
                    "day": record["day"],
                    "memory_ids": record["memory_ids"]
                } for record in result]
        except Exception as e:
            logger.error(f"Pattern detection failed: {str(e)}")
            return []