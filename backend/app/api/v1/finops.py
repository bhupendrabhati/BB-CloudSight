"""
AWS Infra Vision - FinOps Endpoints
FinOps scoring and optimization metrics
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from backend.app.services.finops_scorer import FinOpsScorer
from backend.app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()


class CalculateScoreRequest(BaseModel):
    account_id: str


class FinOpsMetricsRequest(BaseModel):
    account_id: str


@router.get("/score")
async def get_finops_score(
    account_id: str = Query(..., description="AWS account ID"),
    db: Session = Depends(get_db)
):
    """Get current FinOps score"""
    try:
        scorer = FinOpsScorer(account_id, db)
        score = scorer.calculate_score()
        return {
            "success": True,
            "data": score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate score: {str(e)}")


@router.get("/score/history")
async def get_score_history(
    account_id: str = Query(..., description="AWS account ID"),
    days: int = Query(30, ge=1, le=365, description="Days of history"),
    db: Session = Depends(get_db)
):
    """Get FinOps score history"""
    return {
        "success": True,
        "data": {
            "scores": [],
            "account_id": account_id,
            "period_days": days,
            "message": "Score history not yet implemented"
        }
    }


@router.post("/calculate")
async def calculate_finops_score(
    request: CalculateScoreRequest,
    db: Session = Depends(get_db)
):
    """Recalculate FinOps score"""
    try:
        scorer = FinOpsScorer(request.account_id, db)
        score = scorer.calculate_score()
        return {
            "success": True,
            "data": {
                "score": score,
                "status": "calculated",
                "calculated_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate score: {str(e)}")


@router.get("/metrics")
async def get_finops_metrics(
    account_id: str = Query(..., description="AWS account ID"),
    db: Session = Depends(get_db)
):
    """Get detailed FinOps metrics"""
    try:
        scorer = FinOpsScorer(account_id, db)
        score = scorer.calculate_score()
        return {
            "success": True,
            "data": {
                "account_id": account_id,
                "overall_score": score["overall_score"],
                "factors": score["factors"],
                "potential_monthly_savings": score.get("potential_monthly_savings", 0),
                "recommendations_count": score.get("recommendations_count", 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")
