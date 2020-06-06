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


def get_watchlist(name="Default"):
    try:
        return robin_stocks.account.get_watchlist_by_name()
    except Exception as e:
        print("Could not get for watchlist.")
        return None


def get_symbol_by_url(url):
    try:
        return robin_stocks.stocks.get_symbol_by_url(url)
    except Exception as e:
        print(f"Could not get symbol for {url}.")
        return None


def get_name(symbol):
    try:
        return robin_stocks.stocks.get_name_by_symbol(symbol)
    except Exception as e:
        print("Could not get name for '{symbol}'.")
        return ""


def get_fundamentals(symbol):
    try:
        return robin_stocks.stocks.get_fundamentals(symbol)
    except Exception as e:
        print("Could not get fundamentals for '{symbol}'.")
        return None


def get_day_data(symbol):
    try:
        data = robin_stocks.stocks.get_historicals(symbol,
                                                   span="day",
                                                   bounds="extended")
        return data
    except Exception as e:
        print("Could not get day data for '{symbol}'.")
        return None


def get_week_data(symbol):
    try:
        data = robin_stocks.stocks.get_historicals(symbol, span="week")
        return data
    except Exception as e:
        print("Could not get week data for '{symbol}'.")
        return None


def get_year_data(symbol):
    try:
        data = robin_stocks.stocks.get_historicals(symbol, span="year")
        return data
    except Exception as e:
        print("Could not get year data for '{symbol}'.")
        return None
