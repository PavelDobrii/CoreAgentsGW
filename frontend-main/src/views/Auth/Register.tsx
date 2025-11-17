import { Link } from 'react-router';
import { RegisterForm, SocialButtonsAuth } from '@/components/Auth';
import { ScreenView } from '@/components/ScreenView';
import { Divider, Flex, Text, Title } from '@mantine/core';
import { useDocumentTitle } from '@mantine/hooks';

export const Register = () => {
    useDocumentTitle('Регистрация — Gowee')

    return (
        <ScreenView footerOptions={{ onRender: renderFooter, centered: true }}>
            <Flex direction="column" align="center" mb="xl" gap={4}>
                <Title order={1}>Создай аккаунт</Title>
                <Text size="md">И начни путешествие!</Text>
            </Flex>

            <RegisterForm />

            <Divider my="xl" label="Зарегестрироваться с" />

            <SocialButtonsAuth />
        </ScreenView>
    );
};

const renderFooter = () => (
    <Flex gap={4}>
        <span>Есть аккаунт?</span>
        <Link to="/auth/login">Вход</Link>
    </Flex>
);