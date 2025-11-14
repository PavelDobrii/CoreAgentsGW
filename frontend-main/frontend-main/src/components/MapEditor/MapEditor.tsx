import { AspectRatio, Button, Drawer } from '@mantine/core';
import { GoogleMap } from '@react-google-maps/api';
import { type FC, Fragment, useCallback, useState } from 'react';
import { useGeolocation } from '@/hooks';
import type { MapEditorProps } from '@/components/MapEditor';
import {
    FALLBACK_CENTER,
    GOOGLE_MAP_OPTIONS,
    MAP_CONTAINER_STYLE,
    MARKER_STYLE,
} from '@/constants/googleMap.ts';
import { PlacesApi } from '@/api/places';
import type { Location, Place } from '@/api/places';

export const MapEditor: FC<MapEditorProps> = ({ value, onConfirm, ...props }) => {
    const { userCoords } = useGeolocation();
    const handleConfirm = async (selectedPoint: Location) => {
        const place = await PlacesApi.getPlaces(selectedPoint);

        if (place) {
            onConfirm(place[0]);
        }

        props.onClose();
    };

    return (
        <Drawer {...props} title="Выбери локацию" position="bottom" size="100%">
            <MapEditorContent userCoords={userCoords} value={value} onSelect={handleConfirm} />
        </Drawer>
    );
};

export const MapEditorContent: FC<{
    value: Place | null;
    onSelect: (selectedPoint: Location) => void;
    userCoords: Location | null;
}> = ({ value, onSelect, userCoords }) => {
    const [initialCenter] = useState(() => value?.location || userCoords || FALLBACK_CENTER);

    const [map, setMap] = useState<google.maps.Map | null>(null);
    const [selectedPoint, setSelectedPoint] = useState(initialCenter);

    const handleLoad = useCallback((map: google.maps.Map) => setMap(map), []);
    const handleUnmount = useCallback(() => setMap(null), []);

    const handleCenterChanged = useCallback(() => {
        if (!map) return;
        const center = map.getCenter();
        if (!center) return;

        setSelectedPoint({ lat: center.lat(), lng: center.lng() });
    }, [map]);

    return (
        <Fragment>
            <AspectRatio display="flex" flex={1}>
                <GoogleMap
                    mapContainerStyle={MAP_CONTAINER_STYLE}
                    center={initialCenter}
                    zoom={16}
                    onLoad={handleLoad}
                    onUnmount={handleUnmount}
                    onCenterChanged={handleCenterChanged}
                    options={GOOGLE_MAP_OPTIONS}
                >
                    <div style={MARKER_STYLE}>📍</div>
                </GoogleMap>
            </AspectRatio>
            <Button onClick={() => onSelect(selectedPoint)}>Подтвердить</Button>
        </Fragment>
    );
};
