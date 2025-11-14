import { useNavigate } from 'react-router';
import { CalendarDays } from 'lucide-react';
import { Card, Divider, Flex, Image, Loader, Stack, Text } from '@mantine/core';
import { TripStatus, useTrips } from '@/api/trips';
import { useHeader } from '@/hooks';
import { formatDate } from '@/lib';
import { showNotification } from '@mantine/notifications';
import { StatusField } from '@/components/StatusField.tsx';
import { useDocumentTitle } from '@mantine/hooks';

export const Trips = () => {
    useDocumentTitle('Мои путешествия — Gowee');
    useHeader({ title: 'Мои путешествия' });

    const navigate = useNavigate();
    const { data, isFetching, refetch } = useTrips();

    if (isFetching) {
        return <Flex justify="center" my="lg"><Loader size={30} /></Flex>;
    }

    const onNavigate = (id: string, status: TripStatus) => {
        const searchParams = new URLSearchParams();
        searchParams.set('id', id);
        searchParams.set('status', status);

        if (status === TripStatus.InProgress) {
            refetch()
            showNotification({
                title: 'Путешествие создается',
                message: 'Путешествие скоро будет создано, немного подождите :)',
                color: 'green',
                autoClose: 3000,
            });
            return;
        }

        if (status === TripStatus.Draft || status === TripStatus.Created) {
            navigate(`/trip/create/${id}`);
        }

        if (status === TripStatus.Success) {
            navigate(`/trips/${id}`);
        }
    };

    return (
        <Stack>
            {data?.map(({ id, name, createdAt, status, startWaypoint }) => (
                <Card key={id} withBorder onClick={() => onNavigate(id, status)}>
                    <Card.Section display="flex">
                        <Image
                            src={startWaypoint.posterSrc || 'https://placehold.co/80x80'}
                            alt={name}
                            h={80}
                            w={80}
                            fit="cover"
                        />
                        <Stack p="xs" gap={4} flex={1} miw={0}>
                            <Flex w="100%" gap="sm" align="center" miw={0}>
                                <Text fw={700} size="md" truncate="end" flex={1} miw={0}>{name}</Text>
                                <StatusField status={status} />
                            </Flex>
                            <Divider />

                            <Flex align="center" gap={4}>
                                <CalendarDays size={16} />
                                <Text size="sm" c="dimmed">{formatDate(createdAt)}</Text>
                            </Flex>
                        </Stack>
                    </Card.Section>
                </Card>
            ))}
        </Stack>
    );
};
