package com.coreagents.cityguide.data

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path

interface CityGuideApi {
    @POST("login")
    suspend fun login(@Body body: AuthRequest): Profile

    @POST("register")
    suspend fun register(@Body body: RegisterRequest): Profile

    @GET("profile")
    suspend fun profile(): Profile

    @PUT("profile")
    suspend fun updateProfile(@Body body: Profile): Profile

    @GET("places")
    suspend fun places(): PlacesResponse

    @GET("routes")
    suspend fun routes(): RoutesResponse

    @GET("routes/{id}")
    suspend fun route(@Path("id") id: String): Route

    @POST("routes/{id}/generate")
    suspend fun generate(@Path("id") id: String): Route
}
