"""Module dosctring"""
import sys

import dash
import dash_auth
import dash_html_components as html

from rhdash.args import setup_args
from rhdash.config import fetch


def setup_dash(config):
    """Set up dashboard server."""
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    if "user" not in config or "password" not in config:
        print("Please provide 'user' and 'password' in your configuration.")
        sys.exit(1)
    credentials = {config["user"]: config["password"]}
    auth = dash_auth.BasicAuth(app, credentials)
    assert auth
    app.layout = html.Div(children=[html.H1(children="Dashboard")])
    return app


def run():
    """Main entrypoint."""
    args = setup_args()
    if args:
        config = fetch(args.config)
        app = setup_dash(config)
        app.run_server()
        return True
    return False


if __name__ == "__main__":
    run()
