"""UPW Process API - Main Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.core.config import settings
from api.core.database import neo4j_db
from api.routers import (
    equipment_router,
    sensors_router,
    anomalies_router,
    predictions_router,
    maintenance_router
)
from api.services import Neo4jService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    neo4j_db.connect()
    print("Connected to Neo4j")
    yield
    # Shutdown
    neo4j_db.close()
    print("Disconnected from Neo4j")


# Create app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="UPW Process Ontology REST API",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(equipment_router)
app.include_router(sensors_router)
app.include_router(anomalies_router)
app.include_router(predictions_router)
app.include_router(maintenance_router)


@app.get("/", tags=["Root"])
async def root():
    """API root"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "equipment": "/api/equipment",
            "sensors": "/api/sensors",
            "anomalies": "/api/anomalies",
            "predictions": "/api/predictions",
            "maintenance": "/api/maintenance"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return Neo4jService.health_check()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
