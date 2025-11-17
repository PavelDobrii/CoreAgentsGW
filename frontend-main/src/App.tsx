import { AppRouter } from '@/AppRouter.tsx';
import { PlayerProvider, HeaderProvider, ConfirmProvider, useAuthContext } from '@/contexts';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { Notifications } from '@mantine/notifications';

import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import '@mantine/dates/styles.css';

import { useEffect } from 'react';
import { setupInterceptors } from '@/api';
import { localStorageColorSchemeManager, MantineProvider } from '@mantine/core';
import { AppTheme } from '@/lib';
import { useLoadScript } from '@react-google-maps/api';
import { MAP_LIBRARIES } from '@/constants/googleMap.ts';

const THEME_STORAGE_KEY = 'gowee_theme_mode';

export enum ThemeType {
    Dark = 'dark',
    Light = 'light',
    Auto = 'auto',
}

const colorSchemeManager = localStorageColorSchemeManager({
    key: THEME_STORAGE_KEY,
});

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: false,
            retry: 1,
        },
    },
});

export const App = () => {
    const authContext = useAuthContext();

    const { isLoaded, loadError } = useLoadScript({
        googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
        libraries: MAP_LIBRARIES,
    });

    useEffect(() => {
        if (!loadError) return;
        console.error('Map loading error:', loadError);
    }, [loadError]);

    useEffect(() => {
        const eject = setupInterceptors(authContext.refreshToken);
        return () => eject();
    }, [authContext.refreshToken]);

    return (
        <MantineProvider
            theme={AppTheme}
            defaultColorScheme={ThemeType.Auto}
            colorSchemeManager={colorSchemeManager}
        >
            <Notifications position="top-center" limit={1} />

            <QueryClientProvider client={queryClient}>
                <ConfirmProvider>
                    <PlayerProvider>
                        <HeaderProvider>
                            {isLoaded && <AppRouter />}
                        </HeaderProvider>
                    </PlayerProvider>
                </ConfirmProvider>
            </QueryClientProvider>
        </MantineProvider>
    );
};
