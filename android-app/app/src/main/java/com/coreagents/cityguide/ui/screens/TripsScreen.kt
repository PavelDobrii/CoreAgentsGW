package com.coreagents.cityguide.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.coreagents.cityguide.viewmodel.CityGuideState

@Composable
fun TripsScreen(
    state: CityGuideState,
    onRefresh: () -> Unit,
    onOpenProfile: () -> Unit,
    onCreate: () -> Unit,
    onOpenTrip: (String) -> Unit
) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = onRefresh) { Text("Обновить") }
            Button(onClick = onCreate) { Text("Новый маршрут") }
            Button(onClick = onOpenProfile) { Text("Профиль") }
        }

        LazyColumn(modifier = Modifier.fillMaxWidth().padding(top = 12.dp)) {
            items(state.trips) { trip ->
                Column(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp)) {
                    Text(trip.name)
                    trip.description?.let { Text(it) }
                    Text("Статус: ${trip.status}")
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Button(onClick = { onOpenTrip(trip.id) }) { Text("Открыть") }
                    }
                }
            }
        }
    }
}
