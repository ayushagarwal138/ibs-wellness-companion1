"""
Dynamic Configuration Management System for IBS Wellness Companion.
This module provides configurable parameters to replace all hardcoded values.
"""

import os
import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level classifications."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationPriority(str, Enum):
    """Recommendation priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class MLModelConfig(BaseModel):
    """ML Model configuration parameters."""

    # Risk thresholds (configurable)
    high_risk_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    medium_risk_threshold: float = Field(default=0.4, ge=0.0, le=1.0)
    low_risk_threshold: float = Field(default=0.0, ge=0.0, le=1.0)

    # Confidence parameters
    default_confidence: float = Field(default=0.6, ge=0.0, le=1.0)
    min_confidence_threshold: float = Field(default=0.3, ge=0.0, le=1.0)

    # Model versioning
    model_version_prefix: str = "v"
    fallback_model_version: str = "fallback_rule_based"

    # Feature weights (configurable)
    stress_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    sleep_weight: float = Field(default=0.2, ge=0.0, le=1.0)
    diet_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    symptom_weight: float = Field(default=0.25, ge=0.0, le=1.0)

    model_config = {"protected_namespaces": ()}


class NutritionConfig(BaseModel):
    """Nutrition guidelines configuration."""

    # Daily targets (configurable ranges)
    fiber_soluble_min: float = Field(default=10.0, ge=0.0)
    fiber_soluble_max: float = Field(default=15.0, ge=0.0)
    fiber_insoluble_min: float = Field(default=5.0, ge=0.0)
    fiber_insoluble_max: float = Field(default=10.0, ge=0.0)

    protein_min_per_kg: float = Field(default=0.8, ge=0.0)
    protein_max_per_kg: float = Field(default=1.2, ge=0.0)

    fat_min_percent: float = Field(default=20.0, ge=0.0, le=100.0)
    fat_max_percent: float = Field(default=35.0, ge=0.0, le=100.0)

    carbs_min_percent: float = Field(default=45.0, ge=0.0, le=100.0)
    carbs_max_percent: float = Field(default=65.0, ge=0.0, le=100.0)

    water_min_ml: float = Field(default=2000.0, ge=0.0)
    water_max_ml: float = Field(default=3000.0, ge=0.0)

    # Meal timing
    meal_frequency_min: int = Field(default=4, ge=1)
    meal_frequency_max: int = Field(default=6, ge=1)
    meal_spacing_hours: float = Field(default=2.5, ge=0.0)
    last_meal_hours_before_bed: float = Field(default=3.0, ge=0.0)

    # FODMAP thresholds
    fodmap_threshold: float = Field(default=6.0, ge=0.0, le=10.0)


class RecommendationConfig(BaseModel):
    """Recommendation system configuration."""

    # Personalization scoring weights
    data_completeness_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    symptom_history_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    diet_tracking_weight: float = Field(default=0.2, ge=0.0, le=1.0)
    medication_adherence_weight: float = Field(default=0.15, ge=0.0, le=1.0)
    engagement_weight: float = Field(default=0.1, ge=0.0, le=1.0)

    # Recommendation limits
    max_immediate_actions: int = Field(default=3, ge=1)
    max_dietary_suggestions: int = Field(default=5, ge=1)
    max_lifestyle_changes: int = Field(default=4, ge=1)

    # Confidence thresholds for recommendations
    high_confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    medium_confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)

    # Fallback recommendation settings
    fallback_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    min_personalization_score: float = Field(default=25.0, ge=0.0)


class AnalyticsConfig(BaseModel):
    """Analytics and reporting configuration."""

    # Time windows for analysis
    default_analysis_days: int = Field(default=30, ge=1)
    trend_analysis_days: int = Field(default=90, ge=1)
    pattern_detection_days: int = Field(default=14, ge=1)

    # Thresholds for insights
    significant_change_threshold: float = Field(default=0.15, ge=0.0, le=1.0)
    trend_confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

    # Data aggregation settings
    min_data_points_for_trend: int = Field(default=5, ge=1)
    max_data_points_per_chart: int = Field(default=100, ge=1)

    # Refresh intervals (in minutes)
    dashboard_refresh_interval: int = Field(default=15, ge=1)
    analytics_cache_duration: int = Field(default=60, ge=1)


class UIConfig(BaseModel):
    """UI/UX configuration parameters."""

    # Chart and visualization settings
    default_chart_colors: List[str] = Field(
        default=[
            "#3B82F6",
            "#EF4444",
            "#10B981",
            "#F59E0B",
            "#8B5CF6",
            "#EC4899",
            "#06B6D4",
            "#84CC16",
        ]
    )

    # Animation and interaction settings
    animation_duration_ms: int = Field(default=300, ge=0)
    debounce_delay_ms: int = Field(default=500, ge=0)

    # Data display limits
    max_items_per_page: int = Field(default=20, ge=1)
    max_chart_data_points: int = Field(default=50, ge=1)

    # Notification settings
    notification_display_duration_ms: int = Field(default=5000, ge=1000)
    max_notifications: int = Field(default=5, ge=1)


class DynamicSettings(BaseSettings):
    """Main dynamic settings class that combines all configuration modules."""

    # Core configuration modules
    ml_model: MLModelConfig = Field(default_factory=MLModelConfig)
    nutrition: NutritionConfig = Field(default_factory=NutritionConfig)
    recommendations: RecommendationConfig = Field(default_factory=RecommendationConfig)
    analytics: AnalyticsConfig = Field(default_factory=AnalyticsConfig)
    ui: UIConfig = Field(default_factory=UIConfig)

    # Environment-specific overrides
    environment: str = Field(default="development")
    debug_mode: bool = Field(default=False)

    # Feature flags
    enable_ai_recommendations: bool = Field(default=True)
    enable_advanced_analytics: bool = Field(default=True)
    enable_personalization: bool = Field(default=True)
    enable_real_time_updates: bool = Field(default=True)

    class Config:
        env_file = ".env"
        env_prefix = "DYNAMIC_"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields to prevent validation errors

    @classmethod
    def load_from_file(cls, config_path: str) -> "DynamicSettings":
        """Load configuration from JSON file."""
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config_data = json.load(f)
            return cls(**config_data)
        return cls()

    def save_to_file(self, config_path: str) -> None:
        """Save current configuration to JSON file."""
        with open(config_path, "w") as f:
            json.dump(self.dict(), f, indent=2)

    def get_risk_level(self, probability: float) -> RiskLevel:
        """Determine risk level based on configurable thresholds."""
        if probability >= self.ml_model.high_risk_threshold:
            return RiskLevel.HIGH
        elif probability >= self.ml_model.medium_risk_threshold:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def get_nutrition_targets(
        self, user_weight_kg: Optional[float] = None
    ) -> Dict[str, Any]:
        """Get personalized nutrition targets based on user data."""
        targets = {
            "fiber_soluble": {
                "min": self.nutrition.fiber_soluble_min,
                "max": self.nutrition.fiber_soluble_max,
                "unit": "g",
            },
            "fiber_insoluble": {
                "min": self.nutrition.fiber_insoluble_min,
                "max": self.nutrition.fiber_insoluble_max,
                "unit": "g",
            },
            "fat": {
                "min": self.nutrition.fat_min_percent,
                "max": self.nutrition.fat_max_percent,
                "unit": "% of calories",
            },
            "carbs": {
                "min": self.nutrition.carbs_min_percent,
                "max": self.nutrition.carbs_max_percent,
                "unit": "% of calories",
            },
            "water": {
                "min": self.nutrition.water_min_ml,
                "max": self.nutrition.water_max_ml,
                "unit": "ml",
            },
        }

        # Add personalized protein targets if weight is available
        if user_weight_kg:
            targets["protein"] = {
                "min": self.nutrition.protein_min_per_kg * user_weight_kg,
                "max": self.nutrition.protein_max_per_kg * user_weight_kg,
                "unit": "g",
            }

        return targets

    def update_config(self, section: str, updates: Dict[str, Any]) -> None:
        """Update specific configuration section."""
        if hasattr(self, section):
            config_section = getattr(self, section)
            for key, value in updates.items():
                if hasattr(config_section, key):
                    setattr(config_section, key, value)


# Global dynamic settings instance
dynamic_settings = DynamicSettings()

# Configuration file path
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "dynamic_config.json")


def load_dynamic_config() -> DynamicSettings:
    """Load dynamic configuration from file or environment."""
    return DynamicSettings.load_from_file(CONFIG_FILE_PATH)


def save_dynamic_config(settings: DynamicSettings) -> None:
    """Save dynamic configuration to file."""
    settings.save_to_file(CONFIG_FILE_PATH)


def get_config() -> DynamicSettings:
    """Get the current dynamic configuration."""
    return dynamic_settings


def update_config(section: str, updates: Dict[str, Any]) -> None:
    """Update configuration and save to file."""
    dynamic_settings.update_config(section, updates)
    save_dynamic_config(dynamic_settings)
