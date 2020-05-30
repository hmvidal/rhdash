"""Helper functions, mostly math."""


def get_n_ema(days, close_today, ema_yesterday):
    smoothing = 2
    return (close_today * (smoothing /
                           (1 + days))) + ema_yesterday * (1 - (smoothing /
                                                                (1 + days)))
