# memory/graph_manager.py
import logging
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import Neo4jError
from datetime import datetime
from typing import Dict, List, Any, Optional
from common.config import settings
from common.logger import get_logger
from .vector_indexing import EmbeddingModel
from .cypher_queries import CREATE_SCHEMA, STORE_MEMORY, RETRIEVE_CONTEXT

logger = get_logger("graph_manager")

class GraphManager:
    def __init__(self):
        self.driver: Optional[Driver] = None
        self.embedding_model = EmbeddingModel()
        self.connected = False
        self.index_initialized = False
        
    def connect(self):
        """Establish connection to Neo4j"""
        if self.connected:
            return
            
        try:
            self.driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password)
            self.driver.verify_connectivity()
            self.connected = True
            logger.info("Connected to Neo4j database")
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            self.connected = False
            
    def initialize_schema(self):
        """Create database schema and indexes"""
        if not self.connected:
            self.connect()
            
        with self.driver.session() as session:
            try:
                session.run(CREATE_SCHEMA)
                logger.info("Database schema initialized")
            except Neo4jError as e:
                logger.error(f"Schema initialization failed: {str(e)}")
                
        # Initialize vector index
        self.initialize_vector_index()
    
    def initialize_vector_index(self):
        """Create vector index if not exists"""
        if not self.connected:
            self.connect()
            
        if self.index_initialized:
            return
            
        index_manager = IndexManager(self.driver)
        index_manager.create_vector_index()
        self.index_initialized = True
        logger.info("Vector index initialized")
    
    def store_memory(
        self, 
        content: str, 
        memory_type: str = "generic",
        source: str = "user_input",
        entities: Optional[List[str]] = None,
        relationships: Optional[List[Dict]] = None
    ) -> str:
        """Store a memory in the graph database"""
        if not self.connected:
            self.connect()
            if not self.connected:
                return ""
                
        # Generate embedding
        embedding = self.embedding_model.get_embedding(content).tolist()
        
        # Prepare parameters
        params = {
            "content": content,
            "type": memory_type,
            "source": source,
            "embedding": embedding,
            "entities": entities or [],
            "relationships": relationships or [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with self.driver.session() as session:
            try:
                result = session.run(STORE_MEMORY, params)
                memory_id = result.single()["memory_id"]
                logger.info(f"Stored memory {memory_id} ({memory_type})")
                return memory_id
            except Neo4jError as e:
                logger.error(f"Memory storage failed: {str(e)}")
                return ""
    
    def retrieve_context(
        self, 
        query: str, 
        top_k: int = 5,
        max_relationships: int = 3,
        time_window: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context based on query"""
        if not self.connected:
            self.connect()
            if not self.connected:
                return []
                
        # Get query embedding
        query_embedding = self.embedding_model.get_embedding(query).tolist()
        
        # Prepare parameters
        params = {
            "query_embedding": query_embedding,
            "top_k": top_k,
            "max_rels": max_relationships
        }
        
        # Add time window if specified
        if time_window:
            params["time_window"] = f"P{time_window}D"
        
        with self.driver.session() as session:
            try:
                result = session.run(RETRIEVE_CONTEXT, params)
                return [record.data() for record in result]
            except Neo4jError as e:
                logger.error(f"Context retrieval failed: {str(e)}")
                return []
    
    def find_temporal_relationships(
        self, 
        memory_id: str, 
        relationship_type: str = "TEMPORAL",
        depth: int = 2
    ) -> List[Dict[str, Any]]:
        """Find temporal relationships around a memory node"""
        if not self.connected:
            self.connect()
            if not self.connected:
                return []
                
        query = """
        MATCH (start:Memory {id: $memory_id})
        CALL apoc.path.expandConfig(start, {
            relationshipFilter: $relationship_type,
            minLevel: 1,
            maxLevel: $depth
        })
        YIELD path
        RETURN nodes(path) AS nodes, relationships(path) AS relationships
        """
        
        with self.driver.session() as session:
            try:
                result = session.run(query, {
                    "memory_id": memory_id,
                    "relationship_type": relationship_type,
                    "depth": depth
                })
                return [record.data() for record in result]
            except Neo4jError as e:
                logger.error(f"Temporal query failed: {str(e)}")
                return []
    
    def close(self):
        """Close the database connection"""
        if self.driver:
            self.driver.close()
            self.connected = False
            logger.info("Neo4j connection closed")