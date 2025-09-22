from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.models.user import User
from app.models.appointments import Appointment
from app.core.dependencies import get_current_user
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentListResponse
)

router = APIRouter()

@router.get("/", response_model=AppointmentListResponse)
async def get_appointments(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's appointments with optional filtering"""
    query = db.query(Appointment).filter(Appointment.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    if date_from:
        query = query.filter(Appointment.appointment_date >= date_from)
    
    if date_to:
        query = query.filter(Appointment.appointment_date <= date_to)
    
    total = query.count()
    appointments = query.offset(skip).limit(limit).all()
    
    return AppointmentListResponse(
        appointments=appointments,
        total=total,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new appointment"""
    # Check for scheduling conflicts
    existing_appointment = db.query(Appointment).filter(
        and_(
            Appointment.user_id == current_user.id,
            Appointment.appointment_date == appointment_data.appointment_date,
            Appointment.appointment_time == appointment_data.appointment_time,
            Appointment.status.in_(["scheduled", "confirmed"])
        )
    ).first()
    
    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An appointment is already scheduled at this time"
        )
    
    appointment = Appointment(
        user_id=current_user.id,
        **appointment_data.dict()
    )
    
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    return appointment

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific appointment"""
    appointment = db.query(Appointment).filter(
        and_(
            Appointment.id == appointment_id,
            Appointment.user_id == current_user.id
        )
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    return appointment

@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an appointment"""
    appointment = db.query(Appointment).filter(
        and_(
            Appointment.id == appointment_id,
            Appointment.user_id == current_user.id
        )
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check for scheduling conflicts if date/time is being updated
    update_data = appointment_data.dict(exclude_unset=True)
    if "appointment_date" in update_data or "appointment_time" in update_data:
        new_date = update_data.get("appointment_date", appointment.appointment_date)
        new_time = update_data.get("appointment_time", appointment.appointment_time)
        
        existing_appointment = db.query(Appointment).filter(
            and_(
                Appointment.user_id == current_user.id,
                Appointment.appointment_date == new_date,
                Appointment.appointment_time == new_time,
                Appointment.status.in_(["scheduled", "confirmed"]),
                Appointment.id != appointment_id
            )
        ).first()
        
        if existing_appointment:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An appointment is already scheduled at this time"
            )
    
    for field, value in update_data.items():
        setattr(appointment, field, value)
    
    appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(appointment)
    
    return appointment

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an appointment"""
    appointment = db.query(Appointment).filter(
        and_(
            Appointment.id == appointment_id,
            Appointment.user_id == current_user.id
        )
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    db.delete(appointment)
    db.commit()

@router.get("/upcoming/", response_model=List[AppointmentResponse])
async def get_upcoming_appointments(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get upcoming appointments"""
    today = date.today()
    appointments = db.query(Appointment).filter(
        and_(
            Appointment.user_id == current_user.id,
            Appointment.appointment_date >= today,
            Appointment.status.in_(["scheduled", "confirmed"])
        )
    ).order_by(
        Appointment.appointment_date.asc(),
        Appointment.appointment_time.asc()
    ).limit(limit).all()
    
    return appointments

@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
async def update_appointment_status(
    appointment_id: str,
    status_update: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update appointment status"""
    appointment = db.query(Appointment).filter(
        and_(
            Appointment.id == appointment_id,
            Appointment.user_id == current_user.id
        )
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    valid_statuses = ["scheduled", "confirmed", "completed", "cancelled", "no_show"]
    if status_update not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    appointment.status = status_update
    appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(appointment)
    
    return appointment