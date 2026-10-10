
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.core.deps import get_current_user

router = APIRouter(
    prefix="/api/v1/workspace",
    tags=["Workspace"],
)

ALLOWED_PAGES = {
    "Overview",
    "Strategy Builder",
    "Backtest Results",
    "Trade History",
    "Sentiment Analysis",
    "Forecasting",
    "Profile & Settings",
}


class WorkspaceStateUpdate(BaseModel):
    current_page: str = Field(min_length=1, max_length=100)


@router.get("/state")
def get_workspace_state(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    row = db.execute(
        text("""
            SELECT current_page, updated_at
            FROM user_workspace_state
            WHERE user_id = :user_id
        """),
        {"user_id": current_user.id},
    ).mappings().first()

    if not row:
        return {
            "current_page": "Overview",
            "updated_at": None,
        }

    return dict(row)


@router.put("/state")
def save_workspace_state(
    payload: WorkspaceStateUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if payload.current_page not in ALLOWED_PAGES:
        raise HTTPException(
            status_code=422,
            detail="Invalid workspace page",
        )

    db.execute(
        text("""
            INSERT INTO user_workspace_state
                (user_id, current_page, updated_at)
            VALUES
                (:user_id, :current_page, :updated_at)
            ON CONFLICT (user_id)
            DO UPDATE SET
                current_page = EXCLUDED.current_page,
                updated_at = EXCLUDED.updated_at
        """),
        {
            "user_id": current_user.id,
            "current_page": payload.current_page,
            "updated_at": datetime.utcnow(),
        },
    )
    db.commit()

    return {
        "message": "Workspace state saved",
        "current_page": payload.current_page,
    }


@router.delete("/state")
def reset_workspace_state(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db.execute(
        text("""
            DELETE FROM user_workspace_state
            WHERE user_id = :user_id
        """),
        {"user_id": current_user.id},
    )
    db.commit()

    return {"message": "Workspace state reset"}
