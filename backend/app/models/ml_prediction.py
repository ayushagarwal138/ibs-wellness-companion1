"""
ML Prediction Model

SQLAlchemy model for storing ML prediction results and metadata.
"""

from datetime import datetime
from typing import Dict, Any, Optional
import uuid

from sqlalchemy import Column, String, DateTime, Float, JSON, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class MLPrediction(Base):
    """Model for storing ML prediction results."""

    __tablename__ = "ml_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Prediction metadata
    # 'severity', 'flareup', 'recommendations'
    prediction_type = Column(String(50), nullable=False, index=True)
    model_version = Column(String(50), nullable=False, default='unknown')

    # Input and output data
    # User data used for prediction
    input_data = Column(JSON, nullable=False)
    # Raw prediction results
    prediction_data = Column(JSON, nullable=False)

    # Prediction metrics
    confidence_score = Column(Float, nullable=False, default=0.5)

    # Timestamps
    predicted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Optional fields for enhanced tracking
    # Features used in prediction
    model_features_used = Column(JSON, nullable=True)
    # Time taken for prediction
    processing_time_ms = Column(Float, nullable=True)
    # Whether fallback model was used
    is_fallback = Column(Boolean, default=False)

    def __repr__(self):
        return (
            f"<MLPrediction(id={self.id}, type={self.prediction_type}, "
            f"user_id={self.user_id})>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'prediction_type': self.prediction_type,
            'model_version': self.model_version,
            'input_data': self.input_data,
            'prediction_data': self.prediction_data,
            'confidence_score': self.confidence_score,
            'predicted_at': (
                self.predicted_at.isoformat() if self.predicted_at else None
            ),
            'created_at': (
                self.created_at.isoformat() if self.created_at else None
            ),
            'updated_at': (
                self.updated_at.isoformat() if self.updated_at else None
            ),
            'model_features_used': self.model_features_used,
            'processing_time_ms': self.processing_time_ms,
            'is_fallback': self.is_fallback
        }
