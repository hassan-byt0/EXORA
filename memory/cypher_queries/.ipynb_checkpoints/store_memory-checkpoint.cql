// memory/cypher_queries/store_memory.cql
// Store memory node
CREATE (m:Memory {
  id: apoc.create.uuid(),
  content: $content,
  type: $type,
  source: $source,
  embedding: $embedding,
  timestamp: datetime($timestamp)
})

// Create entities
WITH m
UNWIND $entities AS entity_name
MERGE (e:Entity {id: apoc.create.uuid(), name: entity_name})
MERGE (m)-[:MENTIONS]->(e)

// Create relationships
WITH m
UNWIND $relationships AS rel
MATCH (from:Memory {id: rel.from}) 
MATCH (to:Memory {id: rel.to})
CALL apoc.create.relationship(from, rel.type, rel.properties, to) YIELD rel AS createdRel
RETURN m.id AS memory_id