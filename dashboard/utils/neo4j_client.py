"""Neo4j connection utility for UPW Dashboard"""

from neo4j import GraphDatabase
from contextlib import contextmanager
import os

# Default connection settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:17687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")


class Neo4jClient:
    """Neo4j database client"""

    def __init__(self, uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, cypher, parameters=None):
        """Execute a Cypher query and return results as list of dicts"""
        with self.driver.session() as session:
            result = session.run(cypher, parameters or {})
            return [record.data() for record in result]

    def query_single(self, cypher, parameters=None):
        """Execute a query and return single result"""
        results = self.query(cypher, parameters)
        return results[0] if results else None


@contextmanager
def get_client():
    """Context manager for Neo4j client"""
    client = Neo4jClient()
    try:
        yield client
    finally:
        client.close()


# Singleton client for Streamlit caching
_client = None

def get_cached_client():
    """Get or create a cached Neo4j client"""
    global _client
    if _client is None:
        _client = Neo4jClient()
    return _client
