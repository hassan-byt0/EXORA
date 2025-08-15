import os
from neo4j import GraphDatabase
from common.config import settings
from common.logger import get_logger

logger = get_logger("db_setup")

def main():
    logger.info("Initializing Neo4j database schema")
    
    # Read Cypher scripts
    with open('infrastructure/neo4j/cypher/create_schema.cql', 'r') as f:
        create_schema = f.read()
    
    with open('infrastructure/neo4j/cypher/create_vector_index.cql', 'r') as f:
        create_vector_index = f.read()
    
    # Connect to Neo4j
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password)
    )
    
    # Execute schema creation
    with driver.session() as session:
        try:
            # Create constraints and indexes
            session.run(create_schema)
            
            # Create vector index
            session.run(create_vector_index, {
                "dimension": settings.embedding_dimension
            })
            
            logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Schema initialization failed: {str(e)}")
    
    driver.close()

if __name__ == "__main__":
    main()