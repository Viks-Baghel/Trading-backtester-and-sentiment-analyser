from typing import List, Dict
import pandas as pd
from transformers import pipeline


MODEL_NAME = "Vansh180/FinBERT-India-v1"


# Load the model only once
sentiment_pipeline = pipeline(
    "text-classification",
    model=MODEL_NAME,
)


def analyze_sentiment(text: str) -> Dict:
    """
    Analyze a single financial-news headline.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    result = sentiment_pipeline(
        text,
        truncation=True
    )[0]

    label = result["label"].lower()
    confidence = float(result["score"])

    if label == "positive":
        sentiment_score = confidence

    elif label == "negative":
        sentiment_score = -confidence

    else:
        sentiment_score = 0.0

    return {
        "text": text,
        "label": label,
        "confidence": confidence,
        "sentiment_score": sentiment_score,
        "model": MODEL_NAME,
    }


def analyze_headlines(headlines: List[str]) -> List[Dict]:
    """
    Analyze multiple financial-news headlines.
    """

    results = []

    for headline in headlines:
        results.append(
            analyze_sentiment(headline)
        )

    return results


def aggregate_sentiment(results: List[Dict]) -> float:
    """
    Calculate the average sentiment score.
    """

    if not results:
        return 0.0

    total = sum(
        item["sentiment_score"]
        for item in results
    )

    return total / len(results)

def analyze_news_dataframe(news_df):
    """
    Run FinBERT on every news headline.
    """

    if news_df.empty:
        return news_df.copy()

    df = news_df.copy()

    results = []

    for headline in df["headline"]:
        result = analyze_sentiment(headline)

        results.append(result)

    df["sentiment_label"] = [
        result["label"]
        for result in results
    ]

    df["sentiment_confidence"] = [
        result["confidence"]
        for result in results
    ]

    df["sentiment_score"] = [
        result["sentiment_score"]
        for result in results
    ]

    return df

def aggregate_daily_sentiment(news_df):
    """
    Aggregate multiple news articles into one
    sentiment score per calendar day.
    """

    if news_df.empty:
        return pd.DataFrame(
            columns=[
                "news_date",
                "sentiment_score",
                "news_count",
            ]
        )

    daily = (
        news_df
        .groupby("news_date")
        .agg(
            sentiment_score=("sentiment_score", "mean"),
            news_count=("headline", "count"),
        )
        .reset_index()
    )

    return daily