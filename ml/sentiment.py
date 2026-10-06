from transformers import pipeline


MODEL_NAME = "Vansh180/FinBERT-India-v1"


sentiment_pipeline = pipeline(
    "text-classification",
    model=MODEL_NAME,
)


def analyze_sentiment(text: str) -> dict:

    result = sentiment_pipeline(
        text,
        truncation=True,
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
        "label": label,
        "confidence": confidence,
        "sentiment_score": sentiment_score,
    }