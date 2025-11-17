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
import com.coreagents.cityguide.data.ProfileUpdate
import com.coreagents.cityguide.viewmodel.CityGuideState

@Composable
fun ProfileScreen(
    state: CityGuideState,
    onSaveProfile: (ProfileUpdate) -> Unit,
    onOpenTrips: () -> Unit
) {
    val profile = state.profile ?: Profile(id = "", email = "")
    val language = remember(profile.language) { mutableStateOf(profile.language.orEmpty()) }
    val interests = remember(profile.interests) { mutableStateOf(profile.interests.joinToString(", ")) }
    val city = remember(profile.city) { mutableStateOf(profile.city.orEmpty()) }
    val travelStyle = remember(profile.travelStyle) { mutableStateOf(profile.travelStyle.orEmpty()) }

    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("Профиль")
        OutlinedTextField(value = city.value, onValueChange = { city.value = it }, label = { Text("Город") })
        OutlinedTextField(value = language.value, onValueChange = { language.value = it }, label = { Text("Язык") })
        OutlinedTextField(value = travelStyle.value, onValueChange = { travelStyle.value = it }, label = { Text("Стиль путешествий") })
        OutlinedTextField(
            value = interests.value,
            onValueChange = { interests.value = it },
            label = { Text("Интересы через запятую") }
        )

        Row(horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
            Button(onClick = {
                onSaveProfile(
                    ProfileUpdate(
                        city = city.value.takeIf { it.isNotBlank() },
                        language = language.value.takeIf { it.isNotBlank() },
                        interests = interests.value.split(',').mapNotNull { it.trim().takeIf(String::isNotEmpty) },
                        travelStyle = travelStyle.value.takeIf { it.isNotBlank() }
                    )
                )
            }) { Text("Сохранить") }
            Button(onClick = onOpenTrips) { Text("К поездкам") }
        }

        state.error?.let { Text("Ошибка: $it") }
    }
}
