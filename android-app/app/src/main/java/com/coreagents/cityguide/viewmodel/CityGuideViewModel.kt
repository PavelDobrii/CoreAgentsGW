package com.coreagents.cityguide.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.coreagents.cityguide.data.CityGuideRepository
import com.coreagents.cityguide.data.GenerateTripRequest
import com.coreagents.cityguide.data.ProfileUpdate
import com.coreagents.cityguide.data.TripRequest
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class CityGuideViewModel(
    private val repository: CityGuideRepository = CityGuideRepository()
) : ViewModel() {

    private val _state = MutableStateFlow(CityGuideState())
    val state = _state.asStateFlow()

    fun signIn(email: String, password: String, onSuccess: () -> Unit) {
        launchAndCatch {
            val profile = repository.login(email, password)
            updateState(profile = profile, error = null)
            onSuccess()
        }
    }

    fun signUp(
        email: String,
        password: String,
        firstName: String?,
        lastName: String?,
        phone: String?,
        country: String?,
        city: String?,
        onSuccess: () -> Unit
    ) {
        launchAndCatch {
            val profile = repository.register(email, password, firstName, lastName, phone, country, city)
            updateState(profile = profile, error = null)
            onSuccess()
        }
    }

    fun refreshSession() {
        launchAndCatch {
            val tokens = repository.refreshToken()
            updateState(tokens = tokens)
        }
    }

    fun loadProfile() {
        launchAndCatch {
            val profile = repository.profile()
            updateState(profile = profile, error = null)
        }
    }

    fun updateProfile(update: ProfileUpdate) {
        launchAndCatch {
            val updated = repository.updateProfile(update)
            updateState(profile = updated, error = null)
        }
    }

    fun loadTrips() {
        launchAndCatch {
            val trips = repository.trips()
            updateState(trips = trips, error = null)
        }
    }

    fun openTrip(id: String) {
        launchAndCatch {
            val trip = repository.trip(id)
            updateState(currentTrip = trip, error = null)
        }
    }

    fun createTrip(title: String, localityId: String?, description: String?, interests: List<String>) {
        launchAndCatch {
            val trip = repository.createTrip(
                TripRequest(
                    title = title,
                    localityId = localityId,
                    description = description,
                    routeOptions = if (interests.isNotEmpty()) com.coreagents.cityguide.data.RouteOptions(interests = interests) else null
                )
            )
            val updatedList = (state.value.trips + trip).sortedBy { it.name }
            updateState(trips = updatedList, currentTrip = trip, error = null)
        }
    }

    fun generateTrip(id: String) {
        launchAndCatch {
            repository.generateTrip(id, GenerateTripRequest())
            val refreshed = repository.trip(id)
            val updatedTrips = state.value.trips.map { if (it.id == id) refreshed else it }
            updateState(trips = updatedTrips, currentTrip = refreshed, error = null)
        }
    }

    fun rememberOnboarding(notes: String, onDone: () -> Unit) {
        updateState(onboardingNotes = notes)
        onDone()
    }

    private fun launchAndCatch(block: suspend () -> Unit) {
        viewModelScope.launch {
            updateState(isLoading = true, error = null)
            runCatching { block() }
                .onFailure { updateState(error = it.message ?: "Неизвестная ошибка") }
                .also { updateState(isLoading = false) }
        }
    }

    private fun updateState(
        isLoading: Boolean = state.value.isLoading,
        error: String? = state.value.error,
        tokens: com.coreagents.cityguide.data.Tokens? = state.value.tokens,
        profile: com.coreagents.cityguide.data.Profile? = state.value.profile,
        trips: List<com.coreagents.cityguide.data.Trip> = state.value.trips,
        currentTrip: com.coreagents.cityguide.data.Trip? = state.value.currentTrip,
        onboardingNotes: String = state.value.onboardingNotes
    ) {
        _state.value = CityGuideState(
            isLoading = isLoading,
            error = error,
            tokens = tokens,
            profile = profile,
            trips = trips,
            currentTrip = currentTrip,
            onboardingNotes = onboardingNotes
        )
    }
}
