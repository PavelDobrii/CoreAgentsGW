package com.coreagents.cityguide.viewmodel

import com.coreagents.cityguide.data.Profile
import com.coreagents.cityguide.data.Tokens
import com.coreagents.cityguide.data.Trip

data class CityGuideState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val tokens: Tokens? = null,
    val profile: Profile? = null,
    val trips: List<Trip> = emptyList(),
    val currentTrip: Trip? = null,
    val onboardingNotes: String = ""
)
