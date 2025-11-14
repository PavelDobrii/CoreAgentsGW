from __future__ import annotations

from ...http import Application, Request, json_response


def register_routes(app: Application) -> None:
    @app.route("GET", "/healthz", summary="Health Check")
    def healthcheck(_: Request):
        return json_response({"status": "ok"})
