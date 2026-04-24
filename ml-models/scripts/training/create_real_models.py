#!/usr/bin/env python3
"""
Create Real ML Models Script

This script creates synthetic training data and trains real ML models
to replace the fallback implementations in the IBS wellness companion.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
import joblib
import logging
import json
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_synthetic_training_data(n_samples=5000):
    """Create synthetic training data for IBS prediction models."""
    logger.info(f"Creating synthetic training data with {n_samples} samples...")
    
    np.random.seed(42)  # For reproducibility
    
    # Generate user features
    data = {
        # Demographics
        'age': np.random.normal(35, 12, n_samples).clip(18, 80),
        'gender': np.random.choice([0, 1, 2], n_samples, p=[0.4, 0.55, 0.05]),  # 0=M, 1=F, 2=Other
        'bmi': np.random.normal(25, 4, n_samples).clip(16, 45),
        
        # Symptoms (0-10 scale)
        'abdominal_pain': np.random.exponential(2, n_samples).clip(0, 10),
        'bloating': np.random.exponential(2.5, n_samples).clip(0, 10),
        'diarrhea': np.random.exponential(1.8, n_samples).clip(0, 10),
        'constipation': np.random.exponential(1.5, n_samples).clip(0, 10),
        'gas': np.random.exponential(2.2, n_samples).clip(0, 10),
        
        # Lifestyle factors
        'stress_level': np.random.exponential(2, n_samples).clip(0, 10),
        'sleep_quality': 10 - np.random.exponential(2, n_samples).clip(0, 10),
        'exercise_frequency': np.random.poisson(3, n_samples).clip(0, 7),
        'water_intake': np.random.normal(2.5, 0.8, n_samples).clip(0.5, 5),
        
        # Dietary factors
        'fiber_intake': np.random.normal(25, 8, n_samples).clip(5, 50),
        'processed_food_freq': np.random.exponential(2, n_samples).clip(0, 10),
        'dairy_intake': np.random.exponential(1.5, n_samples).clip(0, 10),
        'spicy_food_freq': np.random.exponential(1.8, n_samples).clip(0, 10),
        
        # Medical history
        'medication_adherence': np.random.beta(8, 2, n_samples),
        'previous_flareups': np.random.poisson(2, n_samples).clip(0, 20),
        'family_history': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
    }
    
    df = pd.DataFrame(data)
    
    # Ensure no NaN values
    df = df.fillna(0)
    
    # Create target variables based on realistic relationships
    
    # 1. Severity Score (0-10)
    severity_factors = (
        0.3 * df['abdominal_pain'] +
        0.25 * df['bloating'] +
        0.2 * df['diarrhea'] +
        0.15 * df['constipation'] +
        0.1 * df['gas'] +
        0.2 * df['stress_level'] +
        -0.1 * df['sleep_quality'] +
        0.1 * df['processed_food_freq']
    )
    df['severity_score'] = (severity_factors + np.random.normal(0, 0.5, n_samples)).clip(0, 10)
    
    # 2. Flareup Risk (0-1) - make it more balanced
    flareup_factors = (
        0.25 * (df['severity_score'] / 10) +
        0.2 * (df['stress_level'] / 10) +
        0.15 * (df['processed_food_freq'] / 10) +
        0.1 * (df['previous_flareups'] / 20) +
        -0.1 * (df['sleep_quality'] / 10) +
        -0.05 * (df['medication_adherence']) +
        0.3  # Add baseline to make it more balanced
    )
    df['flareup_risk'] = (flareup_factors + np.random.normal(0, 0.2, n_samples)).clip(0, 1)
    
    # 3. Severity Categories
    severity_cats = pd.cut(df['severity_score'], 
                          bins=[0, 2, 4, 6, 8, 10], 
                          labels=['none', 'mild', 'moderate', 'severe', 'very_severe'])
    df['severity_category'] = severity_cats.astype(str)
    
    # 4. Flareup Binary - use a lower threshold for more balance
    df['will_flareup'] = (df['flareup_risk'] > 0.5).astype(int)
    
    # Final check for any remaining NaN values
    df = df.fillna(0)
    
    logger.info(f"Created synthetic data with shape: {df.shape}")
    logger.info(f"Severity distribution: {df['severity_category'].value_counts().to_dict()}")
    logger.info(f"Flareup distribution: {df['will_flareup'].value_counts().to_dict()}")
    
    return df


def train_severity_classifier(df):
    """Train a severity classification model."""
    logger.info("Training severity classifier...")
    
    # Prepare features
    feature_cols = [col for col in df.columns if col not in ['severity_score', 'severity_category', 'flareup_risk', 'will_flareup']]
    X = df[feature_cols]
    y = df['severity_category']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    logger.info(f"Severity classifier accuracy: {accuracy:.3f}")
    logger.info(f"Classification report:\n{classification_report(y_test, y_pred)}")
    
    return model, feature_cols, accuracy


def train_flareup_predictor(df):
    """Train a flareup prediction model."""
    logger.info("Training flareup predictor...")
    
    # Prepare features
    feature_cols = [col for col in df.columns if col not in ['severity_score', 'severity_category', 'flareup_risk', 'will_flareup']]
    X = df[feature_cols]
    y = df['will_flareup']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=8)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    logger.info(f"Flareup predictor accuracy: {accuracy:.3f}")
    logger.info(f"Classification report:\n{classification_report(y_test, y_pred)}")
    
    return model, feature_cols, accuracy


def train_recommendation_engine(df):
    """Train a recommendation scoring model."""
    logger.info("Training recommendation engine...")
    
    # Create a synthetic recommendation score based on severity and lifestyle factors
    df['recommendation_score'] = (
        0.4 * (10 - df['severity_score']) +  # Lower severity = higher recommendation score
        0.3 * df['sleep_quality'] +
        0.2 * (7 - df['stress_level']) +
        0.1 * df['exercise_frequency']
    ) / 10  # Normalize to 0-1
    
    # Prepare features
    feature_cols = [col for col in df.columns if col not in ['severity_score', 'severity_category', 'flareup_risk', 'will_flareup', 'recommendation_score']]
    X = df[feature_cols]
    y = df['recommendation_score']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=8)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    
    logger.info(f"Recommendation engine MSE: {mse:.3f}")
    
    return model, feature_cols, mse


def save_models_and_metadata(models_info, output_dir):
    """Save trained models and metadata."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save models
    for model_name, info in models_info.items():
        model_path = output_dir / f"{model_name}.pkl"
        joblib.dump(info['model'], model_path)
        logger.info(f"Saved {model_name} to {model_path}")
    
    # Save feature scaler (create a simple one)
    scaler = StandardScaler()
    # Fit on dummy data with the right number of features
    dummy_data = np.random.randn(100, len(models_info['severity_classifier']['features']))
    scaler.fit(dummy_data)
    scaler_path = output_dir / "feature_scaler.pkl"
    joblib.dump(scaler, scaler_path)
    logger.info(f"Saved feature scaler to {scaler_path}")
    
    # Save metadata
    metadata = {
        "created_at": datetime.now().isoformat(),
        "model_versions": {name: "1.0" for name in models_info.keys()},
        "feature_columns": {name: info['features'] for name, info in models_info.items()},
        "performance_metrics": {name: info['metric'] for name, info in models_info.items()},
        "training_samples": 5000,
        "model_type": "synthetic_trained"
    }
    
    metadata_path = output_dir / "model_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved metadata to {metadata_path}")


def main():
    """Main training pipeline."""
    logger.info("🚀 Starting real ML model training pipeline...")
    
    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / "checkpoints"
    
    try:
        # 1. Create synthetic training data
        df = create_synthetic_training_data(n_samples=5000)
        
        # 2. Train models
        severity_model, severity_features, severity_acc = train_severity_classifier(df)
        flareup_model, flareup_features, flareup_acc = train_flareup_predictor(df)
        recommendation_model, rec_features, rec_mse = train_recommendation_engine(df)
        
        # 3. Organize model information
        models_info = {
            "severity_classifier": {
                "model": severity_model,
                "features": severity_features,
                "metric": severity_acc
            },
            "flareup_predictor": {
                "model": flareup_model,
                "features": flareup_features,
                "metric": flareup_acc
            },
            "recommendation_engine": {
                "model": recommendation_model,
                "features": rec_features,
                "metric": rec_mse
            }
        }
        
        # 4. Save models and metadata
        save_models_and_metadata(models_info, output_dir)
        
        logger.info("✅ Successfully trained and saved all ML models!")
        logger.info(f"📁 Models saved to: {output_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in training pipeline: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)