// =============================================================================
// UPW Process Ontology - Neo4j n10s Import Script
// =============================================================================
// Prerequisites:
//   1. Neo4j 4.x or 5.x with n10s plugin installed
//   2. TTL files accessible via file:// or http:// URL
// =============================================================================

// -----------------------------------------------------------------------------
// STEP 1: Initialize n10s and create constraint
// -----------------------------------------------------------------------------

// Create unique constraint for Resource nodes (required by n10s)
CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource) REQUIRE r.uri IS UNIQUE;

// Initialize n10s graph configuration
// handleVocabUris: "MAP" - maps common vocab URIs to simpler labels
// handleMultival: "ARRAY" - stores multiple values as arrays
// handleRDFTypes: "LABELS" - converts rdf:type to Neo4j labels
CALL n10s.graphconfig.init({
  handleVocabUris: "MAP",
  handleMultival: "ARRAY",
  handleRDFTypes: "LABELS_AND_NODES",
  keepLangTag: false,
  keepCustomDataTypes: false
});

// -----------------------------------------------------------------------------
// STEP 2: Add namespace prefixes for cleaner URIs
// -----------------------------------------------------------------------------

// Add prefix mappings for better readability
CALL n10s.nsprefixes.add("upw", "http://example.org/upw#");
CALL n10s.nsprefixes.add("upw-data", "http://example.org/upw/data#");
CALL n10s.nsprefixes.add("sosa", "http://www.w3.org/ns/sosa/");
CALL n10s.nsprefixes.add("ssn", "http://www.w3.org/ns/ssn/");
CALL n10s.nsprefixes.add("time", "http://www.w3.org/2006/time#");
CALL n10s.nsprefixes.add("qudt", "http://qudt.org/schema/qudt/");

// -----------------------------------------------------------------------------
// STEP 3: Import ontology schema (TBox)
// -----------------------------------------------------------------------------

// Option A: Import from local file
// Replace the path with your actual file location
// CALL n10s.onto.import.fetch("file:///path/to/ontology/upw.owl.ttl", "Turtle");

// Option B: Import from HTTP URL (if served by web server)
// CALL n10s.onto.import.fetch("http://localhost:8000/ontology/upw.owl.ttl", "Turtle");

// For local development, use inline fetch with file protocol:
CALL n10s.onto.import.fetch(
  "file:///Users/mckim64/Projects/OntologyPOC/ontology/upw.owl.ttl",
  "Turtle"
);

// -----------------------------------------------------------------------------
// STEP 4: Import instance data (ABox)
// -----------------------------------------------------------------------------

// Option A: Import from local file
// CALL n10s.rdf.import.fetch("file:///path/to/ontology/sample_data.ttl", "Turtle");

// Option B: Import from HTTP URL
// CALL n10s.rdf.import.fetch("http://localhost:8000/ontology/sample_data.ttl", "Turtle");

// For local development:
CALL n10s.rdf.import.fetch(
  "file:///Users/mckim64/Projects/OntologyPOC/ontology/sample_data.ttl",
  "Turtle"
);

// -----------------------------------------------------------------------------
// STEP 5: Verify import success
// -----------------------------------------------------------------------------

// Check node counts by label
CALL db.labels() YIELD label
CALL apoc.cypher.run('MATCH (n:`' + label + '`) RETURN count(n) as count', {})
YIELD value
RETURN label, value.count AS count
ORDER BY count DESC;

// Check relationship counts
CALL db.relationshipTypes() YIELD relationshipType
CALL apoc.cypher.run('MATCH ()-[r:`' + relationshipType + '`]->() RETURN count(r) as count', {})
YIELD value
RETURN relationshipType, value.count AS count
ORDER BY count DESC;

// -----------------------------------------------------------------------------
// ALTERNATIVE: Simplified verification without APOC
// -----------------------------------------------------------------------------

// Count all nodes
// MATCH (n) RETURN count(n) AS totalNodes;

// Count nodes by type
// MATCH (n)
// UNWIND labels(n) AS label
// RETURN label, count(*) AS count
// ORDER BY count DESC;

// Count relationships by type
// MATCH ()-[r]->()
// RETURN type(r) AS relationshipType, count(*) AS count
// ORDER BY count DESC;

// =============================================================================
// CLEANUP COMMANDS (use if you need to reimport)
// =============================================================================

// Delete all data and reset n10s config:
// MATCH (n) DETACH DELETE n;
// CALL n10s.graphconfig.drop();
// DROP CONSTRAINT n10s_unique_uri IF EXISTS;
