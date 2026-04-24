"""
Food Item model for storing food database information.
"""

from sqlalchemy import Column, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class FoodItem(Base):
    """Food item model for storing nutritional and FODMAP information."""

    __tablename__ = "food_items"

    id = Column(String, primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    fodmap_level = Column(String(20), nullable=False)  # low, moderate, high
    calories_per_100g = Column(Float, nullable=True)
    fiber_per_100g = Column(Float, nullable=True)
    fat_per_100g = Column(Float, nullable=True)
    protein_per_100g = Column(Float, nullable=True)
    carbs_per_100g = Column(Float, nullable=True)
    common_triggers = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return (
            f"<FoodItem(name='{self.name}', category='{self.category}', "
            f"fodmap_level='{self.fodmap_level}')>"
        )
