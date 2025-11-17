package com.coreagents.cityguide.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColors = lightColorScheme(
    primary = Color(0xFF6750A4),
    onPrimary = Color.White,
    background = Color(0xFFFFFBFE),
    onBackground = Color(0xFF1D1B20)
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFFCFBCFF),
    onPrimary = Color(0xFF381E72),
    background = Color(0xFF1C1B1F),
    onBackground = Color(0xFFE6E1E5)
)

@Composable
fun CityGuideTheme(useDarkTheme: Boolean = isSystemInDarkTheme(), content: @Composable () -> Unit) {
    val colors = if (useDarkTheme) DarkColors else LightColors
    MaterialTheme(colorScheme = colors, content = content)
}
