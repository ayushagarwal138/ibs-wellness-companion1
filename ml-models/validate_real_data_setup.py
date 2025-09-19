#!/usr/bin/env python3
"""
Validation script for IBS ML model real data training setup.
This script validates that the training pipeline is properly configured to use real data.
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from training.train_models import ModelTrainer
from training.database import check_database_availability, get_database_connection
from training.data_preparation import DataPreparator

def validate_real_data_setup():
    """Validate that the ML training pipeline is configured for real data."""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("=" * 60)
    print("IBS ML Model Real Data Training Setup Validation")
    print("=" * 60)
    
    # 1. Check default configuration
    trainer = ModelTrainer()
    train_method = trainer.train_all_models
    
    # Get function signature to check defaults
    import inspect
    sig = inspect.signature(train_method)
    use_synthetic_default = sig.parameters['use_synthetic_data'].default
    
    print(f"\n✓ Training configuration:")
    print(f"  - Default use_synthetic_data: {use_synthetic_default}")
    print(f"  - Real data is now the default: {'✓ YES' if use_synthetic_default is False else '✗ NO'}")
    
    # 2. Check database connection capability
    print(f"\n✓ Database connection:")
    db_available = check_database_availability()
    print(f"  - Database available: {'✓ YES' if db_available else '✗ NO'}")
    
    if not db_available:
        print(f"  - Note: Database not currently running, but connection logic is in place")
    
    # 3. Check data preparation methods
    data_prep = DataPreparator()
    print(f"\n✓ Data preparation methods:")
    print(f"  - load_data_from_db: {'✓ Available' if hasattr(data_prep, 'load_data_from_db') else '✗ Missing'}")
    print(f"  - create_synthetic_data: {'✓ Available' if hasattr(data_prep, 'create_synthetic_data') else '✗ Missing'}")
    
    # 4. Test training with synthetic data (as fallback)
    print(f"\n✓ Testing training pipeline:")
    try:
        results = trainer.train_all_models(use_synthetic_data=True, n_synthetic_users=10)
        print(f"  - Training execution: ✓ SUCCESS")
        print(f"  - Models trained: {len(results) if results else 0}")
        if results:
            print(f"  - Available models: {', '.join(results.keys())}")
    except Exception as e:
        print(f"  - Training execution: ✗ FAILED - {str(e)}")
        return False
    
    # 5. Summary
    print(f"\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if use_synthetic_default is False:
        print("✓ SUCCESS: ML training pipeline is configured to use real data by default")
        print("\nTo use with real database:")
        print("1. Start PostgreSQL database (docker-compose up -d postgres)")
        print("2. Ensure database contains user and symptom data")
        print("3. Run: python train_with_real_data.py")
        print("\nTo use with synthetic data (fallback):")
        print("1. Run: python -c \"from src.training.train_models import ModelTrainer; ModelTrainer().train_all_models(use_synthetic_data=True)\"")
        return True
    else:
        print("✗ FAILED: Training pipeline still defaults to synthetic data")
        return False

if __name__ == "__main__":
    success = validate_real_data_setup()
    sys.exit(0 if success else 1)