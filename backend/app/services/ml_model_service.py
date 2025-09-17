"""
ML Model Service

Service for loading, managing, and using trained ML models for IBS predictions.
This service handles model loading, feature preparation, and predictions.
"""

import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import logging
import os

from sqlalchemy.orm import Session
import joblib

from app.models.user import User
from app.models.symptom import SymptomLog
from app.models.diet import DietLog
from app.models.medication import MedicationLog

logger = logging.getLogger(__name__)


class MLModelService:
    """Service for managing and using trained ML models."""
    
    def __init__(self):
        self.models_path = Path(__file__).parent.parent.parent.parent / "ml-models"
        self.checkpoints_path = self.models_path / "checkpoints"
        self.models = {}
        self.model_metadata = {}
        self._load_latest_models()
    
    def _load_latest_models(self):
        """Load the latest trained models from checkpoints directory."""
        try:
            # Find the latest checkpoint directory
            latest_checkpoint = self._get_latest_checkpoint()
            if not latest_checkpoint:
                logger.warning("No model checkpoints found")
                return
            
            checkpoint_path = self.checkpoints_path / latest_checkpoint
            logger.info(f"Loading models from checkpoint: {latest_checkpoint}")
            
            # Load metadata
            metadata_path = checkpoint_path / "training_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
                logger.info(f"Loaded model metadata: {self.model_metadata.get('training_date', 'Unknown date')}")
            
            # Load individual models
            self._load_severity_classifier(checkpoint_path)
            self._load_flareup_predictor(checkpoint_path)
            self._load_recommendation_engine(checkpoint_path)
            
        except Exception as e:
            logger.error(f"Error loading ML models: {e}")
            self._initialize_fallback_models()
    
    def _get_latest_checkpoint(self) -> Optional[str]:
        """Get the name of the latest checkpoint directory."""
        if not self.checkpoints_path.exists():
            return None
        
        # Look for 'latest' symlink first
        latest_link = self.checkpoints_path / "latest"
        if latest_link.exists() and latest_link.is_symlink():
            return latest_link.readlink().name
        
        # Otherwise, find the most recent directory
        checkpoint_dirs = [d for d in self.checkpoints_path.iterdir() 
                          if d.is_dir() and d.name.startswith('models_')]
        if not checkpoint_dirs:
            return None
        
        # Sort by modification time and return the latest
        latest_dir = max(checkpoint_dirs, key=lambda d: d.stat().st_mtime)
        return latest_dir.name
    
    def _load_severity_classifier(self, checkpoint_path: Path):
        """Load the severity classifier model."""
        model_path = checkpoint_path / "severity_classifier.pkl"
        if model_path.exists():
            try:
                self.models['severity_classifier'] = joblib.load(model_path)
                logger.info("Loaded severity classifier model")
            except Exception as e:
                logger.error(f"Error loading severity classifier: {e}")
    
    def _load_flareup_predictor(self, checkpoint_path: Path):
        """Load the flareup predictor model."""
        model_path = checkpoint_path / "flareup_predictor.pkl"
        if model_path.exists():
            try:
                self.models['flareup_predictor'] = joblib.load(model_path)
                logger.info("Loaded flareup predictor model")
            except Exception as e:
                logger.error(f"Error loading flareup predictor: {e}")
    
    def _load_recommendation_engine(self, checkpoint_path: Path):
        """Load the recommendation engine model."""
        model_path = checkpoint_path / "recommendation_engine.pkl"
        if model_path.exists():
            try:
                self.models['recommendation_engine'] = joblib.load(model_path)
                logger.info("Loaded recommendation engine model")
            except Exception as e:
                logger.error(f"Error loading recommendation engine: {e}")
    
    def _initialize_fallback_models(self):
        """Initialize simple fallback models if trained models aren't available."""
        logger.warning("Initializing fallback models - trained models not available")
        # Fallback models would be implemented here if needed
        pass
    
    def predict_severity(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict IBS severity based on user data.
        
        Args:
            user_data: Dictionary containing user features
            
        Returns:
            Dictionary with severity prediction and confidence
        """
        if 'severity_classifier' not in self.models:
            return self._fallback_severity_prediction(user_data)
        
        try:
            # Prepare features for the model
            features = self._prepare_severity_features(user_data)
            
            # Make prediction
            model = self.models['severity_classifier']
            prediction = model.predict([features])[0]
            
            # Get prediction probabilities if available
            confidence = 0.5
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba([features])[0]
                confidence = float(np.max(probabilities))
            
            return {
                'severity_score': float(prediction),
                'severity_level': self._score_to_severity_level(prediction),
                'confidence': confidence,
                'model_version': self.model_metadata.get('model_versions', {}).get('severity_classifier', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Error in severity prediction: {e}")
            return self._fallback_severity_prediction(user_data)
    
    def predict_flareup_risk(self, user_data: Dict[str, Any], days_ahead: int = 7) -> Dict[str, Any]:
        """
        Predict flareup risk for the next N days.
        
        Args:
            user_data: Dictionary containing user features
            days_ahead: Number of days to predict ahead
            
        Returns:
            Dictionary with flareup risk prediction
        """
        if 'flareup_predictor' not in self.models:
            return self._fallback_flareup_prediction(user_data)
        
        try:
            # Prepare features for the model
            features = self._prepare_flareup_features(user_data)
            
            # Make prediction
            model = self.models['flareup_predictor']
            
            # Get risk probability
            if hasattr(model, 'predict_proba'):
                risk_prob = model.predict_proba([features])[0][1]  # Probability of positive class
            else:
                risk_score = model.predict([features])[0]
                risk_prob = min(max(risk_score, 0.0), 1.0)  # Clamp to [0, 1]
            
            return {
                'risk_score': float(risk_prob),
                'risk_level': self._score_to_risk_level(risk_prob),
                'days_ahead': days_ahead,
                'confidence': float(risk_prob) if risk_prob > 0.5 else float(1 - risk_prob),
                'model_version': self.model_metadata.get('model_versions', {}).get('flareup_predictor', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Error in flareup prediction: {e}")
            return self._fallback_flareup_prediction(user_data)
    
    def generate_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized recommendations.
        
        Args:
            user_data: Dictionary containing user features
            
        Returns:
            Dictionary with diet and lifestyle recommendations
        """
        if 'recommendation_engine' not in self.models:
            return self._fallback_recommendations(user_data)
        
        try:
            # Prepare features for the model
            features = self._prepare_recommendation_features(user_data)
            
            # Make predictions
            model = self.models['recommendation_engine']
            
            # The recommendation engine returns diet and lifestyle scores
            predictions = model.predict([features])[0]
            
            # Assuming the model returns [diet_score, lifestyle_score]
            if len(predictions) >= 2:
                diet_score = float(predictions[0])
                lifestyle_score = float(predictions[1])
            else:
                diet_score = float(predictions[0])
                lifestyle_score = 0.5
            
            return {
                'diet_recommendations': self._generate_diet_recommendations(diet_score, user_data),
                'lifestyle_recommendations': self._generate_lifestyle_recommendations(lifestyle_score, user_data),
                'diet_score': diet_score,
                'lifestyle_score': lifestyle_score,
                'model_version': self.model_metadata.get('model_versions', {}).get('recommendation_engine', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Error in recommendation generation: {e}")
            return self._fallback_recommendations(user_data)
    
    def _prepare_severity_features(self, user_data: Dict[str, Any]) -> List[float]:
        """Prepare features for severity classification."""
        features = []
        
        # Add symptom features
        symptoms = user_data.get('symptoms', {})
        features.extend([
            symptoms.get('abdominal_pain', 0),
            symptoms.get('bloating', 0),
            symptoms.get('gas', 0),
            symptoms.get('diarrhea', 0),
            symptoms.get('constipation', 0),
            symptoms.get('urgency', 0),
            symptoms.get('incomplete_evacuation', 0),
            symptoms.get('nausea', 0),
            symptoms.get('fatigue', 0),
            symptoms.get('mood_score', 5),
            symptoms.get('stress_level', 5),
            symptoms.get('sleep_quality', 5)
        ])
        
        # Add user profile features
        profile = user_data.get('profile', {})
        features.extend([
            profile.get('age', 30),
            1 if profile.get('gender') == 'female' else 0,
            profile.get('bmi', 25.0),
            profile.get('years_since_diagnosis', 1)
        ])
        
        return features
    
    def _prepare_flareup_features(self, user_data: Dict[str, Any]) -> List[float]:
        """Prepare features for flareup prediction."""
        # Similar to severity features but may include additional temporal features
        features = self._prepare_severity_features(user_data)
        
        # Add recent symptom trends
        recent_symptoms = user_data.get('recent_symptoms', {})
        features.extend([
            recent_symptoms.get('avg_severity_7d', 0),
            recent_symptoms.get('symptom_frequency_7d', 0),
            recent_symptoms.get('stress_trend', 0)
        ])
        
        return features
    
    def _prepare_recommendation_features(self, user_data: Dict[str, Any]) -> List[float]:
        """Prepare features for recommendation generation."""
        # Use severity features as base
        features = self._prepare_severity_features(user_data)
        
        # Add dietary features
        diet = user_data.get('diet', {})
        features.extend([
            diet.get('fodmap_adherence', 0.5),
            diet.get('fiber_intake', 25.0),
            diet.get('trigger_food_frequency', 0.1)
        ])
        
        return features
    
    def _score_to_severity_level(self, score: float) -> str:
        """Convert severity score to level."""
        if score < 0.25:
            return 'none'
        elif score < 0.5:
            return 'mild'
        elif score < 0.75:
            return 'moderate'
        else:
            return 'severe'
    
    def _score_to_risk_level(self, score: float) -> str:
        """Convert risk score to level."""
        if score < 0.3:
            return 'low'
        elif score < 0.6:
            return 'moderate'
        else:
            return 'high'
    
    def _generate_diet_recommendations(self, score: float, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate diet recommendations based on score."""
        recommendations = []
        
        if score > 0.7:
            recommendations.append({
                'category': 'FODMAP Management',
                'recommendation': 'Consider following a strict low FODMAP diet for 2-6 weeks',
                'priority': 'high',
                'rationale': 'Your symptoms suggest high sensitivity to FODMAP foods'
            })
        
        if score > 0.5:
            recommendations.append({
                'category': 'Fiber Intake',
                'recommendation': 'Gradually increase soluble fiber intake to improve symptoms',
                'priority': 'medium',
                'rationale': 'Soluble fiber can help regulate bowel movements and reduce symptoms'
            })
        
        return recommendations
    
    def _generate_lifestyle_recommendations(self, score: float, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate lifestyle recommendations based on score."""
        recommendations = []
        
        stress_level = user_data.get('symptoms', {}).get('stress_level', 5)
        
        if stress_level > 6:
            recommendations.append({
                'category': 'Stress Management',
                'recommendation': 'Practice stress reduction techniques like meditation or yoga',
                'priority': 'high',
                'rationale': f'Your stress level ({stress_level}/10) is elevated, which can worsen IBS symptoms'
            })
        
        if score > 0.6:
            recommendations.append({
                'category': 'Exercise',
                'recommendation': 'Engage in regular, moderate exercise to improve gut health',
                'priority': 'medium',
                'rationale': 'Regular exercise can help regulate digestion and reduce IBS symptoms'
            })
        
        return recommendations
    
    def _fallback_severity_prediction(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback severity prediction when model is not available."""
        symptoms = user_data.get('symptoms', {})
        avg_severity = np.mean([
            symptoms.get('abdominal_pain', 0),
            symptoms.get('bloating', 0),
            symptoms.get('diarrhea', 0),
            symptoms.get('constipation', 0)
        ])
        
        return {
            'severity_score': float(avg_severity / 3.0),  # Normalize to 0-1
            'severity_level': self._score_to_severity_level(avg_severity / 3.0),
            'confidence': 0.5,
            'model_version': 'fallback'
        }
    
    def _fallback_flareup_prediction(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback flareup prediction when model is not available."""
        symptoms = user_data.get('symptoms', {})
        stress_level = symptoms.get('stress_level', 5)
        
        # Simple heuristic: higher stress = higher flareup risk
        risk_score = min(stress_level / 10.0, 1.0)
        
        return {
            'risk_score': risk_score,
            'risk_level': self._score_to_risk_level(risk_score),
            'days_ahead': 7,
            'confidence': 0.5,
            'model_version': 'fallback'
        }
    
    def _fallback_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback recommendations when model is not available."""
        return {
            'diet_recommendations': [
                {
                    'category': 'Food Tracking',
                    'recommendation': 'Keep a food diary to identify trigger foods',
                    'priority': 'medium',
                    'rationale': 'Identifying personal trigger foods is essential for managing IBS symptoms'
                }
            ],
            'lifestyle_recommendations': [
                {
                    'category': 'Stress Management',
                    'recommendation': 'Practice stress reduction techniques',
                    'priority': 'medium',
                    'rationale': 'Stress is a common trigger for IBS symptoms and should be managed'
                }
            ],
            'diet_score': 0.5,
            'lifestyle_score': 0.5,
            'model_version': 'fallback'
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models."""
        return {
            'loaded_models': list(self.models.keys()),
            'metadata': self.model_metadata,
            'models_path': str(self.models_path),
            'checkpoint_path': str(self.checkpoints_path)
        }
    
    def reload_models(self):
        """Reload models from the latest checkpoint."""
        self.models.clear()
        self.model_metadata.clear()
        self._load_latest_models()
        logger.info("Models reloaded successfully")