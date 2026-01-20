"""Anomaly models"""

from pydantic import BaseModel
from typing import Optional


class Anomaly(BaseModel):
    """Anomaly detection model"""
    score: Optional[float] = None
    label: Optional[str] = None
    description: Optional[str] = None
    timestamp: Optional[str] = None
    sensorId: Optional[str] = None
