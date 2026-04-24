#!/usr/bin/env python3
"""
Train and Save Models Script

This script trains all IBS ML models and saves them to the checkpoints directory
with proper versioning and metadata.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from models.ibs_severity_classifier import IBSSeverityClassifier
from models.flareup_predictor import FlareupPredictor
from models.recommendation_engine import RecommendationEngine

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_training_data():
    """Load the training data."""
    logger.info("📊 Loading training data...")
    
    data_dir = Path(__file__).parent.parent.parent / "data"
    
    # Load training data
    train_data = pd.read_csv(data_dir / "train_data.csv")
    val_data = pd.read_csv(data_dir / "val_data.csv")
    test_data = pd.read_csv(data_dir / "test_data.csv")
    
    logger.info(f"   📊 Train data: {train_data.shape}")
    logger.info(f"   📊 Validation data: {val_data.shape}")
    logger.info(f"   📊 Test data: {test_data.shape}")
    
    return train_data, val_data, test_data


def create_checkpoint_dir():
    """Create checkpoints directory with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    checkpoint_dir = Path(__file__).parent / "checkpoints" / f"models_{timestamp}"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📁 Created checkpoint directory: {checkpoint_dir}")
    return checkpoint_dir


def train_severity_classifier(train_data, val_data, checkpoint_dir):
    """Train and save the severity classifier."""
    logger.info("🎯 Training Severity Classifier...")
    
    classifier = IBSSeverityClassifier()
    
    # Create severity labels from severity_score using 5 categories
    train_data_copy = train_data.copy()
    def categorize_severity(score):
        if score <= 2:
            return 'none'
        elif score <= 4:
            return 'mild'
        elif score <= 6:
            return 'moderate'
        elif score <= 8:
            return 'severe'
        else:
            return 'very_severe'
    
    train_data_copy['severity_label'] = train_data_copy['severity_score'].apply(categorize_severity)
    
    # Train the model
    results = classifier.train(train_data_copy, target_column='severity_label')
    
    # Save the model
    model_path = checkpoint_dir / "severity_classifier.pkl"
    classifier.save_model(str(model_path))
    
    logger.info(f"   ✅ Severity classifier saved to {model_path}")
    logger.info(f"   📈 Training accuracy: {results.get('accuracy', 'N/A')}")
    
    return {
        'model_type': 'severity_classifier',
        'model_path': str(model_path),
        'accuracy': results.get('accuracy'),
        'training_samples': len(train_data_copy)
    }


def train_flareup_predictor(train_data, val_data, checkpoint_dir):
    """Train and save the flareup predictor."""
    logger.info("🔮 Training Flareup Predictor...")
    
    predictor = FlareupPredictor()
    
    # Create binary flareup target
    train_data_copy = train_data.copy()
    train_data_copy['flareup'] = (train_data_copy['severity_score'] > 6).astype(int)
    
    # Train the model
    results = predictor.train(train_data_copy, prediction_window_hours=24)
    
    # Save the model
    model_path = checkpoint_dir / "flareup_predictor.pkl"
    predictor.save_model(str(model_path))
    
    logger.info(f"   ✅ Flareup predictor saved to {model_path}")
    logger.info(f"   📈 ROC-AUC: {results.get('roc_auc', 'N/A')}")
    
    return {
        'model_type': 'flareup_predictor',
        'model_path': str(model_path),
        'roc_auc': results.get('roc_auc'),
        'training_samples': len(train_data_copy)
    }


def train_recommendation_engine(train_data, val_data, checkpoint_dir):
    """Train and save the recommendation engine."""
    logger.info("💡 Training Recommendation Engine...")
    
    engine = RecommendationEngine()
    
    # Train the model
    results = engine.train(train_data)
    
    # Save the model
    model_path = checkpoint_dir / "recommendation_engine.pkl"
    engine.save_model(str(model_path))
    
    logger.info(f"   ✅ Recommendation engine saved to {model_path}")
    logger.info(f"   📈 Diet R²: {results.get('diet_r2', 'N/A')}")
    logger.info(f"   📈 Lifestyle R²: {results.get('lifestyle_r2', 'N/A')}")
    
    return {
        'model_type': 'recommendation_engine',
        'model_path': str(model_path),
        'diet_r2': results.get('diet_r2'),
        'lifestyle_r2': results.get('lifestyle_r2'),
        'training_samples': len(train_data)
    }


def save_training_metadata(checkpoint_dir, model_results):
    """Save training metadata and results."""
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'training_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'models': model_results,
        'total_models': len(model_results),
        'python_version': sys.version,
        'training_status': 'completed'
    }
    
    metadata_path = checkpoint_dir / "training_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"📋 Training metadata saved to {metadata_path}")
    
    # Also create a latest symlink
    latest_dir = Path(__file__).parent / "checkpoints" / "latest"
    if latest_dir.exists() or latest_dir.is_symlink():
        latest_dir.unlink()
    latest_dir.symlink_to(checkpoint_dir.name)
    
    logger.info(f"🔗 Created 'latest' symlink pointing to {checkpoint_dir.name}")


def main():
    """Main training function."""
    logger.info("🚀 Starting ML model training and saving process...")
    
    try:
        # Load data
        train_data, val_data, test_data = load_training_data()
        
        # Create checkpoint directory
        checkpoint_dir = create_checkpoint_dir()
        
        # Train and save all models
        model_results = []
        
        # Train severity classifier
        severity_results = train_severity_classifier(train_data, val_data, checkpoint_dir)
        model_results.append(severity_results)
        
        # Train flareup predictor
        flareup_results = train_flareup_predictor(train_data, val_data, checkpoint_dir)
        model_results.append(flareup_results)
        
        # Train recommendation engine
        recommendation_results = train_recommendation_engine(train_data, val_data, checkpoint_dir)
        model_results.append(recommendation_results)
        
        # Save metadata
        save_training_metadata(checkpoint_dir, model_results)
        
        logger.info("=" * 50)
        logger.info("🎉 Training completed successfully!")
        logger.info(f"📁 Models saved to: {checkpoint_dir}")
        logger.info(f"📊 Total models trained: {len(model_results)}")
        logger.info("=" * 50)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)