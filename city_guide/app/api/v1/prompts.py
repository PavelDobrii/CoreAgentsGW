from __future__ import annotations

from ...http import Application, Request, json_response


def register_routes(app: Application) -> None:
    @app.route("POST", "/v1/prompts/route", summary="Generate Route Prompt")
    def route_prompt(request: Request):
        payload = request.json or {}
        prompt = f"Plan a trip in {payload.get('city', 'the city')}"
        return json_response({"prompt": prompt})
