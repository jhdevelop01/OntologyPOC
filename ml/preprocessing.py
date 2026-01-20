"""Preprocessing utilities for anomaly detection"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


class SensorDataPreprocessor:
    """Preprocess sensor data for ML"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.fitted = False

    def fit(self, df: pd.DataFrame) -> 'SensorDataPreprocessor':
        """Fit the preprocessor on training data"""
        features = self.extract_features(df)
        if not features.empty:
            self.scaler.fit(features)
            self.fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transform data using fitted scaler"""
        features = self.extract_features(df)
        if features.empty:
            return np.array([])
        if self.fitted:
            return self.scaler.transform(features)
        return features.values

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        """Fit and transform"""
        self.fit(df)
        return self.transform(df)

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract features from sensor data"""
        if df.empty or 'value' not in df.columns:
            return pd.DataFrame()

        features = pd.DataFrame()

        # Basic features
        features['value'] = df['value'].astype(float)

        # Statistical features (if enough data)
        if len(df) >= 3:
            features['rolling_mean'] = df['value'].rolling(window=3, min_periods=1).mean()
            features['rolling_std'] = df['value'].rolling(window=3, min_periods=1).std().fillna(0)

            # Rate of change
            features['rate_of_change'] = df['value'].diff().fillna(0)

            # Deviation from mean
            mean_val = df['value'].mean()
            features['deviation_from_mean'] = df['value'] - mean_val

        return features.dropna()

    def extract_single_features(self, value: float,
                                history: list = None) -> np.ndarray:
        """Extract features for a single observation"""
        if history is None:
            history = []

        all_values = history + [value]

        features = [value]

        if len(all_values) >= 3:
            # Rolling mean
            features.append(np.mean(all_values[-3:]))
            # Rolling std
            features.append(np.std(all_values[-3:]))
            # Rate of change
            features.append(value - all_values[-2] if len(all_values) > 1 else 0)
            # Deviation from mean
            features.append(value - np.mean(all_values))
        else:
            features.extend([value, 0, 0, 0])

        return np.array(features).reshape(1, -1)


def calculate_zscore(value: float, mean: float, std: float) -> float:
    """Calculate Z-score for anomaly detection"""
    if std == 0:
        return 0
    return abs(value - mean) / std


def zscore_anomaly_score(value: float, mean: float, std: float,
                         threshold: float = 3.0) -> float:
    """Calculate anomaly score based on Z-score (0-1 range)"""
    z = calculate_zscore(value, mean, std)
    # Normalize to 0-1 range using sigmoid-like function
    score = min(z / threshold, 1.0)
    return score
