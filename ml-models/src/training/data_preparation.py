"""
Data Preparation Module

Handles data preprocessing, feature engineering, and preparation for ML model training.
Includes support for external dataset integration from sources like Kaggle.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from .external_data_loader import ExternalDataLoader

logger = logging.getLogger(__name__)


class DataPreparator:
    """
    Handles data preparation and feature engineering for IBS ML models.
    """
    
    def __init__(self, use_external_data: bool = False, external_data_dir: str = "external_datasets"):
        self.scalers = {}
        self.encoders = {}
        self.use_external_data = use_external_data
        self.external_loader = ExternalDataLoader(data_dir=external_data_dir) if use_external_data else None
        
    def load_data_from_db(self, db_connection) -> Dict[str, pd.DataFrame]:
        """
        Load data from database tables.
        
        Args:
            db_connection: Database connection object
            
        Returns:
            Dictionary of DataFrames for each table
        """
        logger.info("Loading data from database...")
        
        tables = {
            'users': 'SELECT * FROM users',
            'symptoms': 'SELECT * FROM symptoms',  # Updated table name
            'diet_logs': 'SELECT * FROM diet_logs',
            'medications': 'SELECT * FROM medications',
            'medication_logs': 'SELECT * FROM medication_logs',
            'food_items': 'SELECT * FROM food_items'
        }
        
        data = {}
        for table_name, query in tables.items():
            try:
                data[table_name] = pd.read_sql(query, db_connection)
                logger.info(f"Loaded {len(data[table_name])} records from {table_name}")
            except Exception as e:
                logger.warning(f"Could not load {table_name}: {e}")
                data[table_name] = pd.DataFrame()
                
        return data
        
    def create_synthetic_data(self, n_users: int = 100, days_per_user: int = 90) -> Dict[str, pd.DataFrame]:
        """Create synthetic data for training ML models with enhanced features from research datasets."""
        logger.info(f"Creating synthetic data for {n_users} users over {days_per_user} days")
        
        # Generate users with enhanced profiles based on research insights
        users = []
        for i in range(n_users):
            # Basic demographics
            age = np.random.randint(18, 80)
            gender = np.random.choice(['male', 'female', 'other'])
            ibs_type = np.random.choice(['IBS-D', 'IBS-C', 'IBS-M', 'IBS-U'])
            
            # Microbiome diversity features (inspired by gut microbiome research)
            # Based on findings that IBS patients have altered microbiome diversity
            microbiome_diversity_index = np.random.normal(2.5, 0.8)  # Shannon diversity index
            bacteroidetes_firmicutes_ratio = np.random.normal(0.6, 0.3)  # Key ratio in IBS
            beneficial_bacteria_count = np.random.normal(45, 15)  # Percentage of beneficial bacteria
            pathogenic_bacteria_count = np.random.normal(15, 8)   # Percentage of pathogenic bacteria
            
            # Psychological factors (from 988 patients clustering study)
            anxiety_score = np.random.uniform(0, 21)  # GAD-7 scale
            depression_score = np.random.uniform(0, 27)  # PHQ-9 scale
            stress_sensitivity = np.random.uniform(0.5, 2.0)
            
            # Dietary sensitivity patterns
            fodmap_sensitivity = np.random.uniform(0.2, 0.9)
            gluten_sensitivity = np.random.choice([True, False], p=[0.3, 0.7])
            lactose_intolerance = np.random.choice([True, False], p=[0.4, 0.6])
            
            users.append({
                'id': f'user_{i+1}',
                'age': age,
                'gender': gender,
                'ibs_type': ibs_type,
                'stress_sensitivity': stress_sensitivity,
                'microbiome_diversity': max(0, microbiome_diversity_index),
                'bf_ratio': max(0.1, bacteroidetes_firmicutes_ratio),
                'beneficial_bacteria_pct': max(10, min(80, beneficial_bacteria_count)),
                'pathogenic_bacteria_pct': max(5, min(40, pathogenic_bacteria_count)),
                'anxiety_score': anxiety_score,
                'depression_score': depression_score,
                'fodmap_sensitivity': fodmap_sensitivity,
                'gluten_sensitivity': gluten_sensitivity,
                'lactose_intolerance': lactose_intolerance,
                'created_at': datetime.now()
            })
            
        users_df = pd.DataFrame(users)
        
        # Generate symptom logs with microbiome and psychological correlations
        symptom_logs = []
        for user in users:
            user_id = user['id']
            base_severity = np.random.uniform(3, 7)
            stress_sensitivity = user['stress_sensitivity']
            
            # Microbiome impact on symptoms
            microbiome_factor = (5 - user['microbiome_diversity']) * 0.5  # Lower diversity = higher symptoms
            pathogenic_factor = user['pathogenic_bacteria_pct'] / 100 * 2  # Higher pathogenic = worse symptoms
            
            # Psychological impact
            anxiety_factor = user['anxiety_score'] / 21 * 2  # Normalized anxiety impact
            depression_factor = user['depression_score'] / 27 * 1.5  # Normalized depression impact
            
            for day in range(days_per_user):
                date = datetime.now() - timedelta(days=days_per_user - day)
                
                # Daily variations
                daily_stress = np.random.uniform(1, 10)
                sleep_quality = np.random.uniform(1, 10)
                
                # Calculate severity with enhanced correlations
                severity = base_severity + (daily_stress - 5) * stress_sensitivity * 0.3
                severity += (5 - sleep_quality) * 0.2
                severity += microbiome_factor  # Microbiome contribution
                severity += pathogenic_factor  # Pathogenic bacteria contribution
                severity += anxiety_factor * 0.3  # Anxiety contribution
                severity += depression_factor * 0.2  # Depression contribution
                severity += np.random.normal(0, 1)  # Random variation
                severity = max(1, min(10, severity))  # Clamp to 1-10
                
                # Bowel movement patterns influenced by microbiome
                bm_type_probs = [0.3, 0.3, 0.2, 0.2]  # normal, loose, hard, watery
                if user['microbiome_diversity'] < 2.0:  # Low diversity
                    bm_type_probs = [0.15, 0.45, 0.25, 0.15]  # More loose/irregular
                
                symptom_logs.append({
                    'id': f'symptom_{user_id}_{day}',
                    'user_id': user_id,
                    'severity_score': round(severity, 1),
                    'pain_severity': max(1, min(10, severity + np.random.normal(0, 0.5))),
                    'pain_level': max(1, min(10, severity + np.random.normal(0, 0.5))),
                    'bloating_level': max(1, min(10, severity + np.random.normal(0, 0.8))),
                    'bowel_movement_type': np.random.choice(['normal', 'loose', 'hard', 'watery'], p=bm_type_probs),
                    'stress_level': daily_stress,
                    'sleep_quality': sleep_quality,
                    'exercise_minutes': max(0, np.random.normal(30, 20)),
                    'mood_score': max(1, min(10, 7 - depression_factor)),  # Mood inversely related to depression
                    'energy_level': max(1, min(10, 6 - anxiety_factor * 0.5)),  # Energy affected by anxiety
                    'notes': f'Day {day} symptoms',
                    'logged_at': date
                })
                
        symptom_logs_df = pd.DataFrame(symptom_logs)
        
        # Generate diet logs with enhanced sensitivity modeling
        diet_logs = []
        foods = [
            {'name': 'Rice', 'fodmap_level': 'low', 'trigger_probability': 0.1, 'gluten_free': True, 'lactose_free': True},
            {'name': 'Wheat bread', 'fodmap_level': 'high', 'trigger_probability': 0.7, 'gluten_free': False, 'lactose_free': True},
            {'name': 'Banana', 'fodmap_level': 'low', 'trigger_probability': 0.05, 'gluten_free': True, 'lactose_free': True},
            {'name': 'Apple', 'fodmap_level': 'high', 'trigger_probability': 0.4, 'gluten_free': True, 'lactose_free': True},
            {'name': 'Chicken', 'fodmap_level': 'low', 'trigger_probability': 0.1, 'gluten_free': True, 'lactose_free': True},
            {'name': 'Beans', 'fodmap_level': 'high', 'trigger_probability': 0.8, 'gluten_free': True, 'lactose_free': True},
            {'name': 'Carrots', 'fodmap_level': 'low', 'trigger_probability': 0.05, 'gluten_free': True, 'lactose_free': True},
            {'name': 'Onions', 'fodmap_level': 'high', 'trigger_probability': 0.9, 'gluten_free': True, 'lactose_free': True},
            {'name': 'Spinach', 'fodmap_level': 'low', 'trigger_probability': 0.1, 'gluten_free': True, 'lactose_free': True},
            {'name': 'Dairy milk', 'fodmap_level': 'high', 'trigger_probability': 0.6, 'gluten_free': True, 'lactose_free': False},
            {'name': 'Yogurt', 'fodmap_level': 'medium', 'trigger_probability': 0.4, 'gluten_free': True, 'lactose_free': False},
            {'name': 'Pasta', 'fodmap_level': 'medium', 'trigger_probability': 0.5, 'gluten_free': False, 'lactose_free': True},
            {'name': 'Garlic', 'fodmap_level': 'high', 'trigger_probability': 0.85, 'gluten_free': True, 'lactose_free': True},
            {'name': 'Broccoli', 'fodmap_level': 'medium', 'trigger_probability': 0.3, 'gluten_free': True, 'lactose_free': True}
        ]
        
        for user in users:
            user_id = user['id']
            
            # Personalized trigger foods based on user sensitivities
            user_triggers = []
            for food in foods:
                trigger_prob = food['trigger_probability']
                
                # Adjust probability based on user sensitivities
                if food['fodmap_level'] == 'high':
                    trigger_prob *= user['fodmap_sensitivity']
                elif food['fodmap_level'] == 'medium':
                    trigger_prob *= (user['fodmap_sensitivity'] * 0.6)
                    
                if not food['gluten_free'] and user['gluten_sensitivity']:
                    trigger_prob *= 1.5
                    
                if not food['lactose_free'] and user['lactose_intolerance']:
                    trigger_prob *= 1.3
                    
                # Microbiome diversity affects food tolerance
                if user['microbiome_diversity'] < 2.0:  # Low diversity
                    trigger_prob *= 1.2
                    
                if np.random.random() < min(trigger_prob, 0.95):
                    user_triggers.append(food['name'])
            
            for day in range(days_per_user):
                date = datetime.now() - timedelta(days=days_per_user - day)
                
                # 3 meals per day
                for meal_num in range(3):
                    meal_time = date.replace(hour=7 + meal_num * 5, minute=np.random.randint(0, 60))
                    food = np.random.choice(foods)
                    
                    is_trigger = food['name'] in user_triggers
                    
                    diet_logs.append({
                        'id': f'diet_{user_id}_{day}_{meal_num}',
                        'user_id': user_id,
                        'food_name': food['name'],
                        'portion_size_g': np.random.uniform(50, 300),
                        'meal_type': ['breakfast', 'lunch', 'dinner'][meal_num],
                        'fodmap_level': food['fodmap_level'],
                        'is_known_trigger': is_trigger,
                        'gluten_free': food['gluten_free'],
                        'lactose_free': food['lactose_free'],
                        'preparation_method': np.random.choice(['raw', 'cooked', 'processed']),
                        'logged_at': meal_time
                    })
                    
        diet_logs_df = pd.DataFrame(diet_logs)
        
        # Generate food reactions
        food_reactions = []
        for _, diet_log in diet_logs_df.iterrows():
            if diet_log['is_known_trigger'] and np.random.random() < 0.3:  # 30% chance of logging reaction
                food_reactions.append({
                    'id': f'reaction_{diet_log["id"]}',
                    'user_id': diet_log['user_id'],
                    'diet_log_id': diet_log['id'],
                    'food_id': diet_log['food_name'],  # Simplified
                    'reaction_severity': np.random.uniform(5, 10),
                    'reaction_type': np.random.choice(['bloating', 'pain', 'diarrhea', 'constipation']),
                    'onset_time_minutes': np.random.randint(15, 240),
                    'duration_minutes': np.random.randint(30, 480),
                    'notes': f'Reaction to {diet_log["food_name"]}',
                    'logged_at': diet_log['logged_at'] + timedelta(minutes=np.random.randint(15, 240))
                })
                
        food_reactions_df = pd.DataFrame(food_reactions)
        
        # Generate medication logs
        medications = []
        for user in users:
            user_id = user['id']
            has_medication = np.random.random() < 0.6  # 60% of users have medication
            
            if has_medication:
                for day in range(days_per_user):
                    date = datetime.now() - timedelta(days=days_per_user - day)
                    
                    # Simulate medication adherence (80% average)
                    taken = np.random.random() < 0.8
                    
                    medications.append({
                        'id': f'med_{user_id}_{day}',
                        'user_id': user_id,
                        'medication_name': np.random.choice(['Loperamide', 'Fiber supplement', 'Probiotic']),
                        'dosage': '1 tablet',
                        'medication_taken': taken,
                        'taken_at': date.replace(hour=8, minute=0) if taken else None,
                        'scheduled_time': date.replace(hour=8, minute=0),
                        'notes': 'Daily medication' if taken else 'Missed dose',
                        'logged_at': date
                    })
                    
        medications_df = pd.DataFrame(medications)
        
        return {
            'users': users_df,
            'symptom_logs': symptom_logs_df,
            'diet_logs': diet_logs_df,
            'food_reactions': food_reactions_df,
            'medications': medications_df
        }
        
    def load_external_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Load external datasets using the ExternalDataLoader.
        
        Returns:
            Dictionary of external datasets
        """
        if not self.use_external_data or not self.external_loader:
            logger.info("External data loading is disabled")
            return {}
        
        logger.info("Loading external datasets...")
        return self.external_loader.load_all_external_datasets()
    
    def integrate_external_data(self, internal_data: Dict[str, pd.DataFrame], 
                               external_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Integrate external datasets with internal data.
        
        Args:
            internal_data: Internal database/synthetic data
            external_data: External datasets from Kaggle/other sources
            
        Returns:
            Combined dataset dictionary
        """
        if not external_data:
            logger.info("No external data to integrate")
            return internal_data
        
        logger.info(f"Integrating {len(external_data)} external datasets")
        combined_data = internal_data.copy()
        
        # Integrate microbiome data
        if 'gut_microbiome' in external_data:
            combined_data = self._integrate_microbiome_data(combined_data, external_data['gut_microbiome'])
        
        # Integrate dietary patterns
        if 'dietary_patterns' in external_data:
            combined_data = self._integrate_dietary_data(combined_data, external_data['dietary_patterns'])
        
        # Integrate symptom tracking data
        if 'symptom_tracking' in external_data:
            combined_data = self._integrate_symptom_data(combined_data, external_data['symptom_tracking'])
        
        return combined_data
    
    def _integrate_microbiome_data(self, internal_data: Dict[str, pd.DataFrame], 
                                  microbiome_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Integrate microbiome data with user profiles."""
        if 'users' not in internal_data or internal_data['users'].empty:
            return internal_data
        
        logger.info("Integrating microbiome data with user profiles")
        
        # Sample microbiome data for existing users
        users_df = internal_data['users'].copy()
        n_users = len(users_df)
        
        if len(microbiome_df) > 0:
            # Sample from external microbiome data
            sampled_microbiome = microbiome_df.sample(n=min(n_users, len(microbiome_df)), replace=True).reset_index(drop=True)
            
            # Map microbiome features to users
            if 'microbiome_diversity' in sampled_microbiome.columns:
                users_df['external_microbiome_diversity'] = sampled_microbiome['microbiome_diversity'].values[:n_users]
            
            if 'ibs_status' in sampled_microbiome.columns:
                users_df['external_ibs_indicator'] = sampled_microbiome['ibs_status'].values[:n_users]
        
        internal_data['users'] = users_df
        return internal_data
    
    def _integrate_dietary_data(self, internal_data: Dict[str, pd.DataFrame], 
                               dietary_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Integrate dietary patterns with food items."""
        if 'food_items' not in internal_data:
            internal_data['food_items'] = pd.DataFrame()
        
        logger.info("Integrating dietary pattern data with food items")
        
        # Enhance food items with external nutritional data
        food_items_df = internal_data['food_items'].copy()
        
        if len(dietary_df) > 0 and 'food_name' in dietary_df.columns:
            # Create mapping of external nutritional data
            nutrition_mapping = dietary_df.set_index('food_name').to_dict('index')
            
            # Add nutritional information to existing food items
            for idx, row in food_items_df.iterrows():
                food_name = row.get('name', '').lower()
                
                # Find matching nutrition data
                for ext_food, nutrition in nutrition_mapping.items():
                    if food_name in ext_food.lower() or ext_food.lower() in food_name:
                        if 'calories_per_serving' in nutrition:
                            food_items_df.at[idx, 'external_calories'] = nutrition['calories_per_serving']
                        if 'fiber_content' in nutrition:
                            food_items_df.at[idx, 'external_fiber'] = nutrition['fiber_content']
                        break
        
        internal_data['food_items'] = food_items_df
        return internal_data
    
    def _integrate_symptom_data(self, internal_data: Dict[str, pd.DataFrame], 
                               symptom_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Integrate external symptom tracking data."""
        if 'symptom_logs' not in internal_data or internal_data['symptom_logs'].empty:
            return internal_data
        
        logger.info("Integrating external symptom tracking data")
        
        symptom_logs_df = internal_data['symptom_logs'].copy()
        
        if len(symptom_df) > 0:
            # Add external symptom patterns as additional features
            n_logs = len(symptom_logs_df)
            
            if 'symptom_severity' in symptom_df.columns:
                # Sample external severity patterns
                external_severity = symptom_df['symptom_severity'].sample(n=n_logs, replace=True).reset_index(drop=True)
                symptom_logs_df['external_severity_pattern'] = external_severity.values
            
            if 'stress_level' in symptom_df.columns:
                # Sample external stress patterns
                external_stress = symptom_df['stress_level'].sample(n=n_logs, replace=True).reset_index(drop=True)
                symptom_logs_df['external_stress_pattern'] = external_stress.values
            
            if 'flare_up' in symptom_df.columns:
                # Sample external flare-up patterns
                external_flareup = symptom_df['flare_up'].sample(n=n_logs, replace=True).reset_index(drop=True)
                symptom_logs_df['external_flareup_indicator'] = external_flareup.values
        
        internal_data['symptom_logs'] = symptom_logs_df
        return internal_data

    def prepare_training_data(self, raw_data: Dict[str, pd.DataFrame], include_external: bool = None) -> pd.DataFrame:
        """
        Prepare and merge data for ML model training.
        
        Args:
            raw_data: Dictionary of raw DataFrames
            include_external: Whether to include external datasets (overrides instance setting)
            
        Returns:
            Merged and processed DataFrame ready for training
        """
        logger.info("Preparing training data...")
        
        # Determine if we should use external data
        use_external = include_external if include_external is not None else self.use_external_data
        
        # Load and integrate external data if enabled
        if use_external:
            external_data = self.load_external_datasets()
            raw_data = self.integrate_external_data(raw_data, external_data)
        
        # Start with symptom logs as the base
        training_data = raw_data['symptom_logs'].copy()
        
        # Extract date from logged_at timestamp
        training_data['date'] = pd.to_datetime(training_data['logged_at']).dt.date
        
        # Add user information
        if not raw_data['users'].empty:
            training_data = training_data.merge(
                raw_data['users'][['id', 'age', 'gender', 'ibs_type']],
                left_on='user_id', right_on='id', how='left', suffixes=('', '_user')
            )
            
        # Add diet information (aggregate by day)
        if not raw_data['diet_logs'].empty:
            diet_daily = self._aggregate_diet_by_day(raw_data['diet_logs'])
            training_data = training_data.merge(
                diet_daily, on=['user_id', 'date'], how='left'
            )
            
        # Add medication information
        if not raw_data['medications'].empty:
            med_daily = self._aggregate_medications_by_day(raw_data['medications'])
            training_data = training_data.merge(
                med_daily, on=['user_id', 'date'], how='left'
            )
            
        # Add food reaction information
        if not raw_data['food_reactions'].empty:
            reaction_daily = self._aggregate_reactions_by_day(raw_data['food_reactions'])
            training_data = training_data.merge(
                reaction_daily, on=['user_id', 'date'], how='left'
            )
            
        # Feature engineering
        training_data = self._engineer_features(training_data)
        
        # Create fodmap_level column for model compatibility
        if 'high_fodmap_count' in training_data.columns:
            training_data['fodmap_level'] = training_data['high_fodmap_count'].apply(
                lambda x: 'high' if x > 0 else 'low'
            )
        
        # Add is_known_trigger column from trigger_food_count
        if 'trigger_food_count' in training_data.columns:
            training_data['is_known_trigger'] = training_data['trigger_food_count'] > 0
        
        # Clean and fill missing values
        training_data = self._clean_data(training_data)
        
        logger.info(f"Prepared training data with {len(training_data)} samples and {len(training_data.columns)} features")
        return training_data
        
    def _aggregate_diet_by_day(self, diet_logs: pd.DataFrame) -> pd.DataFrame:
        """Aggregate diet logs by user and day."""
        diet_logs['date'] = pd.to_datetime(diet_logs['logged_at']).dt.date
        diet_logs['meal_time_hour'] = pd.to_datetime(diet_logs['logged_at']).dt.hour
        
        daily_diet = diet_logs.groupby(['user_id', 'date']).agg({
            'portion_size_g': 'sum',
            'meal_time_hour': 'std',
            'fodmap_level': lambda x: (x == 'high').sum(),
            'is_known_trigger': 'sum'
        }).reset_index()
        
        daily_diet.columns = ['user_id', 'date', 'total_portion_g', 'meal_timing_std', 
                             'high_fodmap_count', 'trigger_food_count']
        
        return daily_diet
        
    def _aggregate_medications_by_day(self, medications: pd.DataFrame) -> pd.DataFrame:
        """Aggregate medication logs by user and day."""
        medications['date'] = pd.to_datetime(medications['logged_at']).dt.date
        
        daily_meds = medications.groupby(['user_id', 'date']).agg({
            'medication_taken': ['sum', 'count']
        }).reset_index()
        
        daily_meds.columns = ['user_id', 'date', 'medications_taken', 'medications_scheduled']
        daily_meds['medication_adherence_rate'] = daily_meds['medications_taken'] / daily_meds['medications_scheduled']
        
        return daily_meds[['user_id', 'date', 'medication_adherence_rate']]
        
    def _aggregate_reactions_by_day(self, reactions: pd.DataFrame) -> pd.DataFrame:
        """Aggregate food reactions by user and day."""
        reactions['date'] = pd.to_datetime(reactions['logged_at']).dt.date
        
        daily_reactions = reactions.groupby(['user_id', 'date']).agg({
            'reaction_severity': 'mean',
            'id': 'count'
        }).reset_index()
        
        daily_reactions.columns = ['user_id', 'date', 'avg_reaction_severity', 'reaction_count']
        
        return daily_reactions
        
    def _engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Engineer additional features for ML models with research-based enhancements."""
        logger.info("Engineering features with microbiome and psychological insights...")
        
        # Convert logged_at to datetime if it's not already
        if 'logged_at' in data.columns:
            data['logged_at'] = pd.to_datetime(data['logged_at'])
            data['date'] = data['logged_at'].dt.date
            data['hour_of_day'] = data['logged_at'].dt.hour
            data['day_of_week'] = data['logged_at'].dt.dayofweek
            data['is_weekend'] = data['day_of_week'].isin([5, 6])
            data['month'] = data['logged_at'].dt.month
            
        # Encode categorical variables
        categorical_columns = ['gender', 'ibs_type', 'bowel_movement_type']
        for col in categorical_columns:
            if col in data.columns:
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    data[f'{col}_encoded'] = self.encoders[col].fit_transform(data[col].fillna('unknown'))
                else:
                    data[f'{col}_encoded'] = self.encoders[col].transform(data[col].fillna('unknown'))
                    
        # Rolling averages for temporal patterns
        if 'severity_score' in data.columns:
            data = data.sort_values(['user_id', 'logged_at'])
            data['severity_7day_avg'] = data.groupby('user_id')['severity_score'].rolling(
                window=7, min_periods=1
            ).mean().reset_index(0, drop=True)
            
            data['severity_trend'] = data.groupby('user_id')['severity_score'].diff()
            
        # Enhanced interaction features based on research findings
        if 'stress_level' in data.columns and 'sleep_quality' in data.columns:
            data['stress_sleep_interaction'] = data['stress_level'] * (10 - data['sleep_quality'])
            
        # Microbiome-based features (inspired by gut microbiome research)
        if 'microbiome_diversity' in data.columns:
            # Microbiome health score
            data['microbiome_health_score'] = (
                data['microbiome_diversity'] * 2 +  # Diversity weight
                data['beneficial_bacteria_pct'] / 10 -  # Beneficial bacteria
                data['pathogenic_bacteria_pct'] / 20  # Pathogenic bacteria (negative impact)
            )
            
            # Dysbiosis indicator (microbiome imbalance)
            data['dysbiosis_score'] = (
                (data['pathogenic_bacteria_pct'] / data['beneficial_bacteria_pct']) * 
                (5 - data['microbiome_diversity'])  # Lower diversity amplifies dysbiosis
            )
            
        # Psychological clustering features (from 988 patients study)
        if 'anxiety_score' in data.columns and 'depression_score' in data.columns:
            # Psychological distress composite score
            data['psychological_distress'] = (
                data['anxiety_score'] / 21 * 0.6 +  # Normalized anxiety (60% weight)
                data['depression_score'] / 27 * 0.4  # Normalized depression (40% weight)
            )
            
            # Mood-symptom interaction
            if 'mood_score' in data.columns:
                data['mood_severity_interaction'] = (10 - data['mood_score']) * data.get('severity_score', 5)
                
            # Energy-anxiety interaction
            if 'energy_level' in data.columns:
                data['energy_anxiety_interaction'] = (10 - data['energy_level']) * data['anxiety_score'] / 21
                
        # Dietary sensitivity composite scores
        if 'fodmap_sensitivity' in data.columns:
            # Create sensitivity profile
            data['dietary_sensitivity_score'] = data['fodmap_sensitivity']
            
            if 'gluten_sensitivity' in data.columns:
                data['dietary_sensitivity_score'] += data['gluten_sensitivity'].astype(int) * 0.3
                
            if 'lactose_intolerance' in data.columns:
                data['dietary_sensitivity_score'] += data['lactose_intolerance'].astype(int) * 0.2
                
        # Advanced temporal features for symptom patterns
        if 'severity_score' in data.columns:
            # Weekly patterns
            data['severity_weekly_std'] = data.groupby('user_id')['severity_score'].rolling(
                window=7, min_periods=3
            ).std().reset_index(0, drop=True)
            
            # Symptom volatility (day-to-day changes)
            data['symptom_volatility'] = data.groupby('user_id')['severity_score'].rolling(
                window=3, min_periods=2
            ).std().reset_index(0, drop=True)
            
        # Bowel movement consistency features
        if 'bowel_movement_type' in data.columns:
            # Create consistency score (normal=4, loose=2, hard=3, watery=1)
            bm_consistency_map = {'normal': 4, 'hard': 3, 'loose': 2, 'watery': 1}
            data['bm_consistency_score'] = data['bowel_movement_type'].map(bm_consistency_map)
            
            # Rolling consistency average
            data['bm_consistency_7day_avg'] = data.groupby('user_id')['bm_consistency_score'].rolling(
                window=7, min_periods=1
            ).mean().reset_index(0, drop=True)
            
        return data
        
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean data and handle missing values with enhanced validation."""
        logger.info("Cleaning data with enhanced validation...")
        
        # Fill missing values
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            data[col] = data[col].fillna(data[col].median())
            
        categorical_columns = data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            data[col] = data[col].fillna('unknown')
            
        # Remove outliers (beyond 3 standard deviations)
        for col in ['severity_score', 'pain_level', 'bloating_level']:
            if col in data.columns:
                mean_val = data[col].mean()
                std_val = data[col].std()
                data[col] = data[col].clip(
                    lower=mean_val - 3 * std_val,
                    upper=mean_val + 3 * std_val
                )
                
        # Validate microbiome features
        if 'microbiome_diversity' in data.columns:
            data['microbiome_diversity'] = data['microbiome_diversity'].clip(lower=0, upper=5)
            
        if 'beneficial_bacteria_pct' in data.columns:
            data['beneficial_bacteria_pct'] = data['beneficial_bacteria_pct'].clip(lower=0, upper=100)
            
        if 'pathogenic_bacteria_pct' in data.columns:
            data['pathogenic_bacteria_pct'] = data['pathogenic_bacteria_pct'].clip(lower=0, upper=100)
            
        # Validate psychological scores
        if 'anxiety_score' in data.columns:
            data['anxiety_score'] = data['anxiety_score'].clip(lower=0, upper=21)
            
        if 'depression_score' in data.columns:
            data['depression_score'] = data['depression_score'].clip(lower=0, upper=27)
            
        # Validate composite scores
        if 'psychological_distress' in data.columns:
            data['psychological_distress'] = data['psychological_distress'].clip(lower=0, upper=1)
            
        if 'dietary_sensitivity_score' in data.columns:
            data['dietary_sensitivity_score'] = data['dietary_sensitivity_score'].clip(lower=0, upper=2)
            
        return data
        
    def validate_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Validate the quality of the prepared data and return quality metrics."""
        logger.info("Validating data quality...")
        
        quality_metrics = {
            'total_records': len(data),
            'missing_values': data.isnull().sum().to_dict(),
            'duplicate_records': data.duplicated().sum(),
            'feature_count': len(data.columns),
            'user_count': data['user_id'].nunique() if 'user_id' in data.columns else 0,
            'date_range': {
                'start': data['logged_at'].min() if 'logged_at' in data.columns else None,
                'end': data['logged_at'].max() if 'logged_at' in data.columns else None
            }
        }
        
        # Validate feature distributions
        if 'severity_score' in data.columns:
            quality_metrics['severity_distribution'] = {
                'mean': data['severity_score'].mean(),
                'std': data['severity_score'].std(),
                'min': data['severity_score'].min(),
                'max': data['severity_score'].max()
            }
            
        # Validate microbiome features
        microbiome_features = ['microbiome_diversity', 'beneficial_bacteria_pct', 'pathogenic_bacteria_pct']
        for feature in microbiome_features:
            if feature in data.columns:
                quality_metrics[f'{feature}_stats'] = {
                    'mean': data[feature].mean(),
                    'std': data[feature].std(),
                    'valid_range': (data[feature] >= 0).all()
                }
                
        # Validate psychological features
        psych_features = ['anxiety_score', 'depression_score', 'psychological_distress']
        for feature in psych_features:
            if feature in data.columns:
                quality_metrics[f'{feature}_stats'] = {
                    'mean': data[feature].mean(),
                    'std': data[feature].std(),
                    'valid_range': (data[feature] >= 0).all()
                }
                
        # Check for data consistency
        quality_metrics['data_consistency'] = {
            'severity_pain_correlation': data[['severity_score', 'pain_level']].corr().iloc[0, 1] 
                if all(col in data.columns for col in ['severity_score', 'pain_level']) else None,
            'stress_sleep_correlation': data[['stress_level', 'sleep_quality']].corr().iloc[0, 1] 
                if all(col in data.columns for col in ['stress_level', 'sleep_quality']) else None
        }
        
        logger.info(f"Data quality validation completed: {quality_metrics['total_records']} records, "
                   f"{quality_metrics['feature_count']} features, {quality_metrics['user_count']} users")
        
        return quality_metrics
        
    def split_data(self, data: pd.DataFrame, test_size: float = 0.2, 
                   validation_size: float = 0.1) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data into train, validation, and test sets.
        
        Args:
            data: Prepared training data
            test_size: Proportion for test set
            validation_size: Proportion for validation set
            
        Returns:
            Tuple of (train, validation, test) DataFrames
        """
        logger.info(f"Splitting data: train={1-test_size-validation_size:.1%}, "
                   f"val={validation_size:.1%}, test={test_size:.1%}")
        
        # First split: separate test set
        train_val, test = train_test_split(
            data, test_size=test_size, random_state=42, 
            stratify=data['user_id'] if 'user_id' in data.columns else None
        )
        
        # Second split: separate validation from training
        val_size_adjusted = validation_size / (1 - test_size)
        train, validation = train_test_split(
            train_val, test_size=val_size_adjusted, random_state=42,
            stratify=train_val['user_id'] if 'user_id' in train_val.columns else None
        )
        
        logger.info(f"Data split complete: train={len(train)}, val={len(validation)}, test={len(test)}")
        return train, validation, test
        
    def save_preprocessors(self, filepath: str):
        """Save preprocessing objects (scalers, encoders) to disk."""
        import joblib
        
        preprocessors = {
            'scalers': self.scalers,
            'encoders': self.encoders
        }
        
        joblib.dump(preprocessors, filepath)
        logger.info(f"Preprocessors saved to {filepath}")
        
    def load_preprocessors(self, filepath: str):
        """Load preprocessing objects from disk."""
        import joblib
        
        preprocessors = joblib.load(filepath)
        self.scalers = preprocessors['scalers']
        self.encoders = preprocessors['encoders']
        
        logger.info(f"Preprocessors loaded from {filepath}")