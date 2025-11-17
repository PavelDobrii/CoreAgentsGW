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
fun RouteDetailScreen(
    routeId: String,
    state: CityGuideState,
    onRefresh: () -> Unit,
    onGenerate: () -> Unit,
    onBack: () -> Unit
) {
    val route = state.currentRoute ?: state.routes.find { it.id == routeId }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = onBack) { Text("Back") }
            Button(onClick = onRefresh) { Text("Refresh") }
            Button(onClick = onGenerate) { Text("Generate") }
        }

        route?.let {
            Text(text = it.title, modifier = Modifier.padding(top = 12.dp))
            it.summary?.let { summary -> Text(summary) }
            LazyColumn(modifier = Modifier.padding(top = 8.dp)) {
                items(it.points) { point ->
                    Column(modifier = Modifier.padding(vertical = 6.dp)) {
                        Text(point.name)
                        point.description?.let { desc -> Text(desc) }
                    }
                }
            }
        } ?: Text("Route not loaded")

        state.error?.let { Text("Error: $it") }
    }
}
