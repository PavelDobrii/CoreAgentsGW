from __future__ import annotations

from ...http import Application, Request, json_response


def register_routes(app: Application) -> None:
    @app.route("GET", "/v1/poi/suggest", summary="Suggest POI")
    def suggest(_: Request):
        sample = [
            {"poi_id": "1", "name": "Museum", "category": "museum"},
            {"poi_id": "2", "name": "Park", "category": "park"},
        ]
        return json_response(sample)
