import { Button, Stack } from '@mantine/core';
import GLogo from '/g_logo.svg';
import FLogo from '/f_logo.svg';
import { showNotification } from '@mantine/notifications';

export const SocialButtonsAuth = () => {
    const onClick = () => {
        showNotification({
            message: 'Авторизация через Google и Facebook появится в следующем обновлении',
            color: 'blue',
            autoClose: 3000
        })
    }
    return (
        <Stack>
            <Button
                color="orange"
                variant="light"
                size="md"
                fullWidth
                radius="xl"
                leftSection={<img src={GLogo} height={20} width={20} alt="Google" />}
                onClick={onClick}
            >
                Google
            </Button>

            <Button
                color="blue"
                variant="light"
                size="md"
                radius="xl"
                leftSection={<img src={FLogo} height={20} width={20} alt="Facebook" />}
                onClick={onClick}
            >
                Facebook
            </Button>
        </Stack>
    );
};
