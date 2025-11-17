import { createContext, type ReactNode, useContext, useMemo, useState } from 'react';
import type { LoginData, LoginResponse, RegisterData, RegisterResponse, Tokens } from '@/api/auth';
import { AuthApi } from '@/api/auth';
import { useLocalStorage } from '@/hooks';

export const TOKEN_STORAGE_KEY = 'gowee_token';
export const REFRESH_TOKEN_STORAGE_KEY = 'gowee_r_token';

export type AuthContextProps = {
    isAuth: boolean;
    token: string | null;
    rToken: string | null;
    isRefreshingToken: boolean;
    onRegister: (data: RegisterData) => Promise<RegisterResponse | null>;
    onLogin: (data: LoginData) => Promise<LoginResponse | null>;
    onLogout: () => void;
    refreshToken: () => Promise<Tokens | null>;
}

let refreshPromise: Promise<Tokens | null> | null = null;

const AuthContext = createContext<AuthContextProps | null>(null);

export const AuthProvider = (({ children }: { children: ReactNode }) => {
    const [token, setToken] = useLocalStorage<string | null>(TOKEN_STORAGE_KEY, null);
    const [rToken, setRToken] = useLocalStorage<string | null>(REFRESH_TOKEN_STORAGE_KEY, null);
    const [isRefreshingToken, setIsRefreshingToken] = useState(false);

    const onRegister = async (data: RegisterData): Promise<RegisterResponse | null> => {
        const response = await AuthApi.register(data);
        if (response?.access_token) {
            setToken(response.access_token);
            setRToken(response.refresh_token);
            return response;
        }

        return null;
    };

    const onLogin = async (data: LoginData): Promise<LoginResponse | null> => {
        const response = await AuthApi.login(data);
        if (response?.access_token) {
            setToken(response.access_token);
            setRToken(response.refresh_token);
            return response;
        }

        return null;
    };

    const onLogout = () => {
        setToken(null);
        setRToken(null);
    };

    const refreshToken = async (): Promise<Tokens | null> => {
        const currentRToken = window.localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);

        if (!currentRToken) return null;
        if (refreshPromise) return refreshPromise;

        setIsRefreshingToken(true);

        refreshPromise = (async () => {
            try {
                const response = await AuthApi.refreshToken(currentRToken);
                if (response?.access_token) {
                    setToken(response.access_token);
                    setRToken(response.refresh_token || currentRToken);
                    return response;
                }
                onLogout();
                return null;
            } catch (err) {
                console.error(err);
                onLogout();
                return null;
            } finally {
                setIsRefreshingToken(false);
                refreshPromise = null;
            }
        })();

        return refreshPromise;
    };

    const context = useMemo(() => ({
        isAuth: !!token,
        token,
        rToken,
        onRegister,
        onLogin,
        onLogout,
        refreshToken,
        isRefreshingToken,
    }), [token]);

    return (
        <AuthContext.Provider value={context}>
            {children}
        </AuthContext.Provider>
    );
});

export const useAuthContext = () => {
    const context = useContext(AuthContext);

    if (context === null || context === undefined) {
        throw new Error('AppContext cannot be null');
    }

    return context;
};
