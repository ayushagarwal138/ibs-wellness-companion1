#!/usr/bin/env python3
"""
Comprehensive Accuracy Evaluation Script for IBS Wellness Companion
====================================================================
Produces verified, reproducible accuracy metrics for official presentation.
Run this script to get accurate ML model performance statistics.
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, mean_squared_error, mean_absolute_error, r2_score,
    classification_report, confusion_matrix
)

# Add ml-models/src to path for DataPreparator
ml_models_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ml_models_root / "src"))

# Configuration
RANDOM_STATE = 42
N_SAMPLES = 5000  # Total dataset size
TEST_SIZE = 0.20   # 20% held out for final evaluation
VAL_SIZE = 0.15    # 15% for validation (from remaining 80%)
N_USERS_SYNTHETIC = 200  # For data_preparation synthetic
DAYS_PER_USER = 90       # For data_preparation synthetic


def create_synthetic_training_data(n_samples: int = N_SAMPLES) -> pd.DataFrame:
    """Create synthetic training data (same as create_real_models.py)."""
    np.random.seed(RANDOM_STATE)
    
    data = {
        'age': np.random.normal(35, 12, n_samples).clip(18, 80),
        'gender': np.random.choice([0, 1, 2], n_samples, p=[0.4, 0.55, 0.05]),
        'bmi': np.random.normal(25, 4, n_samples).clip(16, 45),
        'abdominal_pain': np.random.exponential(2, n_samples).clip(0, 10),
        'bloating': np.random.exponential(2.5, n_samples).clip(0, 10),
        'diarrhea': np.random.exponential(1.8, n_samples).clip(0, 10),
        'constipation': np.random.exponential(1.5, n_samples).clip(0, 10),
        'gas': np.random.exponential(2.2, n_samples).clip(0, 10),
        'stress_level': np.random.exponential(2, n_samples).clip(0, 10),
        'sleep_quality': (10 - np.random.exponential(2, n_samples)).clip(0, 10),
        'exercise_frequency': np.random.poisson(3, n_samples).clip(0, 7),
        'water_intake': np.random.normal(2.5, 0.8, n_samples).clip(0.5, 5),
        'fiber_intake': np.random.normal(25, 8, n_samples).clip(5, 50),
        'processed_food_freq': np.random.exponential(2, n_samples).clip(0, 10),
        'dairy_intake': np.random.exponential(1.5, n_samples).clip(0, 10),
        'spicy_food_freq': np.random.exponential(1.8, n_samples).clip(0, 10),
        'medication_adherence': np.random.beta(8, 2, n_samples),
        'previous_flareups': np.random.poisson(2, n_samples).clip(0, 20),
        'family_history': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
    }
    
    df = pd.DataFrame(data)
    df = df.fillna(0)
    
    severity_factors = (
        0.3 * df['abdominal_pain'] + 0.25 * df['bloating'] + 0.2 * df['diarrhea'] +
        0.15 * df['constipation'] + 0.1 * df['gas'] + 0.2 * df['stress_level'] +
        -0.1 * df['sleep_quality'] + 0.1 * df['processed_food_freq']
    )
    df['severity_score'] = (severity_factors + np.random.normal(0, 0.5, n_samples)).clip(0, 10)
    
    flareup_factors = (
        0.25 * (df['severity_score'] / 10) + 0.2 * (df['stress_level'] / 10) +
        0.15 * (df['processed_food_freq'] / 10) + 0.1 * (df['previous_flareups'] / 20) +
        -0.1 * (df['sleep_quality'] / 10) - 0.05 * df['medication_adherence'] + 0.3
    )
    df['flareup_risk'] = (flareup_factors + np.random.normal(0, 0.2, n_samples)).clip(0, 1)
    
    severity_cats = pd.cut(df['severity_score'], bins=[0, 2, 4, 6, 8, 10],
                           labels=['none', 'mild', 'moderate', 'severe', 'very_severe'])
    df['severity_category'] = severity_cats.astype(str).replace('nan', 'mild')
    df['will_flareup'] = (df['flareup_risk'] > 0.5).astype(int)
    df['recommendation_score'] = (
        0.4 * (10 - df['severity_score']) + 0.3 * df['sleep_quality'] +
        0.2 * (7 - df['stress_level']) + 0.1 * df['exercise_frequency']
    ) / 10
    
    return df.fillna(0)


def evaluate_severity_classifier(df: pd.DataFrame) -> dict:
    """Train and evaluate severity classifier with full metrics."""
    feature_cols = [c for c in df.columns if c not in [
        'severity_score', 'severity_category', 'flareup_risk', 'will_flareup', 'recommendation_score'
    ]]
    
    X = df[feature_cols]
    y = df['severity_category']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    
    model = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, max_depth=10)
    model.fit(X_train_s, y_train)
    
    y_pred = model.predict(X_test_s)
    
    # Handle edge case for precision/recall with some classes missing in test
    unique_classes = np.unique(np.concatenate([y_test, y_pred]))
    
    return {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision_weighted': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
        'recall_weighted': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
        'f1_weighted': float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
        'precision_macro': float(precision_score(y_test, y_pred, average='macro', zero_division=0)),
        'recall_macro': float(recall_score(y_test, y_pred, average='macro', zero_division=0)),
        'f1_macro': float(f1_score(y_test, y_pred, average='macro', zero_division=0)),
        'confusion_matrix': confusion_matrix(y_test, y_pred, labels=unique_classes).tolist(),
        'n_train': len(X_train),
        'n_test': len(X_test),
        'n_features': len(feature_cols),
        'classes': list(unique_classes),
    }


def evaluate_flareup_predictor(df: pd.DataFrame) -> dict:
    """Train and evaluate flare-up predictor with full metrics."""
    feature_cols = [c for c in df.columns if c not in [
        'severity_score', 'severity_category', 'flareup_risk', 'will_flareup', 'recommendation_score'
    ]]
    
    X = df[feature_cols]
    y = df['will_flareup']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    
    model = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, max_depth=8)
    model.fit(X_train_s, y_train)
    
    y_pred = model.predict(X_test_s)
    y_prob = model.predict_proba(X_test_s)[:, 1]  # Probability of class 1 (flare-up)
    
    try:
        roc_auc = float(roc_auc_score(y_test, y_prob))
    except ValueError:
        roc_auc = 0.0
    
    return {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred, zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, zero_division=0)),
        'f1_score': float(f1_score(y_test, y_pred, zero_division=0)),
        'roc_auc': roc_auc,
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'n_train': len(X_train),
        'n_test': len(X_test),
        'n_positive_test': int(y_test.sum()),
        'n_negative_test': int(len(y_test) - y_test.sum()),
    }


def evaluate_recommendation_engine(df: pd.DataFrame) -> dict:
    """Train and evaluate recommendation engine (regression)."""
    feature_cols = [c for c in df.columns if c not in [
        'severity_score', 'severity_category', 'flareup_risk', 'will_flareup', 'recommendation_score'
    ]]
    
    X = df[feature_cols]
    y = df['recommendation_score']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    
    model = RandomForestRegressor(n_estimators=100, random_state=RANDOM_STATE, max_depth=8)
    model.fit(X_train_s, y_train)
    
    y_pred = model.predict(X_test_s)
    
    return {
        'mse': float(mean_squared_error(y_test, y_pred)),
        'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
        'mae': float(mean_absolute_error(y_test, y_pred)),
        'r2_score': float(r2_score(y_test, y_pred)),
        'n_train': len(X_train),
        'n_test': len(X_test),
    }


def get_data_preparation_dataset_info() -> dict:
    """Get info about DataPreparator synthetic data (alternative pipeline)."""
    # Document the DataPreparator pipeline without importing (avoids potential env issues)
    return {
        'source': 'DataPreparator (ml-models/src/training/data_preparation.py)',
        'n_users': N_USERS_SYNTHETIC,
        'days_per_user': DAYS_PER_USER,
        'estimated_records': N_USERS_SYNTHETIC * DAYS_PER_USER,
        'tables': ['users', 'symptom_logs', 'diet_logs', 'food_reactions', 'medications'],
        'note': 'Research-informed synthetic data with microbiome, psychological, dietary features',
    }


def run_full_evaluation() -> dict:
    """Run complete evaluation and return all metrics."""
    print("=" * 70)
    print("IBS WELLNESS COMPANION - COMPREHENSIVE ACCURACY EVALUATION")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Random seed: {RANDOM_STATE}")
    print()
    
    # 1. Dataset information
    print("[1/4] Creating synthetic dataset...")
    df = create_synthetic_training_data(N_SAMPLES)
    
    dataset_info = {
        'total_samples': N_SAMPLES,
        'source': 'Synthetic (create_real_models.py / evaluate_accuracy_comprehensive.py)',
        'method': 'Generated using research-informed distributions (exponential for symptoms, '
                 'normal for demographics, beta for adherence)',
        'train_test_split': f'{int((1-TEST_SIZE)*100)}% train, {int(TEST_SIZE*100)}% test',
        'target_variables': {
            'severity_category': '5 classes (none, mild, moderate, severe, very_severe)',
            'will_flareup': 'Binary (0/1)',
            'recommendation_score': 'Continuous 0-1'
        },
        'feature_count': 18,
        'severity_distribution': df['severity_category'].value_counts().to_dict(),
        'flareup_distribution': df['will_flareup'].value_counts().to_dict(),
    }
    
    # Convert numpy types for JSON
    for k, v in dataset_info.items():
        if hasattr(v, 'item'):
            dataset_info[k] = float(v)
        elif isinstance(v, dict):
            dataset_info[k] = {str(kk): int(vv) if hasattr(vv, 'item') else vv for kk, vv in v.items()}
    
    print(f"   Total samples: {N_SAMPLES}")
    print(f"   Test set size: {int(N_SAMPLES * TEST_SIZE)}")
    print()
    
    # 2. Severity classifier
    print("[2/4] Evaluating Severity Classifier...")
    severity_results = evaluate_severity_classifier(df)
    print(f"   Accuracy: {severity_results['accuracy']:.4f}")
    print(f"   F1 (weighted): {severity_results['f1_weighted']:.4f}")
    print()
    
    # 3. Flare-up predictor
    print("[3/4] Evaluating Flare-up Predictor...")
    flareup_results = evaluate_flareup_predictor(df)
    print(f"   Accuracy: {flareup_results['accuracy']:.4f}")
    print(f"   ROC-AUC: {flareup_results['roc_auc']:.4f}")
    print(f"   F1 Score: {flareup_results['f1_score']:.4f}")
    print()
    
    # 4. Recommendation engine
    print("[4/4] Evaluating Recommendation Engine...")
    rec_results = evaluate_recommendation_engine(df)
    print(f"   R² Score: {rec_results['r2_score']:.4f}")
    print(f"   RMSE: {rec_results['rmse']:.4f}")
    print()
    
    # Alternative dataset info
    print("Gathering alternative dataset info (DataPreparator pipeline)...")
    alt_dataset = get_data_preparation_dataset_info()
    
    report = {
        'evaluation_timestamp': datetime.now().isoformat(),
        'dataset': dataset_info,
        'alternative_data_sources': {
            'data_preparator_synthetic': alt_dataset,
            'external_datasets_configured': {
                'gut_microbiome': 'Kaggle: paultimothymooney/microbiome-data (optional)',
                'dietary_patterns': 'Kaggle: shashwatwork/food-nutrition-dataset (optional)',
                'symptom_tracking': 'Kaggle: uciml/pima-indians-diabetes-database, adapted (optional)',
            },
            'database_seeds': {
                'users': 6,
                'symptoms': 20,
                'diet_logs': 20,
                'food_items': 'from 02_food_items.sql',
                'symptoms_reference': 'from 00_symptoms_reference.sql',
            }
        },
        'models': {
            'severity_classifier': severity_results,
            'flareup_predictor': flareup_results,
            'recommendation_engine': rec_results,
        },
        'summary': {
            'severity_classifier_accuracy': severity_results['accuracy'],
            'flareup_predictor_accuracy': flareup_results['accuracy'],
            'flareup_predictor_roc_auc': flareup_results['roc_auc'],
            'recommendation_engine_r2': rec_results['r2_score'],
        }
    }
    
    return report


def main():
    report = run_full_evaluation()
    
    # Save report
    output_dir = Path(__file__).parent.parent.parent
    report_path = output_dir / "ACCURACY_EVALUATION_REPORT.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print("=" * 70)
    print("EVALUATION COMPLETE - REPORT SAVED")
    print("=" * 70)
    print(f"Full report: {report_path}")
    print()
    print("SUMMARY FOR PRESENTATION:")
    print("-" * 40)
    print(f"Severity Classifier Accuracy:  {report['summary']['severity_classifier_accuracy']:.2%}")
    print(f"Flare-up Predictor Accuracy:  {report['summary']['flareup_predictor_accuracy']:.2%}")
    print(f"Flare-up Predictor ROC-AUC:   {report['summary']['flareup_predictor_roc_auc']:.4f}")
    print(f"Recommendation Engine R²:     {report['summary']['recommendation_engine_r2']:.4f}")
    print(f"Total Dataset Size:           {report['dataset']['total_samples']:,} samples")
    print(f"Data Source:                  {report['dataset']['source']}")
    print()
    
    return report


if __name__ == "__main__":
    report = main()
    sys.exit(0)
