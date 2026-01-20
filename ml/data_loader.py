"""Data loader for anomaly detection"""

import os
import pandas as pd
from neo4j import GraphDatabase


class Neo4jDataLoader:
    """Load data from Neo4j for ML"""

    def __init__(self,
                 uri: str = None,
                 user: str = None,
                 password: str = None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:17687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password123")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def query(self, cypher: str, parameters: dict = None) -> list:
        """Execute Cypher query"""
        with self.driver.session() as session:
            result = session.run(cypher, parameters or {})
            return [record.data() for record in result]

    def get_sensor_observations(self, sensor_id: str = None, limit: int = 1000) -> pd.DataFrame:
        """Get sensor observations as DataFrame"""
        if sensor_id:
            query = """
            MATCH (o:SensorObservation)-[:madeBySensor]->(s:Sensor)
            WHERE s.sensorId[0] = $sensor_id OR s.sensorId = $sensor_id
            RETURN s.sensorId[0] AS sensor_id,
                   labels(s)[1] AS sensor_type,
                   o.timestamp[0] AS timestamp,
                   o.value[0] AS value,
                   o.unit[0] AS unit
            ORDER BY o.timestamp DESC
            LIMIT $limit
            """
            data = self.query(query, {"sensor_id": sensor_id, "limit": limit})
        else:
            query = """
            MATCH (o:SensorObservation)-[:madeBySensor]->(s:Sensor)
            RETURN s.sensorId[0] AS sensor_id,
                   labels(s)[1] AS sensor_type,
                   o.timestamp[0] AS timestamp,
                   o.value[0] AS value,
                   o.unit[0] AS unit
            ORDER BY o.timestamp DESC
            LIMIT $limit
            """
            data = self.query(query, {"limit": limit})

        return pd.DataFrame(data)

    def get_all_sensors(self) -> pd.DataFrame:
        """Get all sensors"""
        query = """
        MATCH (s:Sensor)
        OPTIONAL MATCH (e)-[:hasSensor]->(s)
        WHERE e.equipmentId IS NOT NULL
        RETURN s.sensorId[0] AS sensor_id,
               labels(s)[1] AS sensor_type,
               s.sensorLocation[0] AS location,
               e.equipmentId[0] AS equipment_id,
               e.equipmentName[0] AS equipment_name
        """
        return pd.DataFrame(self.query(query))

    def get_equipment_sensor_data(self, equipment_id: str) -> pd.DataFrame:
        """Get all sensor data for equipment"""
        query = """
        MATCH (e)-[:hasSensor]->(s:Sensor)
        WHERE e.equipmentId[0] = $equipment_id OR e.equipmentId = $equipment_id
        OPTIONAL MATCH (o:SensorObservation)-[:madeBySensor]->(s)
        RETURN s.sensorId[0] AS sensor_id,
               labels(s)[1] AS sensor_type,
               o.timestamp[0] AS timestamp,
               o.value[0] AS value,
               o.unit[0] AS unit
        ORDER BY o.timestamp
        """
        return pd.DataFrame(self.query(query, {"equipment_id": equipment_id}))

    def save_anomaly_detection(self, sensor_id: str, score: float, timestamp: str,
                               label: str = None, description: str = None):
        """Save anomaly detection result to Neo4j"""
        query = """
        MATCH (s:Sensor)
        WHERE s.sensorId[0] = $sensor_id OR s.sensorId = $sensor_id
        CREATE (a:AnomalyDetection:Resource {
            anomalyScore: [$score],
            timestamp: [$timestamp],
            rdfs__label: $label,
            rdfs__comment: $description
        })
        CREATE (a)-[:madeBySensor]->(s)
        RETURN a
        """
        return self.query(query, {
            "sensor_id": sensor_id,
            "score": score,
            "timestamp": timestamp,
            "label": label,
            "description": description
        })


if __name__ == "__main__":
    # Test
    loader = Neo4jDataLoader()
    try:
        sensors = loader.get_all_sensors()
        print("Sensors:")
        print(sensors)

        obs = loader.get_sensor_observations(limit=10)
        print("\nObservations:")
        print(obs)
    finally:
        loader.close()
