"""For building Dash app"""
import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input
from dash.dependencies import Output
from numpy import NaN
from plotly.subplots import make_subplots
from rhdash.alg import ema_n_days
from rhdash.config import fetch_config
from rhdash.rh import get_name
from rhdash.rh import get_year_data
from rhdash.rh import login_using


def setup_dash(config):
    """Set up dashboard server."""

    dash_config = config["dash"]
    external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    if "creds" in dash_config:
        creds = dash_config["creds"]
        if "user" in creds and "password" in creds:
            if creds["user"] != "" and creds["password"] != "":
                dash_auth.BasicAuth(app, {creds["user"]: creds["password"]})

    app.layout = html.Div([
        html.Div(children="Symbol:"),
        dcc.Input(id="symbol", value="", type="text"),
        html.H1(id="heading", children="", style={'textAlign': 'center'}),
        dcc.Graph(id="value-graph")
    ])

    return app


def init_using(config):
    """Do some initialization"""
    robinhood_config = config["robinhood"]
    login_using(robinhood_config)
    return setup_dash(config)


def create_app(arguments=None):
    configuration = fetch_config(arguments)

    if "robinhood" not in configuration:
        configuration["robinhood"] = {}

    app = init_using(configuration)

    rows = 2

    @app.callback(
        [Output("heading", "children"),
         Output("value-graph", "figure")], [Input("symbol", "value")])
    def update_figure(symbol):
        fig = make_subplots(rows=rows,
                            cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.02,
                            row_titles=["EMA % 2nd Derivative", "Price"])

        try:
            symbol = str(symbol).strip().upper()
            name = get_name(symbol) if symbol != "" else ""
            heading = f"{name} ({symbol})" if len(name) > 0 else ""

            year_data = get_year_data(symbol)
            df = pd.DataFrame(year_data)
            float_cols = [
                "open_price", "close_price", "high_price", "low_price"
            ]
            for col in float_cols:
                df[col] = df[col].astype(float)

            df["percent_diff"] = 100.0 * df["close_price"].pct_change()

            ema_days = configuration["robinhood"][
                "ema_days"] if "ema_days" in configuration["robinhood"] else [
                    10, 50, 100
                ]

            if len(ema_days) > 3:
                ema_days = ema_days[:3]

            for n_days in ema_days:
                df[f"ema_{n_days}"] = NaN
                df.at[n_days - 1,
                      f"ema_{n_days}"] = df.iloc[:n_days]["close_price"].sum(
                      ) / n_days

                for i, row in df.iloc[n_days:].iterrows():
                    df.at[i, f"ema_{n_days}"] = ema_n_days(
                        n_days, row["close_price"],
                        df.iloc[i - 1][f"ema_{n_days}"])

            candle_data = {
                "x": df["begins_at"],
                "open": df["open_price"],
                "high": df["high_price"],
                "low": df["low_price"],
                "close": df["close_price"],
                "name": symbol
            }
            candlestick = go.Candlestick(candle_data)

            fig.append_trace(candlestick, 2, 1)

            blank_trace = go.Scatter(
                x=None,
                y=None,
            )
            fig.append_trace(blank_trace, 2, 1)
            fig.append_trace(blank_trace, 2, 1)

            for i, n_days in enumerate(ema_days):
                ema_trace = go.Scatter(x=df["begins_at"],
                                       y=df[f"ema_{n_days}"],
                                       name=f"ema_{n_days}")

                ema_diff = (100.0 / df[f"ema_{n_days}"]) * (
                    df[f"ema_{n_days}"] - df[f"ema_{n_days}"].shift(periods=1))

                ema_diff_rate = ema_diff - ema_diff.shift(periods=1)

                ema_diff_rate_trace = go.Scatter(x=df["begins_at"],
                                                 y=ema_diff_rate,
                                                 name=f"ema_{n_days}_rate")

                fig.append_trace(ema_trace, 2, 1)
                fig.append_trace(ema_diff_rate_trace, 1, 1)

            # fig.update_layout(xaxis_rangeslider_visible=False)
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="Grey")
            fig.update_yaxes(showgrid=True,
                             gridwidth=1,
                             gridcolor="Grey",
                             zeroline=True,
                             zerolinewidth=2,
                             zerolinecolor="Grey")
            fig.update_layout(hovermode="x unified",
                              showlegend=False,
                              height=(420 * rows))

        except Exception as e:
            print(f"Could not update data for '{symbol}'.")
            print(e)

        return heading, fig

    return app


def create_server():
    app = create_app()
    return app.server
