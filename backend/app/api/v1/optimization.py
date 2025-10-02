"""
API endpoints for data storage optimization and monitoring.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.data_optimization import (
    DataOptimizationService,
    OptimizationLevel,
    OptimizationMetrics,
    StorageStats,
)

router = APIRouter()


class OptimizationRequest(BaseModel):
    """Request model for optimization operations."""

    level: OptimizationLevel = OptimizationLevel.STANDARD
    operations: Optional[List[str]] = None  # Specific operations to run


class OptimizationResponse(BaseModel):
    """Response model for optimization operations."""

    success: bool
    message: str
    metrics: List[Dict[str, Any]]
    total_storage_saved_mb: float
    total_execution_time_seconds: float


class StorageAnalysisResponse(BaseModel):
    """Response model for storage analysis."""

    tables: Dict[str, Dict[str, Any]]
    total_size_mb: float
    recommendations: List[str]


@router.get("/storage/analysis", response_model=StorageAnalysisResponse)
async def get_storage_analysis(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get detailed storage usage analysis."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        optimization_service = DataOptimizationService(db)
        storage_stats = await optimization_service.analyze_storage_usage()

        # Convert StorageStats to dict format
        tables_data = {}
        total_size = 0.0

        for table_name, stats in storage_stats.items():
            tables_data[table_name] = {
                "row_count": stats.row_count,
                "table_size_mb": round(stats.table_size_mb, 2),
                "index_size_mb": round(stats.index_size_mb, 2),
                "total_size_mb": round(stats.total_size_mb, 2),
                "avg_row_size_bytes": round(stats.avg_row_size_bytes, 2),
                "last_analyzed": stats.last_analyzed.isoformat()
                if stats.last_analyzed
                else None,
            }
            total_size += stats.total_size_mb

        # Generate recommendations
        recommendations = []
        for table_name, stats in storage_stats.items():
            if stats.total_size_mb > 100:  # Tables larger than 100MB
                recommendations.append(
                    f"Consider archiving old data in {table_name} "
                    f"(current size: {stats.total_size_mb:.1f}MB)"
                )

            if (
                stats.row_count > 10000 and stats.avg_row_size_bytes > 1000
            ):  # Large rows
                recommendations.append(
                    f"Consider compressing large fields in {table_name}"
                )

        if not recommendations:
            recommendations.append("Database storage is well optimized")

        return StorageAnalysisResponse(
            tables=tables_data,
            total_size_mb=round(total_size, 2),
            recommendations=recommendations,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze storage: {str(e)}"
        )


@router.post("/optimize", response_model=OptimizationResponse)
async def run_optimization(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run data optimization operations."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        optimization_service = DataOptimizationService(db)

        # Run optimization in background for long operations
        if request.level == OptimizationLevel.AGGRESSIVE:
            background_tasks.add_task(
                _run_background_optimization, optimization_service, request.level
            )
            return OptimizationResponse(
                success=True,
                message="Aggressive optimization started in background",
                metrics=[],
                total_storage_saved_mb=0.0,
                total_execution_time_seconds=0.0,
            )

        # Run optimization synchronously for lighter operations
        if request.operations:
            metrics = []
            for operation in request.operations:
                if operation == "cleanup":
                    result = await optimization_service.cleanup_old_data()
                    metrics.append(result)
                elif operation == "indexes":
                    result = await optimization_service.optimize_indexes()
                    metrics.append(result)
                elif operation == "diet_logs":
                    result = await optimization_service.optimize_diet_logs(
                        request.level
                    )
                    metrics.append(result)
                elif operation == "summary_tables":
                    result = await optimization_service.create_summary_tables()
                    metrics.append(result)
        else:
            # Run full optimization
            metrics = await optimization_service.run_full_optimization(request.level)

        # Convert metrics to dict format
        metrics_data = []
        total_storage_saved = 0.0
        total_time = 0.0

        for metric in metrics:
            metric_dict = {
                "operation_type": metric.operation_type,
                "records_processed": metric.records_processed,
                "storage_saved_mb": round(metric.storage_saved_mb, 2),
                "execution_time_seconds": round(metric.execution_time_seconds, 2),
                "compression_ratio": metric.compression_ratio,
                "index_efficiency_gain": metric.index_efficiency_gain,
            }
            metrics_data.append(metric_dict)
            total_storage_saved += metric.storage_saved_mb
            total_time += metric.execution_time_seconds

        return OptimizationResponse(
            success=True,
            message=(
                f"Optimization completed successfully with {len(metrics)} operations"
            ),
            metrics=metrics_data,
            total_storage_saved_mb=round(total_storage_saved, 2),
            total_execution_time_seconds=round(total_time, 2),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.get("/history")
async def get_optimization_history(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get optimization operation history."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        optimization_service = DataOptimizationService(db)
        summary = optimization_service.get_optimization_summary()

        return {"success": True, "data": summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.post("/vacuum")
async def run_vacuum_analyze(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Run VACUUM ANALYZE on the database."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        from sqlalchemy import text

        start_time = datetime.utcnow()
        await db.execute(text("VACUUM ANALYZE"))
        execution_time = (datetime.utcnow() - start_time).total_seconds()

        return {
            "success": True,
            "message": "VACUUM ANALYZE completed successfully",
            "execution_time_seconds": round(execution_time, 2),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VACUUM ANALYZE failed: {str(e)}")


async def _run_background_optimization(
    optimization_service: DataOptimizationService, level: OptimizationLevel
):
    """Run optimization in background task."""
    try:
        await optimization_service.run_full_optimization(level)
    except Exception as e:
        # Log error but don't raise since this is a background task
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Background optimization failed: {e}")
