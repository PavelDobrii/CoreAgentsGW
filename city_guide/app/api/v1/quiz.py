from __future__ import annotations

from ...http import Application, Request, json_response


def register_routes(app: Application) -> None:
    @app.route("POST", "/v1/quiz", summary="Submit Quiz")
    def submit_quiz(request: Request):
        payload = request.json or {}
        summary = {
            "interests": payload.get("interests", []),
            "travelStyle": payload.get("travelStyle", "balanced"),
        }
        return json_response(summary)
