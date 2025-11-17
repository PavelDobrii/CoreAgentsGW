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
import com.coreagents.cityguide.ui.screens.PlaceListScreen
import com.coreagents.cityguide.ui.screens.ProfileScreen
import com.coreagents.cityguide.ui.screens.RouteDetailScreen
import com.coreagents.cityguide.ui.screens.RoutesScreen
import com.coreagents.cityguide.ui.screens.SignInScreen
import com.coreagents.cityguide.ui.screens.SignUpScreen
import com.coreagents.cityguide.ui.theme.CityGuideTheme
import com.coreagents.cityguide.viewmodel.CityGuideViewModel

sealed class Route(val path: String) {
    data object SignIn : Route("signin")
    data object SignUp : Route("signup")
    data object Profile : Route("profile")
    data object Places : Route("places")
    data object Routes : Route("routes")
    data object RouteDetail : Route("route/{id}") {
        fun build(id: String) = "route/$id"
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
                                navController.navigate(Route.Profile.path) {
                                    popUpTo(Route.SignIn.path) { inclusive = true }
                                }
                            }
                        }
                    )
                }
                composable(Route.SignUp.path) {
                    SignUpScreen(
                        state = uiState,
                        onSignUp = { name, email, password ->
                            viewModel.signUp(name, email, password) {
                                navController.navigate(Route.Profile.path) {
                                    popUpTo(Route.SignUp.path) { inclusive = true }
                                }
                            }
                        },
                        onNavigateToSignIn = { navController.popBackStack() }
                    )
                }
                composable(Route.Profile.path) {
                    ProfileScreen(
                        state = uiState,
                        onSaveProfile = viewModel::updateProfile,
                        onOpenPlaces = { navController.navigate(Route.Places.path) },
                        onOpenRoutes = { navController.navigate(Route.Routes.path) }
                    )
                }
                composable(Route.Places.path) {
                    PlaceListScreen(
                        state = uiState,
                        onSearch = viewModel::loadPlaces,
                        onBack = { navController.popBackStack() }
                    )
                }
                composable(Route.Routes.path) {
                    RoutesScreen(
                        state = uiState,
                        onRefresh = viewModel::loadRoutes,
                        onGenerate = viewModel::generateRoute,
                        onOpenRoute = { id -> navController.navigate(Route.RouteDetail.build(id)) },
                        onBack = { navController.popBackStack() }
                    )
                }
                composable(Route.RouteDetail.path) { entry ->
                    val routeId = entry.arguments?.getString("id").orEmpty()
                    RouteDetailScreen(
                        routeId = routeId,
                        state = uiState,
                        onRefresh = { viewModel.loadRoute(routeId) },
                        onGenerate = { viewModel.generateRoute(routeId) },
                        onBack = { navController.popBackStack() }
                    )
                }
            }
        }
    }
}
