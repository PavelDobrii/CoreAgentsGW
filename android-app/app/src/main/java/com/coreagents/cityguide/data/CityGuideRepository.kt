package com.coreagents.cityguide.data

import com.coreagents.cityguide.BuildConfig
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory

class CityGuideRepository {
    private var tokens: Tokens? = null

    private val client: OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BODY })
        .addInterceptor(Interceptor { chain ->
            val request = chain.request().newBuilder().apply {
                tokens?.accessToken?.let { header("Authorization", "Bearer $it") }
            }.build()
            chain.proceed(request)
        })
        .build()

    private val api: CityGuideApi = Retrofit.Builder()
        .baseUrl(BuildConfig.API_BASE_URL)
        .addConverterFactory(
            MoshiConverterFactory.create(
                Moshi.Builder()
                    .add(KotlinJsonAdapterFactory())
                    .build()
            )
        )
        .client(client)
        .build()
        .create(CityGuideApi::class.java)

    suspend fun login(email: String, password: String): Profile = withContext(Dispatchers.IO) {
        val response = api.login(AuthRequest(email = email, password = password))
        tokens = response.tokens()
        response.user
    }

    suspend fun register(
        email: String,
        password: String,
        firstName: String?,
        lastName: String?,
        phone: String?,
        country: String?,
        city: String?
    ): Profile = withContext(Dispatchers.IO) {
        val response = api.register(
            RegisterRequest(
                email = email,
                password = password,
                firstName = firstName,
                lastName = lastName,
                phoneNumber = phone,
                country = country,
                city = city
            )
        )
        tokens = response.tokens()
        response.user
    }

    suspend fun refreshToken(): Tokens = withContext(Dispatchers.IO) {
        val refreshed = api.refresh(RefreshRequest(refreshToken = tokens?.refreshToken.orEmpty()))
        tokens = refreshed
        refreshed
    }

    suspend fun profile(): Profile = withContext(Dispatchers.IO) { api.profile() }

    suspend fun updateProfile(profile: ProfileUpdate): Profile = withContext(Dispatchers.IO) { api.updateProfile(profile) }

    suspend fun trips(limit: Int? = null, offset: Int? = null): List<Trip> = withContext(Dispatchers.IO) {
        api.routes(limit = limit, offset = offset)
    }

    suspend fun trip(id: String): Trip = withContext(Dispatchers.IO) { api.route(id) }

    suspend fun createTrip(body: TripRequest): Trip = withContext(Dispatchers.IO) { api.createRoute(body) }

    suspend fun updateTrip(id: String, body: TripRequest): Trip = withContext(Dispatchers.IO) { api.updateRoute(id, body) }

    suspend fun generateTrip(id: String, request: GenerateTripRequest): GenerateTripResponse =
        withContext(Dispatchers.IO) { api.generate(id, request) }
}
