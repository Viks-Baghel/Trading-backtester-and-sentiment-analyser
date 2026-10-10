from fastapi import FastAPI

from backend.app.api.auth import router as auth_router
from backend.app.db import Base, engine
from backend.app.api.assets import router as assets_router
from backend.app.api.backtests import router as backtests_router
from backend.app.api.workspace import router as workspace_router
from backend.app.api.sentiment import router as sentiment_router
from backend.app.api.forecasting import router as forecasting_router

# Import all models so SQLAlchemy registers the tables.
from backend.app import models


app = FastAPI(
    title="Algorithmic Trading Backtester & Sentiment Analyzer",
    description=(
        "AI-augmented platform for technical, sentiment, "
        "and hybrid trading strategy backtesting."
    ),
    version="1.0.0",
)


Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(assets_router)
app.include_router(backtests_router)
app.include_router(workspace_router)
app.include_router(sentiment_router)
app.include_router(forecasting_router)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "message": "Algorithmic Trading API is running",
    }