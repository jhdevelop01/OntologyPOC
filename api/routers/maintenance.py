"""Maintenance API router"""

from fastapi import APIRouter
from typing import List, Optional
from api.models import MaintenanceEvent, APIResponse
from api.services import Neo4jService

router = APIRouter(prefix="/api/maintenance", tags=["Maintenance"])


@router.get("", response_model=APIResponse[List[MaintenanceEvent]])
async def get_maintenance_events(status: Optional[str] = None):
    """Get maintenance events, optionally filtered by status"""
    data = Neo4jService.get_maintenance_events(status)
    return APIResponse(success=True, data=data, count=len(data))
