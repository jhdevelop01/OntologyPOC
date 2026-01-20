#!/usr/bin/env python3
"""Prediction script for anomaly detection"""

import argparse
from datetime import datetime

from anomaly_detection import AnomalyDetector
from data_loader import Neo4jDataLoader


def predict_single(model_path: str, value: float,
                   sensor_id: str = None,
                   save_to_neo4j: bool = False):
    """
    Predict anomaly for a single value.

    Args:
        model_path: Path to trained model
        value: Sensor measurement value
        sensor_id: Sensor ID (for saving to Neo4j)
        save_to_neo4j: Whether to save result to Neo4j
    """
    # Load model
    detector = AnomalyDetector.load(model_path)

    # Predict
    score, label = detector.predict(value)

    # Display result
    status = "🟢" if label == "normal" else "🟡" if label == "warning" else "🔴"
    print(f"\n{status} Anomaly Detection Result")
    print(f"  Value: {value}")
    print(f"  Score: {score:.4f}")
    print(f"  Label: {label}")

    if score >= 0.7:
        print(f"  ⚠️  ALERT: High anomaly score detected!")

    # Save to Neo4j
    if save_to_neo4j and sensor_id:
        print(f"\nSaving to Neo4j...")
        loader = Neo4jDataLoader()
        try:
            timestamp = datetime.now().isoformat()
            description = f"Anomaly detected with score {score:.4f}"
            loader.save_anomaly_detection(
                sensor_id=sensor_id,
                score=score,
                timestamp=timestamp,
                label=f"ML detected anomaly ({label})",
                description=description
            )
            print(f"Saved anomaly detection for sensor {sensor_id}")
        finally:
            loader.close()

    return score, label


def predict_batch(model_path: str, sensor_id: str):
    """
    Predict anomalies for all observations of a sensor.

    Args:
        model_path: Path to trained model
        sensor_id: Sensor ID
    """
    # Load model
    detector = AnomalyDetector.load(model_path)

    # Load data
    print(f"Loading data for sensor {sensor_id}...")
    loader = Neo4jDataLoader()
    try:
        data = loader.get_sensor_observations(sensor_id=sensor_id)
    finally:
        loader.close()

    if data.empty:
        print(f"No data found for sensor {sensor_id}")
        return

    print(f"Loaded {len(data)} observations")

    # Predict
    results = detector.predict_batch(data)

    # Display results
    print("\n--- Anomaly Detection Results ---")
    for _, row in results.iterrows():
        score = row['anomaly_score']
        label = row['anomaly_label']
        value = row['value']
        status = "🟢" if label == "normal" else "🟡" if label == "warning" else "🔴"
        print(f"  {status} Value: {value:.2f} -> Score: {score:.3f} ({label})")

    # Summary
    print("\n--- Summary ---")
    anomalies = results[results['anomaly_label'] == 'anomaly']
    warnings = results[results['anomaly_label'] == 'warning']
    normals = results[results['anomaly_label'] == 'normal']

    print(f"  🟢 Normal:  {len(normals)}")
    print(f"  🟡 Warning: {len(warnings)}")
    print(f"  🔴 Anomaly: {len(anomalies)}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Predict anomalies")
    parser.add_argument("--model", type=str, default="models/anomaly_model.joblib",
                        help="Model path")
    parser.add_argument("--sensor", type=str, default=None,
                        help="Sensor ID")
    parser.add_argument("--value", type=float, default=None,
                        help="Single value to predict")
    parser.add_argument("--batch", action="store_true",
                        help="Batch prediction for sensor")
    parser.add_argument("--save", action="store_true",
                        help="Save results to Neo4j")

    args = parser.parse_args()

    if args.value is not None:
        predict_single(
            model_path=args.model,
            value=args.value,
            sensor_id=args.sensor,
            save_to_neo4j=args.save
        )
    elif args.batch and args.sensor:
        predict_batch(
            model_path=args.model,
            sensor_id=args.sensor
        )
    else:
        print("Please specify --value or (--batch --sensor)")
        parser.print_help()


if __name__ == "__main__":
    main()
