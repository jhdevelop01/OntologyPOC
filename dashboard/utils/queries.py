"""Cypher queries for UPW Dashboard"""

# Equipment queries
GET_ALL_EQUIPMENT = """
MATCH (e)
WHERE e.equipmentId IS NOT NULL
RETURN e.equipmentId[0] AS id,
       e.equipmentName[0] AS name,
       [l IN labels(e) WHERE l <> 'Resource'][0] AS type,
       e.operatingHours[0] AS operatingHours,
       toString(e.installationDate[0]) AS installationDate
ORDER BY e.equipmentName[0]
"""

GET_EQUIPMENT_WITH_SENSORS = """
MATCH (e)-[:hasSensor]->(s)
WHERE e.equipmentId IS NOT NULL AND s.sensorId IS NOT NULL
WITH e, collect({
    id: s.sensorId[0],
    type: [l IN labels(s) WHERE l <> 'Resource'][0],
    location: s.sensorLocation[0]
}) AS sensors
RETURN e.equipmentId[0] AS equipmentId,
       e.equipmentName[0] AS equipmentName,
       sensors
ORDER BY e.equipmentName[0]
"""

GET_EQUIPMENT_STATS = """
MATCH (e)
WHERE e.equipmentId IS NOT NULL
WITH [l IN labels(e) WHERE l <> 'Resource'][0] AS type
RETURN type, count(*) AS count
ORDER BY count DESC
"""

# Anomaly Detection queries
GET_ANOMALIES = """
MATCH (a:AnomalyDetection)
OPTIONAL MATCH (a)-[:madeBySensor]->(s)
WHERE s.sensorId IS NOT NULL OR s IS NULL
RETURN a.anomalyScore[0] AS score,
       a.label[0] AS label,
       a.comment[0] AS description,
       toString(a.timestamp[0]) AS timestamp,
       s.sensorId[0] AS sensorId
ORDER BY a.anomalyScore[0] DESC
"""

GET_ANOMALY_COUNT_BY_THRESHOLD = """
MATCH (a:AnomalyDetection)
WITH a.anomalyScore[0] AS score
RETURN
  CASE
    WHEN score >= 0.7 THEN 'Critical (≥0.7)'
    WHEN score >= 0.5 THEN 'Warning (0.5-0.7)'
    ELSE 'Normal (<0.5)'
  END AS level,
  count(*) AS count
ORDER BY
  CASE level
    WHEN 'Critical (≥0.7)' THEN 1
    WHEN 'Warning (0.5-0.7)' THEN 2
    ELSE 3
  END
"""

# Failure Prediction queries
GET_FAILURE_PREDICTIONS = """
MATCH (fp:FailurePrediction)
OPTIONAL MATCH (e)-[:hasPrediction]->(fp)
WHERE e.equipmentId IS NOT NULL OR e IS NULL
RETURN e.equipmentId[0] AS equipmentId,
       e.equipmentName[0] AS equipmentName,
       fp.failureMode[0] AS failureMode,
       toString(fp.predictedFailureDate[0]) AS predictedDate,
       fp.confidenceScore[0] AS confidence,
       fp.remainingUsefulLife[0] AS rul,
       fp.comment[0] AS comment
ORDER BY fp.predictedFailureDate[0]
"""

# Energy Prediction queries
GET_ENERGY_FORECAST = """
MATCH (ep:EnergyPrediction)-[:hasForecastPoint]->(fp:EnergyForecastPoint)
RETURN toString(ep.forecastDate[0]) AS forecastDate,
       ep.totalDailyEnergy[0] AS totalEnergy,
       ep.peakPower[0] AS peakPower,
       fp.intervalIndex[0] AS intervalIndex,
       toString(fp.intervalStartTime[0]) AS startTime,
       fp.powerConsumption[0] AS powerKW,
       fp.confidenceScore[0] AS confidence
ORDER BY fp.intervalIndex[0]
"""

GET_ENERGY_SUMMARY = """
MATCH (ep:EnergyPrediction)
RETURN toString(ep.forecastDate[0]) AS forecastDate,
       ep.totalDailyEnergy[0] AS totalEnergy,
       ep.peakPower[0] AS peakPower,
       ep.confidenceScore[0] AS confidence
LIMIT 1
"""

# Maintenance queries
GET_MAINTENANCE_EVENTS = """
MATCH (me:MaintenanceEvent)
OPTIONAL MATCH (e)-[:hasMaintenanceSchedule]->(:MaintenanceSchedule)-[:hasMaintenanceEvent]->(me)
WHERE e.equipmentId IS NOT NULL OR e IS NULL
OPTIONAL MATCH (me)-[:hasMaintenanceType]->(mt)
RETURN e.equipmentId[0] AS equipmentId,
       e.equipmentName[0] AS equipmentName,
       me.label[0] AS eventName,
       toString(me.scheduledDate[0]) AS scheduledDate,
       toString(me.completedDate[0]) AS completedDate,
       me.priority[0] AS priority,
       me.estimatedDuration[0] AS duration,
       me.status[0] AS status,
       me.maintenanceDescription[0] AS description,
       mt.label[0] AS maintenanceType
ORDER BY me.scheduledDate[0]
"""

GET_MAINTENANCE_BY_TYPE = """
MATCH (me:MaintenanceEvent)-[:hasMaintenanceType]->(mt)
RETURN mt.label[0] AS type, count(me) AS count
"""

# Dashboard summary
GET_DASHBOARD_SUMMARY = """
MATCH (e) WHERE e.equipmentId IS NOT NULL
WITH count(e) AS equipmentCount
OPTIONAL MATCH (s) WHERE s.sensorId IS NOT NULL
WITH equipmentCount, count(s) AS sensorCount
OPTIONAL MATCH (a:AnomalyDetection)
WITH equipmentCount, sensorCount, count(a) AS anomalyCount
OPTIONAL MATCH (fp:FailurePrediction)
WITH equipmentCount, sensorCount, anomalyCount, count(fp) AS predictionCount
OPTIONAL MATCH (me:MaintenanceEvent)
RETURN equipmentCount, sensorCount, anomalyCount, predictionCount, count(me) AS maintenanceCount
"""
