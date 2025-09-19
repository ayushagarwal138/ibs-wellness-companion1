#!/usr/bin/env python3
"""
Test External Dataset Integration

This script validates that all external dataset integration components
work correctly without requiring actual external data sources.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, Any

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_configuration_system():
    """Test the external dataset configuration system."""
    print("Testing configuration system...")
    
    try:
        from training.external_config import ExternalDataConfig, get_config
        
        # Test default configuration loading
        config = get_config()
        assert len(config.datasets) > 0, "No datasets configured"
        assert hasattr(config, 'global_settings'), "Global settings missing"
        
        # Test dataset management
        dataset_names = list(config.datasets.keys())
        first_dataset = dataset_names[0]
        
        # Test enable/disable functionality
        original_state = config.datasets[first_dataset].enabled
        config.disable_dataset(first_dataset)
        assert not config.datasets[first_dataset].enabled, "Dataset disable failed"
        
        config.enable_dataset(first_dataset)
        assert config.datasets[first_dataset].enabled, "Dataset enable failed"
        
        # Restore original state
        config.datasets[first_dataset].enabled = original_state
        
        # Test validation
        validation = config.validate_configuration()
        assert isinstance(validation, dict), "Validation should return dict"
        assert 'valid' in validation, "Validation missing 'valid' key"
        
        print("✓ Configuration system tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Configuration system test failed: {e}")
        return False


def test_external_data_loader():
    """Test the external data loader functionality."""
    print("Testing external data loader...")
    
    try:
        from training.external_data_loader import ExternalDataLoader
        
        # Test initialization
        loader = ExternalDataLoader()
        assert hasattr(loader, 'cache_dir'), "Cache directory not set"
        assert hasattr(loader, 'logger'), "Logger not initialized"
        
        # Test cache directory creation
        assert loader.cache_dir.exists(), "Cache directory not created"
        
        # Test dataset caching check (should work without actual datasets)
        is_cached = loader.is_dataset_cached('test_dataset')
        assert isinstance(is_cached, bool), "Cache check should return boolean"
        
        # Test credential checking (should handle missing credentials gracefully)
        has_kaggle = loader._check_kaggle_credentials()
        assert isinstance(has_kaggle, bool), "Credential check should return boolean"
        
        print("✓ External data loader tests passed")
        return True
        
    except Exception as e:
        print(f"✗ External data loader test failed: {e}")
        return False


def test_data_preparation_integration():
    """Test data preparation with external dataset support."""
    print("Testing data preparation integration...")
    
    try:
        from training.data_preparation import DataPreparator
        
        # Test initialization with external data support
        prep_with_external = DataPreparator(use_external_data=True)
        assert hasattr(prep_with_external, 'use_external_data'), "External data flag missing"
        assert hasattr(prep_with_external, 'external_loader'), "External loader missing"
        
        prep_without_external = DataPreparator(use_external_data=False)
        assert not prep_without_external.use_external_data, "External data should be disabled"
        
        # Test synthetic data generation
        synthetic_data = prep_with_external.create_synthetic_data(n_users=5, days_per_user=10)
        assert isinstance(synthetic_data, dict), "Synthetic data should be dict"
        assert len(synthetic_data) > 0, "Synthetic data should not be empty"
        
        # Test data preparation pipeline
        training_data = prep_with_external.prepare_training_data(
            synthetic_data, 
            include_external=False  # Don't actually try to load external data
        )
        assert isinstance(training_data, pd.DataFrame), "Training data should be DataFrame"
        assert len(training_data) > 0, "Training data should not be empty"
        assert len(training_data.columns) > 0, "Training data should have features"
        
        # Test external data integration methods exist
        assert hasattr(prep_with_external, 'load_external_datasets'), "Missing load_external_datasets method"
        assert hasattr(prep_with_external, 'integrate_external_data'), "Missing integrate_external_data method"
        
        print("✓ Data preparation integration tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Data preparation integration test failed: {e}")
        return False


def test_training_script_functionality():
    """Test the training script components."""
    print("Testing training script functionality...")
    
    try:
        # Import the training script functions
        sys.path.append(str(Path(__file__).parent))
        from train_with_external_data import (
            setup_kaggle_credentials,
            configure_external_datasets,
            validate_external_config,
            load_training_data
        )
        
        # Test credential setup (should handle missing credentials gracefully)
        creds_result = setup_kaggle_credentials()
        assert isinstance(creds_result, bool), "Credential setup should return boolean"
        
        # Test configuration validation
        from training.external_config import get_config
        config = get_config()
        validation_result = validate_external_config(config)
        assert isinstance(validation_result, bool), "Validation should return boolean"
        
        # Test data loading with synthetic data
        training_data = load_training_data(
            use_synthetic=True,
            use_external=False  # Don't try to load external data
        )
        assert isinstance(training_data, dict), "Training data should be dict"
        assert len(training_data) > 0, "Training data should not be empty"
        
        print("✓ Training script functionality tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Training script functionality test failed: {e}")
        return False


def test_model_training_with_external_support():
    """Test that model training works with external dataset support."""
    print("Testing model training with external support...")
    
    try:
        from training.data_preparation import DataPreparator
        from training.train_models import ModelTrainer
        
        # Prepare data with external support
        prep = DataPreparator(use_external_data=True)
        synthetic_data = prep.create_synthetic_data(n_users=10, days_per_user=20)
        training_data = prep.prepare_training_data(synthetic_data, include_external=False)
        
        # Test model training
        trainer = ModelTrainer(output_dir="test_models")
        results = trainer.train_all_models(data=training_data, use_synthetic_data=False)
        
        assert isinstance(results, dict), "Training results should be dict"
        
        # Clean up test models
        import shutil
        test_models_dir = Path("test_models")
        if test_models_dir.exists():
            shutil.rmtree(test_models_dir)
        
        print("✓ Model training with external support tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Model training with external support test failed: {e}")
        return False


def run_all_tests():
    """Run all external dataset integration tests."""
    print("="*60)
    print("EXTERNAL DATASET INTEGRATION TEST SUITE")
    print("="*60)
    
    tests = [
        test_configuration_system,
        test_external_data_loader,
        test_data_preparation_integration,
        test_training_script_functionality,
        test_model_training_with_external_support
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! External dataset integration is working correctly.")
        return True
    else:
        print(f"\n❌ {failed} test(s) failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)