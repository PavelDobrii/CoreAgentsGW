package com.coreagents.cityguide.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.coreagents.cityguide.ui.screens.OnboardingScreen
import com.coreagents.cityguide.ui.screens.ProfileScreen
import com.coreagents.cityguide.ui.screens.SignInScreen
import com.coreagents.cityguide.ui.screens.SignUpScreen
import com.coreagents.cityguide.ui.screens.TripCreateScreen
import com.coreagents.cityguide.ui.screens.TripDetailScreen
import com.coreagents.cityguide.ui.screens.TripsScreen
import com.coreagents.cityguide.ui.theme.CityGuideTheme
import com.coreagents.cityguide.viewmodel.CityGuideViewModel

sealed class Route(val path: String) {
    data object SignIn : Route("signin")
    data object SignUp : Route("signup")
    data object Onboarding : Route("onboarding")
    data object Profile : Route("profile")
    data object Trips : Route("trips")
    data object TripCreate : Route("trip/create")
    data object TripDetail : Route("trip/{id}") {
        fun build(id: String) = "trip/$id"
    }
}

@Composable
fun CityGuideApp(
    navController: NavHostController = rememberNavController(),
    viewModel: CityGuideViewModel = viewModel()
) {
    val uiState by viewModel.state.collectAsState()

    CityGuideTheme {
        Surface(color = MaterialTheme.colorScheme.background) {
            NavHost(
                navController = navController,
                startDestination = Route.SignIn.path
            ) {
                composable(Route.SignIn.path) {
                    SignInScreen(
                        state = uiState,
                        onNavigateToSignUp = { navController.navigate(Route.SignUp.path) },
                        onLogin = { email, password ->
                            viewModel.signIn(email, password) {
                                navController.navigate(Route.Onboarding.path) {
                                    popUpTo(Route.SignIn.path) { inclusive = true }
                                }
                            }
                        }
                    )
                }
                composable(Route.SignUp.path) {
                    SignUpScreen(
                        state = uiState,
                        onSignUp = { data ->
                            viewModel.signUp(
                                data.email,
                                data.password,
                                data.firstName,
                                data.lastName,
                                data.phone,
                                data.country,
                                data.city
                            ) {
                                navController.navigate(Route.Onboarding.path) {
                                    popUpTo(Route.SignUp.path) { inclusive = true }
                                }
                            }
                        },
                        onNavigateToSignIn = { navController.popBackStack() }
                    )
                }
                composable(Route.Onboarding.path) {
                    OnboardingScreen(
                        state = uiState,
                        onSave = { notes ->
                            viewModel.rememberOnboarding(notes) {
                                navController.navigate(Route.Trips.path) {
                                    popUpTo(Route.Onboarding.path) { inclusive = true }
                                }
                            }
                        }
                    )
                }
                composable(Route.Profile.path) {
                    ProfileScreen(
                        state = uiState,
                        onSaveProfile = viewModel::updateProfile,
                        onOpenTrips = {
                            viewModel.loadTrips()
                            navController.navigate(Route.Trips.path)
                        }
                    )
                }
                composable(Route.Trips.path) {
                    TripsScreen(
                        state = uiState,
                        onRefresh = viewModel::loadTrips,
                        onOpenProfile = {
                            viewModel.loadProfile()
                            navController.navigate(Route.Profile.path)
                        },
                        onCreate = { navController.navigate(Route.TripCreate.path) },
                        onOpenTrip = { id ->
                            viewModel.openTrip(id)
                            navController.navigate(Route.TripDetail.build(id))
                        }
                    )
                }
                composable(Route.TripCreate.path) {
                    TripCreateScreen(
                        state = uiState,
                        onCreate = { title, localityId, description, interests ->
                            viewModel.createTrip(title, localityId, description, interests)
                            navController.navigate(Route.Trips.path) {
                                popUpTo(Route.TripCreate.path) { inclusive = true }
                            }
                        },
                        onBack = { navController.popBackStack() }
                    )
                }
                composable(Route.TripDetail.path) { entry ->
                    val tripId = entry.arguments?.getString("id").orEmpty()
                    TripDetailScreen(
                        tripId = tripId,
                        state = uiState,
                        onRefresh = { viewModel.openTrip(tripId) },
                        onGenerate = { viewModel.generateTrip(tripId) },
                        onBack = { navController.popBackStack() }
                    )
                }
            }
        }
    }
}
