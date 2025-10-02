"""
API endpoints for diet management and food reaction tracking.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, func, desc, or_, select

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_optional_current_user
from app.models.user import User
from app.models.diet import FoodReaction, DietLog, ReactionSeverityEnum, MealTypeEnum
from app.models.food_item import FoodItem
from app.schemas.diet import (
    FoodReactionCreate,
    FoodReactionUpdate,
    FoodReactionResponse,
    FoodReactionList,
    DietLogCreate,
    DietLogUpdate,
    DietLogResponse,
    DietLogList,
    FoodStats,
    DietStats,
    NutritionalAnalysis,
    TriggerFoodAnalysis,
)
from app.services.nutrition_calculator import NutritionCalculator

router = APIRouter()


# Food Reaction endpoints
@router.post("/reactions", response_model=FoodReactionResponse)
async def create_food_reaction(
    reaction_data: FoodReactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new food reaction entry."""
    food_reaction = FoodReaction(
        user_id=current_user.id,
        food_name=reaction_data.food_name,
        severity=reaction_data.severity,
        symptoms=reaction_data.symptoms,
        onset_time_minutes=reaction_data.onset_time_minutes,
        duration_minutes=reaction_data.duration_minutes,
        notes=reaction_data.notes,
        reaction_occurred_at=reaction_data.consumed_at or datetime.utcnow(),
    )

    db.add(food_reaction)
    await db.commit()
    await db.refresh(food_reaction)

    return food_reaction


@router.get("/reactions", response_model=FoodReactionList)
async def get_food_reactions(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    food_name: Optional[str] = Query(None, description="Filter by food name"),
    reaction_type: Optional[str] = Query(
        None, description="Filter by reaction type (placeholder)"
    ),
    severity: Optional[ReactionSeverityEnum] = Query(
        None, description="Filter by severity"
    ),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get paginated list of food reactions for the current user."""
    query = select(FoodReaction).filter(FoodReaction.user_id == current_user.id)

    # Apply filters
    if food_name:
        query = query.filter(FoodReaction.food_name.ilike(f"%{food_name}%"))
    if reaction_type:
        # Placeholder - no reaction_type field in model
        pass
    if severity:
        query = query.filter(FoodReaction.severity == severity)
    if start_date:
        query = query.filter(FoodReaction.reaction_occurred_at >= start_date)
    if end_date:
        query = query.filter(FoodReaction.reaction_occurred_at <= end_date)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * size
    query = (
        query.order_by(desc(FoodReaction.reaction_occurred_at))
        .offset(offset)
        .limit(size)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    pages = (total + size - 1) // size

    return FoodReactionList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/reactions/{reaction_id}", response_model=FoodReactionResponse)
async def get_food_reaction(
    reaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific food reaction by ID."""
    query = select(FoodReaction).filter(
        and_(FoodReaction.id == reaction_id, FoodReaction.user_id == current_user.id)
    )
    result = await db.execute(query)
    food_reaction = result.scalar_one_or_none()

    if not food_reaction:
        raise HTTPException(status_code=404, detail="Food reaction not found")

    return food_reaction


@router.put("/reactions/{reaction_id}", response_model=FoodReactionResponse)
async def update_food_reaction(
    reaction_id: int,
    reaction_data: FoodReactionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a food reaction entry."""
    query = select(FoodReaction).filter(
        and_(FoodReaction.id == reaction_id, FoodReaction.user_id == current_user.id)
    )
    result = await db.execute(query)
    food_reaction = result.scalar_one_or_none()

    if not food_reaction:
        raise HTTPException(status_code=404, detail="Food reaction not found")

    # Update fields
    update_data = reaction_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(food_reaction, field, value)

    food_reaction.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(food_reaction)

    return food_reaction


@router.delete("/reactions/{reaction_id}")
async def delete_food_reaction(
    reaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a food reaction entry."""
    query = select(FoodReaction).filter(
        and_(FoodReaction.id == reaction_id, FoodReaction.user_id == current_user.id)
    )
    result = await db.execute(query)
    food_reaction = result.scalar_one_or_none()

    if not food_reaction:
        raise HTTPException(status_code=404, detail="Food reaction not found")

    await db.delete(food_reaction)
    await db.commit()

    return {"message": "Food reaction deleted successfully"}


# Diet Log endpoints
@router.post("/logs", response_model=DietLogResponse)
async def create_diet_log(
    diet_data: DietLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new diet log entry."""
    from app.models.diet import Food, FoodCategoryEnum, FODMAPLevelEnum

    if not diet_data.foods:
        raise HTTPException(
            status_code=400, detail="At least one food item is required"
        )

    consumed_time = diet_data.consumed_at or datetime.utcnow()
    created_logs = []

    # Process each food item separately
    for food_name in diet_data.foods:
        # Try to find existing food with exact match first (case-sensitive)
        result = await db.execute(select(Food).where(Food.name == food_name))
        food = result.scalar_one_or_none()

        # If no exact match, try case-insensitive exact match with limit
        if not food:
            query = select(Food).where(
                func.lower(Food.name) == func.lower(food_name)
            ).limit(1)
            result = await db.execute(query)
            food = result.scalar_one_or_none()

        # If still no match, try partial match but limit to one result
        if not food:
            result = await db.execute(
                select(Food).where(Food.name.ilike(f"%{food_name}%")).limit(1)
            )
            food = result.scalar_one_or_none()

        # If food doesn't exist, create it
        if not food:
            food = Food(
                name=food_name,
                category=FoodCategoryEnum.SNACKS,  # Default category
                fodmap_level=FODMAPLevelEnum.UNKNOWN,
                is_active=True,
            )
            db.add(food)
            await db.flush()  # Get the ID without committing

        # Create diet log entry for this food
        diet_log = DietLog(
            user_id=current_user.id,
            food_id=food.id,
            meal_type=diet_data.meal_type,
            portion_size_g=100.0,  # Default portion size in grams
            portion_description=diet_data.portion_size,
            notes=diet_data.notes,
            consumed_at=consumed_time,
        )

        db.add(diet_log)
        created_logs.append(diet_log)

    await db.commit()

    # Refresh all created logs
    for log in created_logs:
        await db.refresh(log)

    # Return the first log for backward compatibility
    # In the future, we might want to return all logs or a summary
    return created_logs[0] if created_logs else None


@router.get("/logs", response_model=DietLogList)
async def get_diet_logs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    meal_type: Optional[MealTypeEnum] = Query(None, description="Filter by meal type"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get paginated list of diet logs for the current user."""
    # Build the query using select with join to get food information
    from app.models.diet import Food

    query = (
        select(DietLog, Food.name.label("food_name"))
        .join(Food, DietLog.food_id == Food.id)
        .filter(DietLog.user_id == current_user.id)
    )

    # Apply filters
    if meal_type:
        query = query.filter(DietLog.meal_type == meal_type)
    if start_date:
        query = query.filter(DietLog.consumed_at >= start_date)
    if end_date:
        query = query.filter(DietLog.consumed_at <= end_date)

    # Order by consumed_at to group meals properly
    query = query.order_by(desc(DietLog.consumed_at))

    # Execute the query to get all matching logs
    result = await db.execute(query)
    rows = result.all()

    # Group logs by meal (same consumed_at, meal_type, and user)
    meal_groups = {}
    for diet_log, food_name in rows:
        # Create a key for grouping meals (within 5 minutes of each other)
        meal_key = (
            diet_log.meal_type,
            diet_log.consumed_at.replace(second=0, microsecond=0),  # Group by minute
            diet_log.portion_description or "",
            diet_log.notes or "",
        )

        if meal_key not in meal_groups:
            meal_groups[meal_key] = {"diet_log": diet_log, "foods": []}

        meal_groups[meal_key]["foods"].append(food_name)

    # Convert grouped meals to list and sort by consumed_at
    grouped_meals = list(meal_groups.values())
    grouped_meals.sort(key=lambda x: x["diet_log"].consumed_at, reverse=True)

    # Apply pagination to grouped meals
    total = len(grouped_meals)
    offset = (page - 1) * size
    paginated_meals = grouped_meals[offset : offset + size]

    # Transform the results to include food names
    items = []
    for meal_group in paginated_meals:
        diet_log = meal_group["diet_log"]
        foods = meal_group["foods"]

        # Create a dict with all diet log attributes plus foods array
        item_dict = {
            "id": diet_log.id,
            "user_id": str(diet_log.user_id),
            "food_id": diet_log.food_id,
            "meal_type": diet_log.meal_type,
            "portion_size_g": diet_log.portion_size_g,
            "portion_description": diet_log.portion_description,
            "preparation_method": diet_log.preparation_method,
            "cooking_time_minutes": diet_log.cooking_time_minutes,
            "added_ingredients": diet_log.added_ingredients,
            "eaten_at_home": diet_log.eaten_at_home,
            "restaurant_name": diet_log.restaurant_name,
            "meal_companions": diet_log.meal_companions,
            "stress_level_before": diet_log.stress_level_before,
            "notes": diet_log.notes,
            "consumed_at": diet_log.consumed_at,
            "time_since_last_meal_hours": diet_log.time_since_last_meal_hours,
            "created_at": diet_log.created_at,
            "updated_at": diet_log.updated_at,
            "foods": foods,  # Include all foods from this meal
        }
        items.append(item_dict)

    pages = (total + size - 1) // size

    return DietLogList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/logs/{log_id}", response_model=DietLogResponse)
async def get_diet_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific diet log by ID."""
    diet_log = (
        db.query(DietLog)
        .filter(and_(DietLog.id == log_id, DietLog.user_id == current_user.id))
        .first()
    )

    if not diet_log:
        raise HTTPException(status_code=404, detail="Diet log not found")

    return diet_log


@router.put("/logs/{log_id}", response_model=DietLogResponse)
async def update_diet_log(
    log_id: int,
    diet_data: DietLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a diet log entry."""
    diet_log = (
        db.query(DietLog)
        .filter(and_(DietLog.id == log_id, DietLog.user_id == current_user.id))
        .first()
    )

    if not diet_log:
        raise HTTPException(status_code=404, detail="Diet log not found")

    # Update fields
    update_data = diet_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(diet_log, field, value)

    diet_log.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(diet_log)

    return diet_log


@router.delete("/logs/{log_id}")
async def delete_diet_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a diet log entry."""
    diet_log = (
        db.query(DietLog)
        .filter(and_(DietLog.id == log_id, DietLog.user_id == current_user.id))
        .first()
    )

    if not diet_log:
        raise HTTPException(status_code=404, detail="Diet log not found")

    db.delete(diet_log)
    db.commit()

    return {"message": "Diet log deleted successfully"}


# Enhanced nutritional analysis endpoints
@router.get("/nutrition/daily/{date}")
async def get_daily_nutrition_summary(
    date: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get comprehensive daily nutrition summary."""
    try:
        target_date = datetime.fromisoformat(date.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
        )

    calculator = NutritionCalculator(db)
    summary = await calculator.calculate_daily_nutrition_summary(
        str(current_user.id), target_date
    )

    return summary.to_dict()


@router.get("/nutrition/trends")
async def get_nutrition_trends(
    days: int = Query(30, ge=7, le=90, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get nutrition trends over a specified period."""
    calculator = NutritionCalculator(db)
    trends = await calculator.get_nutrition_trends(str(current_user.id), days)

    return trends


@router.post("/nutrition/calculate")
async def calculate_meal_nutrition(
    food_items: List[str],
    portion_size: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Calculate nutrition for a specific meal combination."""
    if not food_items:
        raise HTTPException(
            status_code=400, detail="At least one food item is required"
        )

    calculator = NutritionCalculator(db)
    nutrition = await calculator.calculate_meal_nutrition(food_items, portion_size)
    macros = calculator.calculate_macronutrient_breakdown(nutrition)

    return {
        "nutrition": nutrition.to_dict(),
        "macronutrient_breakdown": macros.to_dict(),
        "food_items": food_items,
        "portion_size": portion_size,
    }


@router.get("/nutrition/food/{food_name}")
async def get_food_nutrition_data(
    food_name: str,
    portion_size: Optional[str] = Query(
        "100g", description="Portion size (e.g., '1 cup', '150g')"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get detailed nutritional information for a specific food item."""
    calculator = NutritionCalculator(db)

    # Get base nutrition per 100g
    base_nutrition = await calculator.get_food_nutrition_per_100g(food_name)
    if not base_nutrition:
        raise HTTPException(
            status_code=404, detail=f"Food item '{food_name}' not found"
        )

    # Calculate for specified portion
    portion_grams = calculator.parse_portion_size(portion_size)
    portion_nutrition = calculator.calculate_nutrition_for_portion(
        base_nutrition, portion_grams
    )
    macros = calculator.calculate_macronutrient_breakdown(portion_nutrition)

    return {
        "food_name": food_name,
        "portion_size": portion_size,
        "portion_grams": portion_grams,
        "nutrition_per_100g": base_nutrition.to_dict(),
        "nutrition_for_portion": portion_nutrition.to_dict(),
        "macronutrient_breakdown": macros.to_dict(),
    }


# Analytics endpoints
@router.get("/stats/food", response_model=FoodStats)
async def get_food_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get food statistics for the current user."""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Get total reactions count
    total_reactions_result = await db.execute(
        select(func.count(FoodReaction.id)).where(
            and_(
                FoodReaction.user_id == current_user.id,
                FoodReaction.reaction_occurred_at >= start_date,
            )
        )
    )
    total_reactions = total_reactions_result.scalar() or 0

    # Most problematic foods
    problematic_foods_result = await db.execute(
        select(
            FoodReaction.food_name,
            func.count(FoodReaction.id).label("count"),
            func.avg(FoodReaction.severity).label("avg_severity"),
        )
        .where(
            and_(
                FoodReaction.user_id == current_user.id,
                FoodReaction.reaction_occurred_at >= start_date,
            )
        )
        .group_by(FoodReaction.food_name)
        .order_by(desc("count"))
        .limit(10)
    )

    most_problematic_foods = [
        {
            "food_name": row.food_name,
            "reaction_count": row.count,
            "avg_severity": float(row.avg_severity) if row.avg_severity else 0,
        }
        for row in problematic_foods_result.fetchall()
    ]

    # Get reactions by severity
    reactions_by_severity_result = await db.execute(
        select(
            FoodReaction.severity,
            func.count(FoodReaction.id).label("count"),
        )
        .where(
            and_(
                FoodReaction.user_id == current_user.id,
                FoodReaction.reaction_occurred_at >= start_date,
            )
        )
        .group_by(FoodReaction.severity)
    )

    reactions_by_severity = {
        row.severity.value: row.count
        for row in reactions_by_severity_result.fetchall()
    }

    reactions_by_type = {}

    return FoodStats(
        total_reactions=total_reactions,
        most_problematic_foods=most_problematic_foods,
        reaction_severity_distribution=reactions_by_severity,
        reaction_types_distribution=reactions_by_type,
        safe_foods=[],  # TODO: Implement safe foods logic
        trigger_foods=[],  # TODO: Implement trigger foods logic
    )


@router.get("/stats/diet", response_model=DietStats)
async def get_diet_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get diet statistics for the current user."""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Total meals count
    total_meals_result = await db.execute(
        select(func.count(DietLog.id))
        .where(
            and_(
                DietLog.user_id == current_user.id,
                DietLog.consumed_at >= start_date
            )
        )
    )
    total_meals = total_meals_result.scalar() or 0

    # Total calories (note: DietLog model doesn't have calories field based on schema)
    # Using placeholder for now
    average_daily_calories = 0

    # Meals by type
    meals_by_type_result = await db.execute(
        select(
            DietLog.meal_type,
            func.count(DietLog.id).label("count")
        )
        .where(
            and_(
                DietLog.user_id == current_user.id,
                DietLog.consumed_at >= start_date
            )
        )
        .group_by(DietLog.meal_type)
    )

    meals_by_type = {
        row.meal_type.value: row.count
        for row in meals_by_type_result.fetchall()
    }

    # Most frequent foods (simplified)
    frequent_foods = []
    # This would require parsing food_items JSON field
    # For now, returning empty list

    # Nutritional trends (placeholder)
    nutritional_trends = {"calories": "stable", "variety": "increasing"}

    return DietStats(
        total_meals_logged=total_meals,
        average_daily_calories=average_daily_calories,
        meals_by_type=meals_by_type,
        most_consumed_foods=frequent_foods,
        mood_correlation={},  # TODO: Implement mood correlation
    )


@router.get("/analysis/triggers", response_model=TriggerFoodAnalysis)
async def get_trigger_food_analysis(
    days: int = Query(90, ge=30, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get trigger food analysis for the current user."""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Get food reactions using async syntax
    reactions_result = await db.execute(
        select(FoodReaction)
        .where(
            and_(
                FoodReaction.user_id == current_user.id,
                FoodReaction.reaction_occurred_at >= start_date,
            )
        )
    )
    reactions = reactions_result.scalars().all()

    # Analyze trigger foods
    food_reaction_counts = {}
    food_severity_totals = {}

    for reaction in reactions:
        food_name = reaction.food_name.lower()
        if food_name not in food_reaction_counts:
            food_reaction_counts[food_name] = 0
            food_severity_totals[food_name] = 0

        food_reaction_counts[food_name] += 1
        food_severity_totals[food_name] += reaction.severity.value

    # Calculate trigger foods with risk scores
    trigger_foods = []
    for food_name, count in food_reaction_counts.items():
        if count >= 2:  # At least 2 reactions to be considered a trigger
            avg_severity = food_severity_totals[food_name] / count
            risk_score = min(
                100, (count * 20) + (avg_severity * 10)
            )  # Simple risk calculation

            trigger_foods.append(
                {
                    "food_name": food_name.title(),
                    "reaction_count": count,
                    "risk_score": round(risk_score, 1),
                    "average_severity": round(avg_severity, 1),
                }
            )

    # Sort by risk score
    trigger_foods.sort(key=lambda x: x["risk_score"], reverse=True)

    # Safe foods (foods logged but no reactions) - using async syntax
    diet_logs_result = await db.execute(
        select(DietLog)
        .where(
            and_(DietLog.user_id == current_user.id, DietLog.consumed_at >= start_date)
        )
    )
    _diet_logs = diet_logs_result.scalars().all()

    # This would require parsing food_items to identify safe foods
    # For now, returning placeholder
    safe_foods = ["Rice", "Bananas", "Chicken breast", "White bread"]

    # Recommendations
    recommendations = []
    if trigger_foods:
        recommendations.append(
            f"Consider avoiding or limiting {trigger_foods[0]['food_name']} "
            f"as it shows the highest risk score"
        )
        if len(trigger_foods) > 1:
            recommendations.append(
                "Keep a detailed food diary to identify patterns with "
                "trigger foods"
            )
    else:
        recommendations.append(
            "No clear trigger foods identified. Continue monitoring your diet"
        )

    recommendations.append(
        "Consult with a healthcare provider or dietitian for personalized advice"
    )

    return TriggerFoodAnalysis(
        analysis_period_days=days,
        trigger_foods=trigger_foods[:10],  # Top 10 trigger foods
        safe_foods=safe_foods,
        recommendations=recommendations,
    )


@router.get("/analysis/nutritional", response_model=NutritionalAnalysis)
async def get_nutritional_analysis(
    days: int = Query(30, ge=7, le=90, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get nutritional analysis for the current user."""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Note: DietLog model doesn't have calories field based on schema
    # Using placeholder values for nutritional analysis
    total_calories = 0
    average_daily_calories = 0

    # Placeholder nutritional breakdown
    nutritional_breakdown = {
        "carbohydrates": 45.0,  # percentage
        "proteins": 25.0,
        "fats": 30.0,
    }

    # Deficiency warnings (placeholder)
    deficiency_warnings = []
    if average_daily_calories < 1200:
        deficiency_warnings.append("Daily calorie intake appears low")

    # Dietary recommendations
    dietary_recommendations = [
        "Maintain a balanced diet with adequate fiber",
        "Stay hydrated throughout the day",
        "Consider smaller, more frequent meals",
    ]

    # IBS-specific insights
    ibs_specific_insights = [
        "Monitor FODMAP intake if following low-FODMAP diet",
        "Consider probiotic foods for gut health",
        "Track meal timing and portion sizes",
    ]

    return NutritionalAnalysis(
        analysis_period_days=days,
        average_daily_calories=average_daily_calories,
        nutritional_breakdown=nutritional_breakdown,
        deficiency_warnings=deficiency_warnings,
        dietary_recommendations=dietary_recommendations,
        ibs_specific_insights=ibs_specific_insights,
    )


@router.get("/food-suggestions")
async def get_food_suggestions(
    query: str = Query(
        "", description="Search query for food suggestions (empty for popular foods)"
    ),
    limit: int = Query(
        10, ge=1, le=50, description="Maximum number of suggestions to return"
    ),
    db: AsyncSession = Depends(get_db),
):
    """Get food suggestions based on search query for autocomplete functionality."""
    try:
        if query.strip():
            # Search in food_items table with query
            food_query = (
                select(FoodItem)
                .filter(FoodItem.name.ilike(f"%{query}%"))
                .order_by(FoodItem.name)
                .limit(limit)
            )
        else:
            # Return popular/common foods when no query provided
            food_query = select(FoodItem).order_by(FoodItem.name).limit(limit)

        result = await db.execute(food_query)
        food_items = result.scalars().all()

        # Also get user's previously logged foods for personalized suggestions
        user_foods = []
        # Removed user-specific suggestions for now to avoid authentication issues

        # Combine suggestions
        suggestions = []

        # Add database foods with additional info
        for food_item in food_items:
            suggestions.append(
                {
                    "name": food_item.name,
                    "category": food_item.category,
                    "fodmap_level": food_item.fodmap_level,
                    "is_common_trigger": food_item.common_triggers,
                    "source": "database",
                }
            )

        # Add user's previous foods
        for food in user_foods[: limit - len(suggestions)]:
            if len(suggestions) < limit:
                suggestions.append(
                    {
                        "name": food,
                        "category": "user_history",
                        "fodmap_level": None,
                        "is_common_trigger": None,
                        "source": "user_history",
                    }
                )

        # Add common foods if we don't have enough suggestions
        common_foods = [
            "Chicken breast",
            "Brown rice",
            "White rice",
            "Salmon",
            "Eggs",
            "Spinach",
            "Carrots",
            "Bananas",
            "Oats",
            "Quinoa",
            "Sweet potato",
            "Broccoli",
            "Bell pepper",
            "Cucumber",
            "Tomato",
        ]

        for food in common_foods:
            if len(suggestions) < limit and query.lower() in food.lower():
                if not any(s["name"].lower() == food.lower() for s in suggestions):
                    suggestions.append(
                        {
                            "name": food,
                            "category": "common",
                            "fodmap_level": "low",
                            "is_common_trigger": False,
                            "source": "common",
                        }
                    )

        return {"suggestions": suggestions[:limit], "total": len(suggestions[:limit])}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching food suggestions: {str(e)}"
        )
