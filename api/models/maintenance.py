"""Maintenance models"""

from pydantic import BaseModel
from typing import Optional


class MaintenanceEvent(BaseModel):
    """Maintenance event model"""
    equipmentId: Optional[str] = None
    equipmentName: Optional[str] = None
    eventName: Optional[str] = None
    scheduledDate: Optional[str] = None
    completedDate: Optional[str] = None
    priority: Optional[int] = None
    duration: Optional[float] = None
    status: Optional[str] = None
    description: Optional[str] = None
    maintenanceType: Optional[str] = None
