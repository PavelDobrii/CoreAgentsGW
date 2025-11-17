package com.coreagents.cityguide.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.coreagents.cityguide.data.CityGuideRepository
import com.coreagents.cityguide.data.Place
import com.coreagents.cityguide.data.Profile
import com.coreagents.cityguide.data.Route
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

    fun signUp(name: String, email: String, password: String, onSuccess: () -> Unit) {
        launchAndCatch {
            val profile = repository.register(name, email, password)
            updateState(profile = profile, error = null)
            onSuccess()
        }
    }

    fun updateProfile(profile: Profile) {
        launchAndCatch {
            val updated = repository.updateProfile(profile)
            updateState(profile = updated, error = null)
        }
    }

    fun loadPlaces() {
        launchAndCatch {
            val places = repository.places()
            updateState(places = places, error = null)
        }
    }

    fun loadRoutes() {
        launchAndCatch {
            val routes = repository.routes()
            updateState(routes = routes, error = null)
        }
    }

    fun loadRoute(id: String) {
        launchAndCatch {
            val route = repository.route(id)
            updateState(currentRoute = route, error = null)
        }
    }

    fun generateRoute(id: String) {
        launchAndCatch {
            val generated = repository.generateRoute(id)
            val updatedRoutes = state.value.routes.map { route ->
                if (route.id == id) generated else route
            }
            updateState(routes = updatedRoutes, currentRoute = generated, error = null)
        }
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
        profile: Profile? = state.value.profile,
        places: List<Place> = state.value.places,
        routes: List<Route> = state.value.routes,
        currentRoute: Route? = state.value.currentRoute
    ) {
        _state.value = CityGuideState(
            isLoading = isLoading,
            error = error,
            profile = profile,
            places = places,
            routes = routes,
            currentRoute = currentRoute
        )
    }
}
