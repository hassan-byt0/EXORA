// memory/cypher_queries/create_schema.cql
// Create constraints
CREATE CONSTRAINT unique_memory_id IF NOT EXISTS FOR (m:Memory) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT unique_entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;

// Create indexes
CREATE INDEX memory_timestamp IF NOT EXISTS FOR (m:Memory) ON (m.timestamp);
CREATE INDEX memory_type IF NOT EXISTS FOR (m:Memory) ON (m.type);
CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name);

// Create full-text index
CALL db.index.fulltext.createNodeIndex("memory_content", ["Memory"], ["content"]);

// Create vector index (will be managed by Python code)