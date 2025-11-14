import { GeoPicker } from '@/components/GeoPicker';
import { useHeader } from '@/hooks';
import { ActionIcon, Button, Divider, Flex, Image, Loader, Stack, Text } from '@mantine/core';
import {
    TripApi,
    type TripResponse,
    TripStatus,
    useGenerateTrip,
    type Waypoint,
} from '@/api/trips';
import { useNavigate, useParams } from 'react-router';
import { useEffect, useMemo, useState } from 'react';
import { Map, Trash2 } from 'lucide-react';
import { showNotification } from '@mantine/notifications';
import { MapViewer } from '@/components/MapViewer';
import { useDisclosure, useDocumentTitle } from '@mantine/hooks';
import type { Place } from '@/api/places';

const REFETCH_TIMEOUT = 5000;

type WaypointState = Waypoint & { updated?: boolean }

export const TripCreateById = () => {
    useDocumentTitle('Настройка путешествие — Gowee');
    useHeader({ title: 'Настройка путешествия' });
    const [opened, { open, close }] = useDisclosure(false);
    const { mutate: generateTrip } = useGenerateTrip();

    const navigate = useNavigate();
    const params = useParams<{ id?: string }>();
    const [trip, setTrip] = useState<TripResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [waypoints, setWaypoints] = useState<Array<WaypointState>>([]);
    const [places, setPlaces] = useState<Array<WaypointState>>([]);

    const isCreated = useMemo(() => trip?.status === TripStatus.Created, [trip?.status]);

    const fetchTrip = async () => {
        try {
            const data = await TripApi.getTripById(params.id);
            if (!trip || data.status !== TripStatus.Created) {
                setTrip(data);
                setWaypoints(data.waypoints || []);
            }

            if (data?.status === TripStatus.Created) {
                setTimeout(fetchTrip, REFETCH_TIMEOUT);
            }
        } catch (err) {
            console.error('Ошибка при загрузке путешествия', err);
        }
    };

    const loadTrip = async () => {
        if (!params.id) return;
        setIsLoading(true);

        await fetchTrip();
        setIsLoading(false);

    };

    const handleWaypointChange = (index: number, newValue: Place | null) => {
        if (!newValue || !newValue.id) return;

        const waypointWithId: WaypointState = {
            ...newValue,
            id: newValue.id,
            updated: true,
        };

        setPlaces((prev) => {
            const filteredPrev = prev.filter(({ id }) => id !== waypointWithId.id);
            return [...filteredPrev, waypointWithId];
        });

        setWaypoints((prev) => {
            return prev.map((wp, i) => (i === index ? waypointWithId : wp));
        });
    };

    const handleWaypointRemove = (id: string) => {
        setWaypoints((prev) => prev.filter((point) => point.id !== id));
    };

    const onUpdate = async () => {
        const trip = {
            id: params.id!,
            waypoints: waypoints
                .filter(({ updated }) => !updated)
                .map(({ id }) => id),
            places: places.map(({ id }) => id),
        };

        generateTrip(trip, {
            onSuccess: () => {
                showNotification({
                    title: 'Успех',
                    message: 'Скоро будет сгенерирован гид по маршруту!',
                    color: 'green',
                    autoClose: 3000,
                });

                navigate('/trips');
            },
            onError: (err) => {
                console.error('Ошибка при попытке генерации гида', err);
            },
        });
    };

    useEffect(() => {
        loadTrip();
    }, [params.id]);

    if (isLoading) {
        return <Flex justify="center" my="lg"><Loader size={30} /></Flex>;
    }

    return (
        <Stack>
            <MapViewer
                waypoints={waypoints}
                onRemovePoint={handleWaypointRemove}
                defaultZoom={14}
                opened={opened}
                onClose={close}
            />

            {isCreated && (
                <Stack gap={0}>
                    <Text fw={700}>Маршрут создается</Text>
                    <Text size="xs">Примерное время создание 40 секунд</Text>
                    <Flex justify="center" my="lg"><Loader size={30} /></Flex>
                </Stack>
            )}

            <Text size="xl" fw={700} truncate="end">{trip?.name}</Text>
            <Button disabled={isCreated} w="100%" onClick={open} leftSection={<Map />}>
                Карта
            </Button>

            <Divider />

            <GeoPicker disabled placeholder="Старт маршрута" value={trip?.startWaypoint} />

            {waypoints.map((waypoint, index) => (
                <Stack key={waypoint.id}>
                    {waypoint.description && (
                        <Flex gap="md">
                            {waypoint.posterSrc &&
                                <Image
                                    src={waypoint.posterSrc || 'https://placehold.co/100'}
                                    h={100}
                                    w={100}
                                    miw={100}
                                    radius="md"
                                    fit="cover"
                                />
                            }
                            <Stack gap={0}>
                                <Text size="md" fw={700}>{waypoint.name}</Text>
                                <Text size="xs">{waypoint.description}</Text>
                            </Stack>
                        </Flex>
                    )}
                    <Flex align="center" gap="sm">
                        <GeoPicker
                            placeholder={`Waypoint ${index + 1}`}
                            value={waypoint}
                            onChange={(val) => handleWaypointChange(index, val)}
                        />

                        <ActionIcon
                            color="red"
                            size={36}
                            variant="light"
                            onClick={() => handleWaypointRemove(waypoint.id)}
                        >
                            <Trash2 size={16} />
                        </ActionIcon>
                    </Flex>
                    <Divider />
                </Stack>
            ))}

            <GeoPicker disabled placeholder="Конец маршрута" value={trip?.endWaypoint} />

            <Button size="md" fullWidth disabled={isCreated} onClick={() => onUpdate()}>
                Сохранить места
            </Button>
        </Stack>
    );
};
