"""
IBS Severity Classification Model

This model predicts IBS severity levels based on user symptoms, diet, and lifestyle factors.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class IBSSeverityClassifier:
    """
    Machine learning model for classifying IBS severity levels.
    
    Predicts severity categories: none, mild, moderate, severe, very_severe
    based on symptom patterns, dietary factors, and lifestyle indicators.
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.is_trained = False
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for training or prediction.
        
        Args:
            data: Raw data with symptom logs, diet logs, etc.
            
        Returns:
            Processed feature DataFrame
        """
        features = pd.DataFrame()
        
        # Symptom-based features
        features['avg_pain_severity'] = data.groupby('user_id')['pain_severity'].mean()
        features['symptom_frequency'] = data.groupby('user_id')['id'].count()  # Use 'id' instead of 'symptom_id'
        features['bowel_movement_irregularity'] = data.groupby('user_id')['bowel_movement_type_encoded'].std()  # Use encoded version
        features['stress_level_avg'] = data.groupby('user_id')['stress_level'].mean()
        features['sleep_quality_avg'] = data.groupby('user_id')['sleep_quality'].mean()
        
        # Diet-based features
        features['high_fodmap_frequency'] = data[data['fodmap_level'] == 'high'].groupby('user_id').size()
        features['trigger_food_reactions'] = data[data['avg_reaction_severity'] > 5].groupby('user_id').size()  # Use avg_reaction_severity
        features['meal_irregularity'] = data.groupby('user_id')['meal_timing_std'].mean()  # Use meal_timing_std
        
        # Lifestyle features
        features['exercise_frequency'] = data.groupby('user_id')['exercise_minutes'].count()
        features['medication_adherence'] = data.groupby('user_id')['medication_adherence_rate'].mean()  # Use medication_adherence_rate
        
        # Temporal features
        features['symptom_duration_avg'] = data.groupby('user_id')['severity_score'].mean()  # Use severity_score as proxy
        features['flareup_frequency'] = data[data['severity_score'] >= 3].groupby('user_id').size()  # Use severity_score
        
        # Fill missing values
        features = features.fillna(0)
        
        self.feature_names = list(features.columns)
        return features
        
    def train(self, training_data: pd.DataFrame, target_column: str = 'severity_label') -> Dict[str, Any]:
        """
        Train the IBS severity classification model.
        
        Args:
            training_data: DataFrame with features and target labels
            target_column: Name of the target column
            
        Returns:
            Training metrics and results
        """
        logger.info("Starting IBS severity classifier training...")
        
        # Prepare features
        X = self.prepare_features(training_data)
        y = training_data.groupby('user_id')[target_column].first()
        
        # Align indices
        common_indices = X.index.intersection(y.index)
        X = X.loc[common_indices]
        y = y.loc[common_indices]
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Get feature importance
        feature_importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        self.is_trained = True
        
        # Get all possible labels for classification report
        all_labels = list(range(len(self.label_encoder.classes_)))
        
        results = {
            'accuracy': accuracy,
            'feature_importance': feature_importance,
            'classification_report': classification_report(
                y_test, y_pred, 
                labels=all_labels,
                target_names=self.label_encoder.classes_,
                output_dict=True,
                zero_division=0
            ),
            'n_samples': len(X),
            'n_features': len(self.feature_names)
        }
        
        logger.info(f"Training completed. Accuracy: {accuracy:.3f}")
        return results
        
    def predict(self, user_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict IBS severity for a user.
        
        Args:
            user_features: Dictionary of user features
            
        Returns:
            Prediction results with confidence scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
            
        # Convert to DataFrame
        feature_df = pd.DataFrame([user_features])
        
        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in feature_df.columns:
                feature_df[feature] = 0
                
        # Reorder columns to match training
        feature_df = feature_df[self.feature_names]
        
        # Scale features
        features_scaled = self.scaler.transform(feature_df)
        
        # Make prediction
        prediction_encoded = self.model.predict(features_scaled)[0]
        prediction_proba = self.model.predict_proba(features_scaled)[0]
        
        # Decode prediction
        severity_label = self.label_encoder.inverse_transform([prediction_encoded])[0]
        
        # Get confidence scores for all classes
        confidence_scores = dict(zip(
            self.label_encoder.classes_,
            prediction_proba
        ))
        
        return {
            'predicted_severity': severity_label,
            'confidence': float(prediction_proba.max()),
            'confidence_scores': confidence_scores,
            'risk_factors': self._identify_risk_factors(user_features)
        }
        
    def _identify_risk_factors(self, features: Dict[str, Any]) -> List[str]:
        """Identify key risk factors contributing to severity prediction."""
        risk_factors = []
        
        if features.get('avg_pain_severity', 0) > 6:
            risk_factors.append("High average pain severity")
            
        if features.get('high_fodmap_frequency', 0) > 10:
            risk_factors.append("Frequent high-FODMAP food consumption")
            
        if features.get('stress_level_avg', 0) > 7:
            risk_factors.append("Elevated stress levels")
            
        if features.get('sleep_quality_avg', 0) < 4:
            risk_factors.append("Poor sleep quality")
            
        if features.get('trigger_food_reactions', 0) > 5:
            risk_factors.append("Frequent food reactions")
            
        return risk_factors
        
    def save_model(self, filepath: str):
        """Save the trained model to disk."""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
            
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
        
    def load_model(self, filepath: str):
        """Load a trained model from disk."""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Model loaded from {filepath}")
        
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        if not self.is_trained:
            raise ValueError("Model must be trained to get feature importance")
            
        return dict(zip(self.feature_names, self.model.feature_importances_))