"""Sensor models"""

from pydantic import BaseModel
from typing import Optional


class Sensor(BaseModel):
    """Sensor model"""
    id: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    samplingRate: Optional[float] = None


class SensorObservation(BaseModel):
    """Sensor observation model"""
    sensorId: Optional[str] = None
    timestamp: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
