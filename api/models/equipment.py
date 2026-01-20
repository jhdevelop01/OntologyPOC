"""Equipment models"""

from pydantic import BaseModel
from typing import Optional, List


class Equipment(BaseModel):
    """Equipment model"""
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    operatingHours: Optional[float] = None
    installationDate: Optional[str] = None


class SensorInfo(BaseModel):
    """Sensor info for equipment"""
    id: Optional[str] = None
    type: Optional[str] = None


class EquipmentWithSensors(BaseModel):
    """Equipment with sensors"""
    equipmentId: Optional[str] = None
    equipmentName: Optional[str] = None
    sensors: List[SensorInfo] = []
