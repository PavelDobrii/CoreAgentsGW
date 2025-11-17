import { Link } from 'react-router';
import { LoginForm, SocialButtonsAuth } from '@/components/Auth';
import { ScreenView } from '@/components/ScreenView';
import { Divider, Flex, Text, Title } from '@mantine/core';
import { useDocumentTitle } from '@mantine/hooks';

export const Login = () => {
    useDocumentTitle('Вход — Gowee')

    return (
        <ScreenView footerOptions={{ onRender: renderFooter, centered: true }}>
            <Flex direction="column" align="center" mb="xl" gap={4}>
                <Title order={1}>Привет</Title>
                <Text size="md">Мы рады видеть тебя!</Text>
            </Flex>

            <LoginForm />

            <Divider my="xl" label="Войти с" />

            <SocialButtonsAuth />
        </ScreenView>
    );
};

const renderFooter = () => (
    <Flex gap={4}>
        <span>Нет аккаунта?</span>
        <Link to="/auth/register">Зарегистрироваться</Link>
    </Flex>
);