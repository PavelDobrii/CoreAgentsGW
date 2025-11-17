package com.coreagents.cityguide.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.coreagents.cityguide.viewmodel.CityGuideState

data class SignUpData(
    val email: String,
    val password: String,
    val firstName: String?,
    val lastName: String?,
    val phone: String?,
    val country: String?,
    val city: String?
)

@Composable
fun SignUpScreen(
    state: CityGuideState,
    onSignUp: (SignUpData) -> Unit,
    onNavigateToSignIn: () -> Unit
) {
    val email = remember { mutableStateOf("") }
    val password = remember { mutableStateOf("") }
    val firstName = remember { mutableStateOf("") }
    val lastName = remember { mutableStateOf("") }
    val phone = remember { mutableStateOf("") }
    val country = remember { mutableStateOf("") }
    val city = remember { mutableStateOf("") }

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Регистрация")
        AuthField(label = "Email", value = email)
        AuthField(label = "Пароль", value = password)
        AuthField(label = "Имя", value = firstName)
        AuthField(label = "Фамилия", value = lastName)
        AuthField(label = "Телефон", value = phone)
        AuthField(label = "Страна", value = country)
        AuthField(label = "Город", value = city)

        Button(
            onClick = {
                onSignUp(
                    SignUpData(
                        email = email.value,
                        password = password.value,
                        firstName = firstName.value.takeIf { it.isNotBlank() },
                        lastName = lastName.value.takeIf { it.isNotBlank() },
                        phone = phone.value.takeIf { it.isNotBlank() },
                        country = country.value.takeIf { it.isNotBlank() },
                        city = city.value.takeIf { it.isNotBlank() }
                    )
                )
            },
            modifier = Modifier.padding(top = 12.dp)
        ) {
            Text("Создать аккаунт")
        }

        TextButton(onClick = onNavigateToSignIn) { Text("Уже есть аккаунт? Войти") }
        state.error?.let { Text(it) }
    }
}
