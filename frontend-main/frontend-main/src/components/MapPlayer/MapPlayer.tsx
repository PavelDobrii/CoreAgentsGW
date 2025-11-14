import { type FC, useMemo, useState } from 'react';
import type { MapPlayerProps } from '@/components/MapPlayer';
import { useGeolocationWatcher } from '@/hooks/useGeolocationWatcher.ts';
import { usePlayerContext } from '@/contexts';
import { FALLBACK_CENTER, GOOGLE_MAP_OPTIONS, MAP_CONTAINER_STYLE } from '@/constants/googleMap.ts';
import { GoogleMap, InfoWindow, Marker, Polyline } from '@react-google-maps/api';
import { Button, Drawer, Flex, Image, Stack, Text } from '@mantine/core';
import { Play } from 'lucide-react';
import type { Waypoint } from '@/api/trips';

export const MapPlayer: FC<MapPlayerProps> = ({
    startWaypoint,
    waypoints,
    onPlaySong,
    encodedPolyline,
    defaultZoom = 16,
    ...props
}) => {
    const { userCoords } = useGeolocationWatcher();
    const { currentSong } = usePlayerContext();
    const [selectedMarker, setSelectedMarker] = useState<Waypoint | null>(null);

    const closePoint = () => setSelectedMarker(null);
    const playSong = () => selectedMarker && onPlaySong(selectedMarker);

    const center = useMemo(
        () => (currentSong?.location || startWaypoint?.location || FALLBACK_CENTER),
        [currentSong?.location, startWaypoint?.location],
    );

    return (
        <Drawer {...props}>
            <GoogleMap
                mapContainerStyle={MAP_CONTAINER_STYLE}
                zoom={defaultZoom}
                center={center}
                options={GOOGLE_MAP_OPTIONS}
            >
                <Marker
                    key={startWaypoint.id}
                    position={startWaypoint.location}
                    label="Start point"
                />

                {userCoords && (
                    <Marker
                        position={userCoords}
                        options={{ icon: '/map-icons/penguin.svg' }}
                    />
                )}

                {waypoints.map((point) => (
                    <Marker
                        animation={point.id === currentSong?.id ? google.maps.Animation.BOUNCE : undefined}
                        label={point.id === currentSong?.id ? 'Playing' : undefined}
                        key={point.id}
                        position={point.location}
                        onClick={() => setSelectedMarker(point)}
                    />
                ))}

                {selectedMarker && (
                    <InfoWindow
                        position={selectedMarker.location}
                        options={{ headerDisabled: true, minWidth: 300 }}
                    >
                        <div>
                            <Stack>
                                <Flex direction="column" gap="md">
                                    {selectedMarker.posterSrc &&
                                        <Image src={selectedMarker.posterSrc} w="100%" h={150} radius="md" />}
                                    <Stack gap={0}>
                                        <Text c="dark" size="sm">{selectedMarker.name}</Text>
                                        <Text c="dark" size="sm">{selectedMarker.address}</Text>
                                        <Text mt="md" c="dark" size="sm">{selectedMarker.description}</Text>
                                    </Stack>
                                </Flex>
                                <Flex gap="md" justify="space-between">
                                    <Button onClick={closePoint} color="dark">Свернуть</Button>
                                    <Button onClick={playSong} leftSection={<Play size={24} />}>Слушать</Button>
                                </Flex>
                            </Stack>
                        </div>
                    </InfoWindow>
                )}

                {encodedPolyline && (
                    <Polyline
                        path={google.maps.geometry.encoding.decodePath(encodedPolyline)}
                        options={{
                            strokeColor: 'rgb(13,131,243)',
                            strokeOpacity: 0.8,
                            strokeWeight: 4,
                        }}
                    />
                )}
            </GoogleMap>
        </Drawer>
    );
};
