# memory/vector_indexing/index_manager.py
from neo4j import GraphDatabase
from common.config import settings
from common.logger import get_logger
from .embeddings import EmbeddingModel

logger = get_logger("index_manager")

class IndexManager:
    def __init__(self, driver):
        self.driver = driver
        self.embedding_model = EmbeddingModel()
    
    def create_vector_index(self, index_name: str = "memory_embeddings"):
        """Create vector index if it doesn't exist"""
        # Check if index exists
        index_exists = self._check_index_exists(index_name)
        if index_exists:
            logger.info(f"Vector index '{index_name}' already exists")
            return True
            
        # Create index
        dimension = self.embedding_model.get_dimension()
        query = f"""
        CALL db.index.vector.createNodeIndex(
            $index_name,
            'Memory',
            'embedding',
            $dimension,
            'cosine'
        )
        """
        
        try:
            with self.driver.session() as session:
                session.run(query, {
                    "index_name": index_name,
                    "dimension": dimension
                })
            logger.info(f"Vector index '{index_name}' created (dim={dimension})")
            return True
        except Exception as e:
            logger.error(f"Failed to create vector index: {str(e)}")
            return False
    
    def _check_index_exists(self, index_name: str) -> bool:
        """Check if a vector index exists"""
        query = """
        SHOW INDEXES
        WHERE type = 'VECTOR'
        AND name = $index_name
        RETURN count(*) > 0 AS exists
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, {"index_name": index_name})
                record = result.single()
                return record["exists"] if record else False
        except Exception as e:
            logger.error(f"Index check failed: {str(e)}")
            return False
    
    def update_index_config(self, index_name: str, config: dict):
        """Update vector index configuration"""
        # Neo4j doesn't support direct config updates for vector indexes
        # Instead, we drop and recreate the index
        logger.warning("Recreating vector index with new configuration")
        self.delete_index(index_name)
        return self.create_vector_index(index_name)
    
    def delete_index(self, index_name: str):
        """Delete a vector index"""
        query = f"DROP INDEX $index_name"
        try:
            with self.driver.session() as session:
                session.run(query, {"index_name": index_name})
            logger.info(f"Deleted index: {index_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete index: {str(e)}")
            return False