"""Sensors API router"""

from fastapi import APIRouter, HTTPException
from typing import List
from api.models import Sensor, SensorObservation, APIResponse
from api.services import Neo4jService

router = APIRouter(prefix="/api/sensors", tags=["Sensors"])


@router.get("", response_model=APIResponse[List[Sensor]])
async def get_all_sensors():
    """Get all sensors"""
    data = Neo4jService.get_all_sensors()
    return APIResponse(success=True, data=data, count=len(data))


@router.get("/{sensor_id}", response_model=APIResponse[Sensor])
async def get_sensor(sensor_id: str):
    """Get sensor by ID"""
    data = Neo4jService.get_sensor_by_id(sensor_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Sensor {sensor_id} not found")
    return APIResponse(success=True, data=data)


@router.get("/{sensor_id}/observations", response_model=APIResponse[List[SensorObservation]])
async def get_sensor_observations(sensor_id: str, limit: int = 100):
    """Get observations for sensor"""
    data = Neo4jService.get_sensor_observations(sensor_id, limit)
    return APIResponse(success=True, data=data, count=len(data))
