package com.coreagents.cityguide.viewmodel

import com.coreagents.cityguide.data.Place
import com.coreagents.cityguide.data.Profile
import com.coreagents.cityguide.data.Route

data class CityGuideState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val profile: Profile? = null,
    val places: List<Place> = emptyList(),
    val routes: List<Route> = emptyList(),
    val currentRoute: Route? = null
)
