import type { ProfileResponse } from '@/api/profile';

export type LoginData = {
    email: string,
    password: string
}

export type RegisterData = {
    email: string,
    password: string,
    firstName?: string,
    lastName?: string,
    phoneNumber?: string,
    country?: string,
    city?: string
}

export type Tokens = {
    access_token: string;
    refresh_token: string;
}

export type AuthResponse = Tokens & {
    user: ProfileResponse
}

export type LoginResponse = AuthResponse
export type RegisterResponse = AuthResponse
