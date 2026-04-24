"""
ML Models Package

This package contains machine learning models for IBS prediction and analysis.
"""

from .ibs_severity_classifier import IBSSeverityClassifier
from .flareup_predictor import FlareupPredictor
from .recommendation_engine import RecommendationEngine

__all__ = [
    "IBSSeverityClassifier",
    "FlareupPredictor", 
    "RecommendationEngine"
]