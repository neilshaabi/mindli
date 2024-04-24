from datetime import datetime

from flask import render_template_string


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


def get_flashed_message_html(message: str, category: str) -> str:
    return render_template_string(
        """
            {% from '_macros.html' import flashed_message %}
            {{ flashed_message(message=message, category=category) }}
        """,
        message=message,
        category=category,
    )
