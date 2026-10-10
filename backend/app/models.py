from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db import Base


def _utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

class UserType(Base):
    __tablename__ = "user_types"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
    )
class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
    )

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    user_type_id: Mapped[int] = mapped_column(
        ForeignKey("user_types.id"),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
        onupdate=_utcnow_naive,
    )
class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "role_id",
            name="uq_user_role",
        ),
    )

class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    symbol: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    asset_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    exchange: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    currency: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
    )


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    base_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
    )


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    model_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
    )


class Strategy(Base):
    __tablename__ = "strategies"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    strategy_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    parameters: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
    )


class Backtest(Base):
    __tablename__ = "backtests"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    strategy_id: Mapped[int] = mapped_column(
        ForeignKey("strategies.id"),
        nullable=False,
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"),
        nullable=False,
    )

    start_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    end_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    initial_capital: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="configured",
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )


class PriceData(Base):
    __tablename__ = "price_data"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"),
        nullable=False,
        index=True,
    )

    trading_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    open_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    high_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    low_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    close_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    adjusted_close: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    volume: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )


class SentimentScore(Base):
    __tablename__ = "sentiment_scores"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"),
        nullable=False,
    )

    headline: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    source: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    sentiment_label: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    sentiment_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    model_name: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
    )


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    backtest_id: Mapped[int] = mapped_column(
        ForeignKey("backtests.id"),
        nullable=False,
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"),
        nullable=False,
    )

    signal_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    signal_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    indicator_values: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    forecast_value: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    sentiment_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    explanation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
    )


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    backtest_id: Mapped[int] = mapped_column(
        ForeignKey("backtests.id"),
        nullable=False,
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"),
        nullable=False,
    )

    trade_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    trade_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    profit_loss: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
    )


class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    backtest_id: Mapped[int] = mapped_column(
        ForeignKey("backtests.id"),
        nullable=False,
        unique=True,
    )

    total_return: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    cumulative_return: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    sharpe_ratio: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    max_drawdown: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    win_rate: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    total_trades: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
    )


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    entity_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    entity_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_utcnow_naive,
    )