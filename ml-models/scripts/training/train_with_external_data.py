#!/usr/bin/env python3
"""
Train IBS ML Models with External Dataset Integration

This script demonstrates how to train IBS prediction models using both
internal data (database/synthetic) and external datasets from sources like Kaggle.

Usage:
    python train_with_external_data.py [options]

Examples:
    # Train with external data (requires Kaggle credentials)
    python train_with_external_data.py --use-external --kaggle-username your_username --kaggle-key your_key
    
    # Train with synthetic data and external datasets
    python train_with_external_data.py --use-synthetic --use-external
    
    # Train with specific external datasets only
    python train_with_external_data.py --use-external --datasets gut_microbiome,dietary_patterns
    
    # Configure and validate external datasets
    python train_with_external_data.py --configure-external --validate-config
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / 'src'))

from training.data_preparation import DataPreparator
from training.database import DatabaseConnection
from training.train_models import ModelTrainer
from training.external_config import ExternalDataConfig, get_config
from training.external_data_loader import ExternalDataLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('external_training.log')
    ]
)
logger = logging.getLogger(__name__)


def setup_kaggle_credentials(username: str = None, key: str = None) -> bool:
    """
    Setup Kaggle API credentials from arguments or environment.
    
    Args:
        username: Kaggle username
        key: Kaggle API key
        
    Returns:
        bool: True if credentials are configured
    """
    if username and key:
        os.environ['KAGGLE_USERNAME'] = username
        os.environ['KAGGLE_KEY'] = key
        logger.info("Kaggle credentials set from command line arguments")
        return True
    
    # Check if already configured in environment
    if os.getenv('KAGGLE_USERNAME') and os.getenv('KAGGLE_KEY'):
        logger.info("Using existing Kaggle credentials from environment")
        return True
    
    # Check for kaggle.json file
    kaggle_config_path = Path.home() / '.kaggle' / 'kaggle.json'
    if kaggle_config_path.exists():
        logger.info("Using Kaggle credentials from ~/.kaggle/kaggle.json")
        return True
    
    logger.warning("Kaggle credentials not found. External datasets will be skipped.")
    logger.info("To use external datasets, either:")
    logger.info("1. Set KAGGLE_USERNAME and KAGGLE_KEY environment variables")
    logger.info("2. Create ~/.kaggle/kaggle.json with your credentials")
    logger.info("3. Use --kaggle-username and --kaggle-key arguments")
    
    return False


def configure_external_datasets(config: ExternalDataConfig, 
                               enabled_datasets: List[str] = None,
                               cache_days: int = None) -> bool:
    """
    Configure external dataset settings.
    
    Args:
        config: External data configuration
        enabled_datasets: List of datasets to enable
        cache_days: Cache duration in days
        
    Returns:
        bool: True if configuration was successful
    """
    try:
        logger.info("Configuring external datasets...")
        
        # Update global settings
        if cache_days is not None:
            config.global_settings['default_cache_days'] = cache_days
            logger.info(f"Set default cache days to {cache_days}")
        
        # Enable/disable specific datasets
        if enabled_datasets:
            # Disable all datasets first
            for name in config.datasets.keys():
                config.disable_dataset(name)
            
            # Enable specified datasets
            for dataset_name in enabled_datasets:
                if dataset_name in config.datasets:
                    config.enable_dataset(dataset_name)
                else:
                    logger.warning(f"Unknown dataset: {dataset_name}")
                    logger.info(f"Available datasets: {list(config.datasets.keys())}")
        
        # Save configuration
        config.save_config()
        logger.info("External dataset configuration saved")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to configure external datasets: {e}")
        return False


def validate_external_config(config: ExternalDataConfig) -> bool:
    """
    Validate external dataset configuration.
    
    Args:
        config: External data configuration
        
    Returns:
        bool: True if configuration is valid
    """
    logger.info("Validating external dataset configuration...")
    
    validation = config.validate_configuration()
    
    print("\n" + "="*50)
    print("EXTERNAL DATASET CONFIGURATION VALIDATION")
    print("="*50)
    
    # Overall status
    status_icon = "✓" if validation['valid'] else "✗"
    print(f"Overall Status: {status_icon} {'VALID' if validation['valid'] else 'INVALID'}")
    
    # Credentials status
    creds_configured = config.credentials.is_kaggle_configured()
    creds_icon = "✓" if creds_configured else "✗"
    print(f"Kaggle Credentials: {creds_icon} {'Configured' if creds_configured else 'Not Configured'}")
    
    # Dataset status
    enabled_datasets = config.get_enabled_datasets()
    print(f"\nEnabled Datasets: {len(enabled_datasets)}/{len(config.datasets)}")
    
    for name, status in validation['dataset_status'].items():
        dataset_config = config.datasets[name]
        status_icon = "✓" if status['enabled'] and not status['issues'] else "✗" if status['enabled'] else "-"
        
        print(f"  {status_icon} {name}: {dataset_config.description}")
        if status['issues']:
            for issue in status['issues']:
                print(f"    ⚠ {issue}")
    
    # Warnings and errors
    if validation['warnings']:
        print(f"\nWarnings ({len(validation['warnings'])}):")
        for warning in validation['warnings']:
            print(f"  ⚠ {warning}")
    
    if validation['errors']:
        print(f"\nErrors ({len(validation['errors'])}):")
        for error in validation['errors']:
            print(f"  ✗ {error}")
    
    print("="*50)
    
    return validation['valid']


def load_training_data(use_synthetic: bool = True, 
                      use_external: bool = False,
                      external_datasets: List[str] = None) -> Dict[str, pd.DataFrame]:
    """
    Load training data from various sources.
    
    Args:
        use_synthetic: Whether to use synthetic data
        use_external: Whether to include external datasets
        external_datasets: Specific external datasets to use
        
    Returns:
        Dictionary of training data
    """
    logger.info("Loading training data...")
    
    # Initialize data preparator with external data support
    data_prep = DataPreparator(use_external_data=use_external)
    
    # Load base data (synthetic or real)
    if use_synthetic:
        logger.info("Loading synthetic data...")
        raw_data = data_prep.create_synthetic_data(n_users=200, days_per_user=90)
    else:
        logger.info("Loading data from database...")
        try:
            db_connection = DatabaseConnection()
            with db_connection.connect() as conn:
                raw_data = data_prep.load_data_from_db(conn)
        except Exception as e:
            logger.error(f"Failed to load database data: {e}")
            logger.info("Falling back to synthetic data...")
            raw_data = data_prep.create_synthetic_data(n_users=200, days_per_user=90)
    
    # Configure specific external datasets if requested
    if use_external and external_datasets:
        config = get_config()
        
        # Temporarily enable only requested datasets
        original_states = {}
        for name, dataset_config in config.datasets.items():
            original_states[name] = dataset_config.enabled
            dataset_config.enabled = name in external_datasets
        
        try:
            # Load external data
            external_data = data_prep.load_external_datasets()
            raw_data = data_prep.integrate_external_data(raw_data, external_data)
        finally:
            # Restore original states
            for name, original_state in original_states.items():
                config.datasets[name].enabled = original_state
    
    return raw_data


def train_models_with_external_data(raw_data: Dict[str, pd.DataFrame],
                                   model_types: List[str] = None,
                                   output_dir: str = "trained_models") -> Dict[str, Any]:
    """
    Train ML models with the prepared data.
    
    Args:
        raw_data: Training data dictionary
        model_types: List of model types to train (not used with current ModelTrainer)
        output_dir: Directory to save trained models
        
    Returns:
        Training results and metrics
    """
    logger.info("Training ML models with external data integration...")
    
    # Prepare training data
    data_prep = DataPreparator()
    training_data = data_prep.prepare_training_data(raw_data, include_external=True)
    
    logger.info(f"Training data shape: {training_data.shape}")
    logger.info(f"Features: {list(training_data.columns)}")
    
    # Check for external data features
    external_features = [col for col in training_data.columns if 'external' in col.lower()]
    if external_features:
        logger.info(f"External features detected: {external_features}")
    else:
        logger.info("No external features found in training data")
    
    # Initialize and train models
    trainer = ModelTrainer(output_dir=output_dir)
    results = trainer.train_all_models(data=training_data, use_synthetic_data=False)
    
    return results


def main():
    """Main training script with external dataset integration."""
    parser = argparse.ArgumentParser(
        description="Train IBS ML models with external dataset integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Data source options
    parser.add_argument('--use-synthetic', action='store_true',
                       help='Use synthetic data instead of database data')
    parser.add_argument('--use-external', action='store_true',
                       help='Include external datasets in training')
    
    # External dataset options
    parser.add_argument('--datasets', type=str,
                       help='Comma-separated list of external datasets to use')
    parser.add_argument('--cache-days', type=int, default=7,
                       help='Number of days to cache external datasets')
    
    # Kaggle credentials
    parser.add_argument('--kaggle-username', type=str,
                       help='Kaggle username for API access')
    parser.add_argument('--kaggle-key', type=str,
                       help='Kaggle API key for dataset access')
    
    # Model options
    parser.add_argument('--models', type=str,
                       help='Comma-separated list of models to train')
    parser.add_argument('--output-dir', type=str, default='trained_models',
                       help='Directory to save trained models')
    
    # Configuration options
    parser.add_argument('--configure-external', action='store_true',
                       help='Configure external dataset settings')
    parser.add_argument('--validate-config', action='store_true',
                       help='Validate external dataset configuration')
    parser.add_argument('--list-datasets', action='store_true',
                       help='List available external datasets')
    
    # Logging options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress non-error output')
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    try:
        # Setup Kaggle credentials if using external data
        if args.use_external:
            if not setup_kaggle_credentials(args.kaggle_username, args.kaggle_key):
                if not args.configure_external and not args.validate_config:
                    logger.error("Kaggle credentials required for external datasets")
                    return 1
        
        # Get external data configuration
        config = get_config()
        
        # Handle configuration commands
        if args.list_datasets:
            info = config.get_dataset_info()
            print("\nAvailable External Datasets:")
            print("="*40)
            for name, dataset_info in info['datasets'].items():
                status = "✓" if dataset_info['enabled'] else "✗"
                print(f"  {status} {name}: {dataset_info['description']}")
                print(f"    Source: {dataset_info['source']}")
                print(f"    Cache: {dataset_info['cache_days']} days")
            return 0
        
        if args.configure_external:
            datasets_list = args.datasets.split(',') if args.datasets else None
            if not configure_external_datasets(config, datasets_list, args.cache_days):
                return 1
        
        if args.validate_config:
            if not validate_external_config(config):
                return 1
        
        # If only configuration commands were run, exit
        if args.configure_external or args.validate_config or args.list_datasets:
            return 0
        
        # Load training data
        external_datasets_list = args.datasets.split(',') if args.datasets else None
        raw_data = load_training_data(
            use_synthetic=args.use_synthetic,
            use_external=args.use_external,
            external_datasets=external_datasets_list
        )
        
        # Train models
        model_types = args.models.split(',') if args.models else None
        results = train_models_with_external_data(
            raw_data=raw_data,
            model_types=model_types,
            output_dir=args.output_dir
        )
        
        # Display results
        print("\n" + "="*50)
        print("TRAINING RESULTS WITH EXTERNAL DATA")
        print("="*50)
        
        for model_name, metrics in results.items():
            if isinstance(metrics, dict) and 'accuracy' in metrics:
                print(f"{model_name}:")
                print(f"  Accuracy: {metrics['accuracy']:.4f}")
                print(f"  Precision: {metrics.get('precision', 'N/A')}")
                print(f"  Recall: {metrics.get('recall', 'N/A')}")
                print(f"  F1-Score: {metrics.get('f1_score', 'N/A')}")
        
        print("="*50)
        logger.info("Training completed successfully!")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Training failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())