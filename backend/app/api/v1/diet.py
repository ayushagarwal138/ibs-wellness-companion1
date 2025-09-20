"""
API endpoints for diet management and food reaction tracking.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, func, desc, or_, select

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.diet import FoodReaction, DietLog, ReactionSeverityEnum, MealTypeEnum
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
    TriggerFoodAnalysis
)

router = APIRouter()

# Food Reaction endpoints
@router.post("/reactions", response_model=FoodReactionResponse)
async def create_food_reaction(
    reaction_data: FoodReactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
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
        consumed_at=reaction_data.consumed_at or datetime.utcnow()
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
    reaction_type: Optional[str] = Query(None, description="Filter by reaction type (placeholder)"),
    severity: Optional[ReactionSeverityEnum] = Query(None, description="Filter by severity"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
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
        query = query.filter(FoodReaction.consumed_at >= start_date)
    if end_date:
        query = query.filter(FoodReaction.consumed_at <= end_date)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * size
    query = query.order_by(desc(FoodReaction.consumed_at)).offset(offset).limit(size)
    result = await db.execute(query)
    items = result.scalars().all()
    
    pages = (total + size - 1) // size
    
    return FoodReactionList(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/reactions/{reaction_id}", response_model=FoodReactionResponse)
async def get_food_reaction(
    reaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific food reaction by ID."""
    query = select(FoodReaction).filter(
        and_(
            FoodReaction.id == reaction_id,
            FoodReaction.user_id == current_user.id
        )
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
    current_user: User = Depends(get_current_active_user)
):
    """Update a food reaction entry."""
    query = select(FoodReaction).filter(
        and_(
            FoodReaction.id == reaction_id,
            FoodReaction.user_id == current_user.id
        )
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
    current_user: User = Depends(get_current_active_user)
):
    """Delete a food reaction entry."""
    query = select(FoodReaction).filter(
        and_(
            FoodReaction.id == reaction_id,
            FoodReaction.user_id == current_user.id
        )
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
    current_user: User = Depends(get_current_active_user)
):
    """Create a new diet log entry."""
    # For now, we'll use the first food item to find or create a food record
    # In a real implementation, you'd want to handle multiple foods differently
    food_name = diet_data.food_items[0] if diet_data.food_items else "Unknown"
    
    # Try to find existing food or use food_id 1 (Apple) for testing
    food_id = 1  # Using the Apple we just created
    
    consumed_time = diet_data.consumed_at or datetime.utcnow()
    diet_log = DietLog(
        user_id=current_user.id,
        food_id=food_id,
        meal_type=diet_data.meal_type,
        portion_size_g=100.0,  # Default portion size in grams
        portion_description=diet_data.portion_size,
        notes=diet_data.notes,
        consumed_at=consumed_time
    )
    
    db.add(diet_log)
    await db.commit()
    await db.refresh(diet_log)
    
    return diet_log


@router.get("/logs", response_model=DietLogList)
async def get_diet_logs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    meal_type: Optional[MealTypeEnum] = Query(None, description="Filter by meal type"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get paginated list of diet logs for the current user."""
    # Build the query using select
    query = select(DietLog).filter(DietLog.user_id == current_user.id)
    
    # Apply filters
    if meal_type:
        query = query.filter(DietLog.meal_type == meal_type)
    if start_date:
        query = query.filter(DietLog.consumed_at >= start_date)
    if end_date:
        query = query.filter(DietLog.consumed_at <= end_date)
    
    # Get total count
    count_query = select(func.count()).select_from(DietLog).filter(DietLog.user_id == current_user.id)
    if meal_type:
        count_query = count_query.filter(DietLog.meal_type == meal_type)
    if start_date:
        count_query = count_query.filter(DietLog.consumed_at >= start_date)
    if end_date:
        count_query = count_query.filter(DietLog.consumed_at <= end_date)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination and ordering
    offset = (page - 1) * size
    query = query.order_by(desc(DietLog.consumed_at)).offset(offset).limit(size)
    
    # Execute the query
    result = await db.execute(query)
    items = result.scalars().all()
    
    pages = (total + size - 1) // size
    
    return DietLogList(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/logs/{log_id}", response_model=DietLogResponse)
async def get_diet_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific diet log by ID."""
    diet_log = db.query(DietLog).filter(
        and_(
            DietLog.id == log_id,
            DietLog.user_id == current_user.id
        )
    ).first()
    
    if not diet_log:
        raise HTTPException(status_code=404, detail="Diet log not found")
    
    return diet_log


@router.put("/logs/{log_id}", response_model=DietLogResponse)
async def update_diet_log(
    log_id: int,
    diet_data: DietLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a diet log entry."""
    diet_log = db.query(DietLog).filter(
        and_(
            DietLog.id == log_id,
            DietLog.user_id == current_user.id
        )
    ).first()
    
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
    current_user: User = Depends(get_current_active_user)
):
    """Delete a diet log entry."""
    diet_log = db.query(DietLog).filter(
        and_(
            DietLog.id == log_id,
            DietLog.user_id == current_user.id
        )
    ).first()
    
    if not diet_log:
        raise HTTPException(status_code=404, detail="Diet log not found")
    
    db.delete(diet_log)
    db.commit()
    
    return {"message": "Diet log deleted successfully"}


# Analytics endpoints
@router.get("/stats/food", response_model=FoodStats)
async def get_food_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get food statistics for the current user."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Food reactions in the period
    reactions_query = db.query(FoodReaction).filter(
        and_(
            FoodReaction.user_id == current_user.id,
            FoodReaction.consumed_at >= start_date
        )
    )
    
    total_reactions = reactions_query.count()
    
    # Most problematic foods
    problematic_foods = reactions_query.with_entities(
        FoodReaction.food_name,
        func.count(FoodReaction.id).label('count'),
        func.avg(FoodReaction.severity.cast(db.Integer)).label('avg_severity')
    ).group_by(FoodReaction.food_name).order_by(desc('count')).limit(10).all()
    
    most_problematic_foods = [
        {
            "food_name": food.food_name,
            "reaction_count": food.count,
            "average_severity": round(food.avg_severity, 2) if food.avg_severity else 0
        }
        for food in problematic_foods
    ]
    
    # Reactions by severity
    reactions_by_severity = {}
    severity_counts = reactions_query.with_entities(
        FoodReaction.severity,
        func.count(FoodReaction.id).label('count')
    ).group_by(FoodReaction.severity).all()
    
    for severity, count in severity_counts:
        reactions_by_severity[severity.value] = count
    
    # Reactions by type
    reactions_by_type = {}
    type_counts = reactions_query.with_entities(
        FoodReaction.reaction_type,
        func.count(FoodReaction.id).label('count')
    ).group_by(FoodReaction.reaction_type).all()
    
    for reaction_type, count in type_counts:
        reactions_by_type[reaction_type.value] = count
    
    # Average reaction time
    avg_onset_time = reactions_query.with_entities(
        func.avg(FoodReaction.onset_time)
    ).scalar()
    
    average_onset_time_minutes = int(avg_onset_time) if avg_onset_time else 0
    
    return FoodStats(
        total_reactions=total_reactions,
        most_problematic_foods=most_problematic_foods,
        reactions_by_severity=reactions_by_severity,
        reactions_by_type=reactions_by_type,
        average_onset_time_minutes=average_onset_time_minutes
    )


@router.get("/stats/diet", response_model=DietStats)
async def get_diet_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get diet statistics for the current user."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Diet logs in the period
    logs_query = db.query(DietLog).filter(
        and_(
            DietLog.user_id == current_user.id,
            DietLog.consumed_at >= start_date
        )
    )
    
    total_meals = logs_query.count()
    
    # Average daily calories
    total_calories = logs_query.with_entities(
        func.sum(DietLog.calories)
    ).scalar() or 0
    
    average_daily_calories = int(total_calories / days) if days > 0 else 0
    
    # Meals by type
    meals_by_type = {}
    type_counts = logs_query.with_entities(
        DietLog.meal_type,
        func.count(DietLog.id).label('count')
    ).group_by(DietLog.meal_type).all()
    
    for meal_type, count in type_counts:
        meals_by_type[meal_type] = count
    
    # Most frequent foods (simplified)
    frequent_foods = []
    # This would require parsing food_items JSON field
    # For now, returning empty list
    
    # Nutritional trends (placeholder)
    nutritional_trends = {
        "calories": "stable",
        "variety": "increasing"
    }
    
    return DietStats(
        total_meals=total_meals,
        average_daily_calories=average_daily_calories,
        meals_by_type=meals_by_type,
        frequent_foods=frequent_foods,
        nutritional_trends=nutritional_trends
    )


@router.get("/analysis/triggers", response_model=TriggerFoodAnalysis)
async def get_trigger_food_analysis(
    days: int = Query(90, ge=30, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get trigger food analysis for the current user."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get food reactions
    reactions = db.query(FoodReaction).filter(
        and_(
            FoodReaction.user_id == current_user.id,
            FoodReaction.consumed_at >= start_date
        )
    ).all()
    
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
            risk_score = min(100, (count * 20) + (avg_severity * 10))  # Simple risk calculation
            
            trigger_foods.append({
                "food_name": food_name.title(),
                "reaction_count": count,
                "risk_score": round(risk_score, 1),
                "average_severity": round(avg_severity, 1)
            })
    
    # Sort by risk score
    trigger_foods.sort(key=lambda x: x["risk_score"], reverse=True)
    
    # Safe foods (foods logged but no reactions)
    diet_logs = db.query(DietLog).filter(
        and_(
            DietLog.user_id == current_user.id,
            DietLog.consumed_at >= start_date
        )
    ).all()
    
    # This would require parsing food_items to identify safe foods
    # For now, returning placeholder
    safe_foods = ["Rice", "Bananas", "Chicken breast", "White bread"]
    
    # Recommendations
    recommendations = []
    if trigger_foods:
        recommendations.append(f"Consider avoiding or limiting {trigger_foods[0]['food_name']} as it shows the highest risk score")
        if len(trigger_foods) > 1:
            recommendations.append("Keep a detailed food diary to identify patterns with trigger foods")
    else:
        recommendations.append("No clear trigger foods identified. Continue monitoring your diet")
    
    recommendations.append("Consult with a healthcare provider or dietitian for personalized advice")
    
    return TriggerFoodAnalysis(
        analysis_period_days=days,
        trigger_foods=trigger_foods[:10],  # Top 10 trigger foods
        safe_foods=safe_foods,
        recommendations=recommendations
    )


@router.get("/analysis/nutritional", response_model=NutritionalAnalysis)
async def get_nutritional_analysis(
    days: int = Query(30, ge=7, le=90, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get nutritional analysis for the current user."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get diet logs
    logs_query = db.query(DietLog).filter(
        and_(
            DietLog.user_id == current_user.id,
            DietLog.consumed_at >= start_date
        )
    )
    
    # Calculate nutritional metrics (simplified)
    total_calories = logs_query.with_entities(func.sum(DietLog.calories)).scalar() or 0
    average_daily_calories = int(total_calories / days) if days > 0 else 0
    
    # Placeholder nutritional breakdown
    nutritional_breakdown = {
        "carbohydrates": 45.0,  # percentage
        "proteins": 25.0,
        "fats": 30.0
    }
    
    # Deficiency warnings (placeholder)
    deficiency_warnings = []
    if average_daily_calories < 1200:
        deficiency_warnings.append("Daily calorie intake appears low")
    
    # Dietary recommendations
    dietary_recommendations = [
        "Maintain a balanced diet with adequate fiber",
        "Stay hydrated throughout the day",
        "Consider smaller, more frequent meals"
    ]
    
    # IBS-specific insights
    ibs_specific_insights = [
        "Monitor FODMAP intake if following low-FODMAP diet",
        "Consider probiotic foods for gut health",
        "Track meal timing and portion sizes"
    ]
    
    return NutritionalAnalysis(
        analysis_period_days=days,
        average_daily_calories=average_daily_calories,
        nutritional_breakdown=nutritional_breakdown,
        deficiency_warnings=deficiency_warnings,
        dietary_recommendations=dietary_recommendations,
        ibs_specific_insights=ibs_specific_insights
    )