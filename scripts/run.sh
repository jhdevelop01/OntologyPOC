#!/bin/bash
# =============================================================================
# UPW Ontology - Docker Environment Runner
# =============================================================================

set -e
cd "$(dirname "$0")/.."

NEO4J_USER="neo4j"
NEO4J_PASS="password123"
NEO4J_CONTAINER="neo4j-upw"

case "$1" in
  validate)
    echo "Validating TTL files..."
    ./scripts/validate.sh
    ;;

  start)
    echo "Starting Neo4j..."
    docker compose up -d
    echo "Waiting for Neo4j to be ready..."
    sleep 5
    until docker exec $NEO4J_CONTAINER curl -s http://localhost:7474 > /dev/null 2>&1; do
      echo "  waiting..."
      sleep 5
    done
    echo "Neo4j is ready!"
    echo "  Browser: http://localhost:17474"
    echo "  Bolt:    bolt://localhost:17687"
    echo "  Auth:    $NEO4J_USER / $NEO4J_PASS"
    ;;

  stop)
    echo "Stopping Neo4j..."
    docker compose down
    ;;

  logs)
    docker compose logs -f
    ;;

  import)
    echo "Running ontology import..."
    docker exec -i $NEO4J_CONTAINER cypher-shell \
      -u $NEO4J_USER -p $NEO4J_PASS \
      < neo4j/import-docker.cypher
    echo "Import complete!"
    ;;

  verify)
    echo "Verifying n10s procedures..."
    docker exec $NEO4J_CONTAINER cypher-shell \
      -u $NEO4J_USER -p $NEO4J_PASS \
      "SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'n10s' RETURN name LIMIT 10;"
    ;;

  query)
    echo "Running query file: $2"
    docker exec -i $NEO4J_CONTAINER cypher-shell \
      -u $NEO4J_USER -p $NEO4J_PASS \
      < "$2"
    ;;

  shell)
    echo "Opening cypher-shell..."
    docker exec -it $NEO4J_CONTAINER cypher-shell \
      -u $NEO4J_USER -p $NEO4J_PASS
    ;;

  reset)
    echo "Resetting database..."
    docker exec $NEO4J_CONTAINER cypher-shell \
      -u $NEO4J_USER -p $NEO4J_PASS \
      "MATCH (n) DETACH DELETE n;"
    docker exec $NEO4J_CONTAINER cypher-shell \
      -u $NEO4J_USER -p $NEO4J_PASS \
      "CALL n10s.graphconfig.drop();" 2>/dev/null || true
    docker exec $NEO4J_CONTAINER cypher-shell \
      -u $NEO4J_USER -p $NEO4J_PASS \
      "DROP CONSTRAINT n10s_unique_uri IF EXISTS;"
    echo "Database reset complete!"
    ;;

  clean)
    echo "Removing containers and volumes..."
    docker compose down -v
    ;;

  *)
    echo "Usage: $0 {validate|start|stop|logs|import|verify|query <file>|shell|reset|clean}"
    echo ""
    echo "Commands:"
    echo "  validate - Validate TTL files (uses rapper or rdflib)"
    echo "  start    - Start Neo4j container"
    echo "  stop    - Stop Neo4j container"
    echo "  logs    - Show container logs"
    echo "  import  - Run ontology import script"
    echo "  verify  - Verify n10s procedures are loaded"
    echo "  query   - Run a cypher file (e.g., ./run.sh query queries/examples.cypher)"
    echo "  shell   - Open interactive cypher-shell"
    echo "  reset   - Clear database and n10s config"
    echo "  clean   - Remove containers and volumes"
    exit 1
    ;;
esac
