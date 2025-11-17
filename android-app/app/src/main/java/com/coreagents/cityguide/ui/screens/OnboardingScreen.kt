package com.coreagents.cityguide.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
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
import com.coreagents.cityguide.viewmodel.CityGuideState

@Composable
fun OnboardingScreen(
    state: CityGuideState,
    onSave: (String) -> Unit
) {
    val notes = remember(state.onboardingNotes) { mutableStateOf(state.onboardingNotes) }

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Как вы путешествуете?")
        OutlinedTextField(
            value = notes.value,
            onValueChange = { notes.value = it },
            label = { Text("Опишите интересы и ожидания") },
            modifier = Modifier.padding(vertical = 12.dp)
        )

        Button(onClick = { onSave(notes.value) }) { Text("Продолжить") }
    }
}
