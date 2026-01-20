"""Predictions API router"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from api.models import FailurePrediction, EnergyPrediction, APIResponse
from api.services import Neo4jService

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.get("/failure", response_model=APIResponse[List[FailurePrediction]])
async def get_failure_predictions():
    """Get failure predictions"""
    data = Neo4jService.get_failure_predictions()
    return APIResponse(success=True, data=data, count=len(data))


@router.get("/energy", response_model=APIResponse[EnergyPrediction])
async def get_energy_prediction(date: Optional[str] = None):
    """Get energy prediction for date"""
    data = Neo4jService.get_energy_prediction(date)
    if not data:
        raise HTTPException(status_code=404, detail="Energy prediction not found")
    return APIResponse(success=True, data=data)
