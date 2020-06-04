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
from rhdash.alg import percent_diff
from rhdash.config import fetch
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


def create_app(arguments):
    configuration = fetch(arguments.config) if arguments.config else {}

    if "robinhood" not in configuration:
        configuration["robinhood"] = {}
    if "dash" not in configuration:
        configuration["dash"] = {}

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
                            row_titles=["Close Price", "% Diff", "EMA Diff"])

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

            for n_days in ema_days:
                df[f"ema_{n_days}"] = NaN
                df.at[n_days - 1,
                      f"ema_{n_days}"] = df.iloc[:n_days]["close_price"].sum(
                      ) / n_days

                for i, row in df.iloc[n_days:].iterrows():
                    df.at[i, f"ema_{n_days}"] = ema_n_days(
                        n_days, row["close_price"],
                        df.iloc[i - 1][f"ema_{n_days}"])

            traces = {"close_price": [], "ema_diff": []}

            traces["close_price"].append(
                go.Candlestick(x=df["begins_at"],
                               open=df["open_price"],
                               high=df["high_price"],
                               low=df["low_price"],
                               close=df["close_price"],
                               name="price"))

            traces["percent_diff"] = go.Scatter(x=df["begins_at"],
                                                y=df["percent_diff"],
                                                name="percent_diff")

            for i, n_days in enumerate(ema_days):

                traces["close_price"].append(
                    go.Scatter(x=df["begins_at"],
                               y=df[f"ema_{n_days}"],
                               name=f"ema_{n_days}"))

            for line in traces["close_price"]:
                fig.append_trace(line, 1, 1)

            fig.append_trace(traces["percent_diff"], 2, 1)

            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="Grey")

            fig.update_yaxes(showgrid=True,
                             gridwidth=1,
                             gridcolor="Grey",
                             zeroline=True,
                             zerolinewidth=2,
                             zerolinecolor="Grey")

            fig.update_layout(hovermode="x unified",
                              showlegend=False,
                              xaxis_rangeslider_visible=False,
                              height=(400 * rows))

        except Exception as e:
            print(f"Could not update data for '{symbol}'.")

        return heading, fig

    return app
