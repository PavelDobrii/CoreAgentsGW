import axios, { type InternalAxiosRequestConfig } from 'axios';
import { type AuthContextProps, TOKEN_STORAGE_KEY } from '@/contexts';
import { showNotification } from '@mantine/notifications';

const AXIOS_CONFIG = {
    baseURL: import.meta.env.VITE_API_URL,
};

const apiClient = axios.create(AXIOS_CONFIG);

const getToken = () => {
    try {
        return window.localStorage.getItem(TOKEN_STORAGE_KEY);
    } catch (error) {
        throw new Error(`Error getting token ${error}`);
    }
};

const onFulfilled = (config: InternalAxiosRequestConfig) => {
    const authToken = getToken();

    if (authToken) {
        config.headers.Authorization = `Bearer ${authToken}`;
    }

    return config;
};

const parseError = ({ error, errors }: { error?: string, errors?: Record<string, string> }) => {
    if (error) return error;
    if (!errors) return 'Неизвестная ошибка';
    return Object.keys(errors)
        .map((errorKey) => errors[errorKey])
        .join('; ');
}


const setupInterceptors = (refreshToken: AuthContextProps['refreshToken']) => {
    const reqId = apiClient.interceptors.request.use(onFulfilled);
    const resId = apiClient.interceptors.response.use(
        r => r,
        async (error) => {
            const { response, config, message } = error;
            console.error(`${message}\n\n  Error: ${response?.data?.error}`);

            const parsedError = parseError(response?.data);
            if (response?.status !== 403 && parsedError) {
                showNotification({
                    message: parsedError,
                    color: 'red',
                    autoClose: 5000,
                });
            }

            if (response?.status === 403 && !config._retry) {
                config._retry = true;
                const data = await refreshToken();
                if (data?.access_token) {
                    config.headers = config.headers || {};
                    config.headers.Authorization = `Bearer ${data.access_token}`;
                    return apiClient(config);
                }
            }
            return Promise.reject(error);
        }
    );

    return () => {
        apiClient.interceptors.request.eject(reqId);
        apiClient.interceptors.response.eject(resId);
    };
};

export {
    apiClient,
    setupInterceptors
};