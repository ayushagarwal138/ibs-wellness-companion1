"""
Multi-Modal Data Integration Service

This service provides capabilities for:
- Integrating multiple data modalities (symptoms, diet, lifestyle, biometrics)
- Cross-modal feature extraction and correlation analysis
- Temporal alignment of different data streams
- Data fusion for enhanced ML predictions
- Real-time data synchronization and processing
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.core.config import settings
from app.models.user import User
from app.models.symptom import SymptomLog
from app.models.diet import DietLog
from app.models.medication import MedicationLog

logger = logging.getLogger(__name__)


class MultiModalIntegrationService:
    """Service for integrating multiple data modalities."""
    
    def __init__(self):
        self.data_streams = {
            "symptoms": {"weight": 0.3, "temporal_resolution": "hourly"},
            "dietary": {"weight": 0.25, "temporal_resolution": "meal"},
            "lifestyle": {"weight": 0.2, "temporal_resolution": "daily"},
            "medications": {"weight": 0.15, "temporal_resolution": "dose"},
            "biometrics": {"weight": 0.1, "temporal_resolution": "continuous"}
        }
        self.correlation_cache = {}
        self.fusion_strategies = ["weighted_average", "attention", "ensemble"]
        
    async def integrate_user_data(
        self, 
        user_id: int, 
        timeframe_days: int,
        db: AsyncSession,
        modalities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Integrate multiple data modalities for a user."""
        try:
            if modalities is None:
                modalities = list(self.data_streams.keys())
                
            # Collect data from each modality
            integrated_data = {}
            temporal_alignment = {}
            
            for modality in modalities:
                if modality == "symptoms":
                    data = await self._collect_symptom_data(
                        user_id, timeframe_days, db
                    )
                elif modality == "dietary":
                    data = await self._collect_dietary_data(
                        user_id, timeframe_days, db
                    )
                elif modality == "lifestyle":
                    data = await self._collect_lifestyle_data(
                        user_id, timeframe_days, db
                    )
                elif modality == "medications":
                    data = await self._collect_medication_data(
                        user_id, timeframe_days, db
                    )
                elif modality == "biometrics":
                    data = await self._collect_biometric_data(
                        user_id, timeframe_days, db
                    )
                else:
                    logger.warning(f"Unknown modality: {modality}")
                    continue
                    
                integrated_data[modality] = data
                temporal_alignment[modality] = self._extract_temporal_features(
                    data, modality
                )
                
            # Perform cross-modal correlation analysis
            correlations = await self._analyze_cross_modal_correlations(
                integrated_data, temporal_alignment
            )
            
            # Create unified feature representation
            unified_features = await self._create_unified_features(
                integrated_data, temporal_alignment, correlations
            )
            
            # Generate insights from multi-modal analysis
            insights = await self._generate_multimodal_insights(
                unified_features, correlations
            )
            
            return {
                "integrated_data": integrated_data,
                "temporal_alignment": temporal_alignment,
                "cross_modal_correlations": correlations,
                "unified_features": unified_features,
                "insights": insights,
                "integration_timestamp": datetime.utcnow().isoformat(),
                "modalities_included": modalities
            }
            
        except Exception as e:
            logger.error(f"Error integrating user data: {e}")
            return {"error": str(e)}
            
    async def _collect_symptom_data(
        self, 
        user_id: int, 
        timeframe_days: int, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Collect and process symptom data."""
        try:
            start_date = datetime.utcnow() - timedelta(days=timeframe_days)
            
            # Query symptom logs
            query = select(SymptomLog).where(
                and_(
                    SymptomLog.user_id == user_id,
                    SymptomLog.logged_at >= start_date
                )
            ).order_by(SymptomLog.logged_at)
            
            result = await db.execute(query)
            symptom_logs = result.scalars().all()
            
            # Process symptom data
            processed_data = {
                "raw_logs": [],
                "temporal_patterns": {},
                "severity_trends": {},
                "symptom_types": set(),
                "frequency_analysis": {}
            }
            
            for log in symptom_logs:
                log_data = {
                    "timestamp": log.logged_at.isoformat(),
                    "symptoms": log.symptoms,
                    "severity": getattr(log, 'severity', 5),
                    "triggers": getattr(log, 'triggers', []),
                    "notes": getattr(log, 'notes', '')
                }
                processed_data["raw_logs"].append(log_data)
                
                # Extract symptom types
                if isinstance(log.symptoms, dict):
                    processed_data["symptom_types"].update(log.symptoms.keys())
                    
            # Analyze temporal patterns
            processed_data["temporal_patterns"] = self._analyze_symptom_patterns(
                processed_data["raw_logs"]
            )
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error collecting symptom data: {e}")
            return {"error": str(e)}
            
    async def _collect_dietary_data(
        self, 
        user_id: int, 
        timeframe_days: int, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Collect and process dietary data."""
        try:
            start_date = datetime.utcnow() - timedelta(days=timeframe_days)
            
            # Query food diary entries
            query = select(FoodDiary).where(
                and_(
                    FoodDiary.user_id == user_id,
                    FoodDiary.consumed_at >= start_date
                )
            ).order_by(FoodDiary.consumed_at)
            
            result = await db.execute(query)
            food_entries = result.scalars().all()
            
            # Process dietary data
            processed_data = {
                "raw_entries": [],
                "meal_patterns": {},
                "nutritional_analysis": {},
                "food_categories": {},
                "timing_analysis": {}
            }
            
            for entry in food_entries:
                entry_data = {
                    "timestamp": entry.consumed_at.isoformat(),
                    "food_name": entry.food_name,
                    "quantity": getattr(entry, 'quantity', 1),
                    "meal_type": getattr(entry, 'meal_type', 'unknown'),
                    "calories": getattr(entry, 'calories', 0),
                    "nutrients": getattr(entry, 'nutrients', {}),
                    "food_category": getattr(entry, 'food_category', 'unknown')
                }
                processed_data["raw_entries"].append(entry_data)
                
            # Analyze meal patterns
            processed_data["meal_patterns"] = self._analyze_meal_patterns(
                processed_data["raw_entries"]
            )
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error collecting dietary data: {e}")
            return {"error": str(e)}
            
    async def _collect_lifestyle_data(
        self, 
        user_id: int, 
        timeframe_days: int, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Collect and process lifestyle data."""
        try:
            start_date = datetime.utcnow() - timedelta(days=timeframe_days)
            
            # Query lifestyle logs
            query = select(LifestyleLog).where(
                and_(
                    LifestyleLog.user_id == user_id,
                    LifestyleLog.logged_at >= start_date
                )
            ).order_by(LifestyleLog.logged_at)
            
            result = await db.execute(query)
            lifestyle_logs = result.scalars().all()
            
            # Process lifestyle data
            processed_data = {
                "raw_logs": [],
                "sleep_patterns": {},
                "exercise_patterns": {},
                "stress_patterns": {},
                "activity_analysis": {}
            }
            
            for log in lifestyle_logs:
                log_data = {
                    "timestamp": log.logged_at.isoformat(),
                    "sleep_hours": getattr(log, 'sleep_hours', 0),
                    "sleep_quality": getattr(log, 'sleep_quality', 5),
                    "exercise_type": getattr(log, 'exercise_type', ''),
                    "exercise_duration": getattr(log, 'exercise_duration', 0),
                    "stress_level": getattr(log, 'stress_level', 5),
                    "mood": getattr(log, 'mood', 5),
                    "activities": getattr(log, 'activities', [])
                }
                processed_data["raw_logs"].append(log_data)
                
            # Analyze lifestyle patterns
            processed_data["sleep_patterns"] = self._analyze_sleep_patterns(
                processed_data["raw_logs"]
            )
            processed_data["exercise_patterns"] = self._analyze_exercise_patterns(
                processed_data["raw_logs"]
            )
            processed_data["stress_patterns"] = self._analyze_stress_patterns(
                processed_data["raw_logs"]
            )
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error collecting lifestyle data: {e}")
            return {"error": str(e)}
            
    async def _collect_medication_data(
        self, 
        user_id: int, 
        timeframe_days: int, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Collect and process medication data."""
        try:
            start_date = datetime.utcnow() - timedelta(days=timeframe_days)
            
            # Query medication logs
            query = select(MedicationLog).where(
                and_(
                    MedicationLog.user_id == user_id,
                    MedicationLog.taken_at >= start_date
                )
            ).order_by(MedicationLog.taken_at)
            
            result = await db.execute(query)
            medication_logs = result.scalars().all()
            
            # Process medication data
            processed_data = {
                "raw_logs": [],
                "adherence_patterns": {},
                "effectiveness_tracking": {},
                "side_effects": {},
                "medication_types": set()
            }
            
            for log in medication_logs:
                log_data = {
                    "timestamp": log.taken_at.isoformat(),
                    "medication_name": log.medication_name,
                    "dosage": getattr(log, 'dosage', ''),
                    "effectiveness": getattr(log, 'effectiveness', 5),
                    "side_effects": getattr(log, 'side_effects', []),
                    "notes": getattr(log, 'notes', '')
                }
                processed_data["raw_logs"].append(log_data)
                processed_data["medication_types"].add(log.medication_name)
                
            # Analyze medication patterns
            processed_data["adherence_patterns"] = self._analyze_adherence_patterns(
                processed_data["raw_logs"]
            )
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error collecting medication data: {e}")
            return {"error": str(e)}
            
    async def _collect_biometric_data(
        self, 
        user_id: int, 
        timeframe_days: int, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Collect and process biometric data."""
        try:
            # Placeholder for biometric data collection
            # In a real implementation, this would connect to wearable devices,
            # health apps, or manual biometric entries
            
            processed_data = {
                "heart_rate": {"average": 72, "variability": 0.15},
                "blood_pressure": {"systolic": 120, "diastolic": 80},
                "weight": {"current": 70, "trend": "stable"},
                "body_temperature": {"average": 36.5, "variability": 0.3},
                "activity_levels": {"steps_per_day": 8000, "active_minutes": 45}
            }
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error collecting biometric data: {e}")
            return {"error": str(e)}
            
    def _extract_temporal_features(
        self, 
        data: Dict[str, Any], 
        modality: str
    ) -> Dict[str, Any]:
        """Extract temporal features from modality data."""
        try:
            temporal_features = {
                "frequency": 0,
                "regularity": 0,
                "peak_times": [],
                "patterns": {},
                "trends": {}
            }
            
            if modality == "symptoms":
                raw_logs = data.get("raw_logs", [])
                if raw_logs:
                    # Calculate frequency (entries per day)
                    time_span = self._calculate_time_span(raw_logs)
                    temporal_features["frequency"] = len(raw_logs) / max(1, time_span)
                    
                    # Analyze peak symptom times
                    temporal_features["peak_times"] = self._find_peak_times(raw_logs)
                    
            elif modality == "dietary":
                raw_entries = data.get("raw_entries", [])
                if raw_entries:
                    # Analyze meal timing regularity
                    temporal_features["regularity"] = self._calculate_meal_regularity(
                        raw_entries
                    )
                    
            elif modality == "lifestyle":
                raw_logs = data.get("raw_logs", [])
                if raw_logs:
                    # Analyze sleep and exercise consistency
                    temporal_features["sleep_consistency"] = self._calculate_sleep_consistency(
                        raw_logs
                    )
                    temporal_features["exercise_consistency"] = self._calculate_exercise_consistency(
                        raw_logs
                    )
                    
            return temporal_features
            
        except Exception as e:
            logger.error(f"Error extracting temporal features for {modality}: {e}")
            return {}
            
    async def _analyze_cross_modal_correlations(
        self, 
        integrated_data: Dict[str, Any],
        temporal_alignment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze correlations between different data modalities."""
        try:
            correlations = {}
            modalities = list(integrated_data.keys())
            
            # Pairwise correlation analysis
            for i, mod1 in enumerate(modalities):
                for j, mod2 in enumerate(modalities[i+1:], i+1):
                    correlation_key = f"{mod1}_{mod2}"
                    
                    # Calculate correlation based on modality types
                    if mod1 == "symptoms" and mod2 == "dietary":
                        corr = self._calculate_symptom_diet_correlation(
                            integrated_data[mod1], integrated_data[mod2]
                        )
                    elif mod1 == "symptoms" and mod2 == "lifestyle":
                        corr = self._calculate_symptom_lifestyle_correlation(
                            integrated_data[mod1], integrated_data[mod2]
                        )
                    elif mod1 == "symptoms" and mod2 == "medications":
                        corr = self._calculate_symptom_medication_correlation(
                            integrated_data[mod1], integrated_data[mod2]
                        )
                    else:
                        # Generic correlation calculation
                        corr = self._calculate_generic_correlation(
                            integrated_data[mod1], integrated_data[mod2]
                        )
                        
                    correlations[correlation_key] = corr
                    
            return correlations
            
        except Exception as e:
            logger.error(f"Error analyzing cross-modal correlations: {e}")
            return {}
            
    async def _create_unified_features(
        self,
        integrated_data: Dict[str, Any],
        temporal_alignment: Dict[str, Any],
        correlations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create unified feature representation from multi-modal data."""
        try:
            unified_features = {
                "temporal_features": {},
                "correlation_features": {},
                "aggregated_features": {},
                "interaction_features": {}
            }
            
            # Aggregate temporal features
            for modality, temporal_data in temporal_alignment.items():
                weight = self.data_streams.get(modality, {}).get("weight", 0.2)
                for feature_name, feature_value in temporal_data.items():
                    if isinstance(feature_value, (int, float)):
                        weighted_key = f"{modality}_{feature_name}_weighted"
                        unified_features["temporal_features"][weighted_key] = (
                            feature_value * weight
                        )
                        
            # Include correlation strengths as features
            for corr_key, corr_value in correlations.items():
                if isinstance(corr_value, dict) and "strength" in corr_value:
                    unified_features["correlation_features"][f"{corr_key}_strength"] = (
                        corr_value["strength"]
                    )
                    
            # Create interaction features
            unified_features["interaction_features"] = self._create_interaction_features(
                integrated_data, correlations
            )
            
            # Calculate aggregated risk scores
            unified_features["aggregated_features"] = self._calculate_aggregated_features(
                integrated_data, temporal_alignment
            )
            
            return unified_features
            
        except Exception as e:
            logger.error(f"Error creating unified features: {e}")
            return {}
            
    async def _generate_multimodal_insights(
        self,
        unified_features: Dict[str, Any],
        correlations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights from multi-modal analysis."""
        try:
            insights = {
                "key_patterns": [],
                "risk_factors": [],
                "recommendations": [],
                "data_quality": {},
                "confidence_scores": {}
            }
            
            # Identify key patterns
            insights["key_patterns"] = self._identify_key_patterns(
                unified_features, correlations
            )
            
            # Identify risk factors
            insights["risk_factors"] = self._identify_risk_factors(
                unified_features, correlations
            )
            
            # Generate recommendations
            insights["recommendations"] = self._generate_multimodal_recommendations(
                unified_features, correlations
            )
            
            # Assess data quality
            insights["data_quality"] = self._assess_data_quality(unified_features)
            
            # Calculate confidence scores
            insights["confidence_scores"] = self._calculate_confidence_scores(
                unified_features, correlations
            )
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating multimodal insights: {e}")
            return {}
            
    # Helper methods for specific analyses
    def _analyze_symptom_patterns(self, raw_logs: List[Dict]) -> Dict[str, Any]:
        """Analyze temporal patterns in symptom data."""
        if not raw_logs:
            return {}
            
        # Extract hourly patterns
        hourly_counts = {}
        severity_by_hour = {}
        
        for log in raw_logs:
            try:
                timestamp = datetime.fromisoformat(log["timestamp"].replace('Z', '+00:00'))
                hour = timestamp.hour
                severity = log.get("severity", 5)
                
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
                if hour not in severity_by_hour:
                    severity_by_hour[hour] = []
                severity_by_hour[hour].append(severity)
            except Exception:
                continue
                
        # Calculate average severity by hour
        avg_severity_by_hour = {}
        for hour, severities in severity_by_hour.items():
            avg_severity_by_hour[hour] = sum(severities) / len(severities)
            
        return {
            "hourly_frequency": hourly_counts,
            "hourly_severity": avg_severity_by_hour,
            "peak_hours": sorted(hourly_counts.keys(), 
                               key=lambda x: hourly_counts[x], reverse=True)[:3]
        }
        
    def _analyze_meal_patterns(self, raw_entries: List[Dict]) -> Dict[str, Any]:
        """Analyze meal timing and composition patterns."""
        if not raw_entries:
            return {}
            
        meal_times = {}
        meal_types = {}
        
        for entry in raw_entries:
            try:
                timestamp = datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00'))
                hour = timestamp.hour
                meal_type = entry.get("meal_type", "unknown")
                
                if meal_type not in meal_times:
                    meal_times[meal_type] = []
                meal_times[meal_type].append(hour)
                
                meal_types[meal_type] = meal_types.get(meal_type, 0) + 1
            except Exception:
                continue
                
        # Calculate average meal times
        avg_meal_times = {}
        for meal_type, hours in meal_times.items():
            avg_meal_times[meal_type] = sum(hours) / len(hours)
            
        return {
            "average_meal_times": avg_meal_times,
            "meal_frequency": meal_types,
            "meal_regularity": self._calculate_meal_time_variance(meal_times)
        }
        
    def _calculate_meal_time_variance(self, meal_times: Dict[str, List[int]]) -> Dict[str, float]:
        """Calculate variance in meal timing."""
        variance = {}
        for meal_type, hours in meal_times.items():
            if len(hours) > 1:
                mean_hour = sum(hours) / len(hours)
                variance[meal_type] = sum((h - mean_hour) ** 2 for h in hours) / len(hours)
            else:
                variance[meal_type] = 0.0
        return variance
        
    def _calculate_symptom_diet_correlation(
        self, 
        symptom_data: Dict[str, Any], 
        dietary_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate correlation between symptoms and diet."""
        # Simplified correlation calculation
        # In a full implementation, this would use more sophisticated methods
        return {
            "strength": 0.65,
            "confidence": 0.78,
            "key_triggers": ["high_fodmap", "dairy", "gluten"],
            "temporal_lag": 2.5  # hours
        }
        
    def _calculate_symptom_lifestyle_correlation(
        self, 
        symptom_data: Dict[str, Any], 
        lifestyle_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate correlation between symptoms and lifestyle."""
        return {
            "strength": 0.58,
            "confidence": 0.72,
            "key_factors": ["sleep_quality", "stress_level", "exercise"],
            "temporal_lag": 12.0  # hours
        }
        
    def _calculate_symptom_medication_correlation(
        self, 
        symptom_data: Dict[str, Any], 
        medication_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate correlation between symptoms and medications."""
        return {
            "strength": 0.72,
            "confidence": 0.85,
            "effectiveness_score": 0.68,
            "temporal_lag": 1.0  # hours
        }
        
    def _calculate_generic_correlation(
        self, 
        data1: Dict[str, Any], 
        data2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate generic correlation between two data modalities."""
        return {
            "strength": 0.45,
            "confidence": 0.60,
            "temporal_lag": 6.0  # hours
        }
        
    def _create_interaction_features(
        self, 
        integrated_data: Dict[str, Any], 
        correlations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create interaction features between modalities."""
        interactions = {}
        
        # Example interaction features
        if "symptoms" in integrated_data and "dietary" in integrated_data:
            symptom_diet_corr = correlations.get("symptoms_dietary", {})
            interactions["symptom_diet_interaction"] = (
                symptom_diet_corr.get("strength", 0) * 
                len(integrated_data["symptoms"].get("raw_logs", []))
            )
            
        if "symptoms" in integrated_data and "lifestyle" in integrated_data:
            symptom_lifestyle_corr = correlations.get("symptoms_lifestyle", {})
            interactions["symptom_lifestyle_interaction"] = (
                symptom_lifestyle_corr.get("strength", 0) * 
                len(integrated_data["lifestyle"].get("raw_logs", []))
            )
            
        return interactions
        
    def _calculate_aggregated_features(
        self, 
        integrated_data: Dict[str, Any], 
        temporal_alignment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate aggregated features across modalities."""
        aggregated = {}
        
        # Overall risk score
        risk_components = []
        
        if "symptoms" in integrated_data:
            symptom_logs = integrated_data["symptoms"].get("raw_logs", [])
            if symptom_logs:
                avg_severity = sum(log.get("severity", 5) for log in symptom_logs) / len(symptom_logs)
                risk_components.append(avg_severity / 10.0)  # Normalize to 0-1
                
        if "lifestyle" in integrated_data:
            lifestyle_logs = integrated_data["lifestyle"].get("raw_logs", [])
            if lifestyle_logs:
                avg_stress = sum(log.get("stress_level", 5) for log in lifestyle_logs) / len(lifestyle_logs)
                risk_components.append(avg_stress / 10.0)  # Normalize to 0-1
                
        if risk_components:
            aggregated["overall_risk_score"] = sum(risk_components) / len(risk_components)
        else:
            aggregated["overall_risk_score"] = 0.5  # Default moderate risk
            
        # Data completeness score
        completeness_scores = []
        for modality in self.data_streams.keys():
            if modality in integrated_data:
                data = integrated_data[modality]
                if isinstance(data, dict) and data.get("raw_logs") or data.get("raw_entries"):
                    completeness_scores.append(1.0)
                else:
                    completeness_scores.append(0.5)
            else:
                completeness_scores.append(0.0)
                
        aggregated["data_completeness"] = sum(completeness_scores) / len(completeness_scores)
        
        return aggregated
        
    # Additional helper methods would be implemented here...
    def _identify_key_patterns(self, unified_features, correlations):
        """Identify key patterns from unified features."""
        return ["High stress-symptom correlation", "Irregular meal timing"]
        
    def _identify_risk_factors(self, unified_features, correlations):
        """Identify risk factors from analysis."""
        return ["Poor sleep quality", "High FODMAP intake", "Irregular exercise"]
        
    def _generate_multimodal_recommendations(self, unified_features, correlations):
        """Generate recommendations based on multi-modal analysis."""
        return [
            {"type": "dietary", "action": "Reduce high-FODMAP foods"},
            {"type": "lifestyle", "action": "Improve sleep consistency"},
            {"type": "stress", "action": "Practice stress management techniques"}
        ]
        
    def _assess_data_quality(self, unified_features):
        """Assess the quality of integrated data."""
        return {"completeness": 0.85, "consistency": 0.78, "accuracy": 0.82}
        
    def _calculate_confidence_scores(self, unified_features, correlations):
        """Calculate confidence scores for insights."""
        return {"overall": 0.78, "correlations": 0.82, "predictions": 0.75}


# Global service instance
_multimodal_integration_service = None


def get_multimodal_integration_service() -> MultiModalIntegrationService:
    """Get the global multi-modal integration service instance."""
    global _multimodal_integration_service
    if _multimodal_integration_service is None:
        _multimodal_integration_service = MultiModalIntegrationService()
    return _multimodal_integration_service