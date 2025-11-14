import type { LoginData, LoginResponse, RegisterData, RegisterResponse, Tokens } from './auth.types.ts';
import axios from 'axios';

export const authClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
});

const login = async (data: LoginData): Promise<LoginResponse | null> => {
    try {
        const response = await authClient.post<LoginResponse>('login', data);
        return response.data;
    } catch (e: any) {
        console.error('Login Error:', e);
        return null
    }
};

const register = async (data: RegisterData): Promise<RegisterResponse | null> => {
    try {
        const response = await authClient.post<RegisterResponse>('register', data);
        return response.data;
    } catch (e: any) {
        console.error('Register Error:', e);
        return null
    }
};

const refreshToken = async (token: string): Promise<Tokens> => {
    try {
        const { data } = await authClient.post<Tokens>('/refresh', {
            refreshToken: token
        });

        return data;
    } catch (e: any) {
        console.error('Refresh Token Error:', e);
        throw new Error('Refresh Token Error', e);
    }
};

export const AuthApi = {
    login,
    register,
    refreshToken,
}
