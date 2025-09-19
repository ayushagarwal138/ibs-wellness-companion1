"""
External Dataset Configuration System

Manages configuration for external dataset sources, API credentials,
and dataset-specific settings for the IBS ML training pipeline.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DatasetConfig:
    """Configuration for a single external dataset."""
    name: str
    source: str  # 'kaggle', 'url', 'local'
    dataset_id: str  # Kaggle dataset ID or URL
    description: str
    enabled: bool = True
    cache_days: int = 7
    columns_mapping: Dict[str, str] = None
    processing_options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.columns_mapping is None:
            self.columns_mapping = {}
        if self.processing_options is None:
            self.processing_options = {}


@dataclass
class APICredentials:
    """API credentials for external data sources."""
    kaggle_username: Optional[str] = None
    kaggle_key: Optional[str] = None
    
    @classmethod
    def from_environment(cls) -> 'APICredentials':
        """Load credentials from environment variables."""
        return cls(
            kaggle_username=os.getenv('KAGGLE_USERNAME'),
            kaggle_key=os.getenv('KAGGLE_KEY')
        )
    
    def is_kaggle_configured(self) -> bool:
        """Check if Kaggle credentials are available."""
        return bool(self.kaggle_username and self.kaggle_key)


class ExternalDataConfig:
    """
    Configuration manager for external datasets.
    
    Handles loading, saving, and managing configurations for external data sources.
    """
    
    def __init__(self, config_file: str = "external_data_config.json"):
        self.config_file = Path(config_file)
        self.datasets: Dict[str, DatasetConfig] = {}
        self.credentials = APICredentials.from_environment()
        self.global_settings = {
            'default_cache_days': 7,
            'max_dataset_size_mb': 500,
            'auto_update_datasets': False,
            'data_directory': 'external_datasets'
        }
        
        # Load existing configuration
        self.load_config()
        
        # Initialize with default datasets if none exist
        if not self.datasets:
            self._initialize_default_datasets()
    
    def _initialize_default_datasets(self):
        """Initialize with default IBS-related datasets."""
        logger.info("Initializing default external dataset configurations")
        
        # Gut Microbiome Dataset
        self.datasets['gut_microbiome'] = DatasetConfig(
            name='gut_microbiome',
            source='kaggle',
            dataset_id='paultimothymooney/microbiome-data',
            description='Gut microbiome composition data for IBS research',
            columns_mapping={
                'sample_id': 'user_id',
                'bacteria_count': 'microbiome_diversity',
                'condition': 'ibs_status',
                'shannon_index': 'diversity_index',
                'firmicutes_ratio': 'firmicutes_pct'
            },
            processing_options={
                'normalize_diversity': True,
                'filter_low_quality': True,
                'min_sample_size': 100
            }
        )
        
        # Dietary Patterns Dataset
        self.datasets['dietary_patterns'] = DatasetConfig(
            name='dietary_patterns',
            source='kaggle',
            dataset_id='shashwatwork/food-nutrition-dataset',
            description='Nutritional information and dietary patterns',
            columns_mapping={
                'food_item': 'food_name',
                'calories': 'calories_per_serving',
                'fiber': 'fiber_content',
                'protein': 'protein_content',
                'carbs': 'carbohydrate_content'
            },
            processing_options={
                'normalize_nutrients': True,
                'filter_incomplete': True,
                'add_fodmap_classification': True
            }
        )
        
        # Health Tracking Dataset (adapted for IBS symptoms)
        self.datasets['symptom_tracking'] = DatasetConfig(
            name='symptom_tracking',
            source='kaggle',
            dataset_id='uciml/pima-indians-diabetes-database',
            description='Health tracking data adapted for IBS symptom patterns',
            columns_mapping={
                'glucose': 'symptom_severity',
                'bloodpressure': 'stress_level',
                'skinthickness': 'bloating_level',
                'insulin': 'pain_intensity',
                'bmi': 'health_index',
                'outcome': 'flare_up'
            },
            processing_options={
                'scale_to_ibs_range': True,
                'add_temporal_patterns': True,
                'correlate_with_diet': True
            }
        )
        
        # IBS Clinical Trial Dataset (if available)
        self.datasets['clinical_trials'] = DatasetConfig(
            name='clinical_trials',
            source='kaggle',
            dataset_id='ibs-clinical-data/ibs-treatment-outcomes',
            description='IBS clinical trial data with treatment outcomes',
            enabled=False,  # Disabled by default as dataset may not exist
            columns_mapping={
                'patient_id': 'user_id',
                'treatment': 'intervention_type',
                'severity_before': 'baseline_severity',
                'severity_after': 'outcome_severity',
                'duration': 'treatment_duration'
            },
            processing_options={
                'calculate_improvement': True,
                'filter_completed_trials': True,
                'normalize_outcomes': True
            }
        )
        
        # Food Sensitivity Dataset
        self.datasets['food_sensitivities'] = DatasetConfig(
            name='food_sensitivities',
            source='kaggle',
            dataset_id='food-allergy-research/food-sensitivity-data',
            description='Food sensitivity and intolerance patterns',
            enabled=False,  # Disabled by default
            columns_mapping={
                'food_type': 'trigger_food',
                'reaction_severity': 'sensitivity_score',
                'symptoms': 'reaction_symptoms',
                'individual_id': 'user_id'
            },
            processing_options={
                'categorize_foods': True,
                'severity_normalization': True,
                'symptom_mapping': True
            }
        )
    
    def load_config(self):
        """Load configuration from file."""
        if not self.config_file.exists():
            logger.info(f"Configuration file {self.config_file} not found, using defaults")
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Load global settings
            if 'global_settings' in config_data:
                self.global_settings.update(config_data['global_settings'])
            
            # Load dataset configurations
            if 'datasets' in config_data:
                for name, dataset_data in config_data['datasets'].items():
                    self.datasets[name] = DatasetConfig(**dataset_data)
            
            logger.info(f"Loaded configuration for {len(self.datasets)} datasets")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            config_data = {
                'global_settings': self.global_settings,
                'datasets': {name: asdict(config) for name, config in self.datasets.items()},
                'last_updated': datetime.now().isoformat()
            }
            
            # Create directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get_enabled_datasets(self) -> Dict[str, DatasetConfig]:
        """Get only enabled datasets."""
        return {name: config for name, config in self.datasets.items() if config.enabled}
    
    def enable_dataset(self, dataset_name: str):
        """Enable a specific dataset."""
        if dataset_name in self.datasets:
            self.datasets[dataset_name].enabled = True
            logger.info(f"Enabled dataset: {dataset_name}")
        else:
            logger.warning(f"Dataset not found: {dataset_name}")
    
    def disable_dataset(self, dataset_name: str):
        """Disable a specific dataset."""
        if dataset_name in self.datasets:
            self.datasets[dataset_name].enabled = False
            logger.info(f"Disabled dataset: {dataset_name}")
        else:
            logger.warning(f"Dataset not found: {dataset_name}")
    
    def add_custom_dataset(self, config: DatasetConfig):
        """Add a custom dataset configuration."""
        self.datasets[config.name] = config
        logger.info(f"Added custom dataset: {config.name}")
    
    def update_credentials(self, kaggle_username: str = None, kaggle_key: str = None):
        """Update API credentials."""
        if kaggle_username:
            self.credentials.kaggle_username = kaggle_username
            os.environ['KAGGLE_USERNAME'] = kaggle_username
        
        if kaggle_key:
            self.credentials.kaggle_key = kaggle_key
            os.environ['KAGGLE_KEY'] = kaggle_key
        
        logger.info("Updated API credentials")
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the current configuration."""
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'dataset_status': {}
        }
        
        # Check credentials
        if not self.credentials.is_kaggle_configured():
            validation_results['warnings'].append("Kaggle credentials not configured")
        
        # Check each dataset
        for name, config in self.datasets.items():
            dataset_status = {'enabled': config.enabled, 'issues': []}
            
            if config.enabled:
                # Check required fields
                if not config.dataset_id:
                    dataset_status['issues'].append("Missing dataset_id")
                    validation_results['valid'] = False
                
                if config.source == 'kaggle' and not self.credentials.is_kaggle_configured():
                    dataset_status['issues'].append("Kaggle credentials required but not configured")
                
                # Check cache settings
                if config.cache_days < 0:
                    dataset_status['issues'].append("Invalid cache_days value")
            
            validation_results['dataset_status'][name] = dataset_status
        
        return validation_results
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """Get information about all configured datasets."""
        info = {
            'total_datasets': len(self.datasets),
            'enabled_datasets': len(self.get_enabled_datasets()),
            'credentials_configured': self.credentials.is_kaggle_configured(),
            'global_settings': self.global_settings,
            'datasets': {}
        }
        
        for name, config in self.datasets.items():
            info['datasets'][name] = {
                'description': config.description,
                'source': config.source,
                'enabled': config.enabled,
                'cache_days': config.cache_days,
                'has_column_mapping': bool(config.columns_mapping),
                'has_processing_options': bool(config.processing_options)
            }
        
        return info


# Global configuration instance
external_config = ExternalDataConfig()


def get_config() -> ExternalDataConfig:
    """Get the global external data configuration."""
    return external_config


if __name__ == "__main__":
    # Example usage and testing
    config = ExternalDataConfig()
    
    print("External Dataset Configuration")
    print("=" * 40)
    
    # Display configuration info
    info = config.get_dataset_info()
    print(f"Total datasets: {info['total_datasets']}")
    print(f"Enabled datasets: {info['enabled_datasets']}")
    print(f"Credentials configured: {info['credentials_configured']}")
    
    print("\nConfigured datasets:")
    for name, dataset_info in info['datasets'].items():
        status = "✓" if dataset_info['enabled'] else "✗"
        print(f"  {status} {name}: {dataset_info['description']}")
    
    # Validate configuration
    validation = config.validate_configuration()
    print(f"\nConfiguration valid: {validation['valid']}")
    
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    if validation['errors']:
        print("Errors:")
        for error in validation['errors']:
            print(f"  - {error}")