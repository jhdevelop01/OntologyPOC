// =============================================================================
// UPW Process Ontology - Example Cypher Queries
// =============================================================================
// These queries demonstrate common use cases for the UPW ontology in Neo4j
// after importing with n10s.
// =============================================================================

// -----------------------------------------------------------------------------
// 1. EQUIPMENT QUERIES
// -----------------------------------------------------------------------------

// 1.1 List all equipment with their types
MATCH (e:Equipment)
RETURN e.uri AS equipment,
       labels(e) AS types,
       e.equipmentId AS id,
       e.equipmentName AS name,
       e.operatingHours AS hours
ORDER BY e.equipmentName;

// 1.2 Get all equipment with their sensors
MATCH (e:Equipment)-[:hasSensor]->(s:Sensor)
RETURN e.equipmentName AS equipment,
       e.equipmentId AS equipmentId,
       collect({
         sensorId: s.sensorId,
         type: [l IN labels(s) WHERE l <> 'Sensor' AND l <> 'Resource'][0],
         location: s.sensorLocation
       }) AS sensors
ORDER BY e.equipmentName;

// 1.3 Find equipment by type (e.g., all Pumps)
MATCH (e:Pump)
RETURN e.equipmentId AS id,
       e.equipmentName AS name,
       e.installationDate AS installed,
       e.operatingHours AS hours;

// -----------------------------------------------------------------------------
// 2. ANOMALY DETECTION QUERIES
// -----------------------------------------------------------------------------

// 2.1 Find all anomaly detections with score above threshold
MATCH (a:AnomalyDetection)
WHERE a.anomalyScore > 0.5
RETURN a.uri AS anomaly,
       a.anomalyScore AS score,
       a.timestamp AS detectedAt,
       a.rdfs__comment AS description
ORDER BY a.anomalyScore DESC;

// 2.2 Find anomalies with their triggering sensors and equipment
MATCH (a:AnomalyDetection)-[:madeBySensor]->(s:Sensor)<-[:hasSensor]-(e:Equipment)
WHERE a.anomalyScore > 0.5
RETURN e.equipmentName AS equipment,
       e.equipmentId AS equipmentId,
       s.sensorId AS sensor,
       a.anomalyScore AS anomalyScore,
       a.timestamp AS detectedAt
ORDER BY a.anomalyScore DESC;

// 2.3 Get recent anomalies (last 24 hours - adjust timestamp)
MATCH (a:AnomalyDetection)
WHERE datetime(a.timestamp) > datetime() - duration('P1D')
RETURN a.uri AS anomaly,
       a.anomalyScore AS score,
       a.timestamp AS detectedAt
ORDER BY a.timestamp DESC;

// 2.4 Count anomalies by equipment
MATCH (a:AnomalyDetection)-[:madeBySensor]->(s:Sensor)<-[:hasSensor]-(e:Equipment)
RETURN e.equipmentName AS equipment,
       count(a) AS anomalyCount,
       avg(a.anomalyScore) AS avgAnomalyScore,
       max(a.anomalyScore) AS maxAnomalyScore
ORDER BY anomalyCount DESC;

// -----------------------------------------------------------------------------
// 3. FAILURE PREDICTION QUERIES
// -----------------------------------------------------------------------------

// 3.1 Get equipment with predicted failures in the next N days
MATCH (e:Equipment)-[:hasPrediction]->(fp:FailurePrediction)
WHERE datetime(fp.predictedFailureDate) <= datetime() + duration('P30D')
RETURN e.equipmentName AS equipment,
       e.equipmentId AS equipmentId,
       fp.failureMode AS failureType,
       fp.predictedFailureDate AS predictedDate,
       fp.confidenceScore AS confidence,
       fp.remainingUsefulLife AS rulHours
ORDER BY fp.predictedFailureDate;

// 3.2 Get high-confidence failure predictions
MATCH (e:Equipment)-[:hasPrediction]->(fp:FailurePrediction)
WHERE fp.confidenceScore > 0.7
RETURN e.equipmentName AS equipment,
       fp.failureMode AS failureType,
       fp.predictedFailureDate AS predictedDate,
       fp.confidenceScore AS confidence,
       fp.rdfs__comment AS recommendation
ORDER BY fp.confidenceScore DESC;

// 3.3 Failure predictions with triggering anomalies
MATCH (fp:FailurePrediction)-[:triggeredBy]->(a:AnomalyDetection)
MATCH (e:Equipment)-[:hasPrediction]->(fp)
RETURN e.equipmentName AS equipment,
       fp.failureMode AS failureType,
       fp.predictedFailureDate AS predictedDate,
       a.anomalyScore AS triggeringAnomalyScore,
       a.timestamp AS anomalyDetectedAt;

// 3.4 Equipment health dashboard - combine current state with predictions
MATCH (e:Equipment)
OPTIONAL MATCH (e)-[:hasPrediction]->(fp:FailurePrediction)
OPTIONAL MATCH (e)-[:hasSensor]->(s:Sensor)<-[:madeBySensor]-(a:AnomalyDetection)
RETURN e.equipmentName AS equipment,
       e.operatingHours AS operatingHours,
       fp.remainingUsefulLife AS predictedRUL,
       fp.failureMode AS riskType,
       max(a.anomalyScore) AS highestAnomalyScore
ORDER BY fp.remainingUsefulLife;

// -----------------------------------------------------------------------------
// 4. MAINTENANCE SCHEDULE QUERIES
// -----------------------------------------------------------------------------

// 4.1 Get all scheduled maintenance events
MATCH (e:Equipment)-[:hasMaintenanceSchedule]->(ms:MaintenanceSchedule)-[:hasMaintenanceEvent]->(me:MaintenanceEvent)
WHERE me.status = 'Scheduled'
RETURN e.equipmentName AS equipment,
       me.rdfs__label AS eventName,
       me.scheduledDate AS scheduledFor,
       me.priority AS priority,
       me.estimatedDuration AS durationHours,
       me.maintenanceDescription AS description
ORDER BY me.scheduledDate;

// 4.2 Get maintenance events in a date range
MATCH (e:Equipment)-[:hasMaintenanceSchedule]->(ms:MaintenanceSchedule)-[:hasMaintenanceEvent]->(me:MaintenanceEvent)
WHERE datetime(me.scheduledDate) >= datetime('2025-01-20T00:00:00Z')
  AND datetime(me.scheduledDate) <= datetime('2025-02-28T23:59:59Z')
RETURN e.equipmentName AS equipment,
       me.rdfs__label AS event,
       me.scheduledDate AS scheduled,
       me.priority AS priority
ORDER BY me.scheduledDate;

// 4.3 Get high-priority maintenance (priority = 1)
MATCH (e:Equipment)-[:hasMaintenanceSchedule]->(ms:MaintenanceSchedule)-[:hasMaintenanceEvent]->(me:MaintenanceEvent)
WHERE me.priority = 1 AND me.status = 'Scheduled'
RETURN e.equipmentName AS equipment,
       me.rdfs__label AS event,
       me.scheduledDate AS scheduled,
       me.maintenanceDescription AS description
ORDER BY me.scheduledDate;

// 4.4 Maintenance events by type (Predictive, Preventive, Corrective)
MATCH (me:MaintenanceEvent)-[:hasMaintenanceType]->(mt:MaintenanceType)
MATCH (e:Equipment)-[:hasMaintenanceSchedule]->(:MaintenanceSchedule)-[:hasMaintenanceEvent]->(me)
RETURN mt.rdfs__label AS maintenanceType,
       count(me) AS eventCount,
       collect(e.equipmentName) AS equipment;

// 4.5 Optimized maintenance window - find equipment that can be maintained together
MATCH (e:Equipment)-[:hasMaintenanceSchedule]->(ms:MaintenanceSchedule)-[:hasMaintenanceEvent]->(me:MaintenanceEvent)
WHERE me.status = 'Scheduled'
WITH date(datetime(me.scheduledDate)) AS maintenanceDay, collect({
  equipment: e.equipmentName,
  event: me.rdfs__label,
  duration: me.estimatedDuration,
  priority: me.priority
}) AS events
RETURN maintenanceDay,
       size(events) AS eventsCount,
       events
ORDER BY maintenanceDay;

// -----------------------------------------------------------------------------
// 5. ENERGY PREDICTION QUERIES
// -----------------------------------------------------------------------------

// 5.1 Get 96-point energy forecast for a specific date
MATCH (ep:EnergyPrediction)-[:hasForecastPoint]->(fp:EnergyForecastPoint)
WHERE ep.forecastDate = date('2025-01-21')
RETURN ep.forecastDate AS forecastDate,
       ep.totalDailyEnergy AS totalEnergy,
       ep.peakPower AS peakPower,
       fp.intervalIndex AS interval,
       fp.intervalStartTime AS time,
       fp.powerConsumption AS powerKW,
       fp.confidenceScore AS confidence
ORDER BY fp.intervalIndex;

// 5.2 Get energy forecast summary for a date
MATCH (ep:EnergyPrediction)
WHERE ep.forecastDate = date('2025-01-21')
RETURN ep.forecastDate AS date,
       ep.totalDailyEnergy AS totalEnergyKWh,
       ep.peakPower AS peakPowerKW,
       ep.confidenceScore AS overallConfidence,
       ep.timestamp AS generatedAt;

// 5.3 Get peak consumption intervals (top 10)
MATCH (ep:EnergyPrediction)-[:hasForecastPoint]->(fp:EnergyForecastPoint)
WHERE ep.forecastDate = date('2025-01-21')
RETURN fp.intervalIndex AS interval,
       fp.intervalStartTime AS time,
       fp.powerConsumption AS powerKW
ORDER BY fp.powerConsumption DESC
LIMIT 10;

// 5.4 Get low consumption intervals (for maintenance scheduling)
MATCH (ep:EnergyPrediction)-[:hasForecastPoint]->(fp:EnergyForecastPoint)
WHERE ep.forecastDate = date('2025-01-21')
RETURN fp.intervalIndex AS interval,
       fp.intervalStartTime AS time,
       fp.powerConsumption AS powerKW
ORDER BY fp.powerConsumption ASC
LIMIT 10;

// 5.5 Average power by time period
MATCH (ep:EnergyPrediction)-[:hasForecastPoint]->(fp:EnergyForecastPoint)
WHERE ep.forecastDate = date('2025-01-21')
WITH fp,
     CASE
       WHEN fp.intervalIndex < 24 THEN 'Night (00:00-06:00)'
       WHEN fp.intervalIndex < 48 THEN 'Morning (06:00-12:00)'
       WHEN fp.intervalIndex < 72 THEN 'Afternoon (12:00-18:00)'
       ELSE 'Evening (18:00-24:00)'
     END AS period
RETURN period,
       avg(fp.powerConsumption) AS avgPower,
       min(fp.powerConsumption) AS minPower,
       max(fp.powerConsumption) AS maxPower
ORDER BY
  CASE period
    WHEN 'Night (00:00-06:00)' THEN 1
    WHEN 'Morning (06:00-12:00)' THEN 2
    WHEN 'Afternoon (12:00-18:00)' THEN 3
    ELSE 4
  END;

// -----------------------------------------------------------------------------
// 6. SENSOR OBSERVATION QUERIES
// -----------------------------------------------------------------------------

// 6.1 Get latest observations for all sensors
MATCH (s:Sensor)-[:hasObservation]->(o:SensorObservation)
WITH s, o
ORDER BY o.timestamp DESC
WITH s, collect(o)[0] AS latestObs
RETURN s.sensorId AS sensor,
       [l IN labels(s) WHERE l <> 'Sensor' AND l <> 'Resource'][0] AS sensorType,
       latestObs.timestamp AS lastReading,
       latestObs.value AS value,
       latestObs.unit AS unit;

// 6.2 Get observation history for a specific sensor
MATCH (s:Sensor {sensorId: 'VIB-001'})-[:hasObservation]->(o:SensorObservation)
RETURN o.timestamp AS time,
       o.value AS value,
       o.unit AS unit
ORDER BY o.timestamp DESC
LIMIT 50;

// 6.3 Observations made by sensors of specific equipment
MATCH (e:Equipment {equipmentId: 'PUMP-001'})-[:hasSensor]->(s:Sensor)
MATCH (o:SensorObservation)-[:madeBySensor]->(s)
RETURN s.sensorId AS sensor,
       o.timestamp AS time,
       o.value AS value,
       o.unit AS unit
ORDER BY o.timestamp DESC
LIMIT 20;

// -----------------------------------------------------------------------------
// 7. COMBINED ANALYTICS QUERIES
// -----------------------------------------------------------------------------

// 7.1 Equipment risk assessment dashboard
MATCH (e:Equipment)
OPTIONAL MATCH (e)-[:hasPrediction]->(fp:FailurePrediction)
OPTIONAL MATCH (e)-[:hasSensor]->(s:Sensor)<-[:madeBySensor]-(a:AnomalyDetection)
WHERE a.anomalyScore > 0.5
OPTIONAL MATCH (e)-[:hasMaintenanceSchedule]->(:MaintenanceSchedule)-[:hasMaintenanceEvent]->(me:MaintenanceEvent {status: 'Scheduled'})
RETURN e.equipmentName AS equipment,
       e.equipmentId AS id,
       fp.failureMode AS predictedFailure,
       fp.predictedFailureDate AS failureDate,
       fp.confidenceScore AS failureConfidence,
       count(DISTINCT a) AS activeAnomalies,
       max(a.anomalyScore) AS maxAnomalyScore,
       count(DISTINCT me) AS scheduledMaintenance
ORDER BY fp.predictedFailureDate;

// 7.2 Find equipment needing immediate attention
// (high anomaly score + near-term failure prediction + no scheduled maintenance)
MATCH (e:Equipment)-[:hasPrediction]->(fp:FailurePrediction)
WHERE datetime(fp.predictedFailureDate) <= datetime() + duration('P14D')
  AND fp.confidenceScore > 0.6
OPTIONAL MATCH (e)-[:hasSensor]->(s:Sensor)<-[:madeBySensor]-(a:AnomalyDetection)
WHERE a.anomalyScore > 0.7
OPTIONAL MATCH (e)-[:hasMaintenanceSchedule]->(:MaintenanceSchedule)-[:hasMaintenanceEvent]->(me:MaintenanceEvent)
WHERE me.status = 'Scheduled'
  AND datetime(me.scheduledDate) < datetime(fp.predictedFailureDate)
WITH e, fp, a, me
WHERE me IS NULL  // No maintenance scheduled before predicted failure
RETURN e.equipmentName AS equipment,
       e.equipmentId AS id,
       fp.failureMode AS riskType,
       fp.predictedFailureDate AS predictedFailure,
       a.anomalyScore AS activeAnomalyScore,
       'URGENT: Schedule maintenance' AS recommendation;

// 7.3 Optimal maintenance window recommendation
// Find low-energy periods when equipment with predicted failures can be maintained
MATCH (e:Equipment)-[:hasPrediction]->(fp:FailurePrediction)
WHERE datetime(fp.predictedFailureDate) <= datetime() + duration('P30D')
MATCH (ep:EnergyPrediction)-[:hasForecastPoint]->(efp:EnergyForecastPoint)
WHERE efp.powerConsumption < 90  // Low consumption threshold
RETURN e.equipmentName AS equipment,
       fp.failureMode AS issue,
       fp.predictedFailureDate AS mustCompleteBy,
       efp.intervalStartTime AS recommendedSlot,
       efp.powerConsumption AS expectedLoad
ORDER BY efp.powerConsumption ASC
LIMIT 10;

// 7.4 Sensor health overview
MATCH (e:Equipment)-[:hasSensor]->(s:Sensor)
OPTIONAL MATCH (s)<-[:madeBySensor]-(o:SensorObservation)
OPTIONAL MATCH (s)<-[:madeBySensor]-(a:AnomalyDetection)
RETURN e.equipmentName AS equipment,
       s.sensorId AS sensor,
       [l IN labels(s) WHERE l <> 'Sensor' AND l <> 'Resource'][0] AS type,
       count(DISTINCT o) AS totalObservations,
       count(DISTINCT a) AS anomalyDetections,
       max(a.anomalyScore) AS maxAnomalyScore
ORDER BY e.equipmentName, s.sensorId;

// -----------------------------------------------------------------------------
// 8. GRAPH TRAVERSAL QUERIES
// -----------------------------------------------------------------------------

// 8.1 Full traceability: From anomaly to maintenance recommendation
MATCH path = (a:AnomalyDetection)-[:madeBySensor]->(s:Sensor)<-[:hasSensor]-(e:Equipment)
              -[:hasPrediction]->(fp:FailurePrediction)
MATCH (e)-[:hasMaintenanceSchedule]->(ms:MaintenanceSchedule)-[:hasMaintenanceEvent]->(me:MaintenanceEvent)
WHERE a.anomalyScore > 0.5
RETURN a.rdfs__label AS anomaly,
       a.anomalyScore AS score,
       s.sensorId AS sensor,
       e.equipmentName AS equipment,
       fp.failureMode AS predictedFailure,
       me.rdfs__label AS scheduledMaintenance,
       me.scheduledDate AS maintenanceDate;

// 8.2 Equipment dependency graph (if relationships exist)
MATCH (e1:Equipment)-[r]->(e2:Equipment)
RETURN e1.equipmentName AS from,
       type(r) AS relationship,
       e2.equipmentName AS to;

// 8.3 Find all entities related to specific equipment
MATCH (e:Equipment {equipmentId: 'PUMP-001'})-[r*1..3]-(related)
RETURN e.equipmentName AS equipment,
       labels(related) AS relatedTypes,
       related.uri AS relatedEntity
LIMIT 50;
