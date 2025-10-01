"""
API endpoints for symptom logging.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, func, desc, select

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.symptom import SymptomLog, SeverityEnum, BristolStoolTypeEnum
from app.schemas.symptom import (
    SymptomLogCreate,
    SymptomLogUpdate,
    SymptomLogResponse,
    SymptomLogList,
    SymptomStats,
    SymptomAnalytics
)

router = APIRouter()


@router.post("/", response_model=SymptomLogResponse)
async def create_symptom_log(
    symptom_data: SymptomLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new symptom log entry."""
    symptom_log = SymptomLog(
        user_id=current_user.id,
        symptom_id=symptom_data.symptom_id,
        severity=symptom_data.severity,
        bristol_stool_type=symptom_data.bristol_stool_type,
        bowel_movement_frequency=symptom_data.bowel_movement_frequency,
        pain_location=symptom_data.pain_location,
        pain_type=symptom_data.pain_type,
        stress_level=symptom_data.stress_level,
        sleep_quality=symptom_data.sleep_quality,
        exercise_minutes=symptom_data.exercise_minutes,
        potential_triggers=symptom_data.potential_triggers,
        notes=symptom_data.notes,
        logged_at=symptom_data.logged_at or datetime.utcnow()
    )
    
    db.add(symptom_log)
    await db.commit()
    await db.refresh(symptom_log)
    
    return symptom_log


@router.get("/", response_model=SymptomLogList)
async def get_symptom_logs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    severity: Optional[SeverityEnum] = Query(None, description="Filter by severity"),
    start_date: Optional[datetime] = Query(None, description="Filter from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter until this date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> SymptomLogList:
    """Get paginated list of symptom logs for the current user."""
    # Build query
    query = select(SymptomLog).filter(SymptomLog.user_id == current_user.id)
    
    # Apply filters
    if severity:
        query = query.filter(SymptomLog.severity == severity)
    if start_date:
        query = query.filter(SymptomLog.logged_at >= start_date)
    if end_date:
        query = query.filter(SymptomLog.logged_at <= end_date)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination and ordering
    query = query.order_by(desc(SymptomLog.logged_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    pages = (total + limit - 1) // limit
    
    return SymptomLogList(
        items=items,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=pages
    )


@router.get("/{symptom_id}", response_model=SymptomLogResponse)
async def get_symptom_log(
    symptom_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific symptom log by ID."""
    query = select(SymptomLog).filter(
        and_(
            SymptomLog.id == symptom_id,
            SymptomLog.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    symptom_log = result.scalar_one_or_none()
    
    if not symptom_log:
        raise HTTPException(status_code=404, detail="Symptom log not found")
    
    return symptom_log


@router.put("/{symptom_id}", response_model=SymptomLogResponse)
async def update_symptom_log(
    symptom_id: int,
    symptom_data: SymptomLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a symptom log entry."""
    query = select(SymptomLog).filter(
        and_(
            SymptomLog.id == symptom_id,
            SymptomLog.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    symptom_log = result.scalar_one_or_none()
    
    if not symptom_log:
        raise HTTPException(status_code=404, detail="Symptom log not found")
    
    # Update fields
    update_data = symptom_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(symptom_log, field, value)
    
    symptom_log.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(symptom_log)
    
    return symptom_log


@router.delete("/{symptom_id}")
async def delete_symptom_log(
    symptom_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a symptom log entry."""
    query = select(SymptomLog).filter(
        and_(
            SymptomLog.id == symptom_id,
            SymptomLog.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    symptom_log = result.scalar_one_or_none()
    
    if not symptom_log:
        raise HTTPException(status_code=404, detail="Symptom log not found")
    
    await db.delete(symptom_log)
    await db.commit()
    
    return {"message": "Symptom log deleted successfully"}



@router.get("/analytics/detailed", response_model=SymptomAnalytics)
async def get_symptom_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed symptom analytics for the current user."""
    start_date = datetime.utcnow() - timedelta(days=days)
    end_date = datetime.utcnow()
    
    # Date range
    date_range = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "days": days
    }
    
    # Symptom frequency by day (simplified)
    symptom_frequency = {}
    
    # Severity trends over time (simplified)
    severity_trends = {}
    
    # Trigger analysis (simplified)
    trigger_analysis = {}
    
    # Patterns (simplified)
    patterns = []
    
    return SymptomAnalytics(
        date_range=date_range,
        symptom_frequency=symptom_frequency,
        severity_trends=severity_trends,
        trigger_analysis=trigger_analysis,
        patterns=patterns
    )