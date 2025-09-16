"""
Size Estimation Module
Machine learning-based clothing size prediction from body measurements
"""

import numpy as np
import pandas as pd
import pickle
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
from typing import Dict, List, Tuple, Optional
import logging
import os

logger = logging.getLogger(__name__)

class SizeEstimator:
    """
    Machine learning-based size estimation from body measurements.
    """
    
    def __init__(self, model_path: Optional[str] = None, scaler_path: Optional[str] = None):
        """
        Initialize size estimator.
        
        Args:
            model_path: Path to trained model file
            scaler_path: Path to feature scaler file
        """
        
        self.model = None
        self.scaler = None
        self.feature_names = [
            'shoulder_width',
            'chest_width', 
            'waist_width',
            'hip_width',
            'torso_length',
            'arm_length'
        ]
        
        self.size_mapping = {
            0: 'XS',
            1: 'S',
            2: 'M', 
            3: 'L',
            4: 'XL',
            5: 'XXL'
        }
        
        self.reverse_size_mapping = {v: k for k, v in self.size_mapping.items()}
        
        # Load pre-trained model if available
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
            
        if scaler_path and os.path.exists(scaler_path):
            self.load_scaler(scaler_path)
    
    def normalize_measurements(self, measurements: Dict, reference_height: float = 170.0) -> Dict:
        """
        Normalize measurements to standard height.
        
        Args:
            measurements: Raw pixel measurements
            reference_height: Reference height in cm
            
        Returns:
            Normalized measurements
        """
        
        # Estimate person height from pose landmarks (approximate)
        estimated_height_px = measurements.get('torso_length', 100) * 3.5  # Rough estimation
        
        # Calculate normalization factor
        if estimated_height_px > 0:
            height_factor = reference_height / (estimated_height_px * 0.1)  # Convert to cm scale
        else:
            height_factor = 1.0
        
        normalized = {}
        for key, value in measurements.items():
            if isinstance(value, (int, float)):
                normalized[key] = value * height_factor
            else:
                normalized[key] = value
                
        return normalized
    
    def extract_features(self, measurements: Dict) -> np.ndarray:
        """
        Extract feature vector from measurements.
        
        Args:
            measurements: Body measurements dictionary
            
        Returns:
            Feature vector as numpy array
        """
        
        features = []
        
        for feature_name in self.feature_names:
            if feature_name in measurements:
                features.append(measurements[feature_name])
            else:
                # Use default/estimated values for missing measurements
                if feature_name == 'chest_width':
                    # Estimate chest width as 1.1 * shoulder width
                    chest = measurements.get('shoulder_width', 0) * 1.1
                    features.append(chest)
                elif feature_name == 'waist_width':
                    # Estimate waist width as 0.75 * shoulder width
                    waist = measurements.get('shoulder_width', 0) * 0.75
                    features.append(waist)
                else:
                    features.append(0.0)
        
        return np.array(features).reshape(1, -1)
    
    def predict_size(self, measurements: Dict, confidence_threshold: float = 0.7) -> Dict:
        """
        Predict clothing size from measurements.
        
        Args:
            measurements: Body measurements
            confidence_threshold: Minimum confidence for prediction
            
        Returns:
            Dictionary with predicted size and confidence
        """
        
        if self.model is None:
            logger.warning("No model loaded. Using rule-based estimation.")
            return self._rule_based_prediction(measurements)
        
        try:
            # Normalize measurements
            normalized_measurements = self.normalize_measurements(measurements)
            
            # Extract features
            features = self.extract_features(normalized_measurements)
            
            # Scale features if scaler is available
            if self.scaler:
                features = self.scaler.transform(features)
            
            # Predict
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(features)[0]
                predicted_class = np.argmax(probabilities)
                confidence = probabilities[predicted_class]
            else:
                predicted_class = self.model.predict(features)[0]
                confidence = 1.0  # XGBoost doesn't provide probabilities by default
            
            predicted_size = self.size_mapping[predicted_class]
            
            # Check confidence threshold
            if confidence < confidence_threshold:
                logger.warning(f"Low confidence prediction: {confidence:.2f}")
            
            return {
                'predicted_size': predicted_size,
                'confidence': float(confidence),
                'all_probabilities': probabilities.tolist() if hasattr(self.model, 'predict_proba') else None,
                'measurements_used': normalized_measurements
            }
            
        except Exception as e:
            logger.error(f"Error in size prediction: {e}")
            return self._rule_based_prediction(measurements)
    
    def _rule_based_prediction(self, measurements: Dict) -> Dict:
        """
        Fallback rule-based size prediction.
        
        Args:
            measurements: Body measurements
            
        Returns:
            Dictionary with predicted size
        """
        
        shoulder_width = measurements.get('shoulder_width', 0)
        
        # Simple rule-based classification based on shoulder width
        if shoulder_width < 35:
            size = 'XS'
        elif shoulder_width < 40:
            size = 'S'
        elif shoulder_width < 45:
            size = 'M'
        elif shoulder_width < 50:
            size = 'L'
        elif shoulder_width < 55:
            size = 'XL'
        else:
            size = 'XXL'
        
        return {
            'predicted_size': size,
            'confidence': 0.5,
            'method': 'rule_based',
            'measurements_used': measurements
        }
    
    def train_model(self, training_data: pd.DataFrame, model_type: str = 'xgboost') -> Dict:
        """
        Train size estimation model.
        
        Args:
            training_data: DataFrame with measurements and size labels
            model_type: Type of model to train ('xgboost', 'random_forest')
            
        Returns:
            Training results
        """
        
        # Prepare features and labels
        X = training_data[self.feature_names].fillna(0)
        y = training_data['size'].map(self.reverse_size_mapping)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        if model_type == 'xgboost':
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            self.model.fit(X_train_scaled, y_train)
            
        elif model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.model.fit(X_train_scaled, y_train)
            
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        results = {
            'accuracy': accuracy,
            'model_type': model_type,
            'feature_importance': self._get_feature_importance(),
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
        
        logger.info(f"Model trained with accuracy: {accuracy:.3f}")
        
        return results
    
    def _get_feature_importance(self) -> Dict:
        """Get feature importance from trained model."""
        
        if self.model is None:
            return {}
        
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            importance = np.abs(self.model.coef_[0])
        else:
            return {}
        
        return dict(zip(self.feature_names, importance.tolist()))
    
    def save_model(self, model_path: str, scaler_path: str = None):
        """
        Save trained model and scaler.
        
        Args:
            model_path: Path to save model
            scaler_path: Path to save scaler
        """
        
        if self.model:
            joblib.dump(self.model, model_path)
            logger.info(f"Model saved to {model_path}")
        
        if self.scaler and scaler_path:
            joblib.dump(self.scaler, scaler_path)
            logger.info(f"Scaler saved to {scaler_path}")
    
    def load_model(self, model_path: str):
        """Load trained model."""
        
        try:
            self.model = joblib.load(model_path)
            logger.info(f"Model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def load_scaler(self, scaler_path: str):
        """Load feature scaler."""
        
        try:
            self.scaler = joblib.load(scaler_path)
            logger.info(f"Scaler loaded from {scaler_path}")
        except Exception as e:
            logger.error(f"Error loading scaler: {e}")

def generate_synthetic_data(n_samples: int = 1000) -> pd.DataFrame:
    """
    Generate synthetic training data for size estimation.
    
    Args:
        n_samples: Number of samples to generate
        
    Returns:
        DataFrame with synthetic measurements and sizes
    """
    
    np.random.seed(42)
    
    data = []
    
    # Size distributions (approximate)
    size_stats = {
        'XS': {'shoulder': (30, 35), 'chest': (32, 37), 'waist': (24, 28), 'hip': (34, 38)},
        'S':  {'shoulder': (35, 40), 'chest': (37, 42), 'waist': (28, 32), 'hip': (38, 42)},
        'M':  {'shoulder': (40, 45), 'chest': (42, 47), 'waist': (32, 36), 'hip': (42, 46)},
        'L':  {'shoulder': (45, 50), 'chest': (47, 52), 'waist': (36, 40), 'hip': (46, 50)},
        'XL': {'shoulder': (50, 55), 'chest': (52, 57), 'waist': (40, 44), 'hip': (50, 54)},
        'XXL':{'shoulder': (55, 60), 'chest': (57, 62), 'waist': (44, 48), 'hip': (54, 58)}
    }
    
    for _ in range(n_samples):
        # Random size
        size = np.random.choice(list(size_stats.keys()))
        stats = size_stats[size]
        
        # Generate measurements with some correlation
        shoulder_width = np.random.uniform(*stats['shoulder'])
        chest_width = np.random.uniform(*stats['chest'])
        waist_width = np.random.uniform(*stats['waist'])
        hip_width = np.random.uniform(*stats['hip'])
        
        # Correlated measurements
        torso_length = shoulder_width * np.random.uniform(1.8, 2.2)
        arm_length = shoulder_width * np.random.uniform(1.4, 1.8)
        
        data.append({
            'shoulder_width': shoulder_width,
            'chest_width': chest_width,
            'waist_width': waist_width,
            'hip_width': hip_width,
            'torso_length': torso_length,
            'arm_length': arm_length,
            'size': size
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Example usage
    
    # Generate synthetic training data
    training_data = generate_synthetic_data(1000)
    print("Generated synthetic training data")
    print(training_data.head())
    
    # Train model
    estimator = SizeEstimator()
    results = estimator.train_model(training_data, model_type='xgboost')
    print(f"Training completed with accuracy: {results['accuracy']:.3f}")
    
    # Test prediction
    test_measurements = {
        'shoulder_width': 42,
        'chest_width': 44,
        'waist_width': 34,
        'hip_width': 44,
        'torso_length': 85,
        'arm_length': 65
    }
    
    prediction = estimator.predict_size(test_measurements)
    print(f"Predicted size: {prediction['predicted_size']} (confidence: {prediction['confidence']:.2f})")
