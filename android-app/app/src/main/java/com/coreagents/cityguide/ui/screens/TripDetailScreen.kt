package com.coreagents.cityguide.ui.screens

import android.media.MediaPlayer
import android.widget.Toast
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Map
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.SkipNext
import androidx.compose.material.icons.filled.SkipPrevious
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Slider
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.coreagents.cityguide.data.Trip
import com.coreagents.cityguide.data.Waypoint
import com.coreagents.cityguide.viewmodel.CityGuideState
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TripDetailScreen(
    tripId: String,
    state: CityGuideState,
    onRefresh: () -> Unit,
    onGenerate: () -> Unit,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    val trip = state.currentTrip ?: state.trips.find { it.id == tripId }
    val waypoints = remember(trip?.waypoints) { trip?.waypoints?.sortedBy { it.order } ?: emptyList() }

    val mediaPlayer = remember { MediaPlayer() }
    val isPlaying = remember { mutableStateOf(false) }
    val currentIndex = remember { mutableStateOf(-1) }
    val progress = remember { mutableStateOf(0f) }
    val durationMs = remember { mutableStateOf(0) }
    val sheetOpened = remember { mutableStateOf(false) }

    DisposableEffect(Unit) {
        onDispose { mediaPlayer.release() }
    }

    fun formatSeconds(seconds: Int): String {
        val minutes = seconds / 60
        val remainder = seconds % 60
        return "%d:%02d".format(minutes, remainder)
    }

    fun playWaypoint(index: Int) {
        val item = waypoints.getOrNull(index)
        if (item == null) {
            Toast.makeText(context, "Маршрут не найден", Toast.LENGTH_SHORT).show()
            return
        }

        if (item.audioSrc.isNullOrBlank()) {
            Toast.makeText(context, "Нет аудиозаписи для этой точки", Toast.LENGTH_SHORT).show()
            return
        }

        currentIndex.value = index
        progress.value = 0f

        mediaPlayer.reset()
        mediaPlayer.setDataSource(item.audioSrc)
        mediaPlayer.setOnPreparedListener {
            durationMs.value = it.duration
            it.start()
            isPlaying.value = true
        }
        mediaPlayer.setOnCompletionListener {
            val nextIndex = index + 1
            if (nextIndex < waypoints.size) {
                playWaypoint(nextIndex)
            } else {
                isPlaying.value = false
            }
        }
        mediaPlayer.prepareAsync()
    }

    fun togglePlayPause() {
        if (mediaPlayer.isPlaying) {
            mediaPlayer.pause()
            isPlaying.value = false
        } else {
            try {
                mediaPlayer.start()
                isPlaying.value = true
            } catch (_: IllegalStateException) {
                currentIndex.value.takeIf { it >= 0 }?.let { playWaypoint(it) }
            }
        }
    }

    fun seek(percent: Float) {
        if (durationMs.value == 0) return
        val target = (durationMs.value * percent).toInt()
        mediaPlayer.seekTo(target)
        progress.value = percent
    }

    fun skip(seconds: Int) {
        if (durationMs.value == 0) return
        val current = mediaPlayer.currentPosition / 1000
        val target = ((current + seconds).coerceAtLeast(0)).coerceAtMost(durationMs.value / 1000)
        mediaPlayer.seekTo(target * 1000)
    }

    fun playPrev() {
        val prevIndex = currentIndex.value - 1
        if (prevIndex >= 0) {
            playWaypoint(prevIndex)
        }
    }

    fun playNext() {
        val nextIndex = currentIndex.value + 1
        if (nextIndex < waypoints.size) {
            playWaypoint(nextIndex)
        } else {
            isPlaying.value = false
        }
    }

    LaunchedEffect(isPlaying.value) {
        while (isPlaying.value) {
            val total = mediaPlayer.duration
            val position = mediaPlayer.currentPosition
            durationMs.value = total
            progress.value = if (total > 0) position.toFloat() / total else 0f
            delay(500)
        }
    }

    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            IconButton(onClick = onBack) { Icon(Icons.Default.ArrowBack, contentDescription = "Назад") }
            Button(onClick = onRefresh) { Text("Обновить") }
            Button(onClick = onGenerate) { Text("Перегенерировать") }
        }

        Spacer(Modifier.height(12.dp))

        if (trip == null) {
            Text("Маршрут не найден", style = MaterialTheme.typography.titleMedium)
        } else {
            TripHeader(trip = trip)

            Spacer(Modifier.height(12.dp))

            Button(
                modifier = Modifier.fillMaxWidth(),
                onClick = { sheetOpened.value = true }
            ) {
                Icon(Icons.Default.Map, contentDescription = null)
                Spacer(Modifier.width(8.dp))
                Text("Карта")
            }

            Spacer(Modifier.height(16.dp))

            Text("Точки маршрута", style = MaterialTheme.typography.titleMedium)
            Spacer(Modifier.height(8.dp))
            LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                itemsIndexed(waypoints) { index, point ->
                    val isActive = index == currentIndex.value
                    WaypointCard(
                        point = point,
                        isActive = isActive,
                        onClick = { playWaypoint(index) }
                    )
                }
            }
        }
    }

    if (sheetOpened.value) {
        ModalBottomSheet(
            onDismissRequest = { sheetOpened.value = false },
            sheetState = sheetState
        ) {
            MapOverview(trip = trip, waypoints = waypoints)
        }
    }

    AnimatedVisibility(visible = currentIndex.value >= 0 && trip != null) {
        PlayerBottomSheet(
            waypoint = waypoints.getOrNull(currentIndex.value),
            isPlaying = isPlaying,
            progress = progress,
            durationMs = durationMs,
            onSeek = ::seek,
            onPlayPause = ::togglePlayPause,
            onNext = ::playNext,
            onPrev = ::playPrev,
            onSkip = ::skip,
            formatSeconds = ::formatSeconds
        )
    }
}

@Composable
private fun TripHeader(trip: Trip) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(modifier = Modifier.padding(12.dp), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            AsyncImage(
                model = trip.startWaypoint?.posterSrc ?: "https://placehold.co/120x80",
                contentDescription = trip.name,
                modifier = Modifier
                    .width(120.dp)
                    .height(80.dp)
                    .clip(RoundedCornerShape(12.dp)),
                contentScale = ContentScale.Crop
            )
            Column(modifier = Modifier.weight(1f)) {
                Text(trip.name, style = MaterialTheme.typography.titleMedium, maxLines = 2, overflow = TextOverflow.Ellipsis)
                trip.description?.let {
                    Spacer(Modifier.height(4.dp))
                    Text(it, style = MaterialTheme.typography.bodyMedium, maxLines = 2, overflow = TextOverflow.Ellipsis)
                }
                trip.status.let {
                    Spacer(Modifier.height(6.dp))
                    Text("Статус: $it", color = MaterialTheme.colorScheme.primary, style = MaterialTheme.typography.labelMedium)
                }
            }
        }
    }
}

@Composable
private fun WaypointCard(point: Waypoint, isActive: Boolean, onClick: () -> Unit) {
    val borderColor = if (isActive) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(
            containerColor = if (isActive) MaterialTheme.colorScheme.primary.copy(alpha = 0.08f) else MaterialTheme.colorScheme.surface
        ),
        border = BorderStroke(1.dp, borderColor)
    ) {
        Row(modifier = Modifier.padding(12.dp)) {
            Box(modifier = Modifier.size(80.dp).clip(RoundedCornerShape(12.dp))) {
                AsyncImage(
                    model = point.posterSrc ?: "https://placehold.co/120x80",
                    contentDescription = point.name,
                    contentScale = ContentScale.Crop,
                    modifier = Modifier.matchParentSize()
                )
                if (!isActive) {
                    Box(
                        modifier = Modifier
                            .matchParentSize()
                            .background(Color.Black.copy(alpha = 0.35f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Default.PlayArrow, contentDescription = null, tint = Color.White, modifier = Modifier.size(36.dp))
                    }
                }
            }

            Spacer(Modifier.width(12.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(point.name, style = MaterialTheme.typography.titleSmall, maxLines = 1, overflow = TextOverflow.Ellipsis)
                Text(point.address, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 1, overflow = TextOverflow.Ellipsis)
                point.description?.let {
                    Spacer(Modifier.height(6.dp))
                    Text(it, style = MaterialTheme.typography.bodySmall, maxLines = 2, overflow = TextOverflow.Ellipsis)
                }
            }
        }
    }
}

@Composable
private fun MapOverview(trip: Trip?, waypoints: List<Waypoint>) {
    Column(modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp)) {
        Text("Карта маршрута", style = MaterialTheme.typography.titleLarge)
        Spacer(Modifier.height(12.dp))
        Text(
            text = trip?.encodedPolyline?.takeIf { it.isNotBlank() } ?: "Линия маршрута появится после генерации",
            style = MaterialTheme.typography.bodyMedium
        )
        Spacer(Modifier.height(16.dp))
        waypoints.forEach { point ->
            Column(modifier = Modifier.padding(vertical = 6.dp)) {
                Text(point.name, fontWeight = FontWeight.Bold)
                Text(point.address, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}

@Composable
private fun PlayerBottomSheet(
    waypoint: Waypoint?,
    isPlaying: MutableState<Boolean>,
    progress: MutableState<Float>,
    durationMs: MutableState<Int>,
    onSeek: (Float) -> Unit,
    onPlayPause: () -> Unit,
    onNext: () -> Unit,
    onPrev: () -> Unit,
    onSkip: (Int) -> Unit,
    formatSeconds: (Int) -> String,
) {
    if (waypoint == null) return

    Surface(
        tonalElevation = 8.dp,
        shadowElevation = 12.dp,
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                AsyncImage(
                    model = waypoint.posterSrc ?: "https://placehold.co/200",
                    contentDescription = waypoint.name,
                    modifier = Modifier
                        .size(72.dp)
                        .clip(RoundedCornerShape(12.dp)),
                    contentScale = ContentScale.Crop
                )
                Spacer(Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(waypoint.name, style = MaterialTheme.typography.titleMedium, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    Text(waypoint.address, style = MaterialTheme.typography.bodySmall, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }
                IconButton(onClick = onPlayPause) {
                    Icon(
                        if (isPlaying.value) Icons.Default.Pause else Icons.Default.PlayArrow,
                        contentDescription = "play/pause"
                    )
                }
            }

            Spacer(Modifier.height(12.dp))

            Slider(
                value = progress.value,
                onValueChange = { onSeek(it) },
                modifier = Modifier.fillMaxWidth()
            )
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(formatSeconds((progress.value * durationMs.value).toInt() / 1000))
                Text(formatSeconds(durationMs.value / 1000))
            }

            Spacer(Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = { onSkip(-10) }) { Icon(Icons.Default.SkipPrevious, contentDescription = "Назад 10с") }
                IconButton(onClick = onPrev) { Icon(Icons.Default.SkipPrevious, contentDescription = "Предыдущий") }
                IconButton(onClick = onPlayPause) { Icon(if (isPlaying.value) Icons.Default.Pause else Icons.Default.PlayArrow, contentDescription = "Старт/пауза") }
                IconButton(onClick = onNext) { Icon(Icons.Default.SkipNext, contentDescription = "Следующий") }
                IconButton(onClick = { onSkip(10) }) { Icon(Icons.Default.SkipNext, contentDescription = "Вперед 10с") }
            }
        }
    }
}
