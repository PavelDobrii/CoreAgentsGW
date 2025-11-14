import { CalendarDays, CalendarPlus, UserRound } from 'lucide-react';
import { useNavigate } from 'react-router';
import { Button, Group, Stack, Text } from '@mantine/core';
import styles from './Footer.module.css'

export const Footer = () => {
    const navigate = useNavigate()
    const menuItems = [
        {
            title: 'Путешествия',
            Icon: CalendarDays,
            action: () => navigate('/trips')
        },
        {
            title: 'Создать',
            Icon: CalendarPlus,
            action: () => navigate('/trip/create')
        },
        {
            title: 'Профиль',
            Icon: UserRound,
            action: () => navigate('/profile')
        }
    ]

    return (
        <footer className={styles.footer}>
            <Group h="100%" align="center" justify="space-between">
                {menuItems.map(({ title, Icon, action }) => (
                    <Button h="100%" key={title} variant="transparent" size="lg" onClick={action}>
                        <Stack gap={0} align="center" style={{ color: 'var(--mantine-color-text)' }}>
                            <Icon opacity={0.8} size={28} />
                            <Text fz={10}>{title}</Text>
                        </Stack>
                    </Button>
                ))}
            </Group>
        </footer>
    );
};
