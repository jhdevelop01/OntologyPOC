"""Anomaly Detection Model"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from typing import Tuple, Optional, Dict, Any

from preprocessing import SensorDataPreprocessor, zscore_anomaly_score


class AnomalyDetector:
    """Anomaly detection using multiple algorithms"""

    def __init__(self, algorithm: str = "isolation_forest"):
        """
        Initialize anomaly detector.

        Args:
            algorithm: 'isolation_forest', 'one_class_svm', or 'zscore'
        """
        self.algorithm = algorithm
        self.model = None
        self.preprocessor = SensorDataPreprocessor()
        self.trained = False

        # Statistics for zscore
        self.mean = None
        self.std = None

        # Model parameters
        self.params = {
            "isolation_forest": {
                "contamination": 0.1,  # Expected proportion of outliers
                "random_state": 42,
                "n_estimators": 100
            },
            "one_class_svm": {
                "kernel": "rbf",
                "gamma": "auto",
                "nu": 0.1  # Upper bound on fraction of outliers
            }
        }

    def _create_model(self):
        """Create model based on algorithm"""
        if self.algorithm == "isolation_forest":
            self.model = IsolationForest(**self.params["isolation_forest"])
        elif self.algorithm == "one_class_svm":
            self.model = OneClassSVM(**self.params["one_class_svm"])
        elif self.algorithm == "zscore":
            self.model = None  # No model needed for zscore
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")

    def fit(self, data: pd.DataFrame) -> 'AnomalyDetector':
        """
        Train the anomaly detector.

        Args:
            data: DataFrame with 'value' column

        Returns:
            self
        """
        if data.empty or 'value' not in data.columns:
            raise ValueError("Data must have 'value' column")

        # Extract features
        X = self.preprocessor.fit_transform(data)

        if len(X) < 10:
            raise ValueError("Need at least 10 samples for training")

        # Store statistics for zscore
        self.mean = data['value'].mean()
        self.std = data['value'].std()

        # Train model
        if self.algorithm != "zscore":
            self._create_model()
            self.model.fit(X)

        self.trained = True
        return self

    def predict(self, value: float, history: list = None) -> Tuple[float, str]:
        """
        Predict anomaly score for a single value.

        Args:
            value: Sensor measurement value
            history: List of recent historical values

        Returns:
            Tuple of (anomaly_score, label)
            - score: 0.0 (normal) to 1.0 (anomaly)
            - label: 'normal', 'warning', or 'anomaly'
        """
        if not self.trained:
            raise RuntimeError("Model not trained. Call fit() first.")

        if self.algorithm == "zscore":
            score = zscore_anomaly_score(value, self.mean, self.std)
        else:
            # Extract features
            features = self.preprocessor.extract_single_features(value, history)

            if self.preprocessor.fitted:
                features = self.preprocessor.scaler.transform(features)

            # Get prediction
            # Isolation Forest / One-Class SVM return -1 for outliers, 1 for inliers
            prediction = self.model.predict(features)[0]

            # Get anomaly score (decision function)
            if hasattr(self.model, 'decision_function'):
                raw_score = self.model.decision_function(features)[0]
                # Convert to 0-1 range (more negative = more anomalous)
                score = max(0, min(1, -raw_score / 0.5 + 0.5))
            else:
                score = 0.0 if prediction == 1 else 1.0

        # Determine label
        if score >= 0.7:
            label = "anomaly"
        elif score >= 0.5:
            label = "warning"
        else:
            label = "normal"

        return score, label

    def predict_batch(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Predict anomaly scores for batch data.

        Args:
            data: DataFrame with 'value' column

        Returns:
            DataFrame with added 'anomaly_score' and 'anomaly_label' columns
        """
        if not self.trained:
            raise RuntimeError("Model not trained. Call fit() first.")

        result = data.copy()
        scores = []
        labels = []

        values = data['value'].tolist()
        for i, value in enumerate(values):
            history = values[max(0, i-10):i]
            score, label = self.predict(value, history)
            scores.append(score)
            labels.append(label)

        result['anomaly_score'] = scores
        result['anomaly_label'] = labels

        return result

    def save(self, filepath: str):
        """Save model to file"""
        state = {
            'algorithm': self.algorithm,
            'model': self.model,
            'preprocessor': self.preprocessor,
            'mean': self.mean,
            'std': self.std,
            'trained': self.trained,
            'params': self.params
        }
        joblib.dump(state, filepath)
        print(f"Model saved to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> 'AnomalyDetector':
        """Load model from file"""
        state = joblib.load(filepath)
        detector = cls(algorithm=state['algorithm'])
        detector.model = state['model']
        detector.preprocessor = state['preprocessor']
        detector.mean = state['mean']
        detector.std = state['std']
        detector.trained = state['trained']
        detector.params = state['params']
        print(f"Model loaded from {filepath}")
        return detector

    def get_info(self) -> Dict[str, Any]:
        """Get model info"""
        return {
            'algorithm': self.algorithm,
            'trained': self.trained,
            'mean': self.mean,
            'std': self.std,
            'params': self.params.get(self.algorithm, {})
        }


if __name__ == "__main__":
    # Test with sample data
    np.random.seed(42)

    # Generate sample data
    normal_data = np.random.normal(loc=2.5, scale=0.5, size=100)
    anomaly_data = np.array([5.2, 6.0, 7.5])  # Anomalies
    all_data = np.concatenate([normal_data, anomaly_data])

    df = pd.DataFrame({'value': all_data})

    # Train
    detector = AnomalyDetector(algorithm="isolation_forest")
    detector.fit(df)

    print("Model Info:", detector.get_info())

    # Predict
    test_values = [2.5, 3.0, 5.5, 7.0]
    for v in test_values:
        score, label = detector.predict(v)
        print(f"Value: {v:.1f} -> Score: {score:.3f}, Label: {label}")

    # Save and load
    detector.save("models/test_model.joblib")
    loaded = AnomalyDetector.load("models/test_model.joblib")
    score, label = loaded.predict(5.5)
    print(f"Loaded model test: Value 5.5 -> Score: {score:.3f}, Label: {label}")
