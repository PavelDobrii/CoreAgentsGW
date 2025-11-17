import { useGeolocationWatcher } from '@/hooks/useGeolocationWatcher.ts';
import { type FC, useEffect, useMemo, useState } from 'react';
import { GoogleMap, InfoWindow, Marker } from '@react-google-maps/api';
import type { Waypoint } from '@/api/trips';
import { FALLBACK_CENTER, GOOGLE_MAP_OPTIONS, MAP_CONTAINER_STYLE } from '@/constants/googleMap.ts';
import { Button, Drawer, Flex, Image, Stack, Text } from '@mantine/core';
import type { MapViewerProps } from '@/components/MapViewer';

export const MapViewer: FC<MapViewerProps> = ({ onRemovePoint, waypoints, defaultZoom = 16, ...props }) => {
    const { userCoords } = useGeolocationWatcher();
    const [selectedMarker, setSelectedMarker] = useState<Waypoint | null>(null);

    const firstPoint = useMemo(() => waypoints[0], [waypoints]);
    const [initialCenter] = useState(() => {
        if (firstPoint) {
            return firstPoint.location;
        }
        return userCoords || FALLBACK_CENTER;
    });

    const closePoint = () => setSelectedMarker(null);
    const handleRemovePoint = () => {
        if (!selectedMarker) return;

        onRemovePoint(selectedMarker.id);
        closePoint();
    };

    useEffect(() => {
        if (!props.opened) closePoint();
    }, [props.opened]);

    return (
        <Drawer styles={{ body: { padding: 0 } }} {...props} title="Выбранные места">
            <GoogleMap
                mapContainerStyle={MAP_CONTAINER_STYLE}
                zoom={defaultZoom}
                center={initialCenter}
                options={GOOGLE_MAP_OPTIONS}
            >
                {waypoints.map((point) => (
                    <Marker
                        key={point.id}
                        position={point.location}
                        onClick={() => setSelectedMarker(point)}
                    />
                ))}
                {selectedMarker && (
                    <MapViewerInfoWindow
                        point={selectedMarker}
                        removePoint={handleRemovePoint}
                        closePoint={closePoint}
                    />
                )}
            </GoogleMap>
        </Drawer>
    );
};

const MapViewerInfoWindow = ({ point, removePoint, closePoint }: {
    point: Waypoint
    removePoint: () => void,
    closePoint: () => void
}) => {
    const { location, posterSrc, address, name, description } = point;

    return (
        <InfoWindow
            position={location}
            options={{ headerDisabled: true, minWidth: 300 }}
        >
            <Stack>
                <Flex direction="column" gap="md">
                    {posterSrc && <Image src={posterSrc} w="100%" h={150} radius="md" />}
                    <Stack gap={0}>
                        <Text c="dark" size="sm">{name}</Text>
                        <Text c="dimmed" size="sm">{address}</Text>
                        <Text mt="md" c="dark" size="sm">{description}</Text>
                    </Stack>
                </Flex>
                <Flex gap="xl" justify="space-between">
                    <Button fullWidth onClick={removePoint} color="red">Удалить</Button>
                    <Button fullWidth onClick={closePoint}>Ок</Button>
                </Flex>
            </Stack>
        </InfoWindow>
    );
};
