"""Prediction models"""

from pydantic import BaseModel
from typing import Optional, List


class FailurePrediction(BaseModel):
    """Failure prediction model"""
    equipmentId: Optional[str] = None
    equipmentName: Optional[str] = None
    failureMode: Optional[str] = None
    predictedDate: Optional[str] = None
    confidence: Optional[float] = None
    rul: Optional[float] = None
    comment: Optional[str] = None


class EnergyForecastPoint(BaseModel):
    """Energy forecast point model"""
    intervalIndex: Optional[int] = None
    startTime: Optional[str] = None
    powerKW: Optional[float] = None
    confidence: Optional[float] = None


class EnergyPrediction(BaseModel):
    """Energy prediction model"""
    forecastDate: Optional[str] = None
    totalEnergy: Optional[float] = None
    peakPower: Optional[float] = None
    confidence: Optional[float] = None
    forecastPoints: List[EnergyForecastPoint] = []
