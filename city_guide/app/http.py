from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List


@dataclass
class Request:
    method: str
    path: str
    headers: Dict[str, str]
    params: Dict[str, str]
    json: Any
    path_params: Dict[str, str]


@dataclass
class Response:
    status_code: int
    body: Any
    headers: Dict[str, str] | None = None

    def json(self) -> Any:
        return self.body


def json_response(body: Any, status_code: int = 200, headers: Dict[str, str] | None = None) -> Response:
    return Response(status_code, body, headers)


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@dataclass
class Route:
    method: str
    path: str
    segments: List[str]
    handler: Callable[[Request], Response]
    summary: str
    include_in_schema: bool


class Application:
    def __init__(self) -> None:
        self.routes: List[Route] = []
        self.openapi_paths: dict[str, dict[str, Any]] = {}
        self.components: dict[str, Any] = {}

    def _compile(self, path: str) -> List[str]:
        return [segment for segment in path.strip("/").split("/") if segment]

    def add_route(
        self,
        method: str,
        path: str,
        handler: Callable[[Request], Response],
        *,
        summary: str = "",
        include_in_schema: bool = True,
    ) -> None:
        route = Route(method.upper(), path, self._compile(path), handler, summary, include_in_schema)
        self.routes.append(route)
        if include_in_schema:
            entry = self.openapi_paths.setdefault(path, {})
            entry[method.lower()] = {
                "summary": summary,
                "responses": {"200": {"description": "OK"}},
            }

    def route(self, method: str, path: str, *, summary: str = "", include_in_schema: bool = True):
        def decorator(func: Callable[[Request], Response]):
            self.add_route(method, path, func, summary=summary, include_in_schema=include_in_schema)
            return func

        return decorator

    def set_components(self, components: dict[str, Any]) -> None:
        self.components = components

    def match(self, method: str, path: str) -> tuple[Route, dict[str, str]]:
        method = method.upper()
        incoming = [segment for segment in path.strip("/").split("/") if segment]
        for route in self.routes:
            if route.method != method:
                continue
            if len(route.segments) != len(incoming):
                continue
            params: dict[str, str] = {}
            matched = True
            for pattern, value in zip(route.segments, incoming, strict=False):
                if pattern.startswith("{") and pattern.endswith("}"):
                    params[pattern[1:-1]] = value
                elif pattern != value:
                    matched = False
                    break
            if matched:
                return route, params
        raise HTTPException(404, "Not Found")

    def handle_request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        headers: Dict[str, str] | None = None,
        params: Dict[str, str] | None = None,
    ) -> Response:
        headers = {k: v for k, v in (headers or {}).items()}
        params = {k: str(v) for k, v in (params or {}).items()}
        route, path_params = self.match(method, path)
        request = Request(method, path, headers, params, json_body, path_params)
        try:
            response = route.handler(request)
        except HTTPException as exc:  # pragma: no cover - exercised indirectly
            return Response(exc.status_code, {"detail": exc.detail})
        return response

    def openapi(self) -> dict[str, Any]:
        return {
            "openapi": "3.0.0",
            "info": {"title": "City Guide API", "version": "1.0.0"},
            "paths": self.openapi_paths,
            "components": self.components,
        }


class TestClient:
    def __init__(self, app: Application):
        self.app = app

    def request(self, method: str, url: str, **kwargs: Any) -> Response:
        json_body = kwargs.get("json")
        params = kwargs.get("params")
        headers = kwargs.get("headers")
        if isinstance(json_body, str):
            try:
                json_body = json.loads(json_body)
            except json.JSONDecodeError:
                pass
        response = self.app.handle_request(method, url, json_body=json_body, headers=headers, params=params)
        response.headers = response.headers or {}
        return response

    def get(self, url: str, **kwargs: Any) -> Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Response:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Response:
        return self.request("PUT", url, **kwargs)
