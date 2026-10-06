from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.deps import get_current_user
from backend.app.db import get_db
from backend.app.models import Asset, User
from backend.app.schemas import AssetCreate, AssetResponse


router = APIRouter(
    prefix="/api/v1/assets",
    tags=["Assets"],
)


@router.post(
    "/",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_asset(
    asset_data: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_asset = (
        db.query(Asset)
        .filter(Asset.symbol == asset_data.symbol.upper())
        .first()
    )

    if existing_asset:
        raise HTTPException(
            status_code=400,
            detail="Asset already exists",
        )

    asset = Asset(
        symbol=asset_data.symbol.upper(),
        name=asset_data.name,
        asset_type=asset_data.asset_type,
        exchange=asset_data.exchange,
        currency=asset_data.currency,
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)

    return asset


@router.get(
    "/",
    response_model=List[AssetResponse],
)
def get_assets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Asset)
        .filter(Asset.is_active == True)
        .order_by(Asset.symbol)
        .all()
    )


@router.get(
    "/{symbol}",
    response_model=AssetResponse,
)
def get_asset(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    asset = (
        db.query(Asset)
        .filter(Asset.symbol == symbol.upper())
        .first()
    )

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found",
        )

    return asset