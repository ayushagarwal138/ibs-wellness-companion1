"""
Goals API endpoints for user goal management and progress tracking.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.goals import UserGoal, GoalProgress, GoalTypeEnum, GoalStatusEnum
from app.schemas.goal import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    GoalProgressCreate,
    GoalProgressResponse,
    GoalSummaryResponse,
)

router = APIRouter(tags=["Goals"])


# User Goals endpoints
@router.get("/", response_model=List[GoalResponse])
async def get_user_goals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[GoalStatusEnum] = Query(None, description="Filter by goal status"),
    goal_type: Optional[GoalTypeEnum] = Query(None, description="Filter by goal type"),
):
    """Get user's goals."""
    query = select(UserGoal).where(UserGoal.user_id == current_user.id)

    if status:
        query = query.where(UserGoal.status == status)

    if goal_type:
        query = query.where(UserGoal.goal_type == goal_type)

    result = await db.execute(query.order_by(desc(UserGoal.created_at)))
    goals = result.scalars().all()

    return [GoalResponse.model_validate(goal) for goal in goals]


@router.post("/", response_model=GoalResponse)
async def create_goal(
    goal_data: GoalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new goal for the user."""
    goal = UserGoal(user_id=current_user.id, **goal_data.model_dump())

    db.add(goal)
    await db.commit()
    await db.refresh(goal)

    return GoalResponse.model_validate(goal)


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific goal by ID."""
    result = await db.execute(
        select(UserGoal).where(
            and_(UserGoal.id == goal_id, UserGoal.user_id == current_user.id)
        )
    )
    goal = result.scalar_one_or_none()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found"
        )

    return GoalResponse.model_validate(goal)


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    goal_update: GoalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a goal."""
    result = await db.execute(
        select(UserGoal).where(
            and_(UserGoal.id == goal_id, UserGoal.user_id == current_user.id)
        )
    )
    goal = result.scalar_one_or_none()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found"
        )

    update_data = goal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)

    goal.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(goal)

    return GoalResponse.model_validate(goal)


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a goal."""
    result = await db.execute(
        select(UserGoal).where(
            and_(UserGoal.id == goal_id, UserGoal.user_id == current_user.id)
        )
    )
    goal = result.scalar_one_or_none()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found"
        )

    await db.delete(goal)
    await db.commit()

    return {"message": "Goal deleted successfully"}


# Goal Progress endpoints
@router.get("/{goal_id}/progress", response_model=List[GoalProgressResponse])
async def get_goal_progress(
    goal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = Query(30, description="Number of days to retrieve progress for"),
):
    """Get progress entries for a specific goal."""
    # First verify the goal belongs to the user
    goal_result = await db.execute(
        select(UserGoal).where(
            and_(UserGoal.id == goal_id, UserGoal.user_id == current_user.id)
        )
    )
    goal = goal_result.scalar_one_or_none()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found"
        )

    start_date = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(GoalProgress)
        .where(
            and_(
                GoalProgress.goal_id == goal_id, GoalProgress.recorded_at >= start_date
            )
        )
        .order_by(desc(GoalProgress.recorded_at))
    )
    progress_entries = result.scalars().all()

    return [GoalProgressResponse.model_validate(entry) for entry in progress_entries]


@router.post("/{goal_id}/progress", response_model=GoalProgressResponse)
async def record_goal_progress(
    goal_id: str,
    progress_data: GoalProgressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record progress for a specific goal."""
    # First verify the goal belongs to the user
    goal_result = await db.execute(
        select(UserGoal).where(
            and_(UserGoal.id == goal_id, UserGoal.user_id == current_user.id)
        )
    )
    goal = goal_result.scalar_one_or_none()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found"
        )

    progress = GoalProgress(goal_id=goal_id, **progress_data.model_dump())

    db.add(progress)

    # Update goal's current progress
    goal.current_progress = progress_data.progress_value
    goal.updated_at = datetime.utcnow()

    # Check if goal is completed
    if goal.target_value and progress_data.progress_value >= goal.target_value:
        goal.status = GoalStatusEnum.COMPLETED
        goal.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(progress)

    return GoalProgressResponse.model_validate(progress)


@router.get("/summary", response_model=GoalSummaryResponse)
async def get_goals_summary(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get summary of user's goals."""
    # Count goals by status
    active_result = await db.execute(
        select(func.count(UserGoal.id)).where(
            and_(
                UserGoal.user_id == current_user.id,
                UserGoal.status == GoalStatusEnum.ACTIVE,
            )
        )
    )
    active_goals = active_result.scalar() or 0

    completed_result = await db.execute(
        select(func.count(UserGoal.id)).where(
            and_(
                UserGoal.user_id == current_user.id,
                UserGoal.status == GoalStatusEnum.COMPLETED,
            )
        )
    )
    completed_goals = completed_result.scalar() or 0

    paused_result = await db.execute(
        select(func.count(UserGoal.id)).where(
            and_(
                UserGoal.user_id == current_user.id,
                UserGoal.status == GoalStatusEnum.PAUSED,
            )
        )
    )
    paused_goals = paused_result.scalar() or 0

    # Calculate average progress for active goals
    avg_progress_result = await db.execute(
        select(func.avg(UserGoal.current_progress)).where(
            and_(
                UserGoal.user_id == current_user.id,
                UserGoal.status == GoalStatusEnum.ACTIVE,
            )
        )
    )
    avg_progress = avg_progress_result.scalar() or 0

    return GoalSummaryResponse(
        total_goals=active_goals + completed_goals + paused_goals,
        active_goals=active_goals,
        completed_goals=completed_goals,
        paused_goals=paused_goals,
        average_progress=float(avg_progress),
    )
