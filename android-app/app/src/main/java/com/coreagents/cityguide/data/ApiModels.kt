package com.coreagents.cityguide.data

import com.squareup.moshi.Json

// --- Authentication ---

data class AuthRequest(
    val email: String,
    val password: String
)

data class RegisterRequest(
    val email: String,
    val password: String,
    val firstName: String? = null,
    val lastName: String? = null,
    val phoneNumber: String? = null,
    val country: String? = null,
    val city: String? = null
)

data class RefreshRequest(
    val refreshToken: String
)

data class Tokens(
    @field:Json(name = "access_token") val accessToken: String,
    @field:Json(name = "refresh_token") val refreshToken: String
)

data class AuthResponse(
    val access_token: String,
    val refresh_token: String,
    val user: Profile
) {
    fun tokens() = Tokens(accessToken = access_token, refreshToken = refresh_token)
}

// --- Profile ---

data class Profile(
    val id: String,
    val email: String,
    val firstName: String? = null,
    val lastName: String? = null,
    val phone: String? = null,
    val country: String? = null,
    val city: String? = null,
    val isActive: Boolean = true,
    val language: String? = null,
    val gender: String? = null,
    val age: Int? = null,
    val region: String? = null,
    val interests: List<String> = emptyList(),
    val travelStyle: String? = null
)

data class ProfileUpdate(
    val gender: String? = null,
    val age: Int? = null,
    val city: String? = null,
    val language: String? = null,
    val region: String? = null,
    val interests: List<String>? = null,
    val travelStyle: String? = null
)

// --- Trips ---

data class LocationPoint(
    val lat: Double,
    val lng: Double
)

data class Place(
    val id: String,
    val name: String,
    val address: String,
    val location: LocationPoint,
    val description: String? = null,
    val audioSrc: String? = null,
    val posterSrc: String? = null,
    val text: String? = null,
    val order: Int? = null
)

data class Waypoint(
    val id: String? = null,
    val name: String,
    val address: String,
    val location: LocationPoint,
    val description: String? = null,
    val audioSrc: String? = null,
    val posterSrc: String? = null,
    val text: String? = null,
    val order: Int? = null
)

data class RouteOptions(
    val interests: List<String>? = null,
    val moods: List<String>? = null,
    val dateAt: String? = null,
    val duration: String? = null,
    val timeOfDay: String? = null
)

enum class TripStatus {
    created, draft, inProgress, success, failed
}

data class Trip(
    val id: String,
    val name: String,
    val description: String? = null,
    val startWaypoint: Waypoint? = null,
    val endWaypoint: Waypoint? = null,
    val status: TripStatus = TripStatus.created,
    val encodedPolyline: String? = null,
    val distance: Double? = null,
    val rating: Double? = null,
    val waypoints: List<Waypoint>? = null,
    val createdAt: String? = null,
    val updatedAt: String? = null
)

data class TripRequest(
    val title: String,
    val localityId: String?,
    val description: String? = null,
    val start: Waypoint? = null,
    val end: Waypoint? = null,
    val routeOptions: RouteOptions? = null
)

data class GenerateTripRequest(
    val waypoints: List<String> = emptyList(),
    val places: List<String> = emptyList()
)

data class GenerateTripResponse(val message: String)

typealias TripListResponse = List<Trip>

data class ApiError(val message: String)
