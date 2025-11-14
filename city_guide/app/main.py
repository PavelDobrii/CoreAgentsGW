from __future__ import annotations

from .http import Application, Request, json_response
from .api.v1 import auth, health, places, poi, profile, prompts, quiz, routes

app = Application()

for module in (health, auth, quiz, profile, prompts, routes, poi, places):
    module.register_routes(app)

OPENAPI_COMPONENTS = {
    "schemas": {
        "HardConstraints": {
            "type": "object",
            "properties": {
                "time_window_start": {"type": "string", "format": "date-time"},
                "must_include_poi_ids": {"type": "array", "items": {"type": "string", "format": "uuid"}},
            },
        },
        "TripResponse": {
            "type": "object",
            "properties": {"id": {"type": "string", "format": "uuid"}},
        },
    }
}

app.set_components(OPENAPI_COMPONENTS)


@app.route("GET", "/openapi.json", summary="OpenAPI", include_in_schema=False)
def openapi(_: Request):
    return json_response(app.openapi())
