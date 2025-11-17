import { ScreenView } from '@/components/ScreenView';
import { Button, Stack, Text, Title } from '@mantine/core';
import { useNavigate } from 'react-router';
import { Pickaxe } from 'lucide-react';
import { useDocumentTitle } from '@mantine/hooks';

export const Recover = () => {
    useDocumentTitle('Восстановление доступа — Gowee')
    const navigate = useNavigate();

    return (
        <ScreenView
            footerOptions={{
                onRender: () => (<Button fullWidth mt="md" onClick={() => navigate('/auth/login')}>Вернуться</Button>),
            }}
        >
            <Stack>

                <Title order={1}><Pickaxe/> Раздел в разработке</Title>
                <Text size="md">Возможность восстановления пароля появится в ближайших обновлениях</Text>
            </Stack>
        </ScreenView>
    );
};
