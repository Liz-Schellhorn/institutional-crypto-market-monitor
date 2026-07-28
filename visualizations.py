import plotly.graph_objects as go


def create_price_chart(df, asset_name):
    """
    Create an interactive price and moving-average chart.
    """

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["price"],
            mode="lines",
            name=f"{asset_name} Price",
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "Price: $%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["30d_ma"],
            mode="lines",
            name="30-Day Moving Average",
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "30-Day MA: $%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["90d_ma"],
            mode="lines",
            name="90-Day Moving Average",
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "90-Day MA: $%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=f"{asset_name} Price and Moving Averages",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        hovermode="x unified",
        template="plotly_white",
        height=550,
        legend_title="Indicator",
    )

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=[
                dict(
                    count=1,
                    label="1M",
                    step="month",
                    stepmode="backward",
                ),
                dict(
                    count=3,
                    label="3M",
                    step="month",
                    stepmode="backward",
                ),
                dict(
                    count=6,
                    label="6M",
                    step="month",
                    stepmode="backward",
                ),
                dict(
                    count=1,
                    label="1Y",
                    step="year",
                    stepmode="backward",
                ),
                dict(label="All", step="all"),
            ]
        ),
    )

    return fig


def create_normalized_comparison(btc_df, eth_df):
    """
    Create the normalized BTC and ETH comparison dataset.
    """

    btc_prices = btc_df[
        ["date", "price"]
    ].copy()

    btc_prices = btc_prices.rename(
        columns={"price": "btc_price"}
    )

    eth_prices = eth_df[
        ["date", "price"]
    ].copy()

    eth_prices = eth_prices.rename(
        columns={"price": "eth_price"}
    )

    comparison_df = btc_prices.merge(
        eth_prices,
        on="date",
        how="inner",
    )

    comparison_df["btc_normalized"] = (
        comparison_df["btc_price"]
        / comparison_df["btc_price"].iloc[0]
        * 100
    )

    comparison_df["eth_normalized"] = (
        comparison_df["eth_price"]
        / comparison_df["eth_price"].iloc[0]
        * 100
    )

    return comparison_df


def create_normalized_performance_chart(
    btc_df,
    eth_df,
):
    """
    Create an interactive normalized-performance chart.
    """

    comparison_df = create_normalized_comparison(
        btc_df,
        eth_df,
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=comparison_df["date"],
            y=comparison_df["btc_normalized"],
            mode="lines",
            name="Bitcoin",
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "BTC Index: %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=comparison_df["date"],
            y=comparison_df["eth_normalized"],
            mode="lines",
            name="Ethereum",
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "ETH Index: %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_hline(
        y=100,
        line_dash="dash",
        annotation_text="Starting value",
    )

    fig.update_layout(
        title="Bitcoin vs Ethereum: Normalized Performance",
        xaxis_title="Date",
        yaxis_title="Indexed Performance",
        hovermode="x unified",
        template="plotly_white",
        height=550,
        legend_title="Asset",
    )

    return fig


def create_volatility_chart(btc_df, eth_df):
    """
    Create a rolling 30-day volatility comparison chart.
    """

    btc_volatility = btc_df[
        ["date", "30d_volatility"]
    ].rename(
        columns={
            "30d_volatility": "btc_volatility"
        }
    )

    eth_volatility = eth_df[
        ["date", "30d_volatility"]
    ].rename(
        columns={
            "30d_volatility": "eth_volatility"
        }
    )

    volatility_df = btc_volatility.merge(
        eth_volatility,
        on="date",
        how="inner",
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=volatility_df["date"],
            y=volatility_df["btc_volatility"] * 100,
            mode="lines",
            name="Bitcoin",
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "BTC Volatility: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=volatility_df["date"],
            y=volatility_df["eth_volatility"] * 100,
            mode="lines",
            name="Ethereum",
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "ETH Volatility: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Bitcoin vs Ethereum: Rolling 30-Day Volatility",
        xaxis_title="Date",
        yaxis_title="Annualized Volatility (%)",
        hovermode="x unified",
        template="plotly_white",
        height=550,
        legend_title="Asset",
    )

    return fig

def create_drawdown_chart(btc_df, eth_df):
    """
    Create an interactive BTC and ETH drawdown comparison
    and highlight each asset's maximum drawdown point.
    """

    btc_min_index = btc_df["drawdown"].idxmin()
    eth_min_index = eth_df["drawdown"].idxmin()

    btc_min_date = btc_df.loc[btc_min_index, "date"]
    eth_min_date = eth_df.loc[eth_min_index, "date"]

    btc_min_drawdown = (
        btc_df.loc[btc_min_index, "drawdown"] * 100
    )

    eth_min_drawdown = (
        eth_df.loc[eth_min_index, "drawdown"] * 100
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=btc_df["date"],
            y=btc_df["drawdown"] * 100,
            mode="lines",
            name="Bitcoin",
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "BTC Drawdown: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=eth_df["date"],
            y=eth_df["drawdown"] * 100,
            mode="lines",
            name="Ethereum",
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "ETH Drawdown: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[btc_min_date],
            y=[btc_min_drawdown],
            mode="markers",
            name="BTC Maximum Drawdown",
            marker=dict(size=11),
            hovertemplate=(
                "<b>BTC Maximum Drawdown</b><br>"
                "Date: %{x|%Y-%m-%d}<br>"
                "Drawdown: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[eth_min_date],
            y=[eth_min_drawdown],
            mode="markers",
            name="ETH Maximum Drawdown",
            marker=dict(size=11),
            hovertemplate=(
                "<b>ETH Maximum Drawdown</b><br>"
                "Date: %{x|%Y-%m-%d}<br>"
                "Drawdown: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        annotation_text="Previous peak",
        annotation_position="top right",
    )

    fig.update_layout(
        title="Bitcoin vs Ethereum: Drawdown Analysis",
        xaxis_title="Date",
        yaxis_title="Drawdown from Previous Peak (%)",
        hovermode="x unified",
        template="plotly_white",
        height=550,
        legend_title="Asset",
    )

    return fig