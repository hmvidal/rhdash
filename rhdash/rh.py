import sys

import robin_stocks


def login_using(robinhood_config):
    user, passwd = "", ""

    if "creds" in robinhood_config:
        creds = robinhood_config["creds"]
        if "user" in creds:
            user = creds["user"]
            if "password" in creds:
                passwd = creds["password"]

    try:
        robin_stocks.login(user, passwd, by_sms=True)
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
        data = robin_stocks.stocks.get_historicals(symbol, span="year")
        return data
    except Exception as e:
        print("Could not get year data for '{symbol}'.")
        return None
