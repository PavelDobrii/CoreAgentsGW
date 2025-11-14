import { createBrowserRouter, Navigate, RouterProvider } from 'react-router';
import { ErrorLayout, ProtectedLayout } from '@/layouts';
import {
    Auth,
    Login,
    Register,
    Recover,
    Onboarding,
    Profile,
    Trips,
    TripDetails,
    TripCreate,
    TripCreateById,
} from '@/views';

export const AppRouter = () => {
    return <RouterProvider router={appRouter} />;
};

const appRouter = createBrowserRouter([
    {
        path: '/auth',
        errorElement: <ErrorLayout />,
        children: [
            {
                index: true,
                element: <Auth />,
            },
            {
                path: 'login',
                element: <Login />,
            },
            {
                path: 'register',
                element: <Register />,
            },
            {
                path: 'recover',
                element: <Recover />,
            },
        ],
    },
    {
        path: '/onboarding',
        errorElement: <ErrorLayout />,
        element: <Onboarding />,
    },
    {
        path: '/',
        errorElement: <ErrorLayout />,
        element: <ProtectedLayout />,
        children: [
            {
                index: true,
                element: <Navigate to="/trips" />,
            },
            {
                path: 'profile',
                element: <Profile />,
            },
            {
                path: 'trip/create',
                element: <TripCreate />,
            },
            {
                path: 'trip/create/:id',
                element: <TripCreateById />,
            },
            {
                path: 'trips',
                children: [
                    {
                        index: true,
                        element: <Trips />,
                    },
                    {
                        path: ':id',
                        element: <TripDetails />,
                    },
                ],
            },
        ],
    },
]);