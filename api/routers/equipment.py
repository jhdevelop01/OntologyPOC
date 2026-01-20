"""Equipment API router"""

from fastapi import APIRouter, HTTPException
from typing import List
from api.models import Equipment, Sensor, APIResponse
from api.services import Neo4jService

router = APIRouter(prefix="/api/equipment", tags=["Equipment"])


@router.get("", response_model=APIResponse[List[Equipment]])
async def get_all_equipment():
    """Get all equipment"""
    data = Neo4jService.get_all_equipment()
    return APIResponse(success=True, data=data, count=len(data))


@router.get("/{equipment_id}", response_model=APIResponse[Equipment])
async def get_equipment(equipment_id: str):
    """Get equipment by ID"""
    data = Neo4jService.get_equipment_by_id(equipment_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Equipment {equipment_id} not found")
    return APIResponse(success=True, data=data)


@router.get("/{equipment_id}/sensors", response_model=APIResponse[List[Sensor]])
async def get_equipment_sensors(equipment_id: str):
    """Get sensors for equipment"""
    data = Neo4jService.get_equipment_sensors(equipment_id)
    return APIResponse(success=True, data=data, count=len(data))
