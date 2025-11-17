import { useNavigate } from 'react-router';
import { CalendarDays, Plus } from 'lucide-react';
import { Button, Card, Flex, Image, Loader, Stack, Text } from '@mantine/core';
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

    if (isFetching) {
        return <Flex justify="center" my="lg"><Loader size={30} /></Flex>;
    }

    if (!data?.length) {
        return (
            <Card withBorder>
                <Text mb="lg" mx="auto" size="lg" fw={600}>Путешествия отсутствуют :(</Text>
                <Button onClick={() => navigate('/trip/create/')} leftSection={<Plus />}>Создать путешествие</Button>
            </Card>
        )
    }

    return (
        <Stack>
            {data?.map(({ id, name, createdAt, status, startWaypoint }) => (
                <Card key={id} withBorder onClick={() => onNavigate(id, status)}>
                    <Card.Section display="flex">
                        <Image
                            src={startWaypoint.posterSrc}
                            fallbackSrc="https://placehold.co/64x72"
                            alt={name}
                            h={72}
                            w={64}
                            fit="cover"
                        />
                        <Stack p="xs" gap={4} flex={1} miw={0} justify="space-between">
                            <Flex w="100%" gap="sm" align="center" miw={0}>
                                <Text fw={500} size="md" truncate="end" flex={1} miw={0}>{name}</Text>
                                <StatusField status={status} />
                            </Flex>
                            <Flex align="center" gap={4}>
                                <CalendarDays size={14} />
                                <Text c="dimmed" size="xs">{formatDate(createdAt)}</Text>
                            </Flex>
                        </Stack>
                    </Card.Section>
                </Card>
            ))}
        </Stack>
    );
};
