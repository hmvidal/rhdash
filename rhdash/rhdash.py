"""Module dosctring"""
import dash
import dash_auth
import dash_html_components as html

from rhdash.args import setup_args
from rhdash.config import fetch


def setup_dash(config):
    """Set up dashboard server."""

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    dash_config = config["dash"]
    # robinhood_config = config["robinhood"]

    dash_auth.BasicAuth(
        app, {dash_config["creds"]["user"]: dash_config["creds"]["password"]})
    app.layout = html.Div(children=[html.H1(children="Dashboard")])

    return app


def run_with(arguments):
    """Main entrypoint."""
    if arguments:
        configuration = fetch(arguments.config)
        app = setup_dash(configuration)
        app.run_server()
        return True
    return False


if __name__ == "__main__":
    arguments = setup_args()
    run_with(arguments)
