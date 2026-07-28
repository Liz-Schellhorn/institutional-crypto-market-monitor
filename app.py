from datetime import datetime

import streamlit as st

from analytics import (
    add_financial_metrics,
    add_drawdown_metrics,
    calculate_max_drawdown,
    create_executive_summary,
    create_market_commentary,
    get_momentum_signal,
    get_risk_signal,
    get_sentiment_indicator,
    get_trend_signal,
    interpret_fear_greed,
)
from data import (
    create_history_dataframe,
    get_fear_and_greed,
    get_global_market_data,
    get_market_chart,
)
from visualizations import (
    create_normalized_performance_chart,
    create_price_chart,
    create_volatility_chart,
    create_drawdown_chart,
)


st.set_page_config(
    page_title="Crypto Market Intelligence Platform",
    page_icon="📊",
    layout="wide",
)

api_key = st.secrets["COINGECKO_API_KEY"]

@st.cache_data(ttl=900)
def load_crypto_data(api_key, days):
    """
    Load and process all data used by the application.

    Cached for 15 minutes to reduce unnecessary API calls.
    """

    btc_raw = get_market_chart(
        coin_id="bitcoin",
        api_key=api_key,
        days=days,
    )

    eth_raw = get_market_chart(
        coin_id="ethereum",
        api_key=api_key,
        days=days,
    )

    btc_df = create_history_dataframe(btc_raw)
    eth_df = create_history_dataframe(eth_raw)

    btc_df = add_financial_metrics(btc_df)
    eth_df = add_financial_metrics(eth_df)

    btc_df = add_drawdown_metrics(btc_df)
    eth_df = add_drawdown_metrics(eth_df)

    global_data = get_global_market_data(api_key)
    sentiment_data = get_fear_and_greed()

    return (
        btc_df,
        eth_df,
        global_data,
        sentiment_data,
    )


header_col, update_col = st.columns(
    [4, 1],
    vertical_alignment="center",
)

with header_col:
    st.title("Crypto Market Intelligence Platform")

    st.caption(
        "Live market data, sentiment analysis, technical signals, "
        "cross-asset analytics, and automated commentary."
    )

with update_col:
    last_updated = datetime.now().strftime(
        "%d %b %Y · %H:%M"
    )

    st.markdown(
        f"""
        <div style="
            text-align: right;
            color: #9CA3AF;
            font-size: 0.85rem;
        ">
            Last updated<br>
            <strong style="color: #FAFAFA;">
                {last_updated}
            </strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

st.sidebar.header("Dashboard Controls")

history_days = st.sidebar.selectbox(
    "Historical period",
    options=[90, 180, 365],
    index=2,
    format_func=lambda days: f"{days} days",
)

refresh_data = st.sidebar.button(
    "Refresh market data"
)

st.sidebar.divider()

st.sidebar.markdown(
    """
    **Data sources**

    - CoinGecko
    - Alternative.me Fear & Greed Index
    """
)

try:
    api_key = st.secrets["COINGECKO_API_KEY"]

    (
        btc_df,
        eth_df,
        global_data,
        sentiment_data,
    ) = load_crypto_data(
    api_key,
    history_days,
    )

except KeyError:
    st.error(
        "CoinGecko API key not found. Add "
        "COINGECKO_API_KEY to .streamlit/secrets.toml."
    )
    st.stop()

except Exception as error:
    st.error(
        "The market data could not be loaded. "
        f"Technical details: {error}"
    )
    st.stop()


total_market_cap = (
    global_data["total_market_cap"]["usd"]
)

total_volume = (
    global_data["total_volume"]["usd"]
)

btc_dominance = (
    global_data["market_cap_percentage"]["btc"]
)

eth_dominance = (
    global_data["market_cap_percentage"]["eth"]
)

market_cap_change_24h = (
    global_data["market_cap_change_percentage_24h_usd"]
)

fear_greed_value = sentiment_data["value"]
fear_greed_label = sentiment_data["classification"]

sentiment_icon = get_sentiment_indicator(
    fear_greed_label
)

sentiment_interpretation = interpret_fear_greed(
    fear_greed_value
)

btc_trend = get_trend_signal(btc_df)
eth_trend = get_trend_signal(eth_df)

btc_max_drawdown = calculate_max_drawdown(
    btc_df
)

eth_max_drawdown = calculate_max_drawdown(
    eth_df
)

btc_momentum = get_momentum_signal(btc_df)
eth_momentum = get_momentum_signal(eth_df)

btc_risk = get_risk_signal(btc_df)
eth_risk = get_risk_signal(eth_df)


st.markdown("## Market Overview")

st.caption(
    "Global cryptocurrency market conditions and investor sentiment."
)

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(
    5,
    gap="small",
)

with kpi_col1:
    with st.container(border=True):
        st.metric(
            label="Global Market Cap",
            value=f"${total_market_cap / 1e12:.2f}T",
            delta=f"{market_cap_change_24h:.2f}% · 24h",
            width="stretch",
        )

with kpi_col2:
    with st.container(border=True):
        st.metric(
            label="24h Trading Volume",
            value=f"${total_volume / 1e9:.2f}B",
            width="stretch",
        )

with kpi_col3:
    with st.container(border=True):
        st.metric(
            label="Bitcoin Dominance",
            value=f"{btc_dominance:.2f}%",
            width="stretch",
        )

with kpi_col4:
    with st.container(border=True):
        st.metric(
            label="Ethereum Dominance",
            value=f"{eth_dominance:.2f}%",
            width="stretch",
        )

with kpi_col5:
    with st.container(border=True):
        st.metric(
            label="Fear & Greed",
            value=f"{fear_greed_value} / 100",
            delta=f"{sentiment_icon} {fear_greed_label}",
            delta_color="off",
            width="stretch",
        )

st.info(
    f"**Sentiment assessment:** {sentiment_interpretation}",
    icon="💡",
)

st.divider()


st.subheader("Market Signals")

btc_col, eth_col = st.columns(2)

with btc_col:
    st.markdown("### Bitcoin")

    st.write(f"**Trend:** {btc_trend}")
    st.write(f"**Momentum:** {btc_momentum}")
    st.write(f"**Risk:** {btc_risk}")

    st.metric(
        label="Latest Price",
        value=f"${btc_df.iloc[-1]['price']:,.2f}",
        delta=(
            f"{btc_df.iloc[-1]['30d_return'] * 100:.2f}% "
            "over 30 days"
        ),
    )
    st.metric(
    label="Maximum Drawdown",
    value=f"{btc_max_drawdown * 100:.2f}%",
)

with eth_col:
    st.markdown("### Ethereum")

    st.write(f"**Trend:** {eth_trend}")
    st.write(f"**Momentum:** {eth_momentum}")
    st.write(f"**Risk:** {eth_risk}")

    st.metric(
        label="Latest Price",
        value=f"${eth_df.iloc[-1]['price']:,.2f}",
        delta=(
            f"{eth_df.iloc[-1]['30d_return'] * 100:.2f}% "
            "over 30 days"
        ),
    )
    st.metric(
    label="Maximum Drawdown",
    value=f"{eth_max_drawdown * 100:.2f}%",
)

st.divider()


st.subheader("Price and Moving Averages")

chart_tab1, chart_tab2 = st.tabs(
    ["Bitcoin", "Ethereum"]
)

with chart_tab1:
    btc_chart = create_price_chart(
        btc_df,
        "Bitcoin",
    )

    st.plotly_chart(
        btc_chart,
        width="stretch",
    )

with chart_tab2:
    eth_chart = create_price_chart(
        eth_df,
        "Ethereum",
    )

    st.plotly_chart(
        eth_chart,
        width="stretch",
    )


st.divider()


st.subheader("Cross-Asset Analysis")

performance_tab, volatility_tab, drawdown_tab = st.tabs(
    [
        "Normalized Performance",
        "Rolling Volatility",
        "Drawdown Analysis",
    ]
)

with performance_tab:
    performance_chart = (
        create_normalized_performance_chart(
            btc_df,
            eth_df,
        )
    )

    st.plotly_chart(
        performance_chart,
        width="stretch",
    )

with volatility_tab:
    volatility_chart = create_volatility_chart(
        btc_df,
        eth_df,
    )

    st.plotly_chart(
        volatility_chart,
        width="stretch",
    )

with drawdown_tab:
    drawdown_chart = create_drawdown_chart(
        btc_df,
        eth_df,
    )

    st.plotly_chart(
        drawdown_chart,
        width="stretch",
    )

st.divider()


executive_summary = create_executive_summary(
    total_market_cap=total_market_cap,
    btc_dominance=btc_dominance,
    market_cap_change_24h=market_cap_change_24h,
    fear_greed_value=fear_greed_value,
    fear_greed_label=fear_greed_label,
    btc_trend=btc_trend,
    eth_trend=eth_trend,
)

st.subheader("Executive Summary")

for statement in executive_summary:
    st.markdown(f"- {statement}")


st.divider()


market_commentary = create_market_commentary(
    total_market_cap=total_market_cap,
    market_cap_change_24h=market_cap_change_24h,
    btc_dominance=btc_dominance,
    fear_greed_value=fear_greed_value,
    fear_greed_label=fear_greed_label,
    btc_df=btc_df,
    eth_df=eth_df,
)

st.subheader("Automated Market Commentary")

st.write(market_commentary)

st.caption(
    "Commentary is generated through a transparent, "
    "rule-based analytical framework."
)
