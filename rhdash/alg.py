"""Helper functions, mostly math."""


def ema_n_days(days, close_today, ema_yesterday):
    smoothing = 2.0
    smooth_over_days = smoothing / (1 + days)
    return (close_today * smooth_over_days) + (ema_yesterday *
                                               (1 - smooth_over_days))


def percent_diff(price, average):
    return 100.0 * (price - average) / price
