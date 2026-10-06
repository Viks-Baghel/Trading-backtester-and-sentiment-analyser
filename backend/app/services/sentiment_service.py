from typing import List, Dict
import pandas as pd
from transformers import pipeline


# =========================================================
# MODEL CONFIGURATION
# =========================================================

MODEL_NAME = "Vansh180/FinBERT-India-v1"


# =========================================================
# LOAD FINBERT MODEL
#
# Loaded only once when this module is imported.
# =========================================================

sentiment_pipeline = pipeline(
    "text-classification",
    model=MODEL_NAME,
)


# =========================================================
# SINGLE HEADLINE SENTIMENT
# =========================================================

def analyze_sentiment(text: str) -> Dict:
    """
    Analyze a single financial-news headline using FinBERT.

    Returns:
        text
        label
        confidence
        sentiment_score
        model
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    # Do not explicitly set truncation=True.
    # This avoids the HuggingFace warning because this model
    # does not expose a predefined maximum length.

    result = sentiment_pipeline(text)[0]

    label = result["label"].lower()
    confidence = float(result["score"])

    # ---------------------------------------------------------
    # Convert FinBERT classification into numerical score
    #
    # Positive -> +confidence
    # Negative -> -confidence
    # Neutral  -> 0
    # ---------------------------------------------------------

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


# =========================================================
# MULTIPLE HEADLINES
# =========================================================

def analyze_headlines(
    headlines: List[str],
) -> List[Dict]:
    """
    Analyze multiple financial-news headlines.
    """

    results = []

    for headline in headlines:

        if not headline or not headline.strip():
            continue

        results.append(
            analyze_sentiment(headline)
        )

    return results


# =========================================================
# AGGREGATE SENTIMENT
# =========================================================

def aggregate_sentiment(
    results: List[Dict],
) -> float:
    """
    Calculate the average sentiment score.

    Score range:
        -1.0 -> strongly negative
         0.0 -> neutral
        +1.0 -> strongly positive
    """

    if not results:
        return 0.0

    total = sum(
        item["sentiment_score"]
        for item in results
    )

    return total / len(results)


# =========================================================
# NEWS DATAFRAME SENTIMENT
# =========================================================

def analyze_news_dataframe(
    news_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Run FinBERT on every headline in a news DataFrame.

    Expected column:
        headline

    Adds:
        sentiment_label
        sentiment_confidence
        sentiment_score
    """

    if news_df.empty:
        return news_df.copy()

    if "headline" not in news_df.columns:
        raise ValueError(
            "news_df must contain a 'headline' column"
        )

    df = news_df.copy()

    results = []

    for headline in df["headline"]:

        if not isinstance(headline, str):
            headline = str(headline)

        if not headline.strip():
            results.append({
                "label": "neutral",
                "confidence": 0.0,
                "sentiment_score": 0.0,
            })
            continue

        result = analyze_sentiment(headline)

        results.append(result)

    # ---------------------------------------------------------
    # Store FinBERT results
    # ---------------------------------------------------------

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


# =========================================================
# DAILY SENTIMENT AGGREGATION
# =========================================================

def aggregate_daily_sentiment(
    news_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate multiple news articles into one
    sentiment score per calendar day.

    Expected columns:
        news_date
        headline
        sentiment_score

    Returns:
        news_date
        sentiment_score
        news_count
    """

    if news_df.empty:
        return pd.DataFrame(
            columns=[
                "news_date",
                "sentiment_score",
                "news_count",
            ]
        )

    required_columns = {
        "news_date",
        "headline",
        "sentiment_score",
    }

    missing_columns = (
        required_columns
        - set(news_df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    df = news_df.copy()

    # Make sure news_date is a proper datetime
    df["news_date"] = pd.to_datetime(
        df["news_date"],
        errors="coerce",
    )

    # Remove rows with invalid dates
    df = df.dropna(
        subset=["news_date"]
    )

    if df.empty:
        return pd.DataFrame(
            columns=[
                "news_date",
                "sentiment_score",
                "news_count",
            ]
        )

    daily = (
        df
        .groupby("news_date")
        .agg(
            sentiment_score=(
                "sentiment_score",
                "mean",
            ),
            news_count=(
                "headline",
                "count",
            ),
        )
        .reset_index()
    )

    return daily