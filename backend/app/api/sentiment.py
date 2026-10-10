
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.sentiment_service import (
    analyze_headlines,
    aggregate_sentiment,
)

router = APIRouter(prefix="/sentiment", tags=["Sentiment Analysis"])


class SentimentRequest(BaseModel):
    headlines: List[str] = Field(..., min_length=1, max_length=50)


@router.post("/analyze")
def analyze_news(request: SentimentRequest):
    try:
        results = analyze_headlines(request.headlines)

        if not results:
            raise HTTPException(
                status_code=400,
                detail="Provide at least one non-empty headline.",
            )

        average_score = aggregate_sentiment(results)

        positive = sum(
            1 for item in results if item["label"] == "positive"
        )
        negative = sum(
            1 for item in results if item["label"] == "negative"
        )
        neutral = sum(
            1 for item in results if item["label"] == "neutral"
        )

        return {
            "model": results[0]["model"],
            "total_headlines": len(results),
            "average_sentiment_score": average_score,
            "distribution": {
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
            },
            "results": results,
        }

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Sentiment analysis failed: {str(exc)}",
        ) from exc
