from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_openapi_contract(async_client):
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()

    paths = spec["paths"]
    expected_paths = {
        "/healthz",
        "/v1/quiz",
        "/v1/profile",
        "/v1/prompts/route",
        "/v1/routes:generate",
        "/v1/routes/{route_id}",
        "/v1/poi/suggest",
    }
    assert expected_paths.issubset(paths.keys())

    assert paths["/v1/quiz"]["post"]["summary"] == "Submit Quiz"
    assert paths["/v1/profile"]["get"]["summary"] == "Get Profile"
    assert paths["/v1/profile"]["post"]["summary"] == "Create Profile"
    assert paths["/v1/routes:generate"]["post"]["summary"] == "Generate Route"
    assert paths["/v1/routes/{route_id}"]["get"]["summary"] == "Get Route"

    hard_constraints = spec["components"]["schemas"]["HardConstraints"]
    properties = hard_constraints["properties"]
    assert properties["time_window_start"]["format"] == "date-time"
    assert properties["must_include_poi_ids"]["items"]["format"] == "uuid"

    route_response = spec["components"]["schemas"]["RouteDraftResponse"]
    assert route_response["properties"]["route_id"]["format"] == "uuid"
