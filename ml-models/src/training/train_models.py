"""
Main Training Script for IBS ML Models

This script orchestrates the training of all ML models including severity classifier,
flare-up predictor, and recommendation engine.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
import joblib
from typing import Dict, Any, Optional

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from models.ibs_severity_classifier import IBSSeverityClassifier
from models.flareup_predictor import FlareupPredictor
from models.recommendation_engine import RecommendationEngine
from training.data_preparation import DataPreparator
from training.evaluation import ModelEvaluator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Main trainer class that orchestrates the training of all IBS ML models.
    """
    
    def __init__(self, output_dir: str = "trained_models"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.data_preparator = DataPreparator()
        self.evaluator = ModelEvaluator()
        
        # Initialize models
        self.severity_classifier = IBSSeverityClassifier()
        self.flareup_predictor = FlareupPredictor()
        self.recommendation_engine = RecommendationEngine()
        
        self.training_results = {}
        
    def train_all_models(self, data: pd.DataFrame = None, use_synthetic_data: bool = False, 
                        db_connection=None, n_synthetic_users: int = 500) -> Dict[str, Any]:
        """
        Train all IBS models with enhanced features including microbiome and psychological insights.
        
        Args:
            data: Pre-prepared training data (if provided, use_synthetic_data is ignored)
            use_synthetic_data: Whether to generate synthetic data
            db_connection: Database connection for real data
            n_synthetic_users: Number of synthetic users to generate
            
        Returns:
            Dictionary containing training results and model performance metrics
        """
        logger.info("Starting comprehensive model training with enhanced features...")
        
        # Step 1: Prepare enhanced training data
        logger.info("Preparing enhanced training data with microbiome and psychological features...")
        if data is not None:
            # Use provided data
            training_data = data
        elif use_synthetic_data:
            training_data = self.data_preparator.create_synthetic_data(n_users=n_synthetic_users)
            training_data = self.data_preparator.prepare_training_data(training_data)
        else:
            # Load real data from database
            if db_connection is None:
                from training.database import get_database_connection
                db = get_database_connection()
                db_connection = db.get_connection()
            
            raw_data = self.data_preparator.load_data_from_db(db_connection)
            training_data = self.data_preparator.prepare_training_data(raw_data)
            
        # Validate data quality
        quality_metrics = self.data_preparator.validate_data_quality(training_data)
        logger.info(f"Data quality validation: {len(training_data)} records, "
                   f"{len(training_data.columns)} features")
        
        # Split data with stratification for better representation
        train_data, val_data, test_data = self.data_preparator.split_data(
            training_data, test_size=0.2, validation_size=0.1
        )
        
        logger.info(f"Data split - Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")
        
        # Step 2: Train models with enhanced features
        logger.info("Training severity classifier with microbiome and psychological features...")
        severity_results = self._train_severity_classifier_enhanced(train_data, val_data, test_data)
        
        logger.info("Training flare-up predictor with temporal and composite features...")
        flareup_results = self._train_flareup_predictor_enhanced(train_data, val_data, test_data)
        
        logger.info("Training recommendation engine with personalized sensitivity profiles...")
        recommendation_results = self._train_recommendation_engine_enhanced(train_data, val_data, test_data)
        
        # Step 3: Enhanced model evaluation
        logger.info("Performing comprehensive model evaluation...")
        evaluation_results = self.evaluator.evaluate_all_models(
            {
                'severity_classifier': self.severity_classifier,
                'flareup_predictor': self.flareup_predictor,
                'recommendation_engine': self.recommendation_engine
            },
            test_data
        )
        
        # Step 4: Feature importance analysis
        feature_importance = self._analyze_feature_importance(train_data)
        
        # Step 5: Save models and comprehensive results
        self._save_all_models()
        self._save_training_results({
            'severity_classifier': severity_results,
            'flareup_predictor': flareup_results,
            'recommendation_engine': recommendation_results,
            'evaluation': evaluation_results,
            'feature_importance': feature_importance,
            'data_quality': quality_metrics,
            'data_info': {
                'n_samples': len(training_data),
                'n_features': len(training_data.columns),
                'train_size': len(train_data),
                'val_size': len(val_data),
                'test_size': len(test_data),
                'enhanced_features': [
                    'microbiome_diversity', 'beneficial_bacteria_pct', 'pathogenic_bacteria_pct',
                    'anxiety_score', 'depression_score', 'psychological_distress',
                    'dietary_sensitivity_score', 'microbiome_health_score'
                ]
            }
        })
        
        logger.info("Enhanced model training completed successfully!")
        logger.info(f"Key improvements: Microbiome features, psychological profiling, "
                   f"temporal patterns, and personalized sensitivity analysis")
        
        return self.training_results
        
    def _train_severity_classifier_enhanced(self, train_data: pd.DataFrame, 
                                          val_data: pd.DataFrame, 
                                          test_data: pd.DataFrame) -> Dict[str, Any]:
        """Train the IBS severity classifier with enhanced microbiome and psychological features."""
        try:
            # Enhanced training with new features
            results = self.severity_classifier.train(train_data)
            
            # Validate on validation set with enhanced metrics
            val_predictions = []
            val_confidences = []
            
            for _, row in val_data.iterrows():
                pred = self.severity_classifier.predict_severity(row.to_dict())
                val_predictions.append(pred)
                val_confidences.append(pred.get('confidence', 0.5))
                
            # Calculate enhanced validation metrics
            results['validation_accuracy'] = sum(
                1 for i, pred in enumerate(val_predictions) 
                if abs(pred['severity_score'] - val_data.iloc[i]['severity_score']) < 1
            ) / len(val_predictions)
            
            results['validation_confidence'] = np.mean(val_confidences)
            
            # Feature importance for microbiome and psychological features
            if hasattr(self.severity_classifier, 'get_feature_importance'):
                feature_importance = self.severity_classifier.get_feature_importance()
                results['microbiome_feature_importance'] = {
                    k: v for k, v in feature_importance.items() 
                    if any(term in k.lower() for term in ['microbiome', 'bacteria', 'diversity'])
                }
                results['psychological_feature_importance'] = {
                    k: v for k, v in feature_importance.items() 
                    if any(term in k.lower() for term in ['anxiety', 'depression', 'stress', 'psychological'])
                }
            
            logger.info(f"Enhanced severity classifier training completed. "
                       f"Accuracy: {results.get('accuracy', 'N/A')}, "
                       f"Validation Confidence: {results.get('validation_confidence', 'N/A'):.3f}")
            return results
            
        except Exception as e:
            logger.error(f"Error training enhanced severity classifier: {e}")
            return {'error': str(e)}
            
    def _train_flareup_predictor_enhanced(self, train_data: pd.DataFrame, 
                                        val_data: pd.DataFrame, 
                                        test_data: pd.DataFrame) -> Dict[str, Any]:
        """Train the flare-up predictor with enhanced temporal and composite features."""
        try:
            # Enhanced training with temporal patterns and composite features
            results = self.flareup_predictor.train(train_data)
            
            # Validate on validation set with enhanced metrics
            val_predictions = []
            val_risk_scores = []
            
            for _, row in val_data.iterrows():
                pred = self.flareup_predictor.predict_flareup_risk(row.to_dict())
                val_predictions.append(pred)
                val_risk_scores.append(pred.get('risk_score', 0.5))
                
            results['validation_auc'] = self._calculate_validation_auc(val_predictions, val_data)
            results['validation_risk_distribution'] = {
                'mean': np.mean(val_risk_scores),
                'std': np.std(val_risk_scores),
                'high_risk_percentage': sum(1 for score in val_risk_scores if score > 0.7) / len(val_risk_scores)
            }
            
            # Analyze temporal feature importance
            if hasattr(self.flareup_predictor, 'get_feature_importance'):
                feature_importance = self.flareup_predictor.get_feature_importance()
                results['temporal_feature_importance'] = {
                    k: v for k, v in feature_importance.items() 
                    if any(term in k.lower() for term in ['rolling', 'lag', 'trend', 'temporal'])
                }
            
            logger.info(f"Enhanced flare-up predictor training completed. "
                       f"ROC-AUC: {results.get('roc_auc', 'N/A')}, "
                       f"Validation AUC: {results.get('validation_auc', 'N/A'):.3f}")
            return results
            
        except Exception as e:
            logger.error(f"Error training enhanced flare-up predictor: {e}")
            return {'error': str(e)}
            
    def _train_recommendation_engine_enhanced(self, train_data: pd.DataFrame, 
                                            val_data: pd.DataFrame, 
                                            test_data: pd.DataFrame) -> Dict[str, Any]:
        """Train the recommendation engine with personalized sensitivity profiles."""
        try:
            # Enhanced training with personalized sensitivity analysis
            results = self.recommendation_engine.train(train_data)
            
            # Validate on validation set with personalized metrics
            val_recommendations = []
            personalization_scores = []
            
            for _, row in val_data.iterrows():
                rec = self.recommendation_engine.generate_recommendations(row.to_dict())
                val_recommendations.append(rec)
                
                # Calculate personalization score based on user-specific features
                user_features = ['fodmap_sensitivity', 'gluten_sensitivity', 'lactose_sensitivity', 
                               'microbiome_diversity', 'anxiety_score', 'depression_score']
                personalization_score = sum(1 for feature in user_features if feature in rec.get('factors', []))
                personalization_scores.append(personalization_score / len(user_features))
                
            results['validation_recommendations'] = len(val_recommendations)
            results['personalization_score'] = np.mean(personalization_scores)
            
            # Analyze recommendation diversity and coverage
            all_recommendations = [rec.get('recommendations', []) for rec in val_recommendations]
            unique_recommendations = set()
            for rec_list in all_recommendations:
                unique_recommendations.update(rec_list)
                
            results['recommendation_diversity'] = len(unique_recommendations)
            results['average_recommendations_per_user'] = np.mean([len(rec) for rec in all_recommendations])
            
            logger.info(f"Enhanced recommendation engine training completed. "
                       f"R²: {results.get('diet_model_r2', 'N/A')}, "
                       f"Personalization Score: {results.get('personalization_score', 'N/A'):.3f}")
            return results
            
        except Exception as e:
            logger.error(f"Error training enhanced recommendation engine: {e}")
            return {'error': str(e)}
            
    def _analyze_feature_importance(self, train_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze feature importance across all models to understand key predictors."""
        try:
            feature_analysis = {
                'microbiome_features': {},
                'psychological_features': {},
                'temporal_features': {},
                'dietary_features': {},
                'top_predictors': {}
            }
            
            # Analyze features by category
            microbiome_cols = [col for col in train_data.columns 
                             if any(term in col.lower() for term in ['microbiome', 'bacteria', 'diversity'])]
            psychological_cols = [col for col in train_data.columns 
                                if any(term in col.lower() for term in ['anxiety', 'depression', 'stress', 'psychological'])]
            temporal_cols = [col for col in train_data.columns 
                           if any(term in col.lower() for term in ['rolling', 'lag', 'trend', 'temporal'])]
            dietary_cols = [col for col in train_data.columns 
                          if any(term in col.lower() for term in ['fodmap', 'gluten', 'lactose', 'dietary'])]
            
            # Calculate feature statistics
            for category, cols in [
                ('microbiome_features', microbiome_cols),
                ('psychological_features', psychological_cols),
                ('temporal_features', temporal_cols),
                ('dietary_features', dietary_cols)
            ]:
                if cols:
                    feature_analysis[category] = {
                        'count': len(cols),
                        'correlation_with_severity': train_data[cols + ['severity_score']].corr()['severity_score'].drop('severity_score').to_dict(),
                        'variance': train_data[cols].var().to_dict()
                    }
            
            logger.info(f"Feature importance analysis completed: "
                       f"{len(microbiome_cols)} microbiome, {len(psychological_cols)} psychological, "
                       f"{len(temporal_cols)} temporal, {len(dietary_cols)} dietary features")
            
            return feature_analysis
            
        except Exception as e:
            logger.error(f"Error in feature importance analysis: {e}")
            return {'error': str(e)}

    def _calculate_validation_auc(self, predictions: list, val_data: pd.DataFrame) -> float:
        """Calculate AUC for validation predictions."""
        try:
            from sklearn.metrics import roc_auc_score
            
            # Create binary labels for flare-ups (severity >= 7)
            y_true = (val_data['severity_score'] >= 7).astype(int)
            y_pred = [pred['flareup_probability'] for pred in predictions]
            
            return roc_auc_score(y_true, y_pred)
        except Exception as e:
            logger.warning(f"Could not calculate validation AUC: {e}")
            return 0.0
            
    def _save_all_models(self):
        """Save all trained models to disk."""
        models = {
            'severity_classifier': self.severity_classifier,
            'flareup_predictor': self.flareup_predictor,
            'recommendation_engine': self.recommendation_engine
        }
        
        for model_name, model in models.items():
            try:
                model_path = self.output_dir / f"{model_name}.joblib"
                model.save_model(str(model_path))
                logger.info(f"Saved {model_name} to {model_path}")
            except Exception as e:
                logger.error(f"Error saving {model_name}: {e}")
                
        # Save data preprocessors
        try:
            preprocessor_path = self.output_dir / "preprocessors.joblib"
            self.data_preparator.save_preprocessors(str(preprocessor_path))
            logger.info(f"Saved preprocessors to {preprocessor_path}")
        except Exception as e:
            logger.error(f"Error saving preprocessors: {e}")
            
    def _save_training_results(self, results: Dict[str, Any]):
        """Save training results and metadata."""
        self.training_results = results
        self.training_results['training_timestamp'] = datetime.now().isoformat()
        
        results_path = self.output_dir / "training_results.json"
        
        try:
            import json
            with open(results_path, 'w') as f:
                # Convert numpy types to native Python types for JSON serialization
                json_results = self._convert_numpy_types(results)
                json.dump(json_results, f, indent=2, default=str)
            logger.info(f"Saved training results to {results_path}")
        except Exception as e:
            logger.error(f"Error saving training results: {e}")
            
    def _convert_numpy_types(self, obj):
        """Convert numpy types to native Python types for JSON serialization."""
        import numpy as np
        
        if isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
            
    def load_trained_models(self, model_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Load previously trained models.
        
        Args:
            model_dir: Directory containing trained models (defaults to self.output_dir)
            
        Returns:
            Dictionary of loaded models
        """
        if model_dir is None:
            model_dir = self.output_dir
        else:
            model_dir = Path(model_dir)
            
        models = {}
        
        # Load individual models
        model_files = {
            'severity_classifier': 'severity_classifier.joblib',
            'flareup_predictor': 'flareup_predictor.joblib',
            'recommendation_engine': 'recommendation_engine.joblib'
        }
        
        for model_name, filename in model_files.items():
            model_path = model_dir / filename
            if model_path.exists():
                try:
                    if model_name == 'severity_classifier':
                        model = IBSSeverityClassifier()
                    elif model_name == 'flareup_predictor':
                        model = FlareupPredictor()
                    elif model_name == 'recommendation_engine':
                        model = RecommendationEngine()
                        
                    model.load_model(str(model_path))
                    models[model_name] = model
                    logger.info(f"Loaded {model_name} from {model_path}")
                except Exception as e:
                    logger.error(f"Error loading {model_name}: {e}")
            else:
                logger.warning(f"Model file not found: {model_path}")
                
        # Load preprocessors
        preprocessor_path = model_dir / "preprocessors.joblib"
        if preprocessor_path.exists():
            try:
                self.data_preparator.load_preprocessors(str(preprocessor_path))
                logger.info(f"Loaded preprocessors from {preprocessor_path}")
            except Exception as e:
                logger.error(f"Error loading preprocessors: {e}")
                
        return models
        
    def quick_test(self) -> Dict[str, Any]:
        """
        Quick test of all models with minimal synthetic data.
        
        Returns:
            Test results
        """
        logger.info("Running quick test with minimal data...")
        
        # Generate minimal synthetic data
        raw_data = self.data_preparator.create_synthetic_data(n_users=10, days_per_user=30)
        training_data = self.data_preparator.prepare_training_data(raw_data)
        
        # Train models with minimal data
        results = {}
        
        try:
            results['severity_classifier'] = self.severity_classifier.train(training_data)
            results['flareup_predictor'] = self.flareup_predictor.train(training_data)
            results['recommendation_engine'] = self.recommendation_engine.train(training_data)
            
            # Test predictions
            sample_features = training_data.iloc[0].to_dict()
            
            results['test_predictions'] = {
                'severity': self.severity_classifier.predict_severity(sample_features),
                'flareup': self.flareup_predictor.predict_flareup_risk(sample_features),
                'recommendations': self.recommendation_engine.generate_recommendations(sample_features)
            }
            
            logger.info("Quick test completed successfully!")
            
        except Exception as e:
            logger.error(f"Error in quick test: {e}")
            results['error'] = str(e)
            
        return results


def main():
    """Main training function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train IBS ML Models')
    parser.add_argument('--output-dir', default='trained_models', 
                       help='Directory to save trained models')
    parser.add_argument('--n-users', type=int, default=500,
                       help='Number of synthetic users to generate')
    parser.add_argument('--quick-test', action='store_true',
                       help='Run quick test with minimal data')
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = ModelTrainer(output_dir=args.output_dir)
    
    if args.quick_test:
        results = trainer.quick_test()
    else:
        results = trainer.train_all_models(
            use_synthetic_data=True,
            n_synthetic_users=args.n_users
        )
    
    print("\nTraining Results Summary:")
    print("=" * 50)
    for model_name, model_results in results.items():
        if isinstance(model_results, dict) and 'error' not in model_results:
            print(f"\n{model_name.replace('_', ' ').title()}:")
            for key, value in model_results.items():
                if isinstance(value, (int, float)):
                    print(f"  {key}: {value:.4f}")
                elif isinstance(value, str):
                    print(f"  {key}: {value}")
                    
    return results


if __name__ == "__main__":
    main()