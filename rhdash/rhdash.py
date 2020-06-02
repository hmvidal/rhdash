"""Module dosctring"""
import sys

import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import robin_stocks
from dash.dependencies import Input
from dash.dependencies import Output
from plotly.subplots import make_subplots

from rhdash.alg import get_n_ema
from rhdash.alg import get_percent_diff
from rhdash.args import setup_args
from rhdash.config import fetch


def setup_dash(config):
    """Set up dashboard server."""

    dash_config = config["dash"]
    external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    dash_auth.BasicAuth(
        app, {dash_config["creds"]["user"]: dash_config["creds"]["password"]})

    app.layout = html.Div([
        html.Div(children="Symbol:"),
        dcc.Input(id="symbol", value="", type="text"),
        html.H1(id="heading", children=""),
        dcc.Graph(id="value-graph")
    ])

    return app


def login_using(robinhood_config):
    try:
        robin_stocks.login(robinhood_config["creds"]["user"],
                           robinhood_config["creds"]["password"],
                           by_sms=True)
    except Exception:
        print("Could not log into RobinHood.")
        sys.exit(1)


def init_using(config):
    """Do some initialization"""
    robinhood_config = config["robinhood"]
    login_using(robinhood_config)
    return setup_dash(config)


def run_with(arguments):
    """Main entrypoint."""
    if arguments:
        configuration = fetch(arguments.config)
        app = init_using(configuration)

        rows = 2

        @app.callback(
            [Output("heading", "children"),
             Output("value-graph", "figure")], [Input("symbol", "value")])
        def update_figure(symbol):
            fig = make_subplots(rows=rows,
                                cols=1,
                                shared_xaxes=True,
                                vertical_spacing=0.02)

            try:
                symbol = str(symbol).strip().upper()
                name = robin_stocks.stocks.get_name_by_symbol(
                    symbol) if symbol != "" else ""
                heading = f"{name} ({symbol})" if len(name) > 0 else ""

                year_data = robin_stocks.stocks.get_historicals(symbol,
                                                                span="year")
                df = pd.DataFrame(year_data)
                float_cols = [
                    "open_price", "close_price", "high_price", "low_price"
                ]
                for col in float_cols:
                    df[col] = df[col].astype(float)
                ema_days = configuration["robinhood"]["ema_days"]

                for n_days in ema_days:
                    df[f"ema_{n_days}"] = 0.0
                    for i, row in df.iterrows():
                        if i <= (n_days - 1):
                            ema = df.iloc[0:i + 1]["close_price"].sum() / (i +
                                                                           1)
                        else:
                            ema = get_n_ema(n_days, row["close_price"],
                                            df.iloc[i - 1]["close_price"])
                        df.at[i, f"ema_{n_days}"] = ema

                n_total_days = len(df["begins_at"])
                window_boundary = n_total_days * 4 / 9
                df = df.loc[window_boundary:]

                lines_prices = []
                lines_diff = []

                lines_prices.append(
                    go.Scatter(x=df["begins_at"],
                               y=df["close_price"],
                               name="close_price"))

                for i, n_days in enumerate(ema_days):
                    lines_prices.append(
                        go.Scatter(x=df["begins_at"],
                                   y=df[f"ema_{n_days}"],
                                   name=f"ema_{n_days}"))

                    lines_diff.append(
                        go.Scatter(x=df["begins_at"],
                                   y=get_percent_diff(df["close_price"],
                                                      df[f"ema_{n_days}"]),
                                   name=f"ema_{n_days}_diff"))

                for line in lines_prices:
                    fig.append_trace(line, 1, 1)

                for line in lines_diff:
                    fig.append_trace(line, 2, 1)

                fig.update_xaxes(showgrid=True,
                                 gridwidth=1,
                                 gridcolor="LightPink")
                fig.update_yaxes(zeroline=True,
                                 zerolinewidth=3,
                                 zerolinecolor="Pink")

                fig.update_layout(hovermode="x unified", height=300 * rows)

            except Exception as e:
                print(f"Could not update data for '{symbol}'.")

            return heading, fig

        app.run_server()
        return True

    return False


def run():
    arguments = setup_args()
    run_with(arguments)


if __name__ == "__main__":
    run()
