"""
Model Evaluation Module

Provides comprehensive evaluation metrics and validation for IBS ML models.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, mean_squared_error, mean_absolute_error,
    classification_report, confusion_matrix
)
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Comprehensive evaluation suite for IBS ML models.
    """
    
    def __init__(self):
        self.evaluation_results = {}
        
    def evaluate_all_models(self, models: Dict[str, Any], test_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluate all models comprehensively.
        
        Args:
            models: Dictionary of trained models
            test_data: Test dataset
            
        Returns:
            Comprehensive evaluation results
        """
        logger.info("Starting comprehensive model evaluation...")
        
        results = {}
        
        # Evaluate severity classifier
        if 'severity_classifier' in models:
            results['severity_classifier'] = self.evaluate_severity_classifier(
                models['severity_classifier'], test_data
            )
            
        # Evaluate flare-up predictor
        if 'flareup_predictor' in models:
            results['flareup_predictor'] = self.evaluate_flareup_predictor(
                models['flareup_predictor'], test_data
            )
            
        # Evaluate recommendation engine
        if 'recommendation_engine' in models:
            results['recommendation_engine'] = self.evaluate_recommendation_engine(
                models['recommendation_engine'], test_data
            )
            
        # Cross-model evaluation
        results['cross_model_analysis'] = self.cross_model_evaluation(models, test_data)
        
        self.evaluation_results = results
        logger.info("Model evaluation completed")
        
        return results
        
    def evaluate_severity_classifier(self, model, test_data: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate the severity classifier model."""
        logger.info("Evaluating severity classifier...")
        
        results = {}
        predictions = []
        true_values = []
        
        # Generate predictions
        for _, row in test_data.iterrows():
            try:
                pred = model.predict_severity(row.to_dict())
                predictions.append(pred['severity_score'])
                true_values.append(row['severity_score'])
            except Exception as e:
                logger.warning(f"Prediction error: {e}")
                continue
                
        if not predictions:
            return {'error': 'No valid predictions generated'}
            
        predictions = np.array(predictions)
        true_values = np.array(true_values)
        
        # Regression metrics
        results['mse'] = mean_squared_error(true_values, predictions)
        results['mae'] = mean_absolute_error(true_values, predictions)
        results['rmse'] = np.sqrt(results['mse'])
        
        # Classification metrics (binned severity)
        true_bins = self._bin_severity(true_values)
        pred_bins = self._bin_severity(predictions)
        
        results['accuracy'] = accuracy_score(true_bins, pred_bins)
        results['precision'] = precision_score(true_bins, pred_bins, average='weighted', zero_division=0)
        results['recall'] = recall_score(true_bins, pred_bins, average='weighted', zero_division=0)
        results['f1_score'] = f1_score(true_bins, pred_bins, average='weighted', zero_division=0)
        
        # Correlation
        results['correlation'] = np.corrcoef(true_values, predictions)[0, 1]
        
        # Within-1-point accuracy (clinical relevance)
        results['within_1_point_accuracy'] = np.mean(np.abs(true_values - predictions) <= 1.0)
        
        # Risk factor analysis
        results['risk_factor_analysis'] = self._analyze_risk_factors(model, test_data)
        
        logger.info(f"Severity classifier evaluation: MAE={results['mae']:.3f}, "
                   f"Accuracy={results['accuracy']:.3f}")
        
        return results
        
    def evaluate_flareup_predictor(self, model, test_data: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate the flare-up predictor model."""
        logger.info("Evaluating flare-up predictor...")
        
        results = {}
        predictions = []
        true_labels = []
        probabilities = []
        
        # Generate predictions
        for _, row in test_data.iterrows():
            try:
                pred = model.predict_flareup_risk(row.to_dict())
                predictions.append(pred['risk_class'])
                probabilities.append(pred['flareup_probability'])
                
                # Create true label (flare-up if severity >= 7)
                true_labels.append(1 if row['severity_score'] >= 7 else 0)
            except Exception as e:
                logger.warning(f"Prediction error: {e}")
                continue
                
        if not predictions:
            return {'error': 'No valid predictions generated'}
            
        predictions = np.array(predictions)
        true_labels = np.array(true_labels)
        probabilities = np.array(probabilities)
        
        # Binary classification metrics
        results['accuracy'] = accuracy_score(true_labels, predictions)
        results['precision'] = precision_score(true_labels, predictions, zero_division=0)
        results['recall'] = recall_score(true_labels, predictions, zero_division=0)
        results['f1_score'] = f1_score(true_labels, predictions, zero_division=0)
        results['roc_auc'] = roc_auc_score(true_labels, probabilities)
        
        # Confusion matrix
        cm = confusion_matrix(true_labels, predictions)
        results['confusion_matrix'] = cm.tolist()
        
        # Risk level distribution
        risk_levels = []
        for prob in probabilities:
            if prob < 0.3:
                risk_levels.append('low')
            elif prob < 0.6:
                risk_levels.append('moderate')
            else:
                risk_levels.append('high')
                
        results['risk_level_distribution'] = {
            level: risk_levels.count(level) / len(risk_levels)
            for level in ['low', 'moderate', 'high']
        }
        
        # Calibration analysis
        results['calibration_analysis'] = self._analyze_calibration(probabilities, true_labels)
        
        # Feature importance
        if hasattr(model, 'get_feature_importance'):
            try:
                results['feature_importance'] = model.get_feature_importance()
            except Exception as e:
                logger.warning(f"Could not get feature importance: {e}")
                
        logger.info(f"Flare-up predictor evaluation: AUC={results['roc_auc']:.3f}, "
                   f"F1={results['f1_score']:.3f}")
        
        return results
        
    def evaluate_recommendation_engine(self, model, test_data: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate the recommendation engine."""
        logger.info("Evaluating recommendation engine...")
        
        results = {}
        recommendations = []
        
        # Generate recommendations
        for _, row in test_data.iterrows():
            try:
                rec = model.generate_recommendations(row.to_dict())
                recommendations.append(rec)
            except Exception as e:
                logger.warning(f"Recommendation error: {e}")
                continue
                
        if not recommendations:
            return {'error': 'No valid recommendations generated'}
            
        # Recommendation quality metrics
        results['total_recommendations'] = len(recommendations)
        results['avg_diet_recommendations'] = np.mean([len(r['diet']) for r in recommendations])
        results['avg_lifestyle_recommendations'] = np.mean([len(r['lifestyle']) for r in recommendations])
        results['avg_priority_actions'] = np.mean([len(r['priority_actions']) for r in recommendations])
        
        # Effectiveness scores
        diet_scores = [r['effectiveness_scores']['diet'] for r in recommendations]
        lifestyle_scores = [r['effectiveness_scores']['lifestyle'] for r in recommendations]
        
        results['avg_diet_effectiveness'] = np.mean(diet_scores)
        results['avg_lifestyle_effectiveness'] = np.mean(lifestyle_scores)
        results['effectiveness_std'] = {
            'diet': np.std(diet_scores),
            'lifestyle': np.std(lifestyle_scores)
        }
        
        # Recommendation diversity
        results['recommendation_diversity'] = self._analyze_recommendation_diversity(recommendations)
        
        # User cluster analysis
        cluster_distribution = {}
        for rec in recommendations:
            cluster = rec['user_cluster']
            cluster_distribution[cluster] = cluster_distribution.get(cluster, 0) + 1
            
        results['cluster_distribution'] = cluster_distribution
        
        logger.info(f"Recommendation engine evaluation: "
                   f"Avg diet effectiveness={results['avg_diet_effectiveness']:.3f}")
        
        return results
        
    def cross_model_evaluation(self, models: Dict[str, Any], test_data: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate interactions and consistency between models."""
        logger.info("Performing cross-model evaluation...")
        
        results = {}
        
        # Collect predictions from all models
        all_predictions = []
        for _, row in test_data.iterrows():
            row_predictions = {}
            
            try:
                if 'severity_classifier' in models:
                    severity_pred = models['severity_classifier'].predict_severity(row.to_dict())
                    row_predictions['severity'] = severity_pred['severity_score']
                    row_predictions['severity_category'] = severity_pred['severity_category']
                    
                if 'flareup_predictor' in models:
                    flareup_pred = models['flareup_predictor'].predict_flareup_risk(row.to_dict())
                    row_predictions['flareup_probability'] = flareup_pred['flareup_probability']
                    row_predictions['flareup_risk_level'] = flareup_pred['risk_level']
                    
                if 'recommendation_engine' in models:
                    rec_pred = models['recommendation_engine'].generate_recommendations(row.to_dict())
                    row_predictions['n_recommendations'] = len(rec_pred['diet']) + len(rec_pred['lifestyle'])
                    row_predictions['diet_effectiveness'] = rec_pred['effectiveness_scores']['diet']
                    
                row_predictions['true_severity'] = row['severity_score']
                all_predictions.append(row_predictions)
                
            except Exception as e:
                logger.warning(f"Cross-model prediction error: {e}")
                continue
                
        if not all_predictions:
            return {'error': 'No valid cross-model predictions'}
            
        # Analyze consistency
        results['consistency_analysis'] = self._analyze_model_consistency(all_predictions)
        
        # Analyze severity-flareup correlation
        if 'severity' in all_predictions[0] and 'flareup_probability' in all_predictions[0]:
            severities = [p['severity'] for p in all_predictions]
            flareup_probs = [p['flareup_probability'] for p in all_predictions]
            results['severity_flareup_correlation'] = np.corrcoef(severities, flareup_probs)[0, 1]
            
        # Analyze recommendation appropriateness
        results['recommendation_appropriateness'] = self._analyze_recommendation_appropriateness(all_predictions)
        
        return results
        
    def _bin_severity(self, severity_scores: np.ndarray) -> np.ndarray:
        """Bin severity scores into categories."""
        bins = np.array([0, 3, 6, 8, 10])
        return np.digitize(severity_scores, bins) - 1
        
    def _analyze_risk_factors(self, model, test_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze risk factor identification accuracy."""
        analysis = {}
        
        # Sample a few predictions to analyze risk factors
        sample_size = min(50, len(test_data))
        sample_data = test_data.sample(n=sample_size, random_state=42)
        
        risk_factor_counts = {}
        for _, row in sample_data.iterrows():
            try:
                pred = model.predict_severity(row.to_dict())
                if 'risk_factors' in pred:
                    for factor in pred['risk_factors']:
                        factor_name = factor['factor']
                        risk_factor_counts[factor_name] = risk_factor_counts.get(factor_name, 0) + 1
            except Exception:
                continue
                
        analysis['most_common_risk_factors'] = dict(
            sorted(risk_factor_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        return analysis
        
    def _analyze_calibration(self, probabilities: np.ndarray, true_labels: np.ndarray) -> Dict[str, Any]:
        """Analyze probability calibration."""
        # Bin probabilities and calculate calibration
        n_bins = 10
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        calibration_data = []
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            in_bin = (probabilities > bin_lower) & (probabilities <= bin_upper)
            prop_in_bin = in_bin.mean()
            
            if prop_in_bin > 0:
                accuracy_in_bin = true_labels[in_bin].mean()
                avg_confidence_in_bin = probabilities[in_bin].mean()
                
                calibration_data.append({
                    'bin_lower': bin_lower,
                    'bin_upper': bin_upper,
                    'accuracy': accuracy_in_bin,
                    'confidence': avg_confidence_in_bin,
                    'proportion': prop_in_bin
                })
                
        return {'calibration_curve': calibration_data}
        
    def _analyze_recommendation_diversity(self, recommendations: List[Dict]) -> Dict[str, Any]:
        """Analyze diversity of recommendations."""
        all_diet_recs = []
        all_lifestyle_recs = []
        
        for rec in recommendations:
            all_diet_recs.extend([r['recommendation'] for r in rec['diet']])
            all_lifestyle_recs.extend([r['recommendation'] for r in rec['lifestyle']])
            
        diet_diversity = len(set(all_diet_recs)) / max(1, len(all_diet_recs))
        lifestyle_diversity = len(set(all_lifestyle_recs)) / max(1, len(all_lifestyle_recs))
        
        return {
            'diet_diversity': diet_diversity,
            'lifestyle_diversity': lifestyle_diversity,
            'unique_diet_recommendations': len(set(all_diet_recs)),
            'unique_lifestyle_recommendations': len(set(all_lifestyle_recs))
        }
        
    def _analyze_model_consistency(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Analyze consistency between model predictions."""
        consistency = {}
        
        # Check if high severity correlates with high flare-up risk
        if 'severity' in predictions[0] and 'flareup_probability' in predictions[0]:
            high_severity = [p for p in predictions if p['severity'] >= 7]
            if high_severity:
                high_severity_high_risk = [
                    p for p in high_severity if p['flareup_probability'] >= 0.6
                ]
                consistency['high_severity_high_risk_rate'] = len(high_severity_high_risk) / len(high_severity)
                
        # Check if high risk leads to more recommendations
        if 'flareup_probability' in predictions[0] and 'n_recommendations' in predictions[0]:
            high_risk = [p for p in predictions if p['flareup_probability'] >= 0.6]
            low_risk = [p for p in predictions if p['flareup_probability'] < 0.3]
            
            if high_risk and low_risk:
                avg_recs_high_risk = np.mean([p['n_recommendations'] for p in high_risk])
                avg_recs_low_risk = np.mean([p['n_recommendations'] for p in low_risk])
                consistency['recommendation_risk_correlation'] = avg_recs_high_risk - avg_recs_low_risk
                
        return consistency
        
    def _analyze_recommendation_appropriateness(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Analyze if recommendations are appropriate for the predicted risk level."""
        appropriateness = {}
        
        if 'flareup_risk_level' in predictions[0] and 'n_recommendations' in predictions[0]:
            risk_rec_mapping = {}
            for pred in predictions:
                risk_level = pred['flareup_risk_level']
                n_recs = pred['n_recommendations']
                
                if risk_level not in risk_rec_mapping:
                    risk_rec_mapping[risk_level] = []
                risk_rec_mapping[risk_level].append(n_recs)
                
            # Calculate average recommendations per risk level
            for risk_level, rec_counts in risk_rec_mapping.items():
                appropriateness[f'avg_recommendations_{risk_level}_risk'] = np.mean(rec_counts)
                
        return appropriateness
        
    def generate_evaluation_report(self, output_path: str = "evaluation_report.txt"):
        """Generate a comprehensive evaluation report."""
        if not self.evaluation_results:
            logger.warning("No evaluation results available. Run evaluate_all_models first.")
            return
            
        with open(output_path, 'w') as f:
            f.write("IBS ML Models Evaluation Report\n")
            f.write("=" * 50 + "\n\n")
            
            for model_name, results in self.evaluation_results.items():
                f.write(f"{model_name.replace('_', ' ').title()}\n")
                f.write("-" * 30 + "\n")
                
                if isinstance(results, dict) and 'error' not in results:
                    for metric, value in results.items():
                        if isinstance(value, (int, float)):
                            f.write(f"{metric}: {value:.4f}\n")
                        elif isinstance(value, str):
                            f.write(f"{metric}: {value}\n")
                        elif isinstance(value, dict) and len(value) < 10:
                            f.write(f"{metric}:\n")
                            for k, v in value.items():
                                f.write(f"  {k}: {v}\n")
                else:
                    f.write(f"Error: {results.get('error', 'Unknown error')}\n")
                    
                f.write("\n")
                
        logger.info(f"Evaluation report saved to {output_path}")
        
    def plot_evaluation_metrics(self, output_dir: str = "evaluation_plots"):
        """Generate visualization plots for evaluation metrics."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Plot severity classifier metrics
        if 'severity_classifier' in self.evaluation_results:
            self._plot_severity_metrics(
                self.evaluation_results['severity_classifier'],
                os.path.join(output_dir, 'severity_classifier_metrics.png')
            )
            
        # Plot flare-up predictor metrics
        if 'flareup_predictor' in self.evaluation_results:
            self._plot_flareup_metrics(
                self.evaluation_results['flareup_predictor'],
                os.path.join(output_dir, 'flareup_predictor_metrics.png')
            )
            
        logger.info(f"Evaluation plots saved to {output_dir}")
        
    def _plot_severity_metrics(self, results: Dict, output_path: str):
        """Plot severity classifier evaluation metrics."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Severity Classifier Evaluation', fontsize=16)
        
        # Metrics bar plot
        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        values = [results.get(m, 0) for m in metrics]
        
        axes[0, 0].bar(metrics, values)
        axes[0, 0].set_title('Classification Metrics')
        axes[0, 0].set_ylim(0, 1)
        
        # Regression metrics
        reg_metrics = ['mae', 'rmse']
        reg_values = [results.get(m, 0) for m in reg_metrics]
        
        axes[0, 1].bar(reg_metrics, reg_values)
        axes[0, 1].set_title('Regression Metrics')
        
        # Correlation and within-1-point accuracy
        special_metrics = ['correlation', 'within_1_point_accuracy']
        special_values = [results.get(m, 0) for m in special_metrics]
        
        axes[1, 0].bar(special_metrics, special_values)
        axes[1, 0].set_title('Special Metrics')
        axes[1, 0].set_ylim(0, 1)
        
        # Remove empty subplot
        axes[1, 1].remove()
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
    def _plot_flareup_metrics(self, results: Dict, output_path: str):
        """Plot flare-up predictor evaluation metrics."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Flare-up Predictor Evaluation', fontsize=16)
        
        # Classification metrics
        metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
        values = [results.get(m, 0) for m in metrics]
        
        axes[0, 0].bar(metrics, values)
        axes[0, 0].set_title('Classification Metrics')
        axes[0, 0].set_ylim(0, 1)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Risk level distribution
        if 'risk_level_distribution' in results:
            risk_dist = results['risk_level_distribution']
            axes[0, 1].pie(risk_dist.values(), labels=risk_dist.keys(), autopct='%1.1f%%')
            axes[0, 1].set_title('Risk Level Distribution')
            
        # Confusion matrix
        if 'confusion_matrix' in results:
            cm = np.array(results['confusion_matrix'])
            sns.heatmap(cm, annot=True, fmt='d', ax=axes[1, 0])
            axes[1, 0].set_title('Confusion Matrix')
            axes[1, 0].set_xlabel('Predicted')
            axes[1, 0].set_ylabel('Actual')
            
        # Remove empty subplot
        axes[1, 1].remove()
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()