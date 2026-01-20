# CLAUDE.md - UPW Ontology Project Guide

## Quick Start

```bash
# 1. Validate TTL files
./scripts/validate.sh

# 2. Start Neo4j
docker compose up -d

# 3. Wait for ready (check logs)
docker compose logs -f
# Wait for "Started." message, then Ctrl+C

# 4. Import ontology + data
docker exec -i neo4j-upw cypher-shell -u neo4j -p password123 < neo4j/import-docker.cypher

# 5. Run example queries
docker exec -i neo4j-upw cypher-shell -u neo4j -p password123 < queries/examples.cypher
```

### One-liner (all steps)
```bash
./scripts/run.sh validate && ./scripts/run.sh start && sleep 45 && ./scripts/run.sh import
```

---

## Docker Compose Commands

| Command | Description |
|---------|-------------|
| `docker compose up -d` | Start Neo4j container |
| `docker compose down` | Stop container |
| `docker compose down -v` | Stop and remove volumes (full reset) |
| `docker compose logs -f` | Follow logs |
| `docker compose ps` | Check status |

### Helper Script
```bash
./scripts/run.sh validate  # Validate TTL files
./scripts/run.sh start     # Start Neo4j + wait for ready
./scripts/run.sh stop      # Stop Neo4j
./scripts/run.sh import    # Run ontology import
./scripts/run.sh verify    # Check n10s procedures
./scripts/run.sh shell     # Open cypher-shell
./scripts/run.sh reset     # Clear database
./scripts/run.sh clean     # Remove containers + volumes
```

---

## Connection Info

| Property | Value |
|----------|-------|
| Browser URL | http://localhost:17474 |
| Bolt URL | bolt://localhost:17687 |
| Username | `neo4j` |
| Password | `password123` |

```bash
# Open browser
open http://localhost:17474

# Connect via cypher-shell
docker exec -it neo4j-upw cypher-shell -u neo4j -p password123
```

---

## Neo4j Plugin & Security Settings

### Plugins (docker-compose.yml)
```yaml
NEO4J_PLUGINS: '["n10s","apoc"]'
```

- **n10s (neosemantics)**: RDF/OWL import, SPARQL support
- **apoc**: Advanced procedures (optional, for complex queries)

### Security Settings
```yaml
# Allow n10s/apoc procedures to run
NEO4J_dbms_security_procedures_unrestricted: "n10s.*,apoc.*"
NEO4J_dbms_security_procedures_allowlist: "n10s.*,apoc.*,gds.*"

# Allow file:// URLs for import
NEO4J_dbms_security_allow__csv__import__from__file__urls: "true"
```

### Verify Procedures
```cypher
-- Check n10s is loaded
SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'n10s' RETURN count(*);
-- Expected: 55+

-- Check apoc is loaded
SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'apoc' RETURN count(*);
```

---

## Volume Mounts

```yaml
volumes:
  - ./ontology:/import    # TTL files accessible as /import/*
  - neo4j_data:/data      # Persistent database
  - neo4j_logs:/logs      # Log files
```

**Import paths in Cypher:**
```cypher
-- Docker path (use this)
CALL n10s.onto.import.fetch("file:///import/upw.owl.ttl", "Turtle");

-- NOT local path (won't work in container)
-- CALL n10s.onto.import.fetch("file:///Users/.../ontology/upw.owl.ttl", "Turtle");
```

---

## Common Errors & Solutions

### 1. Port already in use
```
Error: Bind for 0.0.0.0:7474 failed: port is already allocated
```
**Solution:** Stop other Neo4j instances or change ports in docker-compose.yml
```bash
# Find what's using the port
lsof -i :7474

# Current config uses 17474/17687 to avoid conflicts
```

### 2. n10s procedures not found
```
Unknown function 'n10s.graphconfig.init'
```
**Solution:** Check plugin installation
```bash
docker compose logs | grep -i n10s
# Should see: "Installing Plugin 'n10s'"
```
If missing, ensure `NEO4J_PLUGINS` is set correctly.

### 3. File import permission denied
```
Couldn't load data from file:///import/upw.owl.ttl
```
**Solutions:**
1. Check volume mount: `docker exec neo4j-upw ls -la /import/`
2. Verify setting: `NEO4J_dbms_security_allow__csv__import__from__file__urls: "true"`
3. Use HTTP instead:
   ```bash
   # Serve files locally
   python3 -m http.server 8000 --directory ontology
   # Then import via HTTP
   CALL n10s.rdf.import.fetch("http://host.docker.internal:8000/sample_data.ttl", "Turtle");
   ```

### 4. Graph config already exists
```
Failed to invoke procedure: GraphConfig already exists
```
**Solution:** Drop existing config first
```cypher
CALL n10s.graphconfig.drop();
DROP CONSTRAINT n10s_unique_uri IF EXISTS;
-- Then re-run import
```

### 5. Empty Equipment query results
```cypher
MATCH (e:Equipment) RETURN e;  -- Returns 0 rows
```
**Explanation:** n10s maps RDF types to specific labels (Pump, Filter, etc.), not parent class.
**Solution:** Query by specific class or property
```cypher
-- By specific class
MATCH (e:Pump) RETURN e;

-- By property
MATCH (e) WHERE e.equipmentId IS NOT NULL RETURN e;

-- All equipment types
MATCH (e) WHERE e:Pump OR e:Filter OR e:ROSystem RETURN e;
```

### 6. Turtle syntax error
```
RDFParseException: Expected '.', found ...
```
**Solution:** Validate before import
```bash
./scripts/validate.sh
# or
rapper -i turtle -c ontology/upw.owl.ttl
```

### 7. Constraint already exists
```
Constraint already exists: Constraint(...)
```
**Solution:** Use IF NOT EXISTS or drop first
```cypher
CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource) REQUIRE r.uri IS UNIQUE;
```

---

## Useful Cypher Queries

### Check import status
```cypher
-- Total counts
MATCH (n) RETURN count(n) AS nodes;
MATCH ()-[r]->() RETURN count(r) AS relationships;

-- Labels distribution
MATCH (n) UNWIND labels(n) AS l RETURN l, count(*) ORDER BY count(*) DESC LIMIT 10;

-- n10s config
CALL n10s.graphconfig.show();
CALL n10s.nsprefixes.list();
```

### Reset database
```cypher
MATCH (n) DETACH DELETE n;
CALL n10s.graphconfig.drop();
DROP CONSTRAINT n10s_unique_uri IF EXISTS;
```

---

## File Structure

```
OntologyPOC/
├── docker-compose.yml       # Neo4j container config
├── CLAUDE.md               # This file
├── README.md               # Project overview
├── ontology/
│   ├── upw.owl.ttl         # OWL ontology (TBox)
│   └── sample_data.ttl     # Instance data (ABox)
├── neo4j/
│   ├── import-docker.cypher # Docker-path import script
│   ├── import.cypher       # Local-path import script
│   └── verify.cypher       # Verification queries
├── queries/
│   └── examples.cypher     # Example queries
└── scripts/
    ├── run.sh              # Helper script
    └── validate.sh         # TTL validator
```
