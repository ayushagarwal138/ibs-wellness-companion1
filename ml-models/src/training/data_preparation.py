"""
Data Preparation Module

Handles data preprocessing, feature engineering, and preparation for ML model training.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


class DataPreparator:
    """
    Handles data preparation and feature engineering for IBS ML models.
    """
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        
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
            'symptom_logs': 'SELECT * FROM symptom_logs',
            'diet_logs': 'SELECT * FROM diet_logs',
            'food_reactions': 'SELECT * FROM food_reactions',
            'medications': 'SELECT * FROM medications',
            'chat_sessions': 'SELECT * FROM chat_sessions'
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
        """
        Create synthetic data for model training and testing.
        
        Args:
            n_users: Number of synthetic users to create
            days_per_user: Number of days of data per user
            
        Returns:
            Dictionary of synthetic DataFrames
        """
        logger.info(f"Creating synthetic data for {n_users} users over {days_per_user} days...")
        
        np.random.seed(42)
        
        # Generate users
        users = []
        for i in range(n_users):
            users.append({
                'id': f'user_{i:03d}',
                'age': np.random.randint(18, 70),
                'gender': np.random.choice(['male', 'female', 'other']),
                'ibs_type': np.random.choice(['IBS-D', 'IBS-C', 'IBS-M', 'IBS-U']),
                'diagnosis_date': datetime.now() - timedelta(days=np.random.randint(30, 1095)),
                'created_at': datetime.now() - timedelta(days=days_per_user)
            })
            
        users_df = pd.DataFrame(users)
        
        # Generate symptom logs
        symptom_logs = []
        for user in users:
            user_id = user['id']
            base_severity = np.random.uniform(3, 7)  # Base severity level
            stress_sensitivity = np.random.uniform(0.5, 2.0)
            
            for day in range(days_per_user):
                date = datetime.now() - timedelta(days=days_per_user - day)
                
                # Simulate daily patterns
                daily_stress = np.random.uniform(1, 10)
                sleep_quality = np.random.uniform(1, 10)
                
                # Calculate severity with some correlation to stress and sleep
                severity = base_severity + (daily_stress - 5) * stress_sensitivity * 0.3
                severity += (5 - sleep_quality) * 0.2
                severity += np.random.normal(0, 1)  # Random variation
                severity = max(1, min(10, severity))  # Clamp to 1-10
                
                symptom_logs.append({
                    'id': f'symptom_{user_id}_{day}',
                    'user_id': user_id,
                    'severity_score': round(severity, 1),
                    'pain_severity': max(1, min(10, severity + np.random.normal(0, 0.5))),
                    'pain_level': max(1, min(10, severity + np.random.normal(0, 0.5))),
                    'bloating_level': max(1, min(10, severity + np.random.normal(0, 0.8))),
                    'bowel_movement_type': np.random.choice(['normal', 'loose', 'hard', 'watery']),
                    'stress_level': daily_stress,
                    'sleep_quality': sleep_quality,
                    'exercise_minutes': max(0, np.random.normal(30, 20)),
                    'notes': f'Day {day} symptoms',
                    'logged_at': date
                })
                
        symptom_logs_df = pd.DataFrame(symptom_logs)
        
        # Generate diet logs
        diet_logs = []
        foods = [
            {'name': 'Rice', 'fodmap_level': 'low', 'trigger_probability': 0.1},
            {'name': 'Wheat bread', 'fodmap_level': 'high', 'trigger_probability': 0.7},
            {'name': 'Banana', 'fodmap_level': 'low', 'trigger_probability': 0.05},
            {'name': 'Apple', 'fodmap_level': 'high', 'trigger_probability': 0.4},
            {'name': 'Chicken', 'fodmap_level': 'low', 'trigger_probability': 0.1},
            {'name': 'Beans', 'fodmap_level': 'high', 'trigger_probability': 0.8},
            {'name': 'Carrots', 'fodmap_level': 'low', 'trigger_probability': 0.05},
            {'name': 'Onions', 'fodmap_level': 'high', 'trigger_probability': 0.9},
            {'name': 'Spinach', 'fodmap_level': 'low', 'trigger_probability': 0.1},
            {'name': 'Dairy milk', 'fodmap_level': 'high', 'trigger_probability': 0.6}
        ]
        
        for user in users:
            user_id = user['id']
            user_triggers = np.random.choice([f['name'] for f in foods], 
                                           size=np.random.randint(2, 5), replace=False)
            
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
        
    def prepare_training_data(self, raw_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Prepare and merge data for ML model training.
        
        Args:
            raw_data: Dictionary of raw DataFrames
            
        Returns:
            Merged and processed DataFrame ready for training
        """
        logger.info("Preparing training data...")
        
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
        """Engineer additional features for ML models."""
        logger.info("Engineering features...")
        
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
            
        # Interaction features
        if 'stress_level' in data.columns and 'sleep_quality' in data.columns:
            data['stress_sleep_interaction'] = data['stress_level'] * (10 - data['sleep_quality'])
            
        return data
        
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean data and handle missing values."""
        logger.info("Cleaning data...")
        
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
                
        return data
        
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