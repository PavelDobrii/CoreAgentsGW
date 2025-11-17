from __future__ import annotations

from ...http import Application, Request, json_response


def register_routes(app: Application) -> None:
    @app.route("GET", "/v1/poi/suggest", summary="Suggest POI")
    def suggest(_: Request):
        sample = [
            {
                "poi_id": "1",
                "name": "Museum",
                "category": "museum",
                "location": {"lat": 54.689, "lng": 25.279},
                "address": "Central District",
                "types": ["museum"],
            },
            {
                "poi_id": "2",
                "name": "Park",
                "category": "park",
                "location": {"lat": 54.684, "lng": 25.293},
                "address": "River side",
                "types": ["park"],
            },
        ]
        return json_response(sample)
