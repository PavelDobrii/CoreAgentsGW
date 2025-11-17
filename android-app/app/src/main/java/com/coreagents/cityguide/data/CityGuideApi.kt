package com.coreagents.cityguide.data

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query

interface CityGuideApi {
    @POST("login")
    suspend fun login(@Body body: AuthRequest): AuthResponse

    @POST("register")
    suspend fun register(@Body body: RegisterRequest): AuthResponse

    @POST("refresh")
    suspend fun refresh(@Body body: RefreshRequest): Tokens

    @GET("profile")
    suspend fun profile(): Profile

    @PUT("profile")
    suspend fun updateProfile(@Body body: ProfileUpdate): Profile

    @GET("routes")
    suspend fun routes(@Query("limit") limit: Int? = null, @Query("offset") offset: Int? = null): TripListResponse

    @GET("routes/{id}")
    suspend fun route(@Path("id") id: String): Trip

    @POST("routes")
    suspend fun createRoute(@Body body: TripRequest): Trip

    @POST("routes/{id}")
    suspend fun updateRoute(@Path("id") id: String, @Body body: TripRequest): Trip

    @POST("routes/{id}/generate")
    suspend fun generate(@Path("id") id: String, @Body body: GenerateTripRequest): GenerateTripResponse
}
