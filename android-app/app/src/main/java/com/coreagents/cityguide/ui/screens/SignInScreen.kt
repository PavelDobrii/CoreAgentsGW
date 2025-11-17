package com.coreagents.cityguide.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.coreagents.cityguide.viewmodel.CityGuideState

@Composable
fun SignInScreen(
    state: CityGuideState,
    onLogin: (String, String) -> Unit,
    onNavigateToSignUp: () -> Unit
) {
    val email = remember { mutableStateOf("") }
    val password = remember { mutableStateOf("") }

    AuthLayout(title = "Добро пожаловать", state = state) {
        AuthField(label = "Email", value = email)
        AuthField(label = "Пароль", value = password)

        Button(onClick = { onLogin(email.value, password.value) }, modifier = Modifier.padding(top = 8.dp)) {
            Text("Войти")
        }

        TextButton(onClick = onNavigateToSignUp) { Text("Создать новый профиль") }
    }
}

@Composable
fun AuthLayout(
    title: String,
    state: CityGuideState,
    content: @Composable () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = title)
        if (state.isLoading) {
            CircularProgressIndicator(modifier = Modifier.padding(12.dp))
        }
        state.error?.let { Text(text = it) }
        content()
    }
}

@Composable
fun AuthField(label: String, value: MutableState<String>) {
    OutlinedTextField(
        value = value.value,
        onValueChange = { value.value = it },
        label = { Text(label) },
        modifier = Modifier.padding(vertical = 4.dp)
    )
}
