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
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.coreagents.cityguide.viewmodel.CityGuideState

@Composable
fun PlaceListScreen(
    state: CityGuideState,
    onSearch: () -> Unit,
    onBack: () -> Unit
) {
    val query = remember { mutableStateOf("") }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
            OutlinedTextField(
                value = query.value,
                onValueChange = { query.value = it },
                label = { Text("Search query") },
                modifier = Modifier.weight(1f)
            )
            Button(onClick = onSearch) { Text("Search") }
        }

        Button(onClick = onBack, modifier = Modifier.padding(top = 8.dp)) { Text("Back") }

        LazyColumn(modifier = Modifier.fillMaxSize().padding(top = 12.dp)) {
            items(state.places) { place ->
                Column(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp)) {
                    Text(place.name)
                    Text("(${place.latitude}, ${place.longitude})")
                }
            }
        }
    }
}
