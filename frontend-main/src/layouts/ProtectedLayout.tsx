import { BaseLayout } from './BaseLayout';
import { useAuthContext } from '@/contexts';
import { Navigate, useLocation } from 'react-router';
import { Flex, Loader } from '@mantine/core';
import { useEffect } from 'react';

export const ProtectedLayout = () => {
    const { isAuth, rToken, isRefreshingToken, refreshToken } = useAuthContext();
    const location = useLocation();

    useEffect(() => {
        if (!isAuth && rToken) {
            void refreshToken();
        }
    }, [isAuth, rToken, refreshToken]);

    if (!isAuth && (rToken || isRefreshingToken)) {
        return <Flex justify="center" my="lg"><Loader size={30} /></Flex>;
    }

    if (!isAuth) {
        return <Navigate to="/auth" state={{ from: location }} replace />;
    }

    if (location.state?.from) {
        const from = location.state.from.pathname || '/';
        return <Navigate to={from} replace />;
    }

    return <BaseLayout />;
};
