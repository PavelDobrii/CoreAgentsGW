package com.coreagents.cityguide.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
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
fun TripDetailScreen(
    tripId: String,
    state: CityGuideState,
    onRefresh: () -> Unit,
    onGenerate: () -> Unit,
    onBack: () -> Unit
) {
    val trip = state.currentTrip ?: state.trips.find { it.id == tripId }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = onBack) { Text("Назад") }
            Button(onClick = onRefresh) { Text("Обновить") }
            Button(onClick = onGenerate) { Text("Перегенерировать") }
        }

        trip?.let {
            Text(text = it.name, modifier = Modifier.padding(top = 12.dp))
            it.description?.let { summary -> Text(summary) }
            it.status.let { status -> Text("Статус: $status") }
            LazyColumn(modifier = Modifier.padding(top = 8.dp)) {
                items(it.waypoints.orEmpty()) { point ->
                    Column(modifier = Modifier.padding(vertical = 6.dp)) {
                        Text(point.name)
                        Text(point.address)
                        point.description?.let { desc -> Text(desc) }
                    }
                }
            }
        } ?: Text("Маршрут не найден")

        state.error?.let { Text("Ошибка: $it") }
    }
}
