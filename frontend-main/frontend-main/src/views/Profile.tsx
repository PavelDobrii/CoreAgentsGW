import { useHeader } from '@/hooks';
import { useProfile } from '@/api/profile';
import { Box, Button, Divider, Flex, Loader, Stack, Text, Title } from '@mantine/core';
import { ThemeSwitcher } from '@/components/ThemeSwitcher.tsx';
import { GOOGLE_MAP_LANGUAGES } from '@/constants/googleMap.ts';
import { HeartHandshake, LogOut, MonitorCog, Pencil, UserRound } from 'lucide-react';
import { useAuthContext, useConfirmation } from '@/contexts';
import { useDisclosure, useDocumentTitle } from '@mantine/hooks';
import { PersonalizationDrawer } from '@/components/Personalization';
import { INTEREST_OPTIONS, TRAVEL_STYLE_OPTIONS } from '@/constants/personalization.ts';
import { Fragment, useMemo } from 'react';

export const Profile = () => {
    useDocumentTitle('Личный кабинет — Gowee');
    useHeader({ title: 'Личный кабинет' });
    const [opened, { open, close }] = useDisclosure(false);
    const { confirmAction } = useConfirmation();
    const { onLogout } = useAuthContext();
    const { data, isFetching } = useProfile();

    const displayData = useMemo(() => {
        if (!data) {
            return null;
        }

        const language = GOOGLE_MAP_LANGUAGES.find(({ value }) => value === data.language);
        const interests = INTEREST_OPTIONS
            .filter(({ value }) => data.interests?.includes(value))
            .map(({ label }) => label)
            .join(', ');

        const travelStyle = TRAVEL_STYLE_OPTIONS.find(({ value }) => value === data.travelStyle);

        return {
            language: language?.label,
            interests,
            travelStyle: travelStyle?.label,
        };
    }, [data]);

    if (isFetching) {
        return <Flex justify="center" my="lg"><Loader size={30} /></Flex>;
    }

    if (!data) {
        return (
            <Stack>
                <Text>Что-то пошло не так при загрузке профиля</Text>
                <Button color="red" variant="light" onClick={onLogout}>Выйти</Button>
            </Stack>
        );
    }

    const handleLogout = async () => {
        const confirmed = await confirmAction({
            confirmLabel: 'Выйти',
        });

        if (!confirmed) {
            return;
        }

        onLogout();
    };

    return (
        <Fragment>
            <PersonalizationDrawer data={data} opened={opened} onClose={close} />
            <Stack gap="xl">
                <Stack>
                    <Divider label={<><UserRound size={14} /> <Box ml={4}>Твой профиль</Box></>} labelPosition="left" />
                    <Text fw={700}>{data.email}</Text>
                </Stack>
                {displayData && (
                    <Stack>
                        <Divider
                            label={<><HeartHandshake size={14} /> <Box ml={4}>Персонализация</Box></>}
                            labelPosition="left"
                        />
                        <Stack gap={4}>
                            <Title order={5}>Язык озвучки:</Title>
                            <Text size="xs">{displayData.language}</Text>
                        </Stack>
                        <Stack gap={4}>
                            <Title order={5}>Интересы:</Title>
                            <Text size="xs">{displayData.interests}</Text>
                        </Stack>
                        <Stack gap={4}>
                            <Title order={5}>Тип путешественника:</Title>
                            <Text size="xs">{displayData.travelStyle}</Text>
                        </Stack>
                        <Button onClick={open} fullWidth leftSection={<Pencil size={20} />}>Изменить</Button>
                    </Stack>
                )}
                <Stack>
                    <Divider label={<><MonitorCog size={14} /> <Box ml={4}>Настройки интерфейса</Box></>}
                             labelPosition="left" />
                    <ThemeSwitcher />
                </Stack>
                <Divider mt="xl" />
                <Button color="red" variant="light" onClick={handleLogout} leftSection={<LogOut size={20} />}>
                    Выйти
                </Button>
            </Stack>
        </Fragment>
    );
};


