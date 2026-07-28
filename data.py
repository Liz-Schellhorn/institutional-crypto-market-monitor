import pandas as pd
import requests


COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
FEAR_GREED_URL = "https://api.alternative.me/fng/"


def get_request_headers(api_key):
    """
    Create the request headers required by the CoinGecko API.
    """

    return {
        "accept": "application/json",
        "x-cg-demo-api-key": api_key,
    }


def get_market_chart(
    coin_id,
    api_key,
    vs_currency="usd",
    days=365,
):
    """
    Download historical price, market-cap, and volume data
    for one cryptocurrency.
    """

    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"

    params = {
        "vs_currency": vs_currency,
        "days": days,
        "interval": "daily",
    }

    response = requests.get(
        url,
        headers=get_request_headers(api_key),
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def create_history_dataframe(raw_data):
    """
    Convert CoinGecko historical API data into a clean DataFrame.
    """

    price_df = pd.DataFrame(
        raw_data["prices"],
        columns=["timestamp", "price"],
    )

    market_cap_df = pd.DataFrame(
        raw_data["market_caps"],
        columns=["timestamp", "market_cap"],
    )

    volume_df = pd.DataFrame(
        raw_data["total_volumes"],
        columns=["timestamp", "volume"],
    )

    history_df = (
        price_df
        .merge(market_cap_df, on="timestamp", how="inner")
        .merge(volume_df, on="timestamp", how="inner")
    )

    history_df["date"] = pd.to_datetime(
        history_df["timestamp"],
        unit="ms",
    )

    history_df = history_df[
        [
            "date",
            "price",
            "market_cap",
            "volume",
        ]
    ]

    history_df = (
        history_df
        .sort_values("date")
        .drop_duplicates(subset="date")
        .reset_index(drop=True)
    )

    return history_df


def get_global_market_data(api_key):
    """
    Download global cryptocurrency market statistics.
    """

    url = f"{COINGECKO_BASE_URL}/global"

    response = requests.get(
        url,
        headers=get_request_headers(api_key),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["data"]


def get_fear_and_greed():
    """
    Download the latest Crypto Fear & Greed Index.
    """

    response = requests.get(
        FEAR_GREED_URL,
        params={"limit": 1},
        timeout=30,
    )

    response.raise_for_status()

    latest_data = response.json()["data"][0]

    return {
        "value": int(latest_data["value"]),
        "classification": latest_data["value_classification"],
    }