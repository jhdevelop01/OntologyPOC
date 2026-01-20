from .equipment import router as equipment_router
from .sensors import router as sensors_router
from .anomalies import router as anomalies_router
from .predictions import router as predictions_router
from .maintenance import router as maintenance_router

__all__ = [
    'equipment_router',
    'sensors_router',
    'anomalies_router',
    'predictions_router',
    'maintenance_router'
]
