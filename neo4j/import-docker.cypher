// =============================================================================
// UPW Process Ontology - Docker Import Script
// =============================================================================
// Usage: cypher-shell -u neo4j -p password123 -f /path/to/import-docker.cypher
// =============================================================================

// Step 1: Create constraint
CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource) REQUIRE r.uri IS UNIQUE;

// Step 2: Initialize n10s graph configuration
CALL n10s.graphconfig.init({
  handleVocabUris: "MAP",
  handleMultival: "ARRAY",
  handleRDFTypes: "LABELS_AND_NODES",
  keepLangTag: false,
  keepCustomDataTypes: false
});

// Step 3: Add namespace prefixes
CALL n10s.nsprefixes.add("upw", "http://example.org/upw#");
CALL n10s.nsprefixes.add("upw-data", "http://example.org/upw/data#");
CALL n10s.nsprefixes.add("sosa", "http://www.w3.org/ns/sosa/");
CALL n10s.nsprefixes.add("ssn", "http://www.w3.org/ns/ssn/");

// Step 4: Import ontology schema (TBox) - Docker path
CALL n10s.onto.import.fetch("file:///import/upw.owl.ttl", "Turtle");

// Step 5: Import instance data (ABox) - Docker path
CALL n10s.rdf.import.fetch("file:///import/sample_data.ttl", "Turtle");

// Step 6: Verification - Count nodes by label
MATCH (n)
UNWIND labels(n) AS label
RETURN label, count(*) AS count
ORDER BY count DESC
LIMIT 20;
