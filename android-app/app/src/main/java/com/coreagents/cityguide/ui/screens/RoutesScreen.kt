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
fun RoutesScreen(
    state: CityGuideState,
    onRefresh: () -> Unit,
    onGenerate: (String) -> Unit,
    onOpenRoute: (String) -> Unit,
    onBack: () -> Unit
) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = onRefresh) { Text("Refresh routes") }
            Button(onClick = onBack) { Text("Back") }
        }

        LazyColumn(modifier = Modifier.fillMaxWidth().padding(top = 12.dp)) {
            items(state.routes) { route ->
                Column(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp)) {
                    Text(route.title)
                    route.summary?.let { Text(it) }
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Button(onClick = { onOpenRoute(route.id) }) { Text("Open") }
                        Button(onClick = { onGenerate(route.id) }) { Text("Generate") }
                    }
                }
            }
        }
    }
}
