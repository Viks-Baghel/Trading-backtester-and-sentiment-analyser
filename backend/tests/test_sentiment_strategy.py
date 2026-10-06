import pandas as pd

from backend.app.services.sentiment_service import (
    analyze_headlines,
    aggregate_sentiment,
)
from backend.app.services.signals import (
    generate_sentiment_signals,
)


headlines = [
    "Reliance Industries reports strong quarterly earnings and robust revenue growth.",
    "Indian stock markets crash amid severe global economic uncertainty.",
    "TCS announces a new board meeting next week.",
]


print("\nFINBERT SENTIMENT ANALYSIS")
print("==========================")

results = analyze_headlines(headlines)

for result in results:
    print("\nHeadline:")
    print(result["text"])

    print("Label:", result["label"])
    print("Confidence:", round(result["confidence"], 4))
    print("Sentiment Score:", round(result["sentiment_score"], 4))


average_sentiment = aggregate_sentiment(results)

print("\nAverage Sentiment:")
print(round(average_sentiment, 4))


# Create a small example dataset
data = pd.DataFrame({
    "Close": [2500, 2520, 2480],
    "Sentiment_Score": [
        results[0]["sentiment_score"],
        results[1]["sentiment_score"],
        results[2]["sentiment_score"],
    ],
})


data = generate_sentiment_signals(data)

print("\nSENTIMENT SIGNALS")
print("=================")

print(
    data[
        [
            "Close",
            "Sentiment_Score",
            "Signal",
        ]
    ]
)