from __future__ import annotations

from ...http import Application, Request, json_response


def register_routes(app: Application) -> None:
    @app.route("GET", "/v1/places", summary="List Places")
    def list_places(request: Request):
        query = (request.params.get("query") or "").lower()
        city = (request.params.get("city") or "").title() or "Vilnius"

        sample = [
            {
                "id": "cathedral-square",
                "name": "Cathedral Square",
                "address": f"{city} Old Town",
                "location": {"lat": 54.685, "lng": 25.287},
                "types": ["tourist_attraction", "square"],
                "source": "stub",
            },
            {
                "id": "mo-museum",
                "name": "MO Museum",
                "address": f"{city} City Center",
                "location": {"lat": 54.689, "lng": 25.279},
                "types": ["museum"],
                "source": "stub",
            },
            {
                "id": "bernardine-park",
                "name": "Bernardine Garden",
                "address": f"{city} Riverside",
                "location": {"lat": 54.684, "lng": 25.293},
                "types": ["park"],
                "source": "stub",
            },
        ]

        if query:
            sample = [place for place in sample if query in place["name"].lower()]
        return json_response(sample)
