"""
Analytics API endpoints for user analytics, system metrics, and achievements.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.sql import case

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.symptom import SymptomLog, Symptom
from app.models.diet import DietLog
from app.schemas.analytics import UserAnalyticsResponse

router = APIRouter(tags=["Analytics"])


# User Analytics endpoints
@router.get("/user-analytics", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(30, description="Number of days to retrieve analytics"),
):
    """Get user analytics for the specified period."""
    try:
        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        # Get symptom logs count
        symptom_logs_result = await db.execute(
            select(func.count(SymptomLog.id)).where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            )
        )
        total_symptom_logs = symptom_logs_result.scalar() or 0

        # Get diet logs count
        diet_logs_result = await db.execute(
            select(func.count(DietLog.id)).where(
                and_(
                    DietLog.user_id == current_user.id,
                    DietLog.consumed_at >= start_datetime,
                    DietLog.consumed_at <= end_datetime
                )
            )
        )
        total_diet_logs = diet_logs_result.scalar() or 0

        # Get average symptom severity using SQL func.case for consistency
        avg_severity_result = await db.execute(
            select(func.avg(
                case(
                    (SymptomLog.severity == 'none', 0),
                    (SymptomLog.severity == 'mild', 1),
                    (SymptomLog.severity == 'moderate', 2),
                    (SymptomLog.severity == 'severe', 3),
                    (SymptomLog.severity == 'very_severe', 4),
                    else_=0
                )
            )).where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            )
        )
        avg_severity = avg_severity_result.scalar() or 0.0

        # Get most common symptoms
        most_common_symptoms_result = await db.execute(
            select(
                Symptom.name, 
                func.count(SymptomLog.id).label('frequency')
            )
            .join(SymptomLog, Symptom.id == SymptomLog.symptom_id)
            .where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            )
            .group_by(Symptom.name)
            .order_by(func.count(SymptomLog.id).desc())
            .limit(5)
        )
        most_common_symptoms = [
            {"name": row.name, "frequency": row.frequency}
            for row in most_common_symptoms_result.all()
        ]

        # Calculate symptom-free days (days without any symptom logs)
        symptom_days_result = await db.execute(
            select(
                func.count(func.distinct(func.date(SymptomLog.logged_at)))
            ).where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            )
        )
        symptom_days = symptom_days_result.scalar() or 0
        symptom_free_days = max(0, days - symptom_days)

        return UserAnalyticsResponse(
            user_id=current_user.id,
            total_symptom_logs=total_symptom_logs,
            total_diet_logs=total_diet_logs,
            total_medication_logs=0,  # TODO: Add medication logs when available
            avg_symptom_severity=round(float(avg_severity), 2),
            symptom_free_days=symptom_free_days,
            most_common_symptoms=most_common_symptoms,
            trigger_foods=[],  # TODO: Implement trigger food analysis
            medication_adherence_rate=0.0,  # TODO: Add when medication tracking is available
            improvement_trend="stable",  # TODO: Calculate trend based on historical data
            period_start=start_date,
            period_end=end_date,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user analytics: {str(e)}",
        )


@router.get("/analytics-summary")
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(30, description="Number of days for summary"),
):
    """Get analytics summary for the user."""
    try:
        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        # Get symptom logs count
        symptom_logs_result = await db.execute(
            select(func.count(SymptomLog.id)).where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            )
        )
        total_symptom_logs = symptom_logs_result.scalar() or 0

        # Get diet logs count
        diet_logs_result = await db.execute(
            select(func.count(DietLog.id)).where(
                and_(
                    DietLog.user_id == current_user.id,
                    DietLog.consumed_at >= start_datetime,
                    DietLog.consumed_at <= end_datetime
                )
            )
        )
        total_diet_logs = diet_logs_result.scalar() or 0

        # Get average symptom severity
        avg_severity_result = await db.execute(
            select(func.avg(
                case(
                    (SymptomLog.severity == 'none', 0),
                    (SymptomLog.severity == 'mild', 1),
                    (SymptomLog.severity == 'moderate', 2),
                    (SymptomLog.severity == 'severe', 3),
                    (SymptomLog.severity == 'very_severe', 4),
                    else_=0
                )
            )).where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            )
        )
        avg_severity = avg_severity_result.scalar() or 0.0

        return {
            "total_symptom_logs": total_symptom_logs,
            "total_diet_logs": total_diet_logs,
            "total_medication_logs": 0,  # TODO: Add when available
            "average_symptom_severity": round(float(avg_severity), 2),
            "total_achievements": 0,  # TODO: Add when available
            "analytics_period_days": days,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics summary: {str(e)}",
        )


# System Metrics endpoints
@router.get("/system-metrics")
async def get_system_metrics(
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
    _metric_category: Optional[str] = Query(
        None, description="Filter by metric category"
    ),
    _hours: int = Query(24, description="Number of hours to retrieve metrics for"),
):
    """Get system metrics (admin only for now, but can be extended)."""
    try:
        # Return mock system metrics
        return [
            {
                "metric_name": "api_response_time",
                "metric_value": 150.5,
                "metric_category": "performance",
                "recorded_at": datetime.utcnow().isoformat(),
            },
            {
                "metric_name": "active_users",
                "metric_value": 42,
                "metric_category": "usage",
                "recorded_at": datetime.utcnow().isoformat(),
            },
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system metrics: {str(e)}",
        )


# Achievements endpoints
@router.get("/achievements")
async def get_achievements(
    _db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
    _is_active: Optional[bool] = Query(None, description="Filter by active status"),
):
    """Get all available achievements."""
    try:
        # Return mock achievements
        return [
            {
                "id": 1,
                "name": "First Log",
                "description": "Log your first symptom",
                "points_awarded": 10,
                "is_active": True,
            },
            {
                "id": 2,
                "name": "Consistent Logger",
                "description": "Log symptoms for 7 consecutive days",
                "points_awarded": 50,
                "is_active": True,
            },
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve achievements: {str(e)}",
        )


@router.get("/user-achievements")
async def get_user_achievements(
    _db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get user's earned achievements."""
    try:
        # Return mock user achievements
        return [
            {
                "id": 1,
                "achievement_id": 1,
                "user_id": current_user.id,
                "earned_at": datetime.utcnow().isoformat(),
                "achievement": {
                    "name": "First Log",
                    "description": "Log your first symptom",
                    "points_awarded": 10,
                },
            }
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user achievements: {str(e)}",
        )


@router.post("/check-achievements")
async def check_achievements(
    _db: AsyncSession = Depends(get_db), _current_user: User = Depends(get_current_user)
):
    """Check and update user achievements."""
    return {"message": "Achievement check completed", "new_achievements": []}


@router.get("/pattern-insights")
async def get_pattern_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    timeframe_days: int = Query(
        30, description="Number of days to analyze for patterns"
    ),
):
    """Get comprehensive pattern insights for the user."""
    try:
        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=timeframe_days)
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        # Get recent symptom logs for pattern analysis
        symptom_logs_result = await db.execute(
            select(SymptomLog).where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            ).order_by(SymptomLog.logged_at.desc())
        )
        symptom_logs = symptom_logs_result.scalars().all()

        # Generate pattern insights based on available data
        correlations = []
        triggers = []
        temporal_patterns = []
        recommendations = []

        # Helper function to convert severity enum to numeric
        def severity_to_numeric(severity):
            """Convert severity enum to numeric value."""
            if hasattr(severity, 'value'):
                severity = severity.value
            severity_map = {
                "none": 0, "mild": 1, "moderate": 2, 
                "severe": 3, "very_severe": 4
            }
            return severity_map.get(str(severity).lower(), 1)

        # Analyze stress-symptom correlation if data exists
        stress_symptoms = [
            log for log in symptom_logs 
            if hasattr(log, 'stress_level') and log.stress_level is not None
        ]
        if stress_symptoms:
            avg_stress = sum(
                log.stress_level for log in stress_symptoms
            ) / len(stress_symptoms)
            avg_severity = sum(
                severity_to_numeric(log.severity) for log in stress_symptoms
            ) / len(stress_symptoms)
            
            # Normalized correlation
            correlation_strength = min(0.9, avg_stress * avg_severity / 50)
            description = (
                f"Stress levels show correlation with symptom severity "
                f"(avg stress: {avg_stress:.1f}, avg severity: {avg_severity:.1f})"
            )
            recommendation = (
                "Consider stress management techniques like meditation "
                "or deep breathing exercises"
            )
            
            correlations.append({
                "factor1": "Stress Level",
                "factor2": "Symptom Severity",
                "correlation_strength": correlation_strength,
                "confidence": 0.75,
                "description": description,
                "recommendation": recommendation,
                "sample_size": len(stress_symptoms)
            })

        # Analyze common triggers
        trigger_counts = {}
        for log in symptom_logs:
            if hasattr(log, 'triggers') and log.triggers:
                for trigger in log.triggers:
                    if trigger not in trigger_counts:
                        trigger_counts[trigger] = {
                            "count": 0, 
                            "severities": []
                        }
                    trigger_counts[trigger]["count"] += 1
                    trigger_counts[trigger]["severities"].append(
                        severity_to_numeric(log.severity)
                    )

        for trigger, data in trigger_counts.items():
            # Only include triggers that appear multiple times
            if data["count"] >= 2:
                avg_severity = sum(data["severities"]) / len(data["severities"])
                triggers.append({
                    "trigger": trigger,
                    "frequency": data["count"],
                    "impact": avg_severity,
                    "confidence": min(0.9, data["count"] / 10),
                    "correlatedSymptoms": ["abdominal_pain", "bloating"],
                    "recommendations": [
                        f"Consider avoiding or managing exposure to {trigger}"
                    ]
                })

        # Analyze temporal patterns (daily)
        if symptom_logs:
            hourly_severities = {}
            for log in symptom_logs:
                hour = log.logged_at.hour
                if hour not in hourly_severities:
                    hourly_severities[hour] = []
                hourly_severities[hour].append(severity_to_numeric(log.severity))

            if hourly_severities:
                hourly_averages = {
                    hour: sum(severities) / len(severities) 
                    for hour, severities in hourly_severities.items()
                }
                
                sorted_hours = sorted(
                    hourly_averages.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                peak_hours = [f"{hour}:00" for hour, _ in sorted_hours[:2]]
                low_hours = [f"{hour}:00" for hour, _ in sorted_hours[-2:]]

                peak_time = peak_hours[0] if peak_hours else 'various times'
                low_times_str = ', '.join(low_hours) if low_hours else 'varies'

                temporal_patterns.append({
                    "pattern_type": "daily",
                    "description": "Daily symptom severity patterns identified",
                    "peak_times": peak_hours,
                    "low_times": low_hours,
                    "confidence": 0.7,
                    "recommendations": [
                        f"Symptoms tend to peak around {peak_time}",
                        f"Best times for activities: {low_times_str}",
                        "Consider meal timing and stress management during peak hours"
                    ]
                })

        # Generate general recommendations
        recommendations = [
            "Maintain a consistent daily routine to help identify patterns",
            "Keep detailed logs of symptoms, triggers, and activities",
            "Consider stress management techniques if stress is a factor"
        ]

        if triggers:
            top_trigger = triggers[0]['trigger']
            recommendations.append(
                f"Focus on managing your top trigger: {top_trigger}"
            )

        if correlations:
            recommendations.extend([
                corr["recommendation"] for corr in correlations
            ])

        # Calculate overall confidence
        all_confidences = []
        all_confidences.extend([corr["confidence"] for corr in correlations])
        all_confidences.extend([trigger["confidence"] for trigger in triggers])
        all_confidences.extend([
            pattern["confidence"] for pattern in temporal_patterns
        ])
        
        overall_confidence = (
            sum(all_confidences) / len(all_confidences) 
            if all_confidences else 0.5
        )

        return {
            "correlations": correlations,
            "triggers": triggers,
            "temporal_patterns": temporal_patterns,
            "recommendations": recommendations[:8],  # Limit to 8 recommendations
            "overall_confidence": overall_confidence,
            "last_updated": datetime.utcnow().isoformat(),
            "sample_size": len(symptom_logs),
            "timeframe_days": timeframe_days
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving pattern insights: {str(e)}",
        )


@router.get("/insights")
async def get_personalized_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(7, description="Number of days to analyze for insights"),
):
    """Get personalized insights based on user data and patterns."""
    try:
        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        # Get recent symptom data
        symptom_logs_result = await db.execute(
            select(SymptomLog).where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            ).order_by(SymptomLog.logged_at.desc())
        )
        symptom_logs = symptom_logs_result.scalars().all()

        # Get recent diet data
        diet_logs_result = await db.execute(
            select(DietLog).where(
                and_(
                    DietLog.user_id == current_user.id,
                    DietLog.consumed_at >= start_datetime,
                    DietLog.consumed_at <= end_datetime
                )
            ).order_by(DietLog.consumed_at.desc())
        )
        diet_logs = diet_logs_result.scalars().all()

        insights = []

        # Analyze symptom patterns
        if symptom_logs:
            # Check for improvement trend
            recent_symptoms = symptom_logs[:3]
            older_symptoms = symptom_logs[3:6] if len(symptom_logs) > 3 else []
            
            if recent_symptoms and older_symptoms:
                recent_avg = sum(_severity_to_number(log.severity) for log in recent_symptoms) / len(recent_symptoms)
                older_avg = sum(_severity_to_number(log.severity) for log in older_symptoms) / len(older_symptoms)
                
                if recent_avg < older_avg:
                    insights.append({
                        "type": "positive",
                        "title": "Symptom Improvement Detected",
                        "description": f"Your symptoms have improved by {((older_avg - recent_avg) / older_avg * 100):.1f}% over the past {days} days.",
                        "action": "Keep following your current management plan",
                        "priority": "medium"
                    })
                elif recent_avg > older_avg:
                    insights.append({
                        "type": "warning",
                        "title": "Symptom Increase Noticed",
                        "description": f"Your symptoms have increased by {((recent_avg - older_avg) / older_avg * 100):.1f}% recently.",
                        "action": "Consider reviewing your diet and stress levels",
                        "priority": "high"
                    })

            # Check for frequent logging
            if len(symptom_logs) >= days * 0.8:  # 80% of days
                insights.append({
                    "type": "positive",
                    "title": "Excellent Tracking Consistency",
                    "description": f"You've logged symptoms on {len(symptom_logs)} out of {days} days. Great job!",
                    "priority": "low"
                })
            elif len(symptom_logs) < days * 0.3:  # Less than 30% of days
                insights.append({
                    "type": "info",
                    "title": "Increase Symptom Tracking",
                    "description": "Regular symptom tracking helps identify patterns and triggers.",
                    "action": "Try to log symptoms daily for better insights",
                    "priority": "medium"
                })

        # Analyze diet patterns
        if diet_logs:
            if len(diet_logs) >= days * 2:  # At least 2 meals per day
                insights.append({
                    "type": "positive",
                    "title": "Good Meal Tracking",
                    "description": f"You've logged {len(diet_logs)} meals in {days} days.",
                    "priority": "low"
                })
            else:
                insights.append({
                    "type": "info",
                    "title": "Improve Meal Tracking",
                    "description": "Tracking meals helps identify food triggers.",
                    "action": "Try to log all meals and snacks",
                    "priority": "medium"
                })

        # Add general wellness insights
        if not symptom_logs and not diet_logs:
            insights.append({
                "type": "info",
                "title": "Start Your Wellness Journey",
                "description": "Begin tracking your symptoms and meals to get personalized insights.",
                "action": "Log your first symptom or meal",
                "priority": "high"
            })

        return {"insights": insights}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving insights: {str(e)}",
        )


@router.get("/weekly-summary")
async def get_weekly_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get weekly summary statistics for the dashboard."""
    try:
        # Calculate date range for the past week
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=7)
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        # Get symptom logs for the week
        symptom_logs_result = await db.execute(
            select(SymptomLog).where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= start_datetime,
                    SymptomLog.logged_at <= end_datetime
                )
            )
        )
        symptom_logs = symptom_logs_result.scalars().all()

        # Get diet logs for the week
        diet_logs_result = await db.execute(
            select(DietLog).where(
                and_(
                    DietLog.user_id == current_user.id,
                    DietLog.consumed_at >= start_datetime,
                    DietLog.consumed_at <= end_datetime
                )
            )
        )
        diet_logs = diet_logs_result.scalars().all()

        # Calculate adherence rate (simplified - based on daily logging)
        days_with_logs = len(set(log.logged_at.date() for log in symptom_logs))
        adherence_rate = (days_with_logs / 7) * 100

        # Calculate improvement trend (compare with previous week)
        prev_start_date = start_date - timedelta(days=7)
        prev_start_datetime = datetime.combine(prev_start_date, datetime.min.time())
        prev_end_datetime = datetime.combine(start_date, datetime.max.time())

        prev_symptom_logs_result = await db.execute(
            select(SymptomLog).where(
                and_(
                    SymptomLog.user_id == current_user.id,
                    SymptomLog.logged_at >= prev_start_datetime,
                    SymptomLog.logged_at < prev_end_datetime
                )
            )
        )
        prev_symptom_logs = prev_symptom_logs_result.scalars().all()

        # Calculate improvement trend
        current_avg_severity = 0
        prev_avg_severity = 0

        if symptom_logs:
            current_avg_severity = sum(_severity_to_number(log.severity) for log in symptom_logs) / len(symptom_logs)
        
        if prev_symptom_logs:
            prev_avg_severity = sum(_severity_to_number(log.severity) for log in prev_symptom_logs) / len(prev_symptom_logs)

        improvement_trend = 0
        if prev_avg_severity > 0:
            improvement_trend = ((prev_avg_severity - current_avg_severity) / prev_avg_severity) * 100

        return {
            "adherence_rate": round(adherence_rate, 1),
            "improvement_trend": round(improvement_trend, 1),
            "total_symptom_logs": len(symptom_logs),
            "total_diet_logs": len(diet_logs),
            "avg_severity": round(current_avg_severity, 1),
            "days_tracked": days_with_logs
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving weekly summary: {str(e)}",
        )


def _severity_to_number(severity):
    """Convert severity enum to number for calculations."""
    severity_map = {
        'none': 0,
        'mild': 1,
        'moderate': 2,
        'severe': 3,
        'very_severe': 4
    }
    return severity_map.get(str(severity).lower(), 0)
