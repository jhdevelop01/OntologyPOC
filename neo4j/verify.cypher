// =============================================================================
// Verification Queries - Run after import to confirm setup
// =============================================================================

// 1. Check n10s procedures are available
SHOW PROCEDURES YIELD name, description
WHERE name STARTS WITH 'n10s'
RETURN name, description
LIMIT 15;

// 2. Check apoc procedures (optional)
// SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'apoc' RETURN name LIMIT 5;

// 3. Check n10s graph config
CALL n10s.graphconfig.show();

// 4. Check namespace prefixes
CALL n10s.nsprefixes.list();

// 5. Count nodes by label
MATCH (n)
UNWIND labels(n) AS label
RETURN label, count(*) AS count
ORDER BY count DESC;

// 6. Count relationships by type
MATCH ()-[r]->()
RETURN type(r) AS relationship, count(*) AS count
ORDER BY count DESC;

// 7. Sample equipment data
MATCH (e:Equipment)
RETURN e.equipmentId AS id, e.equipmentName AS name, labels(e) AS types
LIMIT 10;

// 8. Sample sensor data
MATCH (s:Sensor)
RETURN s.sensorId AS id, labels(s) AS types
LIMIT 10;
