from typing import List, Dict

import pandas as pd
import yfinance as yf


def fetch_news(symbol: str, count: int = 20) -> List[Dict]:
    """
    Fetch recent financial news for a ticker.

    Yahoo Search works more reliably with the company name,
    so we use a small mapping for supported Indian stocks.
    """

    company_queries = {
        "RELIANCE.NS": "Reliance Industries",
        "TCS.NS": "Tata Consultancy Services",
        "INFY.NS": "Infosys",
        "HDFCBANK.NS": "HDFC Bank",
        "ICICIBANK.NS": "ICICI Bank",
        "SBIN.NS": "State Bank of India",
        "ITC.NS": "ITC Limited",
        "BHARTIARTL.NS": "Bharti Airtel",
        "LT.NS": "Larsen Toubro",
        "WIPRO.NS": "Wipro",
    }

    query = company_queries.get(symbol.upper(), symbol)

    try:
        search = yf.Search(
            query,
            max_results=5,
            news_count=count,
        )

        news_items = search.news

    except Exception as exc:
        print(f"Yahoo Finance news search failed for {symbol}: {exc}")
        return []

    normalized_news = []

    for item in news_items:
        content = item.get("content", item)

        title = (
            content.get("title")
            or item.get("title")
        )

        if not title:
            continue

        provider = content.get("provider")

        if isinstance(provider, dict):
            publisher = provider.get("displayName")
        else:
            publisher = content.get("publisher")

        if not publisher:
            publisher = "Yahoo Finance"

        published_time = (
            content.get("pubDate")
            or content.get("published")
            or item.get("providerPublishTime")
        )

        published_at = parse_news_datetime(published_time)

        url = extract_news_url(content)

        normalized_news.append({
            "symbol": symbol,
            "headline": title,
            "source": publisher,
            "published_at": published_at,
            "url": url,
        })

    return normalized_news

def parse_news_datetime(value):

    if value is None:
        return None

    if isinstance(
        value,
        (int, float)
    ):
        return pd.to_datetime(
            value,
            unit="s",
            errors="coerce",
        )

    return pd.to_datetime(
        value,
        errors="coerce",
        utc=True,
    )


def extract_news_url(content: Dict):

    canonical = content.get(
        "canonicalUrl"
    )

    if isinstance(
        canonical,
        dict
    ):
        return canonical.get("url")

    if isinstance(
        canonical,
        str
    ):
        return canonical

    click_through = content.get(
        "clickThroughUrl"
    )

    if isinstance(
        click_through,
        dict
    ):
        return click_through.get("url")

    if isinstance(
        click_through,
        str
    ):
        return click_through

    return None


def news_to_dataframe(
    news: List[Dict]
) -> pd.DataFrame:

    if not news:

        return pd.DataFrame(
            columns=[
                "symbol",
                "headline",
                "source",
                "published_at",
                "url",
                "news_date",
            ]
        )

    df = pd.DataFrame(news)

    df["published_at"] = pd.to_datetime(
        df["published_at"],
        errors="coerce",
        utc=True,
    )

    df = df.dropna(
        subset=[
            "headline",
            "published_at",
        ]
    )

    df["news_date"] = (
        df["published_at"]
        .dt.tz_convert(None)
        .dt.normalize()
    )

    return df