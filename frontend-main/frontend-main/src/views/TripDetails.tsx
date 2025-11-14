import { type SongItem, usePlayerContext } from '@/contexts';
import { useMemo } from 'react';
import { useNavigate, useParams } from 'react-router';
import { CalendarDays, ChevronLeft, Map } from 'lucide-react';
import {
    ActionIcon,
    Button, Card,
    Flex,
    Image,
    Indicator,
    Loader,
    Stack,
    Text,
    Timeline,
} from '@mantine/core';
import { useHeader } from '@/hooks';
import { useTripsById, type Waypoint } from '@/api/trips';
import { formatDate } from '@/lib';
import { useDisclosure, useDocumentTitle } from '@mantine/hooks';
import { MapPlayer } from '@/components/MapPlayer';

export const TripDetails = () => {
    useDocumentTitle('Детали путешествия — Gowee');
    const navigate = useNavigate();
    const [opened, { open, close }] = useDisclosure(false);

    useHeader({
        action: (
            <ActionIcon size="lg" variant="light" color="dark" onClick={() => navigate('/trips')}>
                <ChevronLeft />
            </ActionIcon>
        ),
    });
    const { onPlay, currentSong, initPlayer, isPlaying } = usePlayerContext();
    const params = useParams<{ id: string }>();

    const { data, isFetching, isError } = useTripsById(params.id);

    const songs: Array<SongItem> = useMemo(() => {
        if (!data?.waypoints) {
            return [];
        }

        return data.waypoints.map(({ id, name, audioSrc, address, text, order, posterSrc, location }) => ({
            id,
            title: name,
            audioSrc: audioSrc || '',
            posterSrc: posterSrc || 'https://placehold.co/200',
            address,
            text,
            order,
            location,
        }));
    }, [data]);

    const handlePlay = ({ id, name, audioSrc, address, text, order, location, posterSrc }: Waypoint) => {
        const song: SongItem = {
            id, address, text, order,
            title: name,
            audioSrc: audioSrc || '',
            posterSrc: posterSrc || 'https://placehold.co/200',
            location,
        };

        if (!song.audioSrc) {
            console.error(`Audio src not found: "${song.audioSrc}"`);
            return;
        }

        initPlayer(songs);
        onPlay(song);
    };

    const activeTimelineIndex = songs.findIndex(({ id }) => currentSong?.id === id);

    if (isFetching) {
        return <Flex justify="center" my="lg"><Loader size={30} /></Flex>;
    }

    if (!data || isError) {
        return <Text>Что-то пошло не так, данных нет</Text>;
    }

    return (
        <Stack>
            <Flex align="start" gap="sm">
                <Image
                    src={data.startWaypoint.posterSrc || 'https://placehold.co/84x56'}
                    alt={data.name}
                    h={56}
                    w={84}
                    radius="md"
                    fit="cover"
                />

                <Stack gap={0} style={{ flex: 1, minWidth: 0 }}>
                    <Text lineClamp={1} fw={700} size="lg" truncate="end" p={0}>{data.name}</Text>
                    <Flex align="center" gap={4}>
                        <CalendarDays size={14} />
                        <Text c="dimmed" size="xs">{formatDate(data.createdAt)}</Text>
                    </Flex>
                </Stack>
            </Flex>

            <Button w="100%" onClick={open} leftSection={<Map />}>
                Карта
            </Button>

            <Timeline active={activeTimelineIndex} bulletSize={10} lineWidth={1}>
                {data.waypoints?.map((point) => {
                    const isActive = currentSong?.id === point.id;

                    const bg = isActive
                        ? 'var(--mantine-primary-color-light)'
                        : 'var(--mantine-color-body)';
                    const style = {
                        cursor: 'pointer',
                        borderColor: isActive
                            ? 'var(--mantine-primary-color-filled)'
                            : 'var(--mantine-color-default-border)',
                        transform: isActive ? 'scale(1.01)' : 'none',
                    };

                    const bullet = isActive && <Indicator inline processing={isPlaying} size={12} />

                    return (
                        <Timeline.Item key={point.id} bullet={bullet}>
                            <Card
                                withBorder
                                onClick={() => handlePlay(point)}
                                shadow={isActive ? 'sm' : 'none'}
                                bg={bg}
                                style={style}
                            >
                                <Card.Section display="flex">
                                    <Image
                                        src={point.posterSrc || 'https://placehold.co/56x100'}
                                        alt={point.name}
                                        h="auto"
                                        w={64}
                                        fit="cover"
                                    />
                                    <Stack p="xs" gap={4} flex={1} miw={0}>
                                        <Text size="sm" fw={700} lineClamp={1}>
                                            {point.name}
                                        </Text>
                                        <Text size="xs" c="dimmed" lineClamp={1}>
                                            {point.address}
                                        </Text>
                                        <Text size="xs"   style={{ color: 'var(--mantine-color-text)', opacity: 0.75 }}
                                              lineClamp={3}>
                                            {point.description}
                                        </Text>
                                    </Stack>
                                </Card.Section>
                            </Card>
                        </Timeline.Item>
                    );
                })}
            </Timeline>

            <MapPlayer
                opened={opened}
                onClose={close}
                title={data.name}
                startWaypoint={data.startWaypoint}
                waypoints={data.waypoints || []}
                encodedPolyline={data.encodedPolyline}
                onPlaySong={handlePlay}
            />
        </Stack>
    );
};
