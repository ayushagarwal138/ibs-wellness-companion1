"""
IBS Recommendation Engine

This model generates personalized recommendations for IBS management based on
user patterns, preferences, and current health status.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import joblib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Personalized recommendation engine for IBS management.
    
    Provides recommendations for diet, lifestyle, medication timing,
    and preventive measures based on user patterns and similar user profiles.
    """
    
    def __init__(self):
        self.diet_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.lifestyle_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.user_clusters = None
        self.cluster_model = KMeans(n_clusters=5, random_state=42)
        self.is_trained = False
        
        # Recommendation templates
        self.diet_recommendations = {
            'low_fodmap': [
                "Try incorporating more low-FODMAP foods like rice, quinoa, and lean proteins",
                "Consider eliminating high-FODMAP foods for 2-6 weeks",
                "Focus on portion control even with low-FODMAP foods"
            ],
            'fiber_management': [
                "Gradually increase soluble fiber intake (oats, bananas, carrots)",
                "Reduce insoluble fiber during flare-ups",
                "Consider psyllium husk supplements"
            ],
            'meal_timing': [
                "Eat smaller, more frequent meals throughout the day",
                "Maintain consistent meal times",
                "Avoid eating large meals late in the evening"
            ],
            'hydration': [
                "Increase water intake, especially between meals",
                "Limit carbonated beverages",
                "Consider herbal teas like peppermint or ginger"
            ]
        }
        
        self.lifestyle_recommendations = {
            'stress_management': [
                "Practice daily meditation or mindfulness exercises",
                "Try progressive muscle relaxation techniques",
                "Consider yoga or tai chi for stress reduction",
                "Maintain a regular sleep schedule"
            ],
            'exercise': [
                "Engage in low-impact exercises like walking or swimming",
                "Try gentle yoga poses that aid digestion",
                "Avoid intense exercise during flare-ups",
                "Consider pelvic floor exercises"
            ],
            'sleep': [
                "Establish a consistent bedtime routine",
                "Avoid screens 1 hour before bedtime",
                "Keep bedroom cool and dark",
                "Consider relaxation techniques before sleep"
            ],
            'medication_timing': [
                "Take medications at consistent times daily",
                "Consider timing medications with meals if appropriate",
                "Track medication effectiveness in relation to symptoms",
                "Discuss timing adjustments with healthcare provider"
            ]
        }
        
    def prepare_user_features(self, user_data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare user features for recommendation generation.
        
        Args:
            user_data: User's historical data
            
        Returns:
            Processed feature DataFrame
        """
        features = pd.DataFrame()
        
        # Symptom patterns
        features['avg_severity'] = user_data.groupby('user_id')['severity_score'].mean()
        features['severity_variance'] = user_data.groupby('user_id')['severity_score'].var()
        features['flareup_frequency'] = user_data.groupby('user_id').apply(
            lambda x: len(x[x['severity_score'] >= 7]) / max(1, len(x))
        )
        
        # Diet patterns
        features['high_fodmap_frequency'] = user_data[
            user_data['fodmap_level'] == 'high'
        ].groupby('user_id').size() / user_data.groupby('user_id').size()
        
        features['trigger_food_frequency'] = user_data[
            user_data['is_known_trigger'] == True
        ].groupby('user_id').size() / user_data.groupby('user_id').size()
        
        features['meal_regularity'] = user_data.groupby('user_id')['meal_timing_std'].mean()
        features['avg_portion_size'] = user_data.groupby('user_id')['total_portion_g'].mean()
        
        # Lifestyle factors
        features['avg_stress_level'] = user_data.groupby('user_id')['stress_level'].mean()
        features['avg_sleep_quality'] = user_data.groupby('user_id')['sleep_quality'].mean()
        features['exercise_frequency'] = user_data.groupby('user_id')['exercise_minutes'].apply(
            lambda x: (x > 0).sum() / len(x)
        )
        
        # Medication patterns
        features['medication_adherence'] = user_data.groupby('user_id')['medication_adherence_rate'].mean()
        features['medication_effectiveness'] = user_data.groupby('user_id').apply(
            lambda x: x[x['medication_adherence_rate'] > 0.8]['severity_score'].mean() if len(x[x['medication_adherence_rate'] > 0.8]) > 0 else 5
        )
        
        # Temporal patterns
        features['weekend_severity_diff'] = user_data.groupby('user_id').apply(
            lambda x: x[x['is_weekend'] == True]['severity_score'].mean() - 
                     x[x['is_weekend'] == False]['severity_score'].mean()
        )
        
        features['morning_severity'] = user_data[
            user_data['hour_of_day'].between(6, 12)
        ].groupby('user_id')['severity_score'].mean()
        
        # Fill missing values with appropriate defaults
        numeric_features = features.select_dtypes(include=[np.number])
        features[numeric_features.columns] = numeric_features.fillna(numeric_features.median())
        
        # For any remaining NaN values, fill with 0
        features = features.fillna(0)
        
        return features
        
    def train(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Train the recommendation engine.
        
        Args:
            training_data: Historical user data with outcomes
            
        Returns:
            Training metrics and results
        """
        logger.info("Starting recommendation engine training...")
        
        # Prepare features
        X = self.prepare_user_features(training_data)
        
        # Create targets for different recommendation types
        diet_targets = self._create_diet_effectiveness_targets(training_data)
        lifestyle_targets = self._create_lifestyle_effectiveness_targets(training_data)
        
        # Ensure same length
        min_length = min(len(X), len(diet_targets), len(lifestyle_targets))
        X = X.iloc[:min_length]
        diet_targets = diet_targets.iloc[:min_length]
        lifestyle_targets = lifestyle_targets.iloc[:min_length]
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train models
        self.diet_model.fit(X_scaled, diet_targets)
        self.lifestyle_model.fit(X_scaled, lifestyle_targets)
        
        # Create user clusters for collaborative filtering
        self.cluster_model.fit(X_scaled)
        self.user_clusters = self.cluster_model.labels_
        
        self.is_trained = True
        
        # Evaluate models
        diet_score = self.diet_model.score(X_scaled, diet_targets)
        lifestyle_score = self.lifestyle_model.score(X_scaled, lifestyle_targets)
        
        results = {
            'diet_model_r2': diet_score,
            'lifestyle_model_r2': lifestyle_score,
            'n_clusters': len(np.unique(self.user_clusters)),
            'n_samples': len(X),
            'n_features': len(X.columns)
        }
        
        logger.info(f"Training completed. Diet R²: {diet_score:.3f}, Lifestyle R²: {lifestyle_score:.3f}")
        return results
        
    def _create_diet_effectiveness_targets(self, data: pd.DataFrame) -> pd.Series:
        """Create targets for diet recommendation effectiveness."""
        targets = []
        
        for user_id in data['user_id'].unique():
            user_data = data[data['user_id'] == user_id]
            
            # Calculate improvement when following low-FODMAP diet
            low_fodmap_days = user_data[user_data['fodmap_level'] == 'low']
            high_fodmap_days = user_data[user_data['fodmap_level'] == 'high']
            
            if len(low_fodmap_days) > 0 and len(high_fodmap_days) > 0:
                improvement = high_fodmap_days['severity_score'].mean() - low_fodmap_days['severity_score'].mean()
                targets.append(max(0, improvement))  # Positive improvement
            else:
                targets.append(0)
                
        return pd.Series(targets)
        
    def _create_lifestyle_effectiveness_targets(self, data: pd.DataFrame) -> pd.Series:
        """Create targets for lifestyle recommendation effectiveness."""
        targets = []
        
        for user_id in data['user_id'].unique():
            user_data = data[data['user_id'] == user_id]
            
            # Calculate improvement with good lifestyle habits
            good_habits = user_data[
                (user_data['stress_level'] <= 5) & 
                (user_data['sleep_quality'] >= 6) & 
                (user_data['exercise_minutes'] > 0)
            ]
            
            poor_habits = user_data[
                (user_data['stress_level'] > 7) | 
                (user_data['sleep_quality'] < 4) | 
                (user_data['exercise_minutes'] == 0)
            ]
            
            if len(good_habits) > 0 and len(poor_habits) > 0:
                improvement = poor_habits['severity_score'].mean() - good_habits['severity_score'].mean()
                targets.append(max(0, improvement))
            else:
                targets.append(0)
                
        return pd.Series(targets)
        
    def generate_recommendations(self, user_features: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate personalized recommendations for a user.
        
        Args:
            user_features: Current user features and patterns
            user_id: Optional user ID for collaborative filtering
            
        Returns:
            Comprehensive recommendations
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before generating recommendations")
            
        # Convert to DataFrame and scale
        feature_df = pd.DataFrame([user_features])
        features_scaled = self.scaler.transform(feature_df)
        
        # Get model predictions for effectiveness
        diet_effectiveness = self.diet_model.predict(features_scaled)[0]
        lifestyle_effectiveness = self.lifestyle_model.predict(features_scaled)[0]
        
        # Determine user cluster
        user_cluster = self.cluster_model.predict(features_scaled)[0]
        
        # Generate recommendations
        recommendations = {
            'diet': self._generate_diet_recommendations(user_features, diet_effectiveness),
            'lifestyle': self._generate_lifestyle_recommendations(user_features, lifestyle_effectiveness),
            'medication': self._generate_medication_recommendations(user_features),
            'monitoring': self._generate_monitoring_recommendations(user_features),
            'priority_actions': self._identify_priority_actions(user_features),
            'user_cluster': int(user_cluster),
            'effectiveness_scores': {
                'diet': float(diet_effectiveness),
                'lifestyle': float(lifestyle_effectiveness)
            }
        }
        
        return recommendations
        
    def _generate_diet_recommendations(self, features: Dict[str, Any], effectiveness: float) -> List[Dict[str, Any]]:
        """Generate personalized diet recommendations."""
        recommendations = []
        
        # High FODMAP frequency
        if features.get('high_fodmap_frequency', 0) > 0.3:
            recommendations.extend([
                {
                    'category': 'low_fodmap',
                    'recommendation': rec,
                    'priority': 'high',
                    'expected_benefit': effectiveness * 0.8
                }
                for rec in self.diet_recommendations['low_fodmap']
            ])
            
        # Poor meal timing
        if features.get('meal_regularity', 0) > 3:
            recommendations.extend([
                {
                    'category': 'meal_timing',
                    'recommendation': rec,
                    'priority': 'medium',
                    'expected_benefit': effectiveness * 0.6
                }
                for rec in self.diet_recommendations['meal_timing']
            ])
            
        # Fiber management based on symptoms
        if features.get('avg_severity', 0) > 6:
            recommendations.extend([
                {
                    'category': 'fiber_management',
                    'recommendation': rec,
                    'priority': 'medium',
                    'expected_benefit': effectiveness * 0.5
                }
                for rec in self.diet_recommendations['fiber_management']
            ])
            
        return recommendations[:5]  # Limit to top 5
        
    def _generate_lifestyle_recommendations(self, features: Dict[str, Any], effectiveness: float) -> List[Dict[str, Any]]:
        """Generate personalized lifestyle recommendations."""
        recommendations = []
        
        # High stress levels
        if features.get('avg_stress_level', 0) > 6:
            recommendations.extend([
                {
                    'category': 'stress_management',
                    'recommendation': rec,
                    'priority': 'high',
                    'expected_benefit': effectiveness * 0.9
                }
                for rec in self.lifestyle_recommendations['stress_management']
            ])
            
        # Poor sleep quality
        if features.get('avg_sleep_quality', 5) < 4:
            recommendations.extend([
                {
                    'category': 'sleep',
                    'recommendation': rec,
                    'priority': 'high',
                    'expected_benefit': effectiveness * 0.7
                }
                for rec in self.lifestyle_recommendations['sleep']
            ])
            
        # Low exercise frequency
        if features.get('exercise_frequency', 0) < 0.3:
            recommendations.extend([
                {
                    'category': 'exercise',
                    'recommendation': rec,
                    'priority': 'medium',
                    'expected_benefit': effectiveness * 0.6
                }
                for rec in self.lifestyle_recommendations['exercise']
            ])
            
        return recommendations[:5]  # Limit to top 5
        
    def _generate_medication_recommendations(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate medication-related recommendations."""
        recommendations = []
        
        # Poor medication adherence
        if features.get('medication_adherence', 1.0) < 0.8:
            recommendations.extend([
                {
                    'category': 'medication_timing',
                    'recommendation': rec,
                    'priority': 'high',
                    'expected_benefit': 0.8
                }
                for rec in self.lifestyle_recommendations['medication_timing']
            ])
            
        return recommendations
        
    def _generate_monitoring_recommendations(self, features: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate monitoring and tracking recommendations."""
        recommendations = []
        
        if features.get('flareup_frequency', 0) > 0.3:
            recommendations.append({
                'type': 'symptom_tracking',
                'recommendation': 'Track symptoms daily to identify patterns and triggers',
                'frequency': 'daily'
            })
            
        if features.get('trigger_food_frequency', 0) > 0.2:
            recommendations.append({
                'type': 'food_diary',
                'recommendation': 'Maintain detailed food diary with portion sizes and timing',
                'frequency': 'with_meals'
            })
            
        if features.get('avg_stress_level', 0) > 6:
            recommendations.append({
                'type': 'stress_monitoring',
                'recommendation': 'Monitor stress levels and identify stress triggers',
                'frequency': 'twice_daily'
            })
            
        return recommendations
        
    def _identify_priority_actions(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify the most important actions for the user."""
        actions = []
        
        # Calculate priority scores
        if features.get('high_fodmap_frequency', 0) > 0.4:
            actions.append({
                'action': 'Start low-FODMAP elimination diet',
                'priority_score': 0.9,
                'timeframe': '2-6 weeks',
                'expected_improvement': 'Significant symptom reduction'
            })
            
        if features.get('avg_stress_level', 0) > 7:
            actions.append({
                'action': 'Implement daily stress management routine',
                'priority_score': 0.8,
                'timeframe': '1-2 weeks',
                'expected_improvement': 'Reduced flare-up frequency'
            })
            
        if features.get('medication_adherence', 1.0) < 0.7:
            actions.append({
                'action': 'Improve medication adherence',
                'priority_score': 0.85,
                'timeframe': 'immediate',
                'expected_improvement': 'Better symptom control'
            })
            
        # Sort by priority score
        actions.sort(key=lambda x: x['priority_score'], reverse=True)
        return actions[:3]  # Top 3 priority actions
        
    def get_similar_users(self, user_features: Dict[str, Any], n_similar: int = 5) -> List[int]:
        """Find users with similar patterns for collaborative filtering."""
        if not self.is_trained:
            raise ValueError("Model must be trained to find similar users")
            
        # Convert to DataFrame and scale
        feature_df = pd.DataFrame([user_features])
        features_scaled = self.scaler.transform(feature_df)
        
        # Get user cluster
        user_cluster = self.cluster_model.predict(features_scaled)[0]
        
        # Find users in the same cluster
        similar_user_indices = np.where(self.user_clusters == user_cluster)[0]
        
        return similar_user_indices[:n_similar].tolist()
        
    def save_model(self, filepath: str):
        """Save the trained model to disk."""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
            
        model_data = {
            'diet_model': self.diet_model,
            'lifestyle_model': self.lifestyle_model,
            'scaler': self.scaler,
            'cluster_model': self.cluster_model,
            'user_clusters': self.user_clusters,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Recommendation engine saved to {filepath}")
        
    def load_model(self, filepath: str):
        """Load a trained model from disk."""
        model_data = joblib.load(filepath)
        
        self.diet_model = model_data['diet_model']
        self.lifestyle_model = model_data['lifestyle_model']
        self.scaler = model_data['scaler']
        self.cluster_model = model_data['cluster_model']
        self.user_clusters = model_data['user_clusters']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Recommendation engine loaded from {filepath}")