package com.coreagents.cityguide.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.coreagents.cityguide.data.Profile
import com.coreagents.cityguide.viewmodel.CityGuideState

@Composable
fun ProfileScreen(
    state: CityGuideState,
    onSaveProfile: (Profile) -> Unit,
    onOpenPlaces: () -> Unit,
    onOpenRoutes: () -> Unit
) {
    val profile = state.profile ?: Profile(id = "", name = "", email = "")
    val name = remember(profile.name) { mutableStateOf(profile.name) }
    val city = remember(profile.city) { mutableStateOf(profile.city.orEmpty()) }
    val language = remember(profile.language) { mutableStateOf(profile.language.orEmpty()) }
    val interests = remember(profile.interests) { mutableStateOf(profile.interests.joinToString(", ")) }

    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("Profile")
        OutlinedTextField(value = name.value, onValueChange = { name.value = it }, label = { Text("Name") })
        OutlinedTextField(value = city.value, onValueChange = { city.value = it }, label = { Text("City") })
        OutlinedTextField(value = language.value, onValueChange = { language.value = it }, label = { Text("Language") })
        OutlinedTextField(value = interests.value, onValueChange = { interests.value = it }, label = { Text("Interests (comma separated)") })

        Row(horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
            Button(onClick = {
                onSaveProfile(
                    profile.copy(
                        name = name.value,
                        city = city.value,
                        language = language.value,
                        interests = interests.value.split(',').map { it.trim() }.filter { it.isNotEmpty() }
                    )
                )
            }) { Text("Save") }
            Button(onClick = onOpenPlaces) { Text("Places") }
            Button(onClick = onOpenRoutes) { Text("Routes") }
        }

        state.error?.let { Text("Error: $it") }
    }
}
