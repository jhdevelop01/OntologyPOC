"""Anomalies API router"""

from fastapi import APIRouter
from typing import List
from api.models import Anomaly, APIResponse
from api.services import Neo4jService

router = APIRouter(prefix="/api/anomalies", tags=["Anomalies"])


@router.get("", response_model=APIResponse[List[Anomaly]])
async def get_anomalies(threshold: float = 0.0):
    """Get anomalies above threshold"""
    data = Neo4jService.get_anomalies(threshold)
    return APIResponse(success=True, data=data, count=len(data))
