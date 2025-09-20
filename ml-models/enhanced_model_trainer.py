"""
Enhanced Model Trainer for IBS Prediction with External Data Integration

This module provides an improved training pipeline that incorporates external
datasets and advanced feature engineering to create more accurate IBS prediction
models and personalized dietary recommendations.
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import joblib

# ML Libraries
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.feature_selection import SelectKBest, f_classif

# Import our data integration pipeline
from data_integration_pipeline import DataIntegrationPipeline

logger = logging.getLogger(__name__)


class EnhancedModelTrainer:
    """
    Enhanced model trainer with external data integration and advanced features.
    
    This trainer incorporates multiple external datasets to improve IBS prediction
    accuracy and provide better personalized dietary recommendations.
    """
    
    def __init__(self, 
                 models_dir: str = "trained_models",
                 features_file: str = "enhanced_training_features.csv"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.features_file = features_file
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.training_history = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        
        # Initialize data pipeline
        self.data_pipeline = DataIntegrationPipeline()
    
    def load_enhanced_features(self) -> pd.DataFrame:
        """Load the enhanced features created by the data integration pipeline."""
        if not os.path.exists(self.features_file):
            logger.info("Enhanced features not found. Running data integration pipeline...")
            datasets = self.data_pipeline.integrate_datasets()
            features_df = self.data_pipeline.create_training_features(datasets)
            features_df.to_csv(self.features_file, index=False)
        else:
            features_df = pd.read_csv(self.features_file)
            logger.info(f"Loaded enhanced features from {self.features_file}")
        
        return features_df
    
    def engineer_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create advanced features for improved IBS prediction.
        
        This includes temporal patterns, interaction features, and domain-specific
        engineered features based on IBS research.
        """
        logger.info("Engineering advanced features...")
        
        enhanced_df = df.copy()
        
        # 1. Temporal Pattern Features
        if 'log_date' in enhanced_df.columns:
            enhanced_df['log_date'] = pd.to_datetime(enhanced_df['log_date'])
            
            # Seasonal patterns
            enhanced_df['season'] = enhanced_df['log_date'].dt.month % 12 // 3 + 1
            enhanced_df['is_winter'] = (enhanced_df['season'] == 1).astype(int)
            enhanced_df['is_spring'] = (enhanced_df['season'] == 2).astype(int)
            enhanced_df['is_summer'] = (enhanced_df['season'] == 3).astype(int)
            enhanced_df['is_fall'] = (enhanced_df['season'] == 4).astype(int)
            
            # Weekly patterns
            enhanced_df['is_monday'] = (enhanced_df['day_of_week'] == 0).astype(int)
            enhanced_df['is_friday'] = (enhanced_df['day_of_week'] == 4).astype(int)
        
        # 2. Stress and Sleep Quality Interactions
        if all(col in enhanced_df.columns for col in ['stress_level', 'sleep_score']):
            enhanced_df['stress_sleep_ratio'] = enhanced_df['stress_level'] / (enhanced_df['sleep_score'] + 1)
            enhanced_df['wellness_index'] = (enhanced_df['sleep_score'] - enhanced_df['stress_level']) / 10
            enhanced_df['high_stress_poor_sleep'] = ((enhanced_df['stress_level'] > 7) & 
                                                   (enhanced_df['sleep_score'] < 5)).astype(int)
        
        # 3. FODMAP-based Features
        if 'fodmap_load_score' in enhanced_df.columns:
            enhanced_df['fodmap_severity_interaction'] = (enhanced_df['fodmap_load_score'] * 
                                                        enhanced_df.get('ibs_severity_score', 1))
            enhanced_df['high_fodmap_day'] = (enhanced_df['fodmap_load_score'] > 6).astype(int)
        
        # 4. Nutritional Balance Features
        if all(col in enhanced_df.columns for col in ['daily_fiber_estimate', 'daily_calories_estimate']):
            enhanced_df['fiber_per_1000_cal'] = (enhanced_df['daily_fiber_estimate'] * 1000) / enhanced_df['daily_calories_estimate']
            enhanced_df['adequate_fiber'] = (enhanced_df['daily_fiber_estimate'] >= 25).astype(int)
        
        # 5. Symptom Severity Categories
        if 'ibs_severity_score' in enhanced_df.columns:
            enhanced_df['severity_category'] = pd.cut(
                enhanced_df['ibs_severity_score'],
                bins=[0, 3, 6, 10],
                labels=['Mild', 'Moderate', 'Severe']
            )
            
            # Binary classification for severe symptoms
            enhanced_df['severe_symptoms'] = (enhanced_df['ibs_severity_score'] > 6).astype(int)
        
        # 6. Rolling Statistics for Trend Analysis
        if 'ibs_severity_score' in enhanced_df.columns:
            enhanced_df['severity_trend_3day'] = enhanced_df['ibs_severity_score'].rolling(window=3, min_periods=1).mean()
            enhanced_df['severity_volatility_7day'] = enhanced_df['ibs_severity_score'].rolling(window=7, min_periods=1).std()
            enhanced_df['improving_trend'] = (enhanced_df['severity_trend_3day'] < enhanced_df['severity_7day_avg']).astype(int)
        
        # 7. Composite Health Scores
        if all(col in enhanced_df.columns for col in ['stress_level', 'sleep_score', 'fodmap_load_score']):
            # Overall wellness score (higher is better)
            enhanced_df['wellness_composite'] = (
                (10 - enhanced_df['stress_level']) * 0.3 +
                enhanced_df['sleep_score'] * 0.3 +
                (10 - enhanced_df['fodmap_load_score']) * 0.4
            )
            
            # Risk score for IBS flare-up (higher is worse)
            enhanced_df['flare_risk_score'] = (
                enhanced_df['stress_level'] * 0.25 +
                (10 - enhanced_df['sleep_score']) * 0.25 +
                enhanced_df['fodmap_load_score'] * 0.5
            )
        
        logger.info(f"Advanced feature engineering completed. Features: {len(enhanced_df.columns)}")
        return enhanced_df
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare data for training by selecting features and target variable.
        
        Returns features (X) and target (y) for model training.
        """
        logger.info("Preparing training data...")
        
        # Define target variable
        if 'severe_symptoms' in df.columns:
            target = 'severe_symptoms'
        elif 'ibs_severity_score' in df.columns:
            # Create binary target from severity score
            df['severe_symptoms'] = (df['ibs_severity_score'] > 6).astype(int)
            target = 'severe_symptoms'
        else:
            raise ValueError("No suitable target variable found")
        
        # Select feature columns (exclude target and non-predictive columns)
        exclude_cols = [
            target, 'log_date', 'severity_category', 'ibs_severity_score'
        ]
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Handle categorical variables
        categorical_cols = df[feature_cols].select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
        
        X = df[feature_cols].fillna(0)  # Handle any missing values
        y = df[target]
        
        logger.info(f"Training data prepared: {X.shape[0]} samples, {X.shape[1]} features")
        return X, y
    
    def train_models(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Train multiple ML models with hyperparameter tuning.
        
        Returns training results and model performance metrics.
        """
        logger.info("Training enhanced ML models...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Feature scaling
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers['standard'] = scaler
        
        # Feature selection
        selector = SelectKBest(score_func=f_classif, k=min(15, X_train.shape[1]))
        X_train_selected = selector.fit_transform(X_train_scaled, y_train)
        X_test_selected = selector.transform(X_test_scaled)
        
        self.feature_selectors['kbest'] = selector
        
        # Define models with hyperparameter grids
        model_configs = {
            'random_forest': {
                'model': RandomForestClassifier(random_state=42),
                'params': {
                    'n_estimators': [100, 200],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5],
                    'min_samples_leaf': [1, 2]
                }
            },
            'gradient_boosting': {
                'model': GradientBoostingClassifier(random_state=42),
                'params': {
                    'n_estimators': [100, 200],
                    'learning_rate': [0.05, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                }
            },
            'logistic_regression': {
                'model': LogisticRegression(random_state=42, max_iter=1000),
                'params': {
                    'C': [0.1, 1, 10],
                    'penalty': ['l1', 'l2'],
                    'solver': ['liblinear']
                }
            }
        }
        
        results = {}
        
        for model_name, config in model_configs.items():
            logger.info(f"Training {model_name}...")
            
            # Grid search with cross-validation
            grid_search = GridSearchCV(
                config['model'],
                config['params'],
                cv=5,
                scoring='roc_auc',
                n_jobs=-1
            )
            
            grid_search.fit(X_train_selected, y_train)
            
            # Best model
            best_model = grid_search.best_estimator_
            
            # Predictions
            y_pred = best_model.predict(X_test_selected)
            y_pred_proba = best_model.predict_proba(X_test_selected)[:, 1]
            
            # Metrics
            auc_score = roc_auc_score(y_test, y_pred_proba)
            
            results[model_name] = {
                'model': best_model,
                'best_params': grid_search.best_params_,
                'auc_score': auc_score,
                'classification_report': classification_report(y_test, y_pred, output_dict=True),
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
            }
            
            # Save model
            model_path = self.models_dir / f"{model_name}_enhanced.joblib"
            joblib.dump(best_model, model_path)
            
            self.models[model_name] = best_model
            
            logger.info(f"{model_name} - AUC: {auc_score:.3f}, Best params: {grid_search.best_params_}")
        
        # Save training metadata
        self.training_history = {
            'timestamp': datetime.now().isoformat(),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'features_used': X_train.shape[1],
            'selected_features': X_train_selected.shape[1],
            'feature_names': X.columns.tolist(),
            'selected_feature_indices': selector.get_support(indices=True).tolist(),
            'results': {k: {
                'auc_score': v['auc_score'],
                'best_params': v['best_params']
            } for k, v in results.items()}
        }
        
        return results
    
    def create_personalized_recommendations(self, 
                                          user_features: Dict[str, Any],
                                          model_name: str = 'random_forest') -> Dict[str, Any]:
        """
        Create personalized dietary and lifestyle recommendations based on model predictions.
        
        Args:
            user_features: Dictionary of user's current features
            model_name: Name of the model to use for predictions
            
        Returns:
            Dictionary containing personalized recommendations
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Available models: {list(self.models.keys())}")
        
        model = self.models[model_name]
        scaler = self.scalers['standard']
        selector = self.feature_selectors['kbest']
        
        # Prepare user features
        feature_vector = np.array([list(user_features.values())]).reshape(1, -1)
        feature_vector_scaled = scaler.transform(feature_vector)
        feature_vector_selected = selector.transform(feature_vector_scaled)
        
        # Get prediction and probability
        prediction = model.predict(feature_vector_selected)[0]
        probability = model.predict_proba(feature_vector_selected)[0]
        
        # Generate recommendations based on features and prediction
        recommendations = {
            'risk_assessment': {
                'severe_symptoms_probability': float(probability[1]),
                'risk_level': 'High' if probability[1] > 0.7 else 'Medium' if probability[1] > 0.3 else 'Low'
            },
            'dietary_recommendations': [],
            'lifestyle_recommendations': [],
            'monitoring_suggestions': []
        }
        
        # Dietary recommendations based on FODMAP and nutrition features
        if user_features.get('fodmap_load_score', 0) > 6:
            recommendations['dietary_recommendations'].extend([
                "Consider following a low-FODMAP diet to reduce symptom triggers",
                "Limit high-FODMAP foods like onions, garlic, wheat, and certain fruits",
                "Work with a dietitian to properly implement FODMAP elimination and reintroduction"
            ])
        
        if user_features.get('daily_fiber_estimate', 0) < 25:
            recommendations['dietary_recommendations'].append(
                "Gradually increase fiber intake to 25-35g daily with soluble fiber sources"
            )
        
        # Lifestyle recommendations based on stress and sleep
        if user_features.get('stress_level', 0) > 7:
            recommendations['lifestyle_recommendations'].extend([
                "Practice stress management techniques like meditation or deep breathing",
                "Consider regular exercise to help manage stress levels",
                "Explore stress-reduction activities like yoga or mindfulness"
            ])
        
        if user_features.get('sleep_score', 10) < 6:
            recommendations['lifestyle_recommendations'].extend([
                "Improve sleep hygiene by maintaining consistent sleep schedule",
                "Create a relaxing bedtime routine",
                "Limit screen time before bed and ensure comfortable sleep environment"
            ])
        
        # Monitoring suggestions
        if probability[1] > 0.5:
            recommendations['monitoring_suggestions'].extend([
                "Keep a detailed food and symptom diary",
                "Monitor stress levels and sleep quality daily",
                "Consider consulting with a gastroenterologist",
                "Track bowel movements and symptom patterns"
            ])
        
        return recommendations
    
    def save_training_report(self, results: Dict[str, Any]):
        """Save comprehensive training report."""
        # Create serializable version of results (exclude model objects)
        serializable_results = {}
        for model_name, model_data in results.items():
            serializable_results[model_name] = {
                'auc_score': model_data['auc_score'],
                'best_params': model_data['best_params'],
                'classification_report': model_data['classification_report'],
                'confusion_matrix': model_data['confusion_matrix']
            }
        
        report = {
            'training_metadata': self.training_history,
            'model_performance': serializable_results,
            'feature_importance': {},
            'recommendations_for_improvement': []
        }
        
        # Add feature importance for tree-based models
        for model_name, model_data in results.items():
            if hasattr(model_data['model'], 'feature_importances_'):
                selected_indices = self.feature_selectors['kbest'].get_support(indices=True)
                feature_names = [self.training_history['feature_names'][i] for i in selected_indices]
                
                importance_dict = dict(zip(
                    feature_names,
                    model_data['model'].feature_importances_.tolist()
                ))
                report['feature_importance'][model_name] = importance_dict
        
        # Add improvement recommendations
        best_auc = max(result['auc_score'] for result in results.values())
        if best_auc < 0.8:
            report['recommendations_for_improvement'].append(
                "Consider collecting more training data to improve model performance"
            )
        if best_auc < 0.85:
            report['recommendations_for_improvement'].append(
                "Explore additional feature engineering or external datasets"
            )
        
        # Save report
        report_path = self.models_dir / 'enhanced_training_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Training report saved to {report_path}")


def main():
    """Main function to demonstrate enhanced model training."""
    trainer = EnhancedModelTrainer()
    
    # Load and prepare data
    df = trainer.load_enhanced_features()
    enhanced_df = trainer.engineer_advanced_features(df)
    X, y = trainer.prepare_training_data(enhanced_df)
    
    # Train models
    results = trainer.train_models(X, y)
    
    # Save training report
    trainer.save_training_report(results)
    
    # Demonstrate personalized recommendations
    sample_user = {
        'stress_level': 8,
        'sleep_score': 4,
        'fodmap_load_score': 9,
        'daily_fiber_estimate': 15,
        'is_weekend': 0,
        'wellness_composite': 3.5,
        'flare_risk_score': 7.5
    }
    
    # Add remaining features with default values
    for col in X.columns:
        if col not in sample_user:
            sample_user[col] = 0
    
    recommendations = trainer.create_personalized_recommendations(sample_user)
    
    print("\n" + "="*80)
    print("ENHANCED IBS ML MODEL TRAINING SUMMARY")
    print("="*80)
    print(f"Training samples: {trainer.training_history['training_samples']}")
    print(f"Features engineered: {trainer.training_history['features_used']}")
    print(f"Selected features: {trainer.training_history['selected_features']}")
    print("\nModel Performance (AUC Scores):")
    for model_name, result in results.items():
        print(f"  {model_name}: {result['auc_score']:.3f}")
    
    print(f"\nBest performing model: {max(results.keys(), key=lambda k: results[k]['auc_score'])}")
    
    print("\nSample Personalized Recommendations:")
    print(f"Risk Level: {recommendations['risk_assessment']['risk_level']}")
    print("Dietary Recommendations:")
    for rec in recommendations['dietary_recommendations'][:2]:
        print(f"  • {rec}")
    print("Lifestyle Recommendations:")
    for rec in recommendations['lifestyle_recommendations'][:2]:
        print(f"  • {rec}")
    print("="*80)


if __name__ == "__main__":
    main()