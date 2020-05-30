"""Module dosctring"""
import sys

import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import robin_stocks
from dash.dependencies import Input
from dash.dependencies import Output

from rhdash.args import setup_args
from rhdash.config import fetch


def setup_dash(config):
    """Set up dashboard server."""

    dash_config = config["dash"]
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    dash_auth.BasicAuth(
        app, {dash_config["creds"]["user"]: dash_config["creds"]["password"]})

    app.layout = html.Div([
        html.Div(children="Symbol:"),
        dcc.Input(id='symbol', value='', type='text'),
        # html.H1("Dashboard"),
        dcc.Graph(id="value-graph"),
        # dcc.Graph(id="diff-graph")
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

        @app.callback(Output('value-graph', 'figure'),
                      [Input('symbol', 'value')])
        def update_figure(symbol):
            try:
                symbol = str(symbol).strip().upper()
                name = robin_stocks.stocks.get_name_by_symbol(
                    symbol) if symbol != "" else ""
                year_data = robin_stocks.stocks.get_historicals(symbol,
                                                                span="year")
                df = pd.DataFrame(year_data)

                n_total_days = len(df["begins_at"])
                window_boundary = n_total_days * 4 / 9
                df = df.loc[window_boundary:]

                value_graph_data = [{
                    "x": df["begins_at"],
                    "y": df["close_price"],
                    "type": "line",
                    "name": "close_price"
                }]
            except Exception:
                value_graph_data = [{
                    "x": [],
                    "y": [],
                    "type": "line",
                    "name": "close_price"
                }]

            return {
                'data': value_graph_data,
                'layout': {
                    "title": f"{name} ({symbol})"
                }
            }

        app.run_server()
        return True

    return False


def run():
    arguments = setup_args()
    run_with(arguments)


if __name__ == "__main__":
    run()
