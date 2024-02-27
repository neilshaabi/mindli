from flask import Flask, Response, render_template
from werkzeug.exceptions import HTTPException


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(Exception)
    def handle_exception(e) -> Response:
        return render_template(
            "error.html",
            error=e,
            is_http_exception=isinstance(e, HTTPException),
            is_error_page=True,
        )

    return
