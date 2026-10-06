from ml.sentiment import analyze_sentiment


texts = [
    "Reliance Industries reports strong quarterly earnings and robust revenue growth.",
    "Indian stock markets crash amid severe global economic uncertainty.",
    "TCS announces a new board meeting next week.",
]


for text in texts:

    result = analyze_sentiment(text)

    print("\nHeadline:")
    print(text)

    print("Result:")
    print(result)