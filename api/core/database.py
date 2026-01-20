"""Neo4j database connection"""

from neo4j import GraphDatabase
from .config import settings


class Neo4jDatabase:
    """Neo4j database connection manager"""

    def __init__(self):
        self.driver = None

    def connect(self):
        """Connect to Neo4j"""
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )

    def close(self):
        """Close connection"""
        if self.driver:
            self.driver.close()

    def query(self, cypher: str, parameters: dict = None) -> list:
        """Execute a Cypher query and return results"""
        with self.driver.session() as session:
            result = session.run(cypher, parameters or {})
            return [record.data() for record in result]

    def query_single(self, cypher: str, parameters: dict = None):
        """Execute a query and return single result"""
        results = self.query(cypher, parameters)
        return results[0] if results else None


# Singleton instance
neo4j_db = Neo4jDatabase()
