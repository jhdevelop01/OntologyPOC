"""Application configuration"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API
    app_name: str = "UPW Process API"
    app_version: str = "1.0.0"
    debug: bool = True

    # Neo4j
    neo4j_uri: str = "bolt://localhost:17687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password123"

    class Config:
        env_file = ".env"


settings = Settings()
