import { isRouteErrorResponse, useNavigate, useRouteError } from 'react-router';
import { useEffect, useState } from 'react';
import { Button, Stack, Text, Title } from '@mantine/core';
import { ScreenView } from '@/components/ScreenView';

export const ErrorLayout = () => {
    const error = useRouteError();
    const navigate = useNavigate();
    const [message, setMessage] = useState('');

    useEffect(() => {
        if (isRouteErrorResponse(error)) {
            setMessage(`${error.status} ${error.statusText}`);
        } else if (error instanceof Error) {
            setMessage(error.message);
        } else {
            setMessage('Unknown error');
        }
    }, [error]);

    return (
        <ScreenView
            footerOptions={{
                onRender: () => (<Button fullWidth onClick={() => navigate('/trips')}>Вернуться на главную</Button>),
            }}
        >
            <Stack py="xl" px="md">
                <Title order={2}>Something went wrong</Title>
                <Text>{message}</Text>
            </Stack>
        </ScreenView>
    );
};