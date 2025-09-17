"""
API endpoints for medication tracking.
"""

from datetime import datetime, timedelta, time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.medication import MedicationLog, MedicationTypeEnum, AdherenceEnum, DosageUnitEnum
from app.schemas.medication import (
    MedicationLogCreate,
    MedicationLogUpdate,
    MedicationLogResponse,
    MedicationLogList,
    MedicationStats,
    MedicationSchedule,
    MedicationReminder,
    AdherenceReport
)

router = APIRouter()


@router.post("/", response_model=MedicationLogResponse)
async def create_medication_log(
    medication_data: MedicationLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new medication log entry."""
    # For now, we'll create a simple implementation that doesn't require the full medication reference
    # In a production system, you'd want to have a proper Medication table and reference it
    medication_log = MedicationLog(
        user_id=current_user.id,
        medication_id=1,  # Placeholder - would need proper medication lookup
        dosage_amount=1.0,  # Would parse from medication_data.dosage
        dosage_unit=DosageUnitEnum.MG,  # Would parse from medication_data.dosage
        taken_at=medication_data.taken_at or datetime.utcnow(),
        adherence=medication_data.adherence_status,
        notes=medication_data.notes,
        side_effects_experienced=medication_data.side_effects
    )
    
    db.add(medication_log)
    db.commit()
    db.refresh(medication_log)
    
    return medication_log


@router.get("/", response_model=MedicationLogList)
async def get_medication_logs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    medication_type: Optional[MedicationTypeEnum] = Query(None, description="Filter by medication type"),
    adherence_status: Optional[AdherenceEnum] = Query(None, description="Filter by adherence status"),
    medication_name: Optional[str] = Query(None, description="Filter by medication name"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get paginated list of medication logs for the current user."""
    query = db.query(MedicationLog).filter(MedicationLog.user_id == current_user.id)
    
    # Apply filters
    if medication_type:
        # This would need to be updated to filter by the medication table
        pass  # Placeholder
    if adherence_status:
        query = query.filter(MedicationLog.adherence == adherence_status)
    if medication_name:
        # This would need to join with medication table
        pass  # Placeholder
    if start_date:
        query = query.filter(MedicationLog.taken_at >= start_date)
    if end_date:
        query = query.filter(MedicationLog.taken_at <= end_date)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    items = query.order_by(desc(MedicationLog.taken_at)).offset(offset).limit(size).all()
    
    pages = (total + size - 1) // size
    
    return MedicationLogList(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{medication_id}", response_model=MedicationLogResponse)
async def get_medication_log(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific medication log by ID."""
    medication_log = db.query(MedicationLog).filter(
        and_(
            MedicationLog.id == medication_id,
            MedicationLog.user_id == current_user.id
        )
    ).first()
    
    if not medication_log:
        raise HTTPException(status_code=404, detail="Medication log not found")
    
    return medication_log


@router.put("/{medication_id}", response_model=MedicationLogResponse)
async def update_medication_log(
    medication_id: int,
    medication_data: MedicationLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a medication log entry."""
    medication_log = db.query(MedicationLog).filter(
        and_(
            MedicationLog.id == medication_id,
            MedicationLog.user_id == current_user.id
        )
    ).first()
    
    if not medication_log:
        raise HTTPException(status_code=404, detail="Medication log not found")
    
    # Update fields
    update_data = medication_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(medication_log, field, value)
    
    medication_log.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(medication_log)
    
    return medication_log


@router.delete("/{medication_id}")
async def delete_medication_log(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a medication log entry."""
    medication_log = db.query(MedicationLog).filter(
        and_(
            MedicationLog.id == medication_id,
            MedicationLog.user_id == current_user.id
        )
    ).first()
    
    if not medication_log:
        raise HTTPException(status_code=404, detail="Medication log not found")
    
    db.delete(medication_log)
    db.commit()
    
    return {"message": "Medication log deleted successfully"}


@router.get("/stats/summary", response_model=MedicationStats)
async def get_medication_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get medication statistics for the current user."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Base query for the time period
    base_query = db.query(MedicationLog).filter(
        and_(
            MedicationLog.user_id == current_user.id,
            MedicationLog.taken_at >= start_date
        )
    )
    
    # Total logs
    total_logs = base_query.count()
    
    # Adherence rate calculation
    taken_count = base_query.filter(MedicationLog.adherence == AdherenceEnum.TAKEN).count()
    adherence_rate = (taken_count / total_logs * 100) if total_logs > 0 else 0.0
    
    # Most taken medication (placeholder - would need medication table join)
    most_taken_medication = "Placeholder Medication"
    
    # Medications by type (placeholder)
    medications_by_type = {"prescription": total_logs}
    
    # Adherence by status
    adherence_by_status = {}
    status_counts = base_query.with_entities(
        MedicationLog.adherence,
        func.count(MedicationLog.id).label('count')
    ).group_by(MedicationLog.adherence).all()
    
    for status, count in status_counts:
        adherence_by_status[status.value] = count
    
    # Recent adherence trend (simplified)
    recent_adherence_trend = "stable"  # TODO: Implement trend analysis
    
    return MedicationStats(
        total_logs=total_logs,
        adherence_rate=adherence_rate,
        most_taken_medication=most_taken_medication,
        medications_by_type=medications_by_type,
        adherence_by_status=adherence_by_status,
        recent_adherence_trend=recent_adherence_trend
    )


@router.get("/adherence/report", response_model=AdherenceReport)
async def get_adherence_report(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed adherence report for the current user."""
    start_date = datetime.utcnow() - timedelta(days=days)
    end_date = datetime.utcnow()
    
    # Base query for the time period
    base_query = db.query(MedicationLog).filter(
        and_(
            MedicationLog.user_id == current_user.id,
            MedicationLog.taken_at >= start_date
        )
    )
    
    # Date range
    date_range = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "days": days
    }
    
    # Overall adherence rate
    total_logs = base_query.count()
    taken_count = base_query.filter(MedicationLog.adherence == AdherenceEnum.TAKEN).count()
    overall_adherence_rate = (taken_count / total_logs * 100) if total_logs > 0 else 0.0
    
    # Medication-specific adherence (placeholder)
    medication_adherence = {"Placeholder Medication": overall_adherence_rate}
    
    # Missed doses
    missed_doses = []
    missed_logs = base_query.filter(MedicationLog.adherence == AdherenceEnum.MISSED).all()
    
    for log in missed_logs:
        missed_doses.append({
            "medication_name": "Placeholder Medication",  # Would need medication table join
            "scheduled_time": None,  # Would need scheduling system
            "date": log.taken_at.date().isoformat(),
            "reason": log.notes
        })
    
    # Side effects reported
    side_effects_reported = base_query.filter(
        MedicationLog.side_effects_experienced.isnot(None),
        MedicationLog.side_effects_experienced != ""
    ).count()
    
    # Recommendations (simplified)
    recommendations = []
    if overall_adherence_rate < 80:
        recommendations.append("Consider setting up medication reminders to improve adherence")
    if side_effects_reported > 0:
        recommendations.append("Discuss reported side effects with your healthcare provider")
    if not recommendations:
        recommendations.append("Great job maintaining good medication adherence!")
    
    return AdherenceReport(
        date_range=date_range,
        overall_adherence_rate=overall_adherence_rate,
        medication_adherence=medication_adherence,
        missed_doses=missed_doses,
        side_effects_reported=side_effects_reported,
        recommendations=recommendations
    )


@router.post("/schedule", response_model=dict)
async def create_medication_schedule(
    schedule_data: MedicationSchedule,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a medication schedule (placeholder for future implementation)."""
    # TODO: Implement medication scheduling functionality
    # This would involve creating a separate MedicationSchedule model
    # and potentially integrating with a task scheduler for reminders
    
    return {
        "message": "Medication schedule created successfully",
        "schedule_id": "placeholder",
        "medication_name": schedule_data.medication_name,
        "frequency": schedule_data.frequency
    }


@router.get("/reminders", response_model=List[MedicationReminder])
async def get_medication_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get medication reminders for the current user (placeholder)."""
    # TODO: Implement medication reminders functionality
    # This would involve creating a MedicationReminder model
    # and integrating with a notification system
    
    return []


@router.post("/mark-taken/{medication_id}")
async def mark_medication_taken(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a scheduled medication as taken."""
    # For now, this creates a new log entry
    # TODO: Integrate with scheduling system
    
    return {"message": "Medication marked as taken", "medication_id": medication_id}