#!/usr/bin/env python3
"""Training script for anomaly detection models"""

import os
import argparse
import pandas as pd
import numpy as np
from datetime import datetime

from data_loader import Neo4jDataLoader
from anomaly_detection import AnomalyDetector


def generate_synthetic_data(n_samples: int = 500) -> pd.DataFrame:
    """Generate synthetic sensor data for training"""
    np.random.seed(42)

    # Normal vibration data (2-3 mm/s)
    normal_vibration = np.random.normal(loc=2.5, scale=0.5, size=n_samples)

    # Add some anomalies (5%)
    n_anomalies = int(n_samples * 0.05)
    anomaly_indices = np.random.choice(n_samples, n_anomalies, replace=False)
    normal_vibration[anomaly_indices] = np.random.uniform(4.5, 7.0, n_anomalies)

    # Create timestamps
    timestamps = pd.date_range(start='2025-01-01', periods=n_samples, freq='15min')

    return pd.DataFrame({
        'sensor_id': 'VIB-001',
        'sensor_type': 'VibrationSensor',
        'timestamp': timestamps,
        'value': normal_vibration,
        'unit': 'mm/s'
    })


def train_model(sensor_id: str = None,
                algorithm: str = "isolation_forest",
                use_synthetic: bool = False) -> AnomalyDetector:
    """
    Train anomaly detection model.

    Args:
        sensor_id: Specific sensor to train on (None for all)
        algorithm: Algorithm to use
        use_synthetic: Use synthetic data instead of Neo4j

    Returns:
        Trained AnomalyDetector
    """
    print(f"Training {algorithm} model...")
    print(f"Sensor: {sensor_id or 'all'}")

    # Load data
    if use_synthetic:
        print("Using synthetic data...")
        data = generate_synthetic_data()
    else:
        print("Loading data from Neo4j...")
        loader = Neo4jDataLoader()
        try:
            data = loader.get_sensor_observations(sensor_id=sensor_id, limit=1000)
            if data.empty:
                print("No data found in Neo4j. Using synthetic data...")
                data = generate_synthetic_data()
        finally:
            loader.close()

    print(f"Loaded {len(data)} samples")

    # Filter by sensor if specified
    if sensor_id and 'sensor_id' in data.columns:
        data = data[data['sensor_id'] == sensor_id]
        print(f"Filtered to {len(data)} samples for sensor {sensor_id}")

    if data.empty or len(data) < 10:
        print("Not enough data. Using synthetic data...")
        data = generate_synthetic_data()

    # Train model
    detector = AnomalyDetector(algorithm=algorithm)
    detector.fit(data)

    print("Training complete!")
    print(f"Model info: {detector.get_info()}")

    return detector


def main():
    parser = argparse.ArgumentParser(description="Train anomaly detection model")
    parser.add_argument("--sensor", type=str, default=None,
                        help="Sensor ID to train on")
    parser.add_argument("--algorithm", type=str, default="isolation_forest",
                        choices=["isolation_forest", "one_class_svm", "zscore"],
                        help="Algorithm to use")
    parser.add_argument("--synthetic", action="store_true",
                        help="Use synthetic data")
    parser.add_argument("--output", type=str, default="models/anomaly_model.joblib",
                        help="Output model path")

    args = parser.parse_args()

    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)

    # Train
    detector = train_model(
        sensor_id=args.sensor,
        algorithm=args.algorithm,
        use_synthetic=args.synthetic
    )

    # Save
    detector.save(args.output)

    # Test predictions
    print("\n--- Test Predictions ---")
    test_values = [2.5, 3.5, 5.0, 6.5]
    for v in test_values:
        score, label = detector.predict(v)
        status = "🟢" if label == "normal" else "🟡" if label == "warning" else "🔴"
        print(f"  {status} Value: {v:.1f} -> Score: {score:.3f} ({label})")


if __name__ == "__main__":
    main()
