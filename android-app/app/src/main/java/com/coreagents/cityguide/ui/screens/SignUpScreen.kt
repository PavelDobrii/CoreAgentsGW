package com.coreagents.cityguide.ui.screens

import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import com.coreagents.cityguide.viewmodel.CityGuideState

@Composable
fun SignUpScreen(
    state: CityGuideState,
    onSignUp: (String, String, String) -> Unit,
    onNavigateToSignIn: () -> Unit
) {
    val name = remember { mutableStateOf("") }
    val email = remember { mutableStateOf("") }
    val password = remember { mutableStateOf("") }

    AuthLayout(title = "Sign Up", state = state) {
        AuthField(label = "Name", value = name)
        AuthField(label = "Email", value = email)
        AuthField(label = "Password", value = password)

        Button(onClick = { onSignUp(name.value, email.value, password.value) }, modifier = Modifier) {
            Text("Create account")
        }

        TextButton(onClick = onNavigateToSignIn) {
            Text("Already have an account? Sign in")
        }
    }
}
