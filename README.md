# UPW (Ultra Pure Water) Process Ontology

An OWL ontology for factory Ultra Pure Water process monitoring, supporting predictive maintenance and energy forecasting.

## Overview

This ontology models the UPW process domain with support for:

- **Predictive Maintenance**: Anomaly detection, failure prediction, maintenance scheduling
- **Energy Prediction**: 96-point (15-minute intervals) next-day forecasting from 10-day history

## File Structure

```
OntologyPOC/
├── ontology/
│   ├── upw.owl.ttl          # Main OWL ontology (Turtle format)
│   └── sample_data.ttl      # Sample instances (sensors, observations, predictions)
├── neo4j/
│   └── import.cypher        # n10s import script
├── queries/
│   └── examples.cypher      # Query examples for all use cases
└── README.md                # This file
```

## Namespace Prefixes

| Prefix | URI | Purpose |
|--------|-----|---------|
| upw | http://example.org/upw# | Main ontology namespace |
| upw-data | http://example.org/upw/data# | Instance data |
| sosa | http://www.w3.org/ns/sosa/ | Sensor/Observation (W3C SSN) |
| ssn | http://www.w3.org/ns/ssn/ | Semantic Sensor Network |
| time | http://www.w3.org/2006/time# | OWL Time |
| qudt | http://qudt.org/schema/qudt/ | Units of measure |

## Ontology Structure

### Equipment Classes

```
upw:Equipment
├── upw:Pump
├── upw:Filter
├── upw:ROSystem
├── upw:IonExchanger
├── upw:UVSterilizer
└── upw:StorageTank
```

### Sensor Classes

```
upw:Sensor (subClassOf sosa:Sensor)
├── upw:VibrationSensor
├── upw:PressureSensor
├── upw:FlowSensor
├── upw:TemperatureSensor
├── upw:CurrentSensor
├── upw:DifferentialPressureSensor
├── upw:ConductivitySensor
├── upw:ResistivitySensor
├── upw:UVIntensitySensor
└── upw:LevelSensor
```

### Observation/Prediction Classes

```
sosa:Observation
├── upw:SensorObservation
├── upw:AnomalyDetection
├── upw:FailurePrediction
└── upw:EnergyPrediction
    └── upw:EnergyForecastPoint (15-min interval prediction)

upw:MaintenanceSchedule
upw:MaintenanceEvent
```

## Sample Data Summary

The `sample_data.ttl` file contains:

| Entity Type | Count | Description |
|------------|-------|-------------|
| Equipment | 6 | One instance per equipment type |
| Sensors | 18 | Various sensors attached to equipment |
| Observations | 12 | Recent sensor readings |
| Anomaly Detections | 3 | Detected anomalies with scores |
| Failure Predictions | 2 | Predicted failures with confidence |
| Energy Forecast Points | 21 | Sample 15-min interval predictions |
| Maintenance Events | 8 | Scheduled and completed maintenance |

## Prerequisites

### Neo4j Setup

1. Install Neo4j 4.x or 5.x
2. Install the [n10s (neosemantics) plugin](https://neo4j.com/labs/neosemantics/)

   For Neo4j Desktop:
   - Open your project
   - Click on the database plugins
   - Install "neosemantics"

   For Docker:
   ```bash
   docker run \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password \
     -e NEO4J_PLUGINS='["n10s"]' \
     neo4j:5
   ```

3. (Optional) Install APOC plugin for advanced verification queries

## Execution Guide

### Step 1: Validate TTL Files (Optional)

Using rapper (part of raptor-utils):

```bash
# Install rapper (macOS)
brew install raptor

# Validate ontology
rapper -i turtle -c ontology/upw.owl.ttl

# Validate sample data
rapper -i turtle -c ontology/sample_data.ttl
```

Or use an online validator like [RDF Validator](http://rdf.greggkellogg.net/distiller).

### Step 2: Start Neo4j

Ensure Neo4j is running with the n10s plugin enabled.

```bash
# Neo4j Desktop: Start your database from the UI

# Docker:
docker-compose up -d  # if using docker-compose
# or
neo4j start  # if installed locally
```

### Step 3: Import the Ontology

Open Neo4j Browser (http://localhost:7474) and run the import script.

**Option A: Run the full import script**

Copy and paste contents from `neo4j/import.cypher` into the Neo4j Browser.

**Option B: Run step by step**

```cypher
// 1. Create constraint
CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource) REQUIRE r.uri IS UNIQUE;

// 2. Initialize n10s
CALL n10s.graphconfig.init({
  handleVocabUris: "MAP",
  handleMultival: "ARRAY",
  handleRDFTypes: "LABELS_AND_NODES"
});

// 3. Add prefixes
CALL n10s.nsprefixes.add("upw", "http://example.org/upw#");
CALL n10s.nsprefixes.add("upw-data", "http://example.org/upw/data#");

// 4. Import ontology (adjust path)
CALL n10s.onto.import.fetch(
  "file:///path/to/OntologyPOC/ontology/upw.owl.ttl",
  "Turtle"
);

// 5. Import data (adjust path)
CALL n10s.rdf.import.fetch(
  "file:///path/to/OntologyPOC/ontology/sample_data.ttl",
  "Turtle"
);
```

**Note**: For file:// URLs, use the absolute path. For remote import, you can serve the files via HTTP:

```bash
# Serve files locally
cd OntologyPOC
python3 -m http.server 8000

# Then import using HTTP URLs
CALL n10s.onto.import.fetch("http://localhost:8000/ontology/upw.owl.ttl", "Turtle");
CALL n10s.rdf.import.fetch("http://localhost:8000/ontology/sample_data.ttl", "Turtle");
```

### Step 4: Verify Import

```cypher
// Count nodes by label
MATCH (n)
UNWIND labels(n) AS label
RETURN label, count(*) AS count
ORDER BY count DESC;

// Count relationships
MATCH ()-[r]->()
RETURN type(r) AS type, count(*) AS count
ORDER BY count DESC;
```

Expected results:
- ~50+ nodes across various labels (Equipment, Sensor, Observation, etc.)
- Multiple relationship types (hasSensor, hasObservation, hasPrediction, etc.)

### Step 5: Run Example Queries

Open `queries/examples.cypher` and run the queries relevant to your use case:

1. **Anomaly Detection**: Find sensors with high anomaly scores
2. **Failure Prediction**: Get equipment with predicted failures
3. **Maintenance Schedule**: Retrieve optimized maintenance windows
4. **Energy Prediction**: Get 96-point forecast data

## Key Query Examples

### Find High-Risk Equipment

```cypher
MATCH (e:Equipment)-[:hasPrediction]->(fp:FailurePrediction)
WHERE fp.confidenceScore > 0.7
RETURN e.equipmentName, fp.failureMode, fp.predictedFailureDate, fp.confidenceScore
ORDER BY fp.predictedFailureDate;
```

### Get Anomalies Above Threshold

```cypher
MATCH (a:AnomalyDetection)-[:madeBySensor]->(s:Sensor)<-[:hasSensor]-(e:Equipment)
WHERE a.anomalyScore > 0.5
RETURN e.equipmentName, s.sensorId, a.anomalyScore, a.timestamp
ORDER BY a.anomalyScore DESC;
```

### Get Energy Forecast

```cypher
MATCH (ep:EnergyPrediction)-[:hasForecastPoint]->(fp:EnergyForecastPoint)
WHERE ep.forecastDate = date('2025-01-21')
RETURN fp.intervalIndex, fp.intervalStartTime, fp.powerConsumption
ORDER BY fp.intervalIndex;
```

### Upcoming Maintenance

```cypher
MATCH (e:Equipment)-[:hasMaintenanceSchedule]->()-[:hasMaintenanceEvent]->(me:MaintenanceEvent)
WHERE me.status = 'Scheduled'
RETURN e.equipmentName, me.rdfs__label, me.scheduledDate, me.priority
ORDER BY me.scheduledDate;
```

## Cleanup

To reset the database and reimport:

```cypher
// Delete all data
MATCH (n) DETACH DELETE n;

// Drop n10s config
CALL n10s.graphconfig.drop();

// Drop constraint
DROP CONSTRAINT n10s_unique_uri IF EXISTS;
```

## Extending the Ontology

### Adding New Equipment Types

```turtle
upw:NewEquipmentType a owl:Class ;
    rdfs:subClassOf upw:Equipment ;
    rdfs:label "New Equipment Type"@en .
```

### Adding New Sensor Types

```turtle
upw:NewSensorType a owl:Class ;
    rdfs:subClassOf upw:Sensor ;
    rdfs:label "New Sensor Type"@en .
```

### Adding Instance Data

```turtle
upw-data:new-equipment-001 a upw:NewEquipmentType ;
    upw:equipmentId "NEW-001" ;
    upw:equipmentName "New Equipment Instance" ;
    upw:hasSensor upw-data:sensor-new-001 .
```

## License

This ontology is provided for demonstration purposes.
