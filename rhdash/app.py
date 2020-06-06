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
from rhdash.rh import get_day_data
from rhdash.rh import get_fundamentals
from rhdash.rh import get_name
from rhdash.rh import get_week_data
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
        html.H1(id="heading", children="", style={"textAlign": "center"}),
        html.Div(id="description-blob", style={"textAlign": "center"}),
        html.Div(id="fundamentals-table"),
        dcc.Graph(id="day-graph"),
        dcc.Graph(id="week-graph"),
        dcc.Graph(id="year-graphs")
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
    if "dash" not in configuration:
        configuration["dash"] = {}

    app = init_using(configuration)

    rows = 2

    @app.callback([
        Output("heading", "children"),
        Output("description-blob", "children"),
        Output("fundamentals-table", "children"),
        Output("day-graph", "figure"),
        Output("week-graph", "figure"),
        Output("year-graphs", "figure")
    ], [Input("symbol", "value")])
    def update_figure(symbol):
        symbol = str(symbol).strip().upper()
        description = ""
        fundamentals_table = html.Table()
        day_fig = make_subplots(rows=rows,
                                cols=1,
                                shared_xaxes=True,
                                vertical_spacing=0.02,
                                row_titles=["Day", symbol])

        week_fig = make_subplots(rows=rows,
                                 cols=1,
                                 shared_xaxes=True,
                                 vertical_spacing=0.02,
                                 row_titles=["Week", symbol])

        fig = make_subplots(rows=rows,
                            cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.02,
                            row_titles=["Year", symbol])

        try:
            name = get_name(symbol) if symbol != "" else ""
            heading = f"{name} ({symbol})" if len(name) > 0 else ""

            fundamentals_data = get_fundamentals(symbol)
            fundamentals_df = pd.DataFrame(fundamentals_data)
            fundamentals_df_values = fundamentals_df.iloc[0]

            fundamentals = {}
            fundamentals[
                "OPEN"] = f"{float(fundamentals_df_values['open']):,.4f}"
            fundamentals[
                "HIGH"] = f"{float(fundamentals_df_values['high']):,.4f}"
            fundamentals[
                "LOW"] = f"{float(fundamentals_df_values['low']):,.4f}"
            fundamentals[
                "MARKET CAP"] = f"${float(fundamentals_df_values['market_cap']):,.0f}"
            fundamentals[
                "AVG VOL"] = f"{float(fundamentals_df_values['average_volume']):,.0f}"
            fundamentals[
                "CURR VOL"] = f"{float(fundamentals_df_values['volume']):,.0f}"

            description = [
                html.Br(),
                html.P(f"{fundamentals_df_values['description']}"),
                html.Br(),
                html.Br()
            ]

            day_data = get_day_data(symbol)
            day_df = pd.DataFrame(day_data)
            day_df["begins_at"] = pd.to_datetime(day_df["begins_at"])
            day_df["begins_at"] = day_df["begins_at"].dt.tz_convert(
                'US/Eastern')

            week_data = get_week_data(symbol)
            week_df = pd.DataFrame(week_data)
            week_df["begins_at"] = pd.to_datetime(week_df["begins_at"])
            week_df["begins_at"] = week_df["begins_at"].dt.tz_convert(
                'US/Eastern')

            year_data = get_year_data(symbol)
            df = pd.DataFrame(year_data)
            df["begins_at"] = pd.to_datetime(df["begins_at"])

            float_cols = [
                "open_price", "close_price", "high_price", "low_price"
            ]

            for col in float_cols:
                day_df[col] = day_df[col].astype(float)
                week_df[col] = week_df[col].astype(float)
                df[col] = df[col].astype(float)

            # df["percent_diff"] = 100.0 * df["close_price"].pct_change()

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

            day_close_price_data = {
                "x": day_df["begins_at"],
                "y": day_df["close_price"],
                "name": "close_price"
            }

            week_close_price_data = {
                "x": week_df["begins_at"],
                "y": week_df["close_price"],
                "name": "close_price"
            }

            close_price_data = {
                "x": df["begins_at"],
                "y": df["close_price"],
                "name": "close_price"
            }

            day_candle_data = {
                "x": day_df["begins_at"],
                "open": day_df["open_price"],
                "high": day_df["high_price"],
                "low": day_df["low_price"],
                "close": day_df["close_price"],
                "name": symbol
            }

            week_candle_data = {
                "x": week_df["begins_at"],
                "open": week_df["open_price"],
                "high": week_df["high_price"],
                "low": week_df["low_price"],
                "close": week_df["close_price"],
                "name": symbol
            }

            candle_data = {
                "x": df["begins_at"],
                "open": df["open_price"],
                "high": df["high_price"],
                "low": df["low_price"],
                "close": df["close_price"],
                "name": symbol
            }

            fundamentals_headers = html.Tr(
                [html.Th(field) for field in fundamentals])
            fundamentals_row = html.Tr(
                [html.Td(fundamentals[field]) for field in fundamentals])
            fundamentals_table = html.Table([fundamentals_headers] +
                                            [fundamentals_row],
                                            style={
                                                "marginLeft": "auto",
                                                "marginRight": "auto"
                                            })

            day_close_price = go.Scatter(day_close_price_data)
            day_candlestick = go.Candlestick(day_candle_data)

            week_close_price = go.Scatter(week_close_price_data)
            week_candlestick = go.Candlestick(week_candle_data)

            close_price = go.Scatter(close_price_data)
            candlestick = go.Candlestick(candle_data)

            day_fig.append_trace(day_close_price, 1, 1)
            day_fig.append_trace(day_candlestick, 2, 1)

            week_fig.append_trace(week_close_price, 1, 1)
            week_fig.append_trace(week_candlestick, 2, 1)

            fig.append_trace(close_price, 1, 1)
            fig.append_trace(candlestick, 2, 1)

            # blank_trace = go.Scatter(
            #     x=None,
            #     y=None,
            # )
            # fig.append_trace(blank_trace, 2, 1)
            # fig.append_trace(blank_trace, 2, 1)

            for i, n_days in enumerate(ema_days):
                ema_trace = go.Scatter(x=df["begins_at"],
                                       y=df[f"ema_{n_days}"],
                                       name=f"ema_{n_days}")

                # ema_diff = (100.0 / df[f"ema_{n_days}"]) * (
                #     df[f"ema_{n_days}"] - df[f"ema_{n_days}"].shift(periods=1))

                # ema_diff_rate = ema_diff - ema_diff.shift(periods=1)

                # ema_diff_rate_trace = go.Scatter(x=df["begins_at"],
                #                                  y=ema_diff_rate,
                #                                  name=f"ema_{n_days}_rate")

                fig.append_trace(ema_trace, 1, 1)
                # fig.append_trace(ema_diff_rate_trace, 1, 1)

            day_fig.update_xaxes()
            day_fig.update_yaxes(showgrid=True,
                                 gridwidth=1,
                                 gridcolor="Grey",
                                 zeroline=True,
                                 zerolinewidth=2,
                                 zerolinecolor="Grey")
            day_fig.update_layout(hovermode="x unified",
                                  showlegend=False,
                                  height=(420 * rows),
                                  xaxis=dict(type="category"))

            week_fig.update_xaxes(
                rangebreaks=[dict(pattern="hour", bounds=[16, 9.5])])
            week_fig.update_yaxes(showgrid=True,
                                  gridwidth=1,
                                  gridcolor="Grey",
                                  zeroline=True,
                                  zerolinewidth=2,
                                  zerolinecolor="Grey")
            week_fig.update_layout(hovermode="x unified",
                                   showlegend=False,
                                   height=(420 * rows),
                                   xaxis=dict(type="category"))

            fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
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

        return heading, description, fundamentals_table, day_fig, week_fig, fig

    return app


def create_server():
    app = create_app()
    return app.server
