package com.coreagents.cityguide.data

import com.coreagents.cityguide.BuildConfig
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory

class CityGuideRepository {
    private var authToken: String? = null

    private val client: OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BODY })
        .addInterceptor(Interceptor { chain ->
            val request = chain.request().newBuilder().apply {
                authToken?.let { header("Authorization", "Bearer $it") }
            }.build()
            chain.proceed(request)
        })
        .build()

    private val api: CityGuideApi = Retrofit.Builder()
        .baseUrl(BuildConfig.API_BASE_URL)
        .addConverterFactory(MoshiConverterFactory.create())
        .client(client)
        .build()
        .create(CityGuideApi::class.java)

    suspend fun login(email: String, password: String): Profile = withContext(Dispatchers.IO) {
        val profile = api.login(AuthRequest(email = email, password = password))
        authToken = profile.id
        profile
    }

    suspend fun register(name: String, email: String, password: String): Profile = withContext(Dispatchers.IO) {
        val profile = api.register(RegisterRequest(name, email, password))
        authToken = profile.id
        profile
    }

    suspend fun profile(): Profile = withContext(Dispatchers.IO) { api.profile() }

    suspend fun updateProfile(profile: Profile): Profile = withContext(Dispatchers.IO) { api.updateProfile(profile) }

    suspend fun places(): List<Place> = withContext(Dispatchers.IO) { api.places().items }

    suspend fun routes(): List<Route> = withContext(Dispatchers.IO) { api.routes().items }

    suspend fun route(id: String): Route = withContext(Dispatchers.IO) { api.route(id) }

    suspend fun generateRoute(id: String): Route = withContext(Dispatchers.IO) { api.generate(id) }
}
