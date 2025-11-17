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
fun TripCreateScreen(
    state: CityGuideState,
    onCreate: (String, String?, String?, List<String>) -> Unit,
    onBack: () -> Unit
) {
    val title = remember { mutableStateOf("") }
    val localityId = remember { mutableStateOf("") }
    val description = remember { mutableStateOf("") }
    val interests = remember { mutableStateOf(state.onboardingNotes) }

    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Создать маршрут")
        OutlinedTextField(value = title.value, onValueChange = { title.value = it }, label = { Text("Название") })
        OutlinedTextField(value = localityId.value, onValueChange = { localityId.value = it }, label = { Text("Код города") })
        OutlinedTextField(value = description.value, onValueChange = { description.value = it }, label = { Text("Описание") })
        OutlinedTextField(
            value = interests.value,
            onValueChange = { interests.value = it },
            label = { Text("Интересы через запятую") }
        )

        Button(
            onClick = {
                onCreate(
                    title.value,
                    localityId.value.ifBlank { null },
                    description.value.ifBlank { null },
                    interests.value.split(',').mapNotNull { it.trim().takeIf(String::isNotEmpty) }
                )
            },
            modifier = Modifier.padding(top = 12.dp)
        ) { Text("Сохранить") }

        Button(onClick = onBack, modifier = Modifier.padding(top = 8.dp)) { Text("Назад") }
        state.error?.let { Text(it) }
    }
}
