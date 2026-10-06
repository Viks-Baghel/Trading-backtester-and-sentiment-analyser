from typing import List, Dict, Optional
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf


# =========================================================
# COMPANY SEARCH MAPPING
# =========================================================

COMPANY_QUERIES = {
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


# =========================================================
# DATETIME PARSER
# =========================================================

def parse_news_datetime(value) -> Optional[datetime]:
    """
    Convert Yahoo Finance news timestamps into datetime.
    """

    if value is None:
        return None

    try:

        # Unix timestamp
        if isinstance(value, (int, float)):

            return datetime.fromtimestamp(
                value,
                tz=timezone.utc,
            )

        # Existing datetime
        if isinstance(value, datetime):

            if value.tzinfo is None:
                return value.replace(
                    tzinfo=timezone.utc
                )

            return value

        # String timestamp
        parsed = pd.to_datetime(
            value,
            errors="coerce",
            utc=True,
        )

        if pd.isna(parsed):
            return None

        return parsed.to_pydatetime()

    except Exception:
        return None


# =========================================================
# URL EXTRACTION
# =========================================================

def extract_news_url(content: Dict) -> str:
    """
    Extract article URL from Yahoo Finance news response.
    """

    if not isinstance(content, dict):
        return ""

    # New Yahoo structure
    canonical_url = content.get("canonicalUrl")

    if isinstance(canonical_url, dict):

        url = canonical_url.get("url")

        if url:
            return str(url)

    # Direct URL
    if content.get("url"):
        return str(content["url"])

    # Click-through URL
    click_url = content.get("clickThroughUrl")

    if isinstance(click_url, dict):

        url = click_url.get("url")

        if url:
            return str(url)

    return ""


# =========================================================
# FETCH NEWS
# =========================================================

def fetch_news(
    symbol: str,
    count: int = 20,
) -> List[Dict]:
    """
    Fetch financial news for a stock symbol using Yahoo Finance.

    Returns normalized news records.
    """

    query = COMPANY_QUERIES.get(
        symbol.upper(),
        symbol.replace(".NS", ""),
    )

    try:

        search = yf.Search(
            query,
            max_results=5,
            news_count=count,
        )

        raw_news = getattr(
            search,
            "news",
            None,
        )

        if not raw_news:
            return []

        normalized_news = []

        for item in raw_news:

            if not isinstance(item, dict):
                continue

            content = item.get(
                "content",
                item,
            )

            if not isinstance(content, dict):
                continue

            # -------------------------------------------------
            # Headline
            # -------------------------------------------------

            headline = (
                content.get("title")
                or item.get("title")
                or ""
            )

            if not headline:
                continue

            # -------------------------------------------------
            # Source / publisher
            # -------------------------------------------------

            provider = (
                content.get("provider")
                or item.get("provider")
                or ""
            )

            if isinstance(provider, dict):
                source = (
                    provider.get("displayName")
                    or provider.get("name")
                    or ""
                )
            else:
                source = str(provider)

            # -------------------------------------------------
            # Published timestamp
            # -------------------------------------------------

            published_value = (
                content.get("pubDate")
                or content.get("published")
                or item.get("providerPublishTime")
                or item.get("pubDate")
            )

            published_at = parse_news_datetime(
                published_value
            )

            if published_at is None:
                continue

            # -------------------------------------------------
            # URL
            # -------------------------------------------------

            url = extract_news_url(content)

            if not url:
                url = extract_news_url(item)

            normalized_news.append(
                {
                    "symbol": symbol.upper(),
                    "headline": str(headline).strip(),
                    "source": source,
                    "published_at": published_at,
                    "url": url,
                }
            )

        # -----------------------------------------------------
        # Remove duplicate headlines
        # -----------------------------------------------------

        unique_news = []

        seen = set()

        for article in normalized_news:

            key = (
                article["headline"].strip().lower(),
                article["published_at"],
            )

            if key in seen:
                continue

            seen.add(key)
            unique_news.append(article)

        return unique_news[:count]

    except Exception as exc:

        print(
            f"News fetch failed for {symbol}: {exc}"
        )

        return []


# =========================================================
# NEWS -> DATAFRAME
# =========================================================

def news_to_dataframe(
    news: List[Dict],
) -> pd.DataFrame:
    """
    Convert normalized news records into a DataFrame.
    """

    columns = [
        "symbol",
        "headline",
        "source",
        "published_at",
        "url",
        "news_date",
    ]

    if not news:
        return pd.DataFrame(
            columns=columns
        )

    df = pd.DataFrame(news)

    # Make sure expected columns exist
    for column in [
        "symbol",
        "headline",
        "source",
        "published_at",
        "url",
    ]:

        if column not in df.columns:
            df[column] = ""

    # ---------------------------------------------------------
    # Normalize published_at
    # ---------------------------------------------------------

    df["published_at"] = pd.to_datetime(
        df["published_at"],
        errors="coerce",
        utc=True,
    )

    # Remove articles without valid date
    df = df.dropna(
        subset=[
            "published_at",
        ]
    ).copy()

    if df.empty:

        return pd.DataFrame(
            columns=columns
        )

    # ---------------------------------------------------------
    # Create calendar news date
    # ---------------------------------------------------------

    df["news_date"] = (
        df["published_at"]
        .dt.tz_convert(None)
        .dt.normalize()
    )

    # ---------------------------------------------------------
    # Clean headline
    # ---------------------------------------------------------

    df["headline"] = (
        df["headline"]
        .astype(str)
        .str.strip()
    )

    df = df[
        df["headline"] != ""
    ].copy()

    # ---------------------------------------------------------
    # Sort chronologically
    # ---------------------------------------------------------

    df = df.sort_values(
        "published_at"
    ).reset_index(
        drop=True
    )

    return df[
        columns
    ]