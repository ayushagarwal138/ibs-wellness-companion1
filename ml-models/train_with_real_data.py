#!/usr/bin/env python3
"""
Train IBS ML models using real database data.
This script connects to the PostgreSQL database and trains models with actual user data.
"""

import os
import sys
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / "src"))

from training.train_models import ModelTrainer
from training.database import get_database_connection, check_database_availability

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_data_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main training function using real database data."""
    logger.info("Starting IBS ML model training with real database data...")
    
    try:
        # Step 1: Check database availability
        logger.info("Checking database availability...")
        if not check_database_availability():
            logger.error("Database is not available or lacks sufficient data.")
            logger.info("Please ensure:")
            logger.info("1. PostgreSQL is running")
            logger.info("2. Database contains user and symptom data")
            logger.info("3. Database connection string is correct")
            return False
        
        # Step 2: Get database connection
        logger.info("Establishing database connection...")
        db = get_database_connection()
        db_connection = db.get_connection()
        
        # Step 3: Get table information
        table_info = db.get_table_info()
        logger.info("Available tables:")
        for table, info in table_info.items():
            if info['available']:
                logger.info(f"  - {table}: {info['row_count']} rows")
            else:
                logger.warning(f"  - {table}: Not available ({info.get('error', 'Unknown error')})")
        
        # Step 4: Initialize trainer and train models
        logger.info("Initializing model trainer...")
        trainer = ModelTrainer(output_dir="trained_models_real_data")
        
        logger.info("Training models with real database data...")
        results = trainer.train_all_models(
            use_synthetic_data=False,  # Use real data
            db_connection=db_connection
        )
        
        # Step 5: Display results
        logger.info("Training completed successfully!")
        logger.info("Training Results Summary:")
        logger.info(f"  - Total samples processed: {results.get('total_samples', 'N/A')}")
        logger.info(f"  - Training duration: {results.get('training_duration', 'N/A')}")
        
        if 'model_performance' in results:
            logger.info("Model Performance:")
            for model_name, performance in results['model_performance'].items():
                logger.info(f"  - {model_name}: {performance}")
        
        # Step 6: Close database connection
        db.close()
        
        logger.info("Real data training completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Training failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)