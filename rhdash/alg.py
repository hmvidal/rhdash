"""Helper functions, mostly math."""


def ema_n_days(days, close_today, ema_yesterday):
    smoothing = 2
    return (close_today * (smoothing /
                           (1 + days))) + ema_yesterday * (1 - (smoothing /
                                                                (1 + days)))


def percent_diff(price, average):
    return 100.0 * (price - average) / price
