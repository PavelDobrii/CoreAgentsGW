package com.coreagents.cityguide.data

data class AuthRequest(
    val email: String,
    val password: String
)

data class RegisterRequest(
    val name: String,
    val email: String,
    val password: String
)

data class Profile(
    val id: String,
    val name: String,
    val email: String,
    val city: String? = null,
    val language: String? = null,
    val interests: List<String> = emptyList()
)

data class Place(
    val id: String,
    val name: String,
    val latitude: Double,
    val longitude: Double
)

data class RoutePoint(
    val id: String,
    val name: String,
    val description: String? = null
)

data class Route(
    val id: String,
    val title: String,
    val summary: String? = null,
    val points: List<RoutePoint> = emptyList()
)

data class PlacesResponse(val items: List<Place>)
data class RoutesResponse(val items: List<Route>)

data class ApiError(val message: String)
