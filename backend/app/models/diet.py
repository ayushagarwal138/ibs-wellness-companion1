"""
Diet models for tracking food intake and reactions.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, Float, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class FoodCategoryEnum(str, enum.Enum):
    """Food category enumeration."""
    GRAINS = "grains"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    PROTEINS = "proteins"
    DAIRY = "dairy"
    FATS_OILS = "fats_oils"
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    CONDIMENTS = "condiments"
    SUPPLEMENTS = "supplements"


class FODMAPLevelEnum(str, enum.Enum):
    """FODMAP level enumeration."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    UNKNOWN = "unknown"


class MealTypeEnum(str, enum.Enum):
    """Meal type enumeration."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    BEVERAGE = "beverage"


class ReactionSeverityEnum(str, enum.Enum):
    """Food reaction severity enumeration."""
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class Food(Base):
    """Food reference table."""

    __tablename__ = "foods"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Food details
    name = Column(String(200), nullable=False, index=True)
    brand = Column(String(100), nullable=True)
    category: Column[FoodCategoryEnum] = Column(Enum(FoodCategoryEnum), nullable=False, index=True)

    # Nutritional information (per 100g)
    calories_per_100g = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    fiber_g = Column(Float, nullable=True)
    sugar_g = Column(Float, nullable=True)
    sodium_mg = Column(Float, nullable=True)

    # IBS-specific information
    fodmap_level: Column[FODMAPLevelEnum] = Column(Enum(FODMAPLevelEnum), nullable=True, index=True)
    fodmap_details = Column(Text, nullable=True)  # JSON string with specific FODMAP types
    common_triggers = Column(Text, nullable=True)  # JSON array of common trigger compounds

    # Additional information
    ingredients = Column(Text, nullable=True)  # JSON array of ingredients
    allergens = Column(Text, nullable=True)  # JSON array of allergens
    preparation_notes = Column(Text, nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    diet_logs = relationship("DietLog", back_populates="food")
    food_reactions = relationship("FoodReaction", back_populates="food")

    def __repr__(self) -> str:
        return f"<Food(id={self.id}, name='{self.name}', category='{self.category}')>"


class DietLog(Base):
    """User diet log entries - matching actual database schema."""

    __tablename__ = "diet_logs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False, index=True)

    # Basic log info
    meal_type: Column[MealTypeEnum] = Column(Enum(MealTypeEnum), nullable=False)
    portion_size_g = Column(Numeric(10, 2), nullable=True)
    portion_description = Column(String(100), nullable=True)
    preparation_method = Column(String(100), nullable=True)
    cooking_time_minutes = Column(Integer, nullable=True)
    added_ingredients = Column(Text, nullable=True)
    eaten_at_home = Column(Boolean, nullable=True)
    restaurant_name = Column(String(200), nullable=True)
    meal_companions = Column(Integer, nullable=True)
    stress_level_before = Column(Integer, nullable=True)
    
    # Mood tracking
    mood_before = Column(Integer, nullable=True)  # 1-10 scale
    mood_after = Column(Integer, nullable=True)   # 1-10 scale

    # Timing
    consumed_at = Column(DateTime(timezone=True), nullable=False)
    time_since_last_meal_hours = Column(Numeric(5, 2), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="diet_logs")
    food = relationship("Food", back_populates="diet_logs")

    def __repr__(self) -> str:
        return f"<DietLog(id={self.id}, user_id={self.user_id}, meal_type='{self.meal_type}')>"


class FoodReaction(Base):
    """User food reaction tracking."""

    __tablename__ = "food_reactions"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False, index=True)
    diet_log_id = Column(
        UUID(as_uuid=True), ForeignKey("diet_logs.id"), nullable=True, index=True
    )  # Optional link to specific consumption

    # Reaction details
    severity: Column[ReactionSeverityEnum] = Column(Enum(ReactionSeverityEnum), nullable=False)
    symptoms = Column(Text, nullable=False)  # JSON array of symptoms experienced
    onset_time_minutes = Column(Integer, nullable=True)  # Time after eating when reaction started
    duration_minutes = Column(Integer, nullable=True)

    # Context
    suspected_trigger = Column(String(200), nullable=True)  # Specific ingredient suspected
    confidence_level = Column(
        Integer, nullable=True
    )  # 1-10 scale of confidence this food caused reaction
    other_foods_consumed = Column(
        Text, nullable=True
    )  # JSON array of other foods eaten around same time

    # Environmental factors
    stress_level = Column(Integer, nullable=True)  # 1-10 scale
    sleep_quality_previous_night = Column(Integer, nullable=True)  # 1-10 scale
    menstrual_cycle_day = Column(Integer, nullable=True)  # For female users

    # Reaction management
    treatment_taken = Column(Text, nullable=True)  # What was done to manage the reaction
    effectiveness_of_treatment = Column(Integer, nullable=True)  # 1-10 scale

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    reaction_occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="food_reactions")
    food = relationship("Food", back_populates="food_reactions")
    diet_log = relationship("DietLog")

    def __repr__(self) -> str:
        return (
            f"<FoodReaction(id={self.id}, user_id={self.user_id}, "
            f"food_id={self.food_id}, severity='{self.severity}')>"
        )

    @property
    def severity_score(self) -> int:
        """Convert severity enum to numeric score."""
        severity_scores = {
            ReactionSeverityEnum.NONE: 0,
            ReactionSeverityEnum.MILD: 1,
            ReactionSeverityEnum.MODERATE: 2,
            ReactionSeverityEnum.SEVERE: 3,
        }
        return severity_scores.get(ReactionSeverityEnum(self.severity), 0)
