"""
External Dataset Loader for IBS Wellness Companion ML Models

This module provides functionality to download and process external datasets
from sources like Kaggle to enhance the training data for IBS prediction models.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict

import requests
import zipfile

# Import kaggle and opendatasets only when needed to avoid authentication issues
try:
    import kaggle
    KAGGLE_AVAILABLE = True
except (ImportError, OSError):
    KAGGLE_AVAILABLE = False

try:
    import opendatasets as od
    OPENDATASETS_AVAILABLE = True
except ImportError:
    OPENDATASETS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExternalDataLoader:
    """
    Handles downloading and processing external datasets for IBS research.
    
    Supports multiple data sources including Kaggle datasets and direct downloads.
    """
    
    def __init__(self, data_dir: str = "external_datasets", cache_days: int = 7):
        """
        Initialize the external data loader.
        
        Args:
            data_dir: Directory to store downloaded datasets
            cache_days: Number of days to cache datasets before re-downloading
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.cache_days = cache_days
        
        # Popular IBS-related datasets configuration
        self.dataset_configs = {
            'gut_microbiome': {
                'source': 'kaggle',
                'dataset_id': 'paultimothymooney/microbiome-data',
                'description': 'Gut microbiome composition data',
                'columns_mapping': {
                    'sample_id': 'user_id',
                    'bacteria_count': 'microbiome_diversity',
                    'condition': 'ibs_status'
                }
            },
            'dietary_patterns': {
                'source': 'kaggle', 
                'dataset_id': 'shashwatwork/food-nutrition-dataset',
                'description': 'Nutritional information and dietary patterns',
                'columns_mapping': {
                    'food_item': 'food_name',
                    'calories': 'calories_per_serving',
                    'fiber': 'fiber_content'
                }
            },
            'symptom_tracking': {
                'source': 'kaggle',
                'dataset_id': 'uciml/pima-indians-diabetes-database',
                'description': 'Health tracking data (adapted for IBS symptoms)',
                'columns_mapping': {
                    'glucose': 'symptom_severity',
                    'bloodpressure': 'stress_level',
                    'outcome': 'flare_up'
                }
            }
        }
    
    def setup_kaggle_credentials(self, username: str = None, key: str = None) -> bool:
        """
        Setup Kaggle API credentials with proper authentication handling.
        
        Args:
            username: Kaggle username
            key: Kaggle API key
            
        Returns:
            bool: True if Kaggle API is available and authenticated
        """
        if not KAGGLE_AVAILABLE:
            self.logger.warning("Kaggle package not available")
            return False
            
        try:
            # Check if credentials are provided as parameters
            if username and key:
                os.environ['KAGGLE_USERNAME'] = username
                os.environ['KAGGLE_KEY'] = key
            
            # Check if credentials are available
            if not self._check_kaggle_credentials():
                self.logger.warning("Kaggle credentials not found")
                return False
                
            # Initialize Kaggle API
            from kaggle.api.kaggle_api_extended import KaggleApi
            self.kaggle_api = KaggleApi()
            self.kaggle_api.authenticate()
            
            self.logger.info("Kaggle API authenticated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup Kaggle API: {e}")
            return False
    
    def _check_kaggle_credentials(self) -> bool:
        """
        Check if Kaggle credentials are available.
        
        Returns:
            bool: True if credentials are found
        """
        # Check environment variables
        if os.getenv('KAGGLE_USERNAME') and os.getenv('KAGGLE_KEY'):
            return True
            
        # Check kaggle.json file
        kaggle_config_path = Path.home() / '.kaggle' / 'kaggle.json'
        if kaggle_config_path.exists():
            return True
            
        return False
    
    def is_dataset_cached(self, dataset_name: str) -> bool:
        """
        Check if dataset is cached and still valid.
        
        Args:
            dataset_name: Name of the dataset
            
        Returns:
            bool: True if dataset is cached and valid
        """
        dataset_path = self.data_dir / f"{dataset_name}.csv"
        metadata_path = self.data_dir / f"{dataset_name}_metadata.json"
        
        if not (dataset_path.exists() and metadata_path.exists()):
            return False
        
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            download_date = datetime.fromisoformat(metadata['download_date'])
            cache_expiry = download_date + timedelta(days=self.cache_days)
            
            return datetime.now() < cache_expiry
            
        except Exception as e:
            logger.warning(f"Error checking cache for {dataset_name}: {e}")
            return False
    
    def download_kaggle_dataset(self, dataset_id: str, dataset_name: str) -> Optional[pd.DataFrame]:
        """
        Download a dataset from Kaggle.
        
        Args:
            dataset_id: Kaggle dataset identifier (e.g., 'username/dataset-name')
            dataset_name: Local name for the dataset
            
        Returns:
            pd.DataFrame: Downloaded dataset or None if failed
        """
        if not KAGGLE_AVAILABLE:
            logger.warning("Kaggle package not available")
            return None
            
        if not hasattr(self, 'kaggle_api') or self.kaggle_api is None:
            if not self.setup_kaggle_credentials():
                return None
        
        try:
            # Check if dataset is cached
            if self.is_dataset_cached(dataset_name):
                logger.info(f"Loading cached dataset: {dataset_name}")
                return pd.read_csv(self.data_dir / f"{dataset_name}.csv")
            
            logger.info(f"Downloading Kaggle dataset: {dataset_id}")
            
            # Download dataset
            download_path = self.data_dir / "temp"
            download_path.mkdir(exist_ok=True)
            
            self.kaggle_api.dataset_download_files(
                dataset_id, 
                path=str(download_path), 
                unzip=True
            )
            
            # Find CSV files in downloaded content
            csv_files = list(download_path.glob("*.csv"))
            if not csv_files:
                logger.error(f"No CSV files found in dataset {dataset_id}")
                return None
            
            # Load the first CSV file (or combine multiple if needed)
            df = pd.read_csv(csv_files[0])
            
            # Save to cache
            df.to_csv(self.data_dir / f"{dataset_name}.csv", index=False)
            
            # Save metadata
            metadata = {
                'dataset_id': dataset_id,
                'download_date': datetime.now().isoformat(),
                'rows': len(df),
                'columns': list(df.columns)
            }
            
            with open(self.data_dir / f"{dataset_name}_metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Cleanup temp directory
            import shutil
            shutil.rmtree(download_path)
            
            logger.info(f"Successfully downloaded {dataset_name}: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Failed to download dataset {dataset_id}: {e}")
            return None
    
    def process_dataset(self, df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
        """
        Process and standardize external dataset for IBS model training.
        
        Args:
            df: Raw dataset
            dataset_name: Name of the dataset for processing rules
            
        Returns:
            pd.DataFrame: Processed dataset
        """
        if dataset_name not in self.dataset_configs:
            logger.warning(f"No processing configuration for {dataset_name}")
            return df
        
        config = self.dataset_configs[dataset_name]
        processed_df = df.copy()
        
        # Apply column mapping
        if 'columns_mapping' in config:
            mapping = config['columns_mapping']
            # Only rename columns that exist in the dataset
            existing_mapping = {old: new for old, new in mapping.items() if old in processed_df.columns}
            processed_df = processed_df.rename(columns=existing_mapping)
        
        # Dataset-specific processing
        if dataset_name == 'gut_microbiome':
            processed_df = self._process_microbiome_data(processed_df)
        elif dataset_name == 'dietary_patterns':
            processed_df = self._process_dietary_data(processed_df)
        elif dataset_name == 'symptom_tracking':
            processed_df = self._process_symptom_data(processed_df)
        
        # General data cleaning
        processed_df = self._clean_dataset(processed_df)
        
        logger.info(f"Processed {dataset_name}: {len(processed_df)} rows after cleaning")
        return processed_df
    
    def _process_microbiome_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process microbiome-specific data."""
        # Normalize microbiome diversity scores
        if 'microbiome_diversity' in df.columns:
            df['microbiome_diversity'] = (df['microbiome_diversity'] - df['microbiome_diversity'].mean()) / df['microbiome_diversity'].std()
        
        # Convert IBS status to binary
        if 'ibs_status' in df.columns:
            df['ibs_status'] = df['ibs_status'].map({'healthy': 0, 'ibs': 1, 'control': 0, 'case': 1}).fillna(0)
        
        return df
    
    def _process_dietary_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process dietary pattern data."""
        # Normalize nutritional values
        numeric_cols = ['calories_per_serving', 'fiber_content']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(df[col].median())
        
        return df
    
    def _process_symptom_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process symptom tracking data."""
        # Normalize symptom severity and stress levels
        if 'symptom_severity' in df.columns:
            df['symptom_severity'] = np.clip(df['symptom_severity'] / 100, 0, 1)
        
        if 'stress_level' in df.columns:
            df['stress_level'] = np.clip(df['stress_level'] / 120, 0, 1)
        
        return df
    
    def _clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply general data cleaning."""
        # Remove rows with too many missing values
        threshold = len(df.columns) * 0.5
        df = df.dropna(thresh=threshold)
        
        # Remove duplicate rows
        df = df.drop_duplicates()
        
        # Handle remaining missing values
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 'unknown')
        
        return df
    
    def load_all_external_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Load all configured external datasets.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of dataset name to DataFrame
        """
        datasets = {}
        
        # Setup Kaggle credentials
        if not self.setup_kaggle_credentials():
            logger.warning("Kaggle credentials not configured. Skipping Kaggle datasets.")
            return datasets
        
        for dataset_name, config in self.dataset_configs.items():
            try:
                if config['source'] == 'kaggle':
                    df = self.download_kaggle_dataset(config['dataset_id'], dataset_name)
                    if df is not None:
                        processed_df = self.process_dataset(df, dataset_name)
                        datasets[dataset_name] = processed_df
                        logger.info(f"Loaded external dataset: {dataset_name}")
                
            except Exception as e:
                logger.error(f"Failed to load dataset {dataset_name}: {e}")
                continue
        
        logger.info(f"Successfully loaded {len(datasets)} external datasets")
        return datasets
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """
        Get information about available datasets.
        
        Returns:
            Dict: Information about configured datasets
        """
        info = {}
        for name, config in self.dataset_configs.items():
            info[name] = {
                'description': config['description'],
                'source': config['source'],
                'cached': self.is_dataset_cached(name)
            }
        return info


if __name__ == "__main__":
    # Example usage
    loader = ExternalDataLoader()
    
    # Print available datasets
    print("Available external datasets:")
    for name, info in loader.get_dataset_info().items():
        print(f"- {name}: {info['description']} (cached: {info['cached']})")
    
    # Load all datasets
    datasets = loader.load_all_external_datasets()
    
    for name, df in datasets.items():
        print(f"\n{name} dataset shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")