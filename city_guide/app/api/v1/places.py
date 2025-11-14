from __future__ import annotations

from ...http import Application, Request, json_response


def register_routes(app: Application) -> None:
    @app.route("GET", "/v1/places", summary="List Places")
    def list_places(_: Request):
        return json_response([])
