from datetime import datetime


def format_time_since(dt: datetime) -> str:
    """
    Returns a string representing time since `dt` (datetime) in a short format.
    """
    now = datetime.now()
    diff = now - dt

    periods = [
        ("y", 60 * 60 * 24 * 365),
        ("m", 60 * 60 * 24 * 30),
        ("w", 60 * 60 * 24 * 7),
        ("d", 60 * 60 * 24),
        ("h", 60 * 60),
        ("min", 60),
        ("s", 1),
    ]

    for period_name, period_seconds in periods:
        if diff.total_seconds() >= period_seconds:
            period_value = int(diff.total_seconds() / period_seconds)
            return f"{period_value}{period_name}"

    return "now"
