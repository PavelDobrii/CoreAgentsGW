import Logo from '/logo.svg';
import { Button, Flex, Stack } from '@mantine/core';
import { useNavigate } from 'react-router';
import { ScreenView } from '@/components/ScreenView';

export const Auth = () => {
    const navigate = useNavigate();
    return (
        <ScreenView footerOptions={{ onRender: renderFooter, centered: true }}>
            <Stack gap={96}>
                <Flex justify="center"><img src={Logo} alt="Gowee" /></Flex>

                <Flex direction="column" gap="lg">
                    <Button fullWidth size="md" onClick={() => navigate('/auth/login')}>
                        Вход
                    </Button>

                    <Button fullWidth size="md" variant="light" color="dark" onClick={() => navigate('/auth/register')}>
                        Регистрация
                    </Button>
                </Flex>
            </Stack>
        </ScreenView>
    );
};

// const renderFooter = () => (<Link to="/?mode=guest">Продолжить как гость</Link>);
const renderFooter = () => null;
