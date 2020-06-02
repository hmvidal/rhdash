import sys

import robin_stocks


def login_using(robinhood_config):
    try:
        robin_stocks.login(robinhood_config["creds"]["user"],
                           robinhood_config["creds"]["password"],
                           by_sms=True)
    except Exception:
        print("Could not log into RobinHood.")
        sys.exit(1)


def get_name(symbol):
    try:
        return robin_stocks.stocks.get_name_by_symbol(symbol)
    except Exception as e:
        print("Could not get name for '{symbol}'.")
        return ""


def get_year_data(symbol):
    try:
        return robin_stocks.stocks.get_historicals(symbol, span="year")
    except Exception as e:
        print("Could not get year data for '{symbol}'.")
        return None
