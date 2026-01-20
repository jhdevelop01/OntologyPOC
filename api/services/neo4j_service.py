"""Neo4j service layer"""

from api.core.database import neo4j_db


class Neo4jService:
    """Service for Neo4j operations"""

    # Equipment queries
    @staticmethod
    def get_all_equipment():
        """Get all equipment"""
        query = """
        MATCH (e)
        WHERE e.equipmentId IS NOT NULL
        RETURN e.equipmentId[0] AS id,
               e.equipmentName[0] AS name,
               labels(e)[1] AS type,
               e.operatingHours[0] AS operatingHours,
               e.installationDate[0] AS installationDate
        ORDER BY e.equipmentName
        """
        return neo4j_db.query(query)

    @staticmethod
    def get_equipment_by_id(equipment_id: str):
        """Get equipment by ID"""
        query = """
        MATCH (e)
        WHERE e.equipmentId[0] = $id OR e.equipmentId = $id
        RETURN e.equipmentId[0] AS id,
               e.equipmentName[0] AS name,
               labels(e)[1] AS type,
               e.operatingHours[0] AS operatingHours,
               e.installationDate[0] AS installationDate
        """
        return neo4j_db.query_single(query, {"id": equipment_id})

    @staticmethod
    def get_equipment_sensors(equipment_id: str):
        """Get sensors for equipment"""
        query = """
        MATCH (e)-[:hasSensor]->(s:Sensor)
        WHERE e.equipmentId[0] = $id OR e.equipmentId = $id
        RETURN s.sensorId[0] AS id,
               labels(s)[1] AS type,
               s.sensorLocation[0] AS location,
               s.samplingRate[0] AS samplingRate
        """
        return neo4j_db.query(query, {"id": equipment_id})

    # Sensor queries
    @staticmethod
    def get_all_sensors():
        """Get all sensors"""
        query = """
        MATCH (s:Sensor)
        RETURN s.sensorId[0] AS id,
               labels(s)[1] AS type,
               s.sensorLocation[0] AS location,
               s.samplingRate[0] AS samplingRate
        ORDER BY s.sensorId
        """
        return neo4j_db.query(query)

    @staticmethod
    def get_sensor_by_id(sensor_id: str):
        """Get sensor by ID"""
        query = """
        MATCH (s:Sensor)
        WHERE s.sensorId[0] = $id OR s.sensorId = $id
        RETURN s.sensorId[0] AS id,
               labels(s)[1] AS type,
               s.sensorLocation[0] AS location,
               s.samplingRate[0] AS samplingRate
        """
        return neo4j_db.query_single(query, {"id": sensor_id})

    @staticmethod
    def get_sensor_observations(sensor_id: str, limit: int = 100):
        """Get observations for sensor"""
        query = """
        MATCH (o:SensorObservation)-[:madeBySensor]->(s:Sensor)
        WHERE s.sensorId[0] = $id OR s.sensorId = $id
        RETURN s.sensorId[0] AS sensorId,
               o.timestamp[0] AS timestamp,
               o.value[0] AS value,
               o.unit[0] AS unit
        ORDER BY o.timestamp DESC
        LIMIT $limit
        """
        return neo4j_db.query(query, {"id": sensor_id, "limit": limit})

    # Anomaly queries
    @staticmethod
    def get_anomalies(threshold: float = 0.0):
        """Get anomalies above threshold"""
        query = """
        MATCH (a:AnomalyDetection)
        WHERE a.anomalyScore[0] >= $threshold
        OPTIONAL MATCH (a)-[:madeBySensor]->(s:Sensor)
        RETURN a.anomalyScore[0] AS score,
               a.rdfs__label AS label,
               a.rdfs__comment AS description,
               a.timestamp[0] AS timestamp,
               s.sensorId[0] AS sensorId
        ORDER BY a.anomalyScore DESC
        """
        return neo4j_db.query(query, {"threshold": threshold})

    # Prediction queries
    @staticmethod
    def get_failure_predictions():
        """Get failure predictions"""
        query = """
        MATCH (fp:FailurePrediction)
        OPTIONAL MATCH (e)-[:hasPrediction]->(fp)
        WHERE e.equipmentId IS NOT NULL
        RETURN e.equipmentId[0] AS equipmentId,
               e.equipmentName[0] AS equipmentName,
               fp.failureMode[0] AS failureMode,
               fp.predictedFailureDate[0] AS predictedDate,
               fp.confidenceScore[0] AS confidence,
               fp.remainingUsefulLife[0] AS rul,
               fp.rdfs__comment AS comment
        ORDER BY fp.predictedFailureDate
        """
        return neo4j_db.query(query)

    @staticmethod
    def get_energy_prediction(forecast_date: str = None):
        """Get energy prediction"""
        if forecast_date:
            query = """
            MATCH (ep:EnergyPrediction)
            WHERE ep.forecastDate[0] = $date
            OPTIONAL MATCH (ep)-[:hasForecastPoint]->(fp:EnergyForecastPoint)
            RETURN ep.forecastDate[0] AS forecastDate,
                   ep.totalDailyEnergy[0] AS totalEnergy,
                   ep.peakPower[0] AS peakPower,
                   ep.confidenceScore[0] AS confidence,
                   collect({
                     intervalIndex: fp.intervalIndex[0],
                     startTime: fp.intervalStartTime[0],
                     powerKW: fp.powerConsumption[0],
                     confidence: fp.confidenceScore[0]
                   }) AS forecastPoints
            """
            return neo4j_db.query_single(query, {"date": forecast_date})
        else:
            query = """
            MATCH (ep:EnergyPrediction)
            OPTIONAL MATCH (ep)-[:hasForecastPoint]->(fp:EnergyForecastPoint)
            RETURN ep.forecastDate[0] AS forecastDate,
                   ep.totalDailyEnergy[0] AS totalEnergy,
                   ep.peakPower[0] AS peakPower,
                   ep.confidenceScore[0] AS confidence,
                   collect({
                     intervalIndex: fp.intervalIndex[0],
                     startTime: fp.intervalStartTime[0],
                     powerKW: fp.powerConsumption[0],
                     confidence: fp.confidenceScore[0]
                   }) AS forecastPoints
            LIMIT 1
            """
            return neo4j_db.query_single(query)

    # Maintenance queries
    @staticmethod
    def get_maintenance_events(status: str = None):
        """Get maintenance events"""
        if status:
            query = """
            MATCH (e)-[:hasMaintenanceSchedule]->(ms:MaintenanceSchedule)-[:hasMaintenanceEvent]->(me:MaintenanceEvent)
            WHERE e.equipmentId IS NOT NULL AND me.status[0] = $status
            OPTIONAL MATCH (me)-[:hasMaintenanceType]->(mt:MaintenanceType)
            RETURN e.equipmentId[0] AS equipmentId,
                   e.equipmentName[0] AS equipmentName,
                   me.rdfs__label AS eventName,
                   me.scheduledDate[0] AS scheduledDate,
                   me.completedDate[0] AS completedDate,
                   me.priority[0] AS priority,
                   me.estimatedDuration[0] AS duration,
                   me.status[0] AS status,
                   me.maintenanceDescription[0] AS description,
                   mt.rdfs__label AS maintenanceType
            ORDER BY me.scheduledDate
            """
            return neo4j_db.query(query, {"status": status})
        else:
            query = """
            MATCH (e)-[:hasMaintenanceSchedule]->(ms:MaintenanceSchedule)-[:hasMaintenanceEvent]->(me:MaintenanceEvent)
            WHERE e.equipmentId IS NOT NULL
            OPTIONAL MATCH (me)-[:hasMaintenanceType]->(mt:MaintenanceType)
            RETURN e.equipmentId[0] AS equipmentId,
                   e.equipmentName[0] AS equipmentName,
                   me.rdfs__label AS eventName,
                   me.scheduledDate[0] AS scheduledDate,
                   me.completedDate[0] AS completedDate,
                   me.priority[0] AS priority,
                   me.estimatedDuration[0] AS duration,
                   me.status[0] AS status,
                   me.maintenanceDescription[0] AS description,
                   mt.rdfs__label AS maintenanceType
            ORDER BY me.scheduledDate
            """
            return neo4j_db.query(query)

    # Health check
    @staticmethod
    def health_check():
        """Check Neo4j connection"""
        try:
            result = neo4j_db.query("RETURN 1 AS status")
            return {"status": "healthy", "neo4j": "connected"}
        except Exception as e:
            return {"status": "unhealthy", "neo4j": str(e)}
