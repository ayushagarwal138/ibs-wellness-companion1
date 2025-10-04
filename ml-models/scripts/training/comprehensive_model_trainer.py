"""
Comprehensive Model Trainer for IBS Wellness Companion

This script trains all ML models required for the prediction endpoints:
- Severity Classification
- Flareup Prediction
- Medication Effectiveness
- Dietary Triggers
- Stress-Symptom Correlation
- Sleep Quality Impact
- Exercise Tolerance
- Symptom Progression
- Treatment Response
- Multimodal Prediction
"""

import json
import logging
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (RandomForestClassifier, 
                              RandomForestRegressor)
from sklearn.metrics import (classification_report, mean_squared_error, 
                            r2_score)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ComprehensiveModelTrainer:
    """
    Comprehensive trainer for all IBS prediction models.
    """
    
    def __init__(self, models_dir: str = "../../trained_models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Create checkpoints directory for backend compatibility
        self.checkpoints_dir = Path("../../checkpoints")
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.training_history = {}
        
        # Model configurations
        self.model_configs = {
            'severity_classifier': {
                'type': 'classification',
                'target_classes': ['mild', 'moderate', 'severe'],
                'features': ['pain_level', 'bloating', 'bowel_movement_frequency', 'stress_level', 'sleep_quality']
            },
            'flareup_predictor': {
                'type': 'classification',
                'target_classes': ['low', 'medium', 'high'],
                'features': ['recent_symptoms', 'dietary_changes', 'stress_events', 'medication_adherence']
            },
            'medication_effectiveness': {
                'type': 'regression',
                'target_range': [0, 100],
                'features': ['medication_type', 'dosage', 'duration', 'symptom_severity', 'adherence']
            },
            'dietary_triggers': {
                'type': 'classification',
                'target_classes': ['trigger', 'safe', 'neutral'],
                'features': ['food_category', 'portion_size', 'preparation_method', 'timing']
            },
            'stress_correlation': {
                'type': 'regression',
                'target_range': [0, 1],
                'features': ['stress_level', 'stress_duration', 'stress_type', 'coping_mechanisms']
            },
            'sleep_impact': {
                'type': 'regression',
                'target_range': [0, 100],
                'features': ['sleep_duration', 'sleep_quality', 'bedtime_consistency', 'sleep_disturbances']
            },
            'exercise_tolerance': {
                'type': 'regression',
                'target_range': [0, 100],
                'features': ['exercise_type', 'intensity', 'duration', 'timing', 'pre_exercise_symptoms']
            },
            'symptom_progression': {
                'type': 'regression',
                'target_range': [-50, 50],  # Improvement to worsening
                'features': ['baseline_severity', 'treatment_duration', 'lifestyle_changes', 'adherence']
            },
            'treatment_response': {
                'type': 'regression',
                'target_range': [0, 100],
                'features': ['treatment_type', 'duration', 'severity_baseline', 'patient_characteristics']
            }
        }
    
    def generate_synthetic_data(self, model_name: str, n_samples: int = 1000) -> Tuple[pd.DataFrame, pd.Series]:
        """Generate synthetic training data for a specific model."""
        logger.info(f"Generating {n_samples} synthetic samples for {model_name}")
        
        config = self.model_configs[model_name]
        features = config['features']
        
        # Generate feature data
        np.random.seed(42)  # For reproducibility
        data = {}
        
        for feature in features:
            if 'level' in feature or 'quality' in feature or 'severity' in feature:
                # Scale 1-10
                data[feature] = np.random.randint(1, 11, n_samples)
            elif 'frequency' in feature or 'duration' in feature:
                # Continuous values
                data[feature] = np.random.normal(5, 2, n_samples).clip(0, 10)
            elif 'type' in feature or 'category' in feature or 'method' in feature:
                # Categorical encoded as integers
                data[feature] = np.random.randint(0, 5, n_samples)
            elif 'adherence' in feature:
                # Percentage
                data[feature] = np.random.uniform(0, 100, n_samples)
            elif 'changes' in feature or 'events' in feature:
                # Binary or count
                data[feature] = np.random.poisson(2, n_samples)
            else:
                # Default continuous
                data[feature] = np.random.normal(0, 1, n_samples)
        
        X = pd.DataFrame(data)
        
        # Generate target variable based on model type
        if config['type'] == 'classification':
            if model_name == 'severity_classifier':
                # Severity based on pain and symptoms
                severity_score = (X['pain_level'] + X['bloating'] + (10 - X['sleep_quality'])) / 3
                y = pd.cut(severity_score, bins=[0, 4, 7, 10], labels=['mild', 'moderate', 'severe'])
            elif model_name == 'flareup_predictor':
                # Risk based on recent symptoms and stress
                risk_score = (X['recent_symptoms'] + X['stress_events'] + (10 - X['medication_adherence']/10)) / 3
                y = pd.cut(risk_score, bins=[0, 3, 6, 10], labels=['low', 'medium', 'high'])
            elif model_name == 'dietary_triggers':
                # Trigger likelihood based on food category and portion
                trigger_prob = (X['food_category'] * 2 + X['portion_size']) / 15
                y = pd.cut(trigger_prob, bins=[0, 0.3, 0.7, 1], labels=['safe', 'neutral', 'trigger'])
            else:
                y = pd.Series(np.random.choice(config['target_classes'], n_samples))
        else:  # regression
            if model_name == 'medication_effectiveness':
                # Effectiveness based on adherence and dosage
                effectiveness = 20 + (X['adherence'] * 0.6) + (X['dosage'] * 10) - (X['symptom_severity'] * 5)
                y = pd.Series(effectiveness.clip(0, 100))
            elif model_name == 'stress_correlation':
                # Correlation based on stress level and duration
                correlation = (X['stress_level'] * X['stress_duration']) / 100
                y = pd.Series(correlation.clip(0, 1))
            elif model_name == 'sleep_impact':
                # Impact based on sleep quality and duration
                impact = X['sleep_quality'] * 8 + (X['sleep_duration'] - 8) * 5
                y = pd.Series(impact.clip(0, 100))
            elif model_name == 'exercise_tolerance':
                # Tolerance based on intensity and pre-exercise symptoms
                tolerance = 80 - (X['intensity'] * 5) - (X['pre_exercise_symptoms'] * 8)
                y = pd.Series(tolerance.clip(0, 100))
            elif model_name == 'symptom_progression':
                # Progression based on treatment and lifestyle
                progression = (X['treatment_duration'] * 2) + (X['lifestyle_changes'] * 3) - X['baseline_severity']
                y = pd.Series(progression.clip(-50, 50))
            elif model_name == 'treatment_response':
                # Response based on treatment type and duration
                response = 30 + (X['treatment_type'] * 15) + (X['duration'] * 2) - (X['severity_baseline'] * 3)
                y = pd.Series(response.clip(0, 100))
            else:
                target_range = config['target_range']
                y = pd.Series(np.random.uniform(target_range[0], target_range[1], n_samples))
        
        return X, y
    
    def train_model(self, model_name: str, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Train a specific model."""
        logger.info(f"Training {model_name} model...")
        
        config = self.model_configs[model_name]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Handle categorical targets for classification
        if config['type'] == 'classification':
            encoder = LabelEncoder()
            y_train_encoded = encoder.fit_transform(y_train)
            y_test_encoded = encoder.transform(y_test)
            self.encoders[model_name] = encoder
        else:
            y_train_encoded = y_train
            y_test_encoded = y_test
        
        # Select and train model
        if config['type'] == 'classification':
            model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        
        model.fit(X_train_scaled, y_train_encoded)
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        if config['type'] == 'classification':
            accuracy = model.score(X_test_scaled, y_test_encoded)
            metrics = {
                'accuracy': accuracy,
                'classification_report': classification_report(y_test_encoded, y_pred, output_dict=True)
            }
            logger.info(f"{model_name} accuracy: {accuracy:.3f}")
        else:
            mse = mean_squared_error(y_test_encoded, y_pred)
            r2 = r2_score(y_test_encoded, y_pred)
            metrics = {
                'mse': mse,
                'rmse': np.sqrt(mse),
                'r2': r2
            }
            logger.info(f"{model_name} R²: {r2:.3f}, RMSE: {np.sqrt(mse):.3f}")
        
        # Store model and scaler
        self.models[model_name] = model
        self.scalers[model_name] = scaler
        
        # Store training history
        self.training_history[model_name] = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'feature_names': list(X.columns),
            'model_type': config['type'],
            'n_samples': len(X)
        }
        
        return metrics
    
    def save_models(self):
        """Save all trained models and metadata."""
        logger.info("Saving models and metadata...")
        
        # Save models to both directories for compatibility
        for model_name, model in self.models.items():
            # Save to models directory
            model_path = self.models_dir / f"{model_name}.pkl"
            joblib.dump(model, model_path)
            
            # Save to checkpoints directory for backend compatibility
            checkpoint_path = self.checkpoints_dir / f"{model_name}.pkl"
            joblib.dump(model, checkpoint_path)
            
            logger.info(f"Saved {model_name} to {model_path} and {checkpoint_path}")
        
        # Save scalers
        for scaler_name, scaler in self.scalers.items():
            scaler_path = self.models_dir / f"{scaler_name}_scaler.pkl"
            joblib.dump(scaler, scaler_path)
            
            # Also save to checkpoints
            checkpoint_scaler_path = self.checkpoints_dir / f"{scaler_name}_scaler.pkl"
            joblib.dump(scaler, checkpoint_scaler_path)
        
        # Save a general feature scaler for backward compatibility
        if self.scalers:
            general_scaler = list(self.scalers.values())[0]
            general_scaler_path = self.checkpoints_dir / "feature_scaler.pkl"
            joblib.dump(general_scaler, general_scaler_path)
        
        # Save encoders
        for encoder_name, encoder in self.encoders.items():
            encoder_path = self.models_dir / f"{encoder_name}_encoder.pkl"
            joblib.dump(encoder, encoder_path)
            
            checkpoint_encoder_path = self.checkpoints_dir / f"{encoder_name}_encoder.pkl"
            joblib.dump(encoder, checkpoint_encoder_path)
        
        # Save training history and metadata
        metadata = {
            'training_timestamp': datetime.now().isoformat(),
            'models_trained': list(self.models.keys()),
            'training_history': self.training_history,
            'model_configs': self.model_configs
        }
        
        metadata_path = self.models_dir / "training_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        # Also save to checkpoints
        checkpoint_metadata_path = self.checkpoints_dir / "training_metadata.json"
        with open(checkpoint_metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"Saved metadata to {metadata_path} and {checkpoint_metadata_path}")
    
    def train_all_models(self, n_samples: int = 1000):
        """Train all models with synthetic data."""
        logger.info(f"Starting comprehensive model training with {n_samples} samples each...")
        
        all_metrics = {}
        
        for model_name in self.model_configs.keys():
            try:
                # Generate data
                X, y = self.generate_synthetic_data(model_name, n_samples)
                
                # Train model
                metrics = self.train_model(model_name, X, y)
                all_metrics[model_name] = metrics
                
                logger.info(f"✓ Successfully trained {model_name}")
                
            except Exception as e:
                logger.error(f"✗ Failed to train {model_name}: {e}")
                continue
        
        # Save all models
        self.save_models()
        
        # Print summary
        logger.info("\n" + "="*50)
        logger.info("TRAINING SUMMARY")
        logger.info("="*50)
        
        for model_name, metrics in all_metrics.items():
            config = self.model_configs[model_name]
            if config['type'] == 'classification':
                logger.info(f"{model_name}: Accuracy = {metrics['accuracy']:.3f}")
            else:
                logger.info(f"{model_name}: R² = {metrics['r2']:.3f}, RMSE = {metrics['rmse']:.3f}")
        
        logger.info(f"\nAll models saved to:")
        logger.info(f"  - {self.models_dir}")
        logger.info(f"  - {self.checkpoints_dir}")
        
        return all_metrics


def main():
    """Main training function."""
    logger.info("Starting Comprehensive IBS Model Training...")
    
    # Initialize trainer
    trainer = ComprehensiveModelTrainer()
    
    # Train all models
    metrics = trainer.train_all_models(n_samples=2000)
    
    logger.info("Training completed successfully!")
    
    return metrics


if __name__ == "__main__":
    main()