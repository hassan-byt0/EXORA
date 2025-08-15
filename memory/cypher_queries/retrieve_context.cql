// memory/cypher_queries/retrieve_context.cql
// Retrieve using vector similarity
CALL db.index.vector.queryNodes('memory_embeddings', $top_k, $query_embedding)
YIELD node, score

// Optionally filter by time window
WHERE $time_window IS NULL OR 
      datetime().epochMillis - node.timestamp.epochMillis < duration($time_window).milliseconds

// Retrieve related entities and memories
WITH node, score
OPTIONAL MATCH (node)-[:MENTIONS]->(e:Entity)
WITH node, score, COLLECT(DISTINCT e.name) AS entities

// Retrieve related memories
OPTIONAL MATCH (node)-[r]->(related:Memory)
WHERE SIZE(r) > 0
WITH node, score, entities, 
     COLLECT(DISTINCT {id: related.id, content: related.content, type: TYPE(r)})[0..$max_rels] AS related_memories

// Format response
RETURN {
  id: node.id,
  content: node.content,
  type: node.type,
  source: node.source,
  timestamp: node.timestamp,
  entities: entities,
  related_memories: related_memories,
  similarity_score: score
} AS context
ORDER BY score DESC