import numpy as np


def add_financial_metrics(df):
    """
    Add returns, moving averages, and volatility metrics.
    """

    result = df.copy()

    result["daily_return"] = result["price"].pct_change()

    result["7d_return"] = (
        result["price"].pct_change(periods=7)
    )

    result["30d_return"] = (
        result["price"].pct_change(periods=30)
    )

    result["30d_ma"] = (
        result["price"].rolling(window=30).mean()
    )

    result["90d_ma"] = (
        result["price"].rolling(window=90).mean()
    )

    result["30d_volatility"] = (
        result["daily_return"]
        .rolling(window=30)
        .std()
        * np.sqrt(365)
    )

    return result

def add_drawdown_metrics(df):
    """
    Add running peak and drawdown calculations.

    Drawdown measures the percentage decline from the
    highest price previously reached.
    """

    result = df.copy()

    result["running_peak"] = (
        result["price"].cummax()
    )

    result["drawdown"] = (
        result["price"]
        / result["running_peak"]
        - 1
    )

    return result

def calculate_max_drawdown(df):
    """
    Return the maximum drawdown as a decimal.

    Example:
    -0.35 represents a maximum drawdown of -35%.
    """

    if "drawdown" not in df.columns:
        df = add_drawdown_metrics(df)

    return df["drawdown"].min()

def get_trend_signal(df):
    """
    Classify the price trend using price and moving averages.
    """

    latest = df.iloc[-1]

    price = latest["price"]
    ma_30 = latest["30d_ma"]
    ma_90 = latest["90d_ma"]

    if price > ma_30 and ma_30 > ma_90:
        return "🟢 Bullish"

    if price < ma_30 and ma_30 < ma_90:
        return "🔴 Bearish"

    return "🟡 Mixed"


def get_momentum_signal(df):
    """
    Classify momentum using 7-day and 30-day returns.
    """

    latest = df.iloc[-1]

    return_7d = latest["7d_return"]
    return_30d = latest["30d_return"]

    if return_7d > 0 and return_30d > 0:
        return "🟢 Positive"

    if return_7d < 0 and return_30d < 0:
        return "🔴 Negative"

    return "🟡 Mixed"


def get_risk_signal(df):
    """
    Classify risk using annualized 30-day volatility.
    """

    volatility = df.iloc[-1]["30d_volatility"]

    if volatility < 0.40:
        return "🟢 Low"

    if volatility < 0.70:
        return "🟠 Medium"

    return "🔴 High"


def get_sentiment_indicator(classification):
    """
    Return an emoji corresponding to the sentiment category.
    """

    indicators = {
        "Extreme Fear": "🔴",
        "Fear": "🟠",
        "Neutral": "🟡",
        "Greed": "🟢",
        "Extreme Greed": "🟢",
    }

    return indicators.get(classification, "⚪")


def interpret_fear_greed(score):
    """
    Convert the Fear & Greed score into a short explanation.
    """

    if score <= 25:
        return (
            "Extreme fear suggests investors may be "
            "overly pessimistic."
        )

    if score <= 45:
        return "Market participants remain cautious."

    if score <= 55:
        return "Market sentiment is balanced."

    if score <= 75:
        return (
            "Investors are becoming increasingly optimistic."
        )

    return (
        "Extreme optimism may indicate excessive "
        "market speculation."
    )


def create_executive_summary(
    total_market_cap,
    btc_dominance,
    market_cap_change_24h,
    fear_greed_value,
    fear_greed_label,
    btc_trend,
    eth_trend,
):
    """
    Generate a concise market summary.
    """

    if market_cap_change_24h > 0:
        market_direction = "increased"
    elif market_cap_change_24h < 0:
        market_direction = "declined"
    else:
        market_direction = "remained unchanged"

    return [
        (
            "Total cryptocurrency market capitalization "
            f"stands at ${total_market_cap / 1e12:.2f}T."
        ),
        (
            f"Bitcoin accounts for {btc_dominance:.2f}% "
            "of total crypto market capitalization."
        ),
        (
            f"The overall market {market_direction} by "
            f"{abs(market_cap_change_24h):.2f}% "
            "over the last 24 hours."
        ),
        (
            f"The Fear & Greed Index is "
            f"{fear_greed_value}/100, indicating "
            f"{fear_greed_label.lower()}."
        ),
        (
            f"Current technical conditions classify "
            f"Bitcoin as {btc_trend[2:].lower()} and "
            f"Ethereum as {eth_trend[2:].lower()}."
        ),
    ]


def create_market_commentary(
    total_market_cap,
    market_cap_change_24h,
    btc_dominance,
    fear_greed_value,
    fear_greed_label,
    btc_df,
    eth_df,
):
    """
    Generate rule-based institutional-style market commentary.
    """

    btc_latest = btc_df.iloc[-1]
    eth_latest = eth_df.iloc[-1]

    btc_trend = get_trend_signal(btc_df)
    eth_trend = get_trend_signal(eth_df)

    btc_momentum = get_momentum_signal(btc_df)
    eth_momentum = get_momentum_signal(eth_df)

    btc_risk = get_risk_signal(btc_df)
    eth_risk = get_risk_signal(eth_df)

    if market_cap_change_24h > 0:
        market_direction = (
            f"rose by {market_cap_change_24h:.2f}%"
        )
    elif market_cap_change_24h < 0:
        market_direction = (
            f"declined by {abs(market_cap_change_24h):.2f}%"
        )
    else:
        market_direction = "was broadly unchanged"

    if btc_dominance >= 60:
        dominance_comment = (
            "Bitcoin dominance remains elevated, suggesting "
            "capital is concentrated in the market's largest asset."
        )
    elif btc_dominance >= 50:
        dominance_comment = (
            "Bitcoin continues to represent more than half "
            "of total crypto market capitalization."
        )
    else:
        dominance_comment = (
            "Bitcoin dominance is below 50%, indicating "
            "greater participation across alternative assets."
        )

    if fear_greed_value <= 25:
        sentiment_comment = (
            "Sentiment is in extreme fear territory, indicating "
            "significant risk aversion among market participants."
        )
    elif fear_greed_value <= 45:
        sentiment_comment = (
            "Sentiment remains cautious, with investors showing "
            "a preference for lower-risk positioning."
        )
    elif fear_greed_value <= 55:
        sentiment_comment = (
            "Sentiment is broadly neutral, suggesting no strong "
            "directional conviction."
        )
    elif fear_greed_value <= 75:
        sentiment_comment = (
            "Sentiment is optimistic, although positioning does "
            "not yet appear excessively speculative."
        )
    else:
        sentiment_comment = (
            "Sentiment is extremely optimistic, which may increase "
            "the risk of short-term overheating."
        )

    commentary = (
        f"The total cryptocurrency market is valued at approximately "
        f"${total_market_cap / 1e12:.2f}T and {market_direction} over "
        f"the past 24 hours. {dominance_comment} "
        f"The Fear & Greed Index stands at {fear_greed_value}/100 "
        f"and is classified as {fear_greed_label.lower()}. "
        f"{sentiment_comment} "
        f"Bitcoin currently shows a {btc_trend[2:].lower()} trend, "
        f"{btc_momentum[2:].lower()} momentum, and "
        f"{btc_risk[2:].lower()} volatility risk. "
        f"Ethereum shows a {eth_trend[2:].lower()} trend, "
        f"{eth_momentum[2:].lower()} momentum, and "
        f"{eth_risk[2:].lower()} volatility risk. "
        f"Bitcoin's latest 30-day return is "
        f"{btc_latest['30d_return'] * 100:.2f}%, compared with "
        f"{eth_latest['30d_return'] * 100:.2f}% for Ethereum."
    )

    return commentary
